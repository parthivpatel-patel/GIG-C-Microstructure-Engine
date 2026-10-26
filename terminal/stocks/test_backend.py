"""Backend audit regressions:authored disclosures only,never SEC observations."""
import copy,unittest
from decimal import Decimal,localcontext
from . import sec
from .test_workspace import submissions,facts,CIK

class Integrity(unittest.TestCase):
    def test_exact_magnitude_check_ignores_decimal_context_rounding(self):
        over=Decimal('1000000000000000000000000000000.000000000001')
        for precision in (8,28,80):
            with localcontext() as context:
                context.prec=precision
                with self.assertRaisesRegex(ValueError,'sec_numeric'):sec.exact(over)
                with self.assertRaisesRegex(ValueError,'sec_numeric'):sec.exact(over.copy_negate())
                from .option_feed import signed
                edge=Decimal('1000000.000000000001')
                for candidate in (edge,edge.copy_negate()):
                    with self.assertRaisesRegex(ValueError,'option_model_value'):signed(candidate)
                self.assertEqual(signed(Decimal('1000000')),'1000000')
    def test_duplicate_accession_cannot_disagree_about_filing(self):
        p=submissions();p['filings']['recent']['accessionNumber'][1]=p['filings']['recent']['accessionNumber'][0]
        with self.assertRaisesRegex(ValueError,'contradictory'):sec.filings(p,CIK)


class Structure(unittest.TestCase):
    def test_malformed_provider_containers_are_structured_failures(self):
        for field in ('facts','filings'):
            for malformed in ([],None,'invalid'):
                p={'cik':320193,field:malformed}
                with self.assertRaisesRegex(ValueError,'sec_structure'):
                    sec.facts(p,CIK,'2024-12-31') if field=='facts' else sec.filings(p,CIK)
        for p in ([],None):
            with self.assertRaisesRegex(ValueError,'sec_structure'):sec.facts(p,CIK,'2024-12-31')
    def test_malformed_concept_units_cannot_be_silently_accepted(self):
        for entry in ([],{'units':[]}):
            p=facts();p['facts']['us-gaap']['Revenues']=entry
            with self.assertRaisesRegex(ValueError,'sec_structure'):sec.facts(p,CIK,'2024-12-31')

class FinancialMetrics(unittest.TestCase):
    def normalized(self):
        from .test_workspace import fact
        p=facts();g=p['facts']['us-gaap'];add=lambda tag,rows:g.update({tag:{'units':{'USD':rows}}})
        add('GrossProfit',[fact(60)]);add('OperatingIncomeLoss',[fact(40)]);add('NetCashProvidedByUsedInOperatingActivities',[fact(30)]);add('PaymentsToAcquirePropertyPlantAndEquipment',[fact(10)])
        add('AssetsCurrent',[fact(400,None)]);add('LiabilitiesCurrent',[fact(200,None)]);add('StockholdersEquity',[fact(600,None),fact(400,None,end='2022-12-31',filed='2023-02-01')])
        add('Assets',[fact(1000,None),fact(800,None,end='2022-12-31',filed='2023-02-01')]);add('ShortTermBorrowings',[fact(10,None)]);add('LongTermDebtCurrent',[fact(20,None)]);add('LongTermDebtNoncurrent',[fact(30,None)])
        add('NetIncomeLoss',[fact(20),fact(16,start='2022-01-01',end='2022-12-31',filed='2023-02-01')]);g['EarningsPerShareDiluted']={'units':{'USD/shares':[fact(Decimal('2.5')),fact(2,start='2022-01-01',end='2022-12-31',filed='2023-02-01')]}}
        add('Revenues',[fact(100),fact(80,start='2022-01-01',end='2022-12-31',filed='2023-02-01',accn='0000000123-23-000001')])
        return sec.facts(p,CIK,'2024-12-31')
    def calc(self,n=None):
        from .financials import calculate
        return calculate(n or self.normalized())['metrics']
    def value(self,m):
        from fractions import Fraction
        self.assertEqual(m['status'],'AVAILABLE',m['reason']);v=m['value'];return Fraction(int(v['numerator']),int(v['denominator']))
    def test_independent_fraction_formulas_and_average_balances(self):
        from fractions import Fraction
        x=self.calc()
        references={'gross_margin':Fraction(3,5),'operating_margin':Fraction(2,5),'net_profit_margin':Fraction(1,5),'current_ratio':Fraction(2),'debt_to_equity':Fraction(1,10),'free_cash_flow':Fraction(20),'cash_conversion':Fraction(3,2),'return_on_assets':Fraction(1,45),'return_on_equity':Fraction(1,25),'annual_revenue_growth':Fraction(1,4),'annual_net_income_growth':Fraction(1,4),'annual_eps_growth':Fraction(1,4)}
        for name,expected in references.items():self.assertEqual(self.value(x[name]),expected,name)
    def test_missing_beginning_balance_never_uses_ending_proxy(self):
        n=self.normalized();n['history']['assets']=n['history']['assets'][:1];m=self.calc(n)['return_on_assets'];self.assertIsNone(m['value']);self.assertIn('missing_compatible',m['reason'])
    def test_no_quarter_subtraction_or_ytd_annualization(self):
        n=self.normalized();n['history']['net_income'][0]['start']='2023-07-01';x=self.calc(n);self.assertIsNone(x['net_profit_margin']['value']);self.assertIsNone(x['cash_conversion']['value']);self.assertEqual(x['return_on_assets']['period']['start'],'2023-07-01')
    def test_ambiguous_revenue_and_missing_debt_never_zero(self):
        n=self.normalized();r=copy.deepcopy(n['history']['revenue'][0]);r['concept']='DifferentRevenueConcept';r['value']='101';n['history']['revenue'].append(r);n['history']['short_term_borrowings']=[];x=self.calc(n);self.assertIsNone(x['net_profit_margin']['value']);self.assertIn('ambiguous',x['net_profit_margin']['reason']);self.assertIsNone(x['debt_to_equity']['value'])
    def test_latest_period_missing_denominator_does_not_fall_back(self):
        n=self.normalized();n['history']['liabilities_current'][0]['end']='2022-12-31';self.assertIsNone(self.calc(n)['current_ratio']['value'])
    def test_negative_base_and_zero_denominator_are_explicit(self):
        n=self.normalized();n['history']['revenue'][1]['value']='0';n['history']['liabilities_current'][0]['value']='0';x=self.calc(n);self.assertEqual(x['annual_revenue_growth']['reason'],'non_positive_growth_base');self.assertEqual(x['current_ratio']['reason'],'non_positive_current_liabilities')
    def test_missing_growth_pair_and_53_week_boundaries(self):
        n=self.normalized();n['history']['revenue'][0].update(start='2023-01-01',end='2024-01-06',duration_days=371);x=self.calc(n);self.assertEqual(self.value(x['annual_revenue_growth']),__import__('fractions').Fraction(1,4));self.assertEqual(x['annual_revenue_growth']['period']['duration_days'],371)
        n['history']['revenue'][0]['start']='2023-01-02';self.assertIsNone(self.calc(n)['annual_revenue_growth']['value'])
    def test_fiscal_context_revisions_precision_and_source_ids(self):
        from .test_workspace import fact
        p=facts();row=p['facts']['us-gaap']['Revenues']['units']['USD'][0];row.update(fy=2024,fp='Q1',frame='CY2023');p['facts']['us-gaap']['Revenues']['units']['USD'].append(fact(Decimal('110.1234567890123456'),filed='2024-03-01',accn='0000000123-24-000002'))
        n=sec.facts(p,CIK,'2024-12-31');self.assertEqual(len(n['revision_history']['revenue']),2);old=n['revision_history']['revenue'][1];self.assertEqual(old['filing_fiscal_year'],2024);self.assertEqual(old['start'],'2023-01-01');self.assertEqual(len(old['source_fact_id']),64);self.assertEqual(n['history']['revenue'][0]['value'],'110.1234567890123456')
    def test_duplicate_identical_filings_are_counted(self):
        p=submissions();r=p['filings']['recent']
        for values in r.values():values.append(values[0])
        out=sec.filings(p,CIK);self.assertEqual(out['integrity']['duplicate_rows'],1);self.assertEqual(len(out['filings']),2)
    def test_two_thousand_independent_margin_candidates(self):
        import random
        from fractions import Fraction
        rng=random.Random(20261026)
        for _ in range(2000):
            revenue=rng.randint(1,10**12);income=rng.randint(-10**12,10**12);raw=facts();raw['facts']['us-gaap']['Revenues']['units']['USD'][0]['val']=revenue;raw['facts']['us-gaap']['NetIncomeLoss']['units']['USD'][0]['val']=income;n=sec.facts(raw,CIK,'2024-12-31')
            self.assertEqual(self.value(self.calc(n)['net_profit_margin']),Fraction(income,revenue))

class ContractV2(unittest.TestCase):
    def setUp(self):
        import os
        from unittest.mock import patch
        self.env=patch.dict(os.environ,{'GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0','GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'});self.env.start();self.addCleanup(self.env.stop)
    def test_unavailable_schema_no_fake_zero_and_v1_compatibility(self):
        import json,jsonschema
        from pathlib import Path
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        with TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
            response=c.get('/api/v2/companies/AAPL');self.assertEqual(response.status_code,200);x=response.json();jsonschema.validate(x,json.loads((Path(__file__).resolve().parents[2]/'terminal/server/schemas/backend_company_v2.schema.json').read_text()));self.assertTrue(all(m['value'] is None for m in x['financials']['metrics'].values()));self.assertEqual(c.get('/api/v1/stocks/company?symbol=AAPL').json()['instrument']['cik'],CIK)
    def test_filing_pagination_read_only_query_validation(self):
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        with TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
            before=c.get('/api/v1/state').json();self.assertEqual(c.get('/api/v2/companies/AAPL/filings?limit=0').status_code,400);self.assertEqual(c.get('/api/v2/companies/AAPL/filings?offset=-1').status_code,400);self.assertEqual(c.get('/api/v2/companies/AAPL/filings?form=10-K&limit=1').status_code,200);self.assertEqual(c.get('/api/v1/state').json()['book'],before['book'])
    def test_populated_contract_preserves_synthetic_origin_and_source_inputs(self):
        from .service import StockWorkspace
        from .test_repair import ENV,authored_fetcher
        from terminal.server.backend_contract import company_contract
        n=FinancialMetrics().normalized();w=StockWorkspace(environment=ENV,fetcher=authored_fetcher);w.cache['AAPL']={'sec':{'status':'AVAILABLE','financials':n,'source_records':[{'component':'financials','sha256':'a'*64,'url':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json'}]}}
        x=company_contract(w,'AAPL');self.assertEqual(x['data_origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(x['quality']['source_reconciliation'],'NOT_INDEPENDENTLY_RECONCILED_BY_THIS_SERVER');self.assertTrue(x['financials']['metrics']['net_profit_margin']['input_facts'])
        import json,jsonschema
        from pathlib import Path
        jsonschema.validate(x,json.loads((Path(__file__).resolve().parents[2]/'terminal/server/schemas/backend_company_v2.schema.json').read_text()))



class IndependentReconciliation(unittest.TestCase):
    def module(self):
        import importlib.util
        from pathlib import Path
        s=importlib.util.spec_from_file_location('independent_sec',Path(__file__).resolve().parents[2]/'scripts/qualify_sec_sources.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def test_raw_source_matches_production_and_detects_mutation(self):
        import json
        raw=json.dumps(facts()).encode();n=sec.facts(facts(),CIK,'2024-12-31');m=self.module();self.assertEqual(m.reconcile(raw,n,'2024-12-31')['mismatch_count'],0)
        n['history']['revenue'][0]['value']='101';self.assertGreater(m.reconcile(raw,n,'2024-12-31')['mismatch_count'],0)
    def test_missing_metric_or_wrong_issuer_cannot_vacuously_pass(self):
        import json
        raw=json.dumps(facts()).encode();n=sec.facts(facts(),CIK,'2024-12-31');n['history'].pop('net_income');self.assertGreater(self.module().reconcile(raw,n,'2024-12-31')['mismatch_count'],0)
        n=sec.facts(facts(),CIK,'2024-12-31');n['issuer_cik']='0000000001';self.assertGreater(self.module().reconcile(raw,n,'2024-12-31')['mismatch_count'],0)
    def test_no_supported_rows_is_inconclusive_not_validation(self):
        import json
        p={'cik':320193,'facts':{'us-gaap':{}}};n=sec.facts(p,CIK,'2024-12-31');self.assertEqual(self.module().reconcile(json.dumps(p).encode(),n,'2024-12-31')['status'],'INCONCLUSIVE_NO_SUPPORTED_RECORDS')
    def test_official_fetch_requires_existing_SEC_review_before_network(self):
        from unittest.mock import patch
        m=self.module()
        with patch('httpx.Client') as client:
            with self.assertRaises(ValueError):m.official_fetch(CIK,{})
            client.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
