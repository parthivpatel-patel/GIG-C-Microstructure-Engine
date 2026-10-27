"""Versioned exact,period-aware financial descriptors;no accounting concept imputation."""
import datetime
from fractions import Fraction

DEFINITIONS={
 'gross_margin':('gross_profit / revenue','ratio',('revenue','gross_profit')),
 'operating_margin':('operating_income / revenue','ratio',('revenue','operating_income')),
 'net_profit_margin':('net_income / revenue','ratio',('revenue','net_income')),
 'current_ratio':('assets_current / liabilities_current','ratio',('assets_current','liabilities_current')),
 'debt_to_equity':('(short_term_borrowings + long_term_debt_current + long_term_debt_noncurrent) / equity','ratio',('equity','short_term_borrowings','long_term_debt_current','long_term_debt_noncurrent')),
 'free_cash_flow':('operating_cash_flow - capex','USD',('operating_cash_flow','capex')),
 'cash_conversion':('operating_cash_flow / net_income','ratio',('operating_cash_flow','net_income')),
 'return_on_assets':('net_income / mean(beginning_assets,ending_assets)','ratio',('net_income','assets')),
 'return_on_equity':('net_income / mean(beginning_equity,ending_equity)','ratio',('net_income','equity')),
 'annual_revenue_growth':('(new_revenue - previous_revenue) / previous_revenue','ratio',('revenue',)),
 'annual_net_income_growth':('(new_net_income - previous_net_income) / previous_net_income','ratio',('net_income',)),
 'annual_eps_growth':('(new_diluted_eps - previous_diluted_eps) / previous_diluted_eps','ratio',('eps',)),
}

class Ineligible(ValueError):pass

def calculate(normalized,*,target_period=None):
    history=normalized['history'];as_of=normalized['as_of_filing_date']
    # Index actual reported periods;filing FY/FP are context,not fact-period labels.
    index={name:{} for name in history}
    for name,records in history.items():
        for r in records:index[name].setdefault((r['start'],r['end']),[]).append(r)
    def rows(name,key,inputs):
        found=index.get(name,{}).get(key,[])
        if not found:raise Ineligible('missing_compatible_reported_'+name)
        if len({(r['concept'],r['unit']) for r in found})>1:raise Ineligible('ambiguous_accounting_concepts_'+name)
        if len({Fraction(r['value']) for r in found})!=1:raise Ineligible('ambiguous_reported_value_'+name)
        r=found[0]
        expected='USD/shares' if name=='eps' else 'USD'
        if r['unit']!=expected:raise Ineligible('unsupported_reported_unit')
        inputs.append({k:r.get(k) for k in ('issuer_cik','source_fact_id','concept','value','unit','start','end','filed','accession','form','filing_fiscal_year','filing_fiscal_period')})
        return Fraction(r['value'])
    def key_for(name,instant=False,annual=False):
        keys=list(index.get(name,{}))
        if instant:keys=[k for k in keys if k[0] is None]
        else:keys=[k for k in keys if k[0] is not None]
        if annual:keys=[k for k in keys if annual_period(name,k)]
        if target_period is not None:keys=[k for k in keys if k==target_period]
        if not keys:raise Ineligible('missing_eligible_reported_period_'+name)
        # Most recent end,then longest actual duration at that end;no inferred quarter.
        return max(keys,key=lambda k:(k[1],-datetime.date.fromisoformat(k[0]).toordinal() if k[0] else 0))
    def days(k):return (datetime.date.fromisoformat(k[1])-datetime.date.fromisoformat(k[0])).days+1 if k[0] else None
    def annual_period(name,k):
        return k[0] is not None and 350<=days(k)<=380 and all(r['form'] in ('10-K','10-K/A') for r in index[name][k])
    def positive(x,reason):
        if x<=0:raise Ineligible(reason)
        return x
    metrics={}
    for name,(formula,unit,names) in DEFINITIONS.items():
        inputs=[];key=None;limitations=['Descriptive reported facts,not a forecast or investment recommendation.','Latest filing-per-concept policy;not original intraday point-in-time history.']
        try:
            if name.startswith('annual_'):
                base=names[0];key=key_for(base,annual=True);start=datetime.date.fromisoformat(key[0])
                candidates=[k for k in index[base] if annual_period(base,k) and datetime.date.fromisoformat(k[1])+datetime.timedelta(days=1)==start]
                if len(candidates)!=1:raise Ineligible('missing_unique_adjacent_reported_annual_period')
                before=candidates[0];old=positive(rows(base,before,inputs),'non_positive_growth_base');new=rows(base,key,inputs);value=(new-old)/old
                limitations.append('Reported full-year350..380-day10-K periods only;adjacent boundaries;52/53-week duration differences retained,not calendar-normalized.')
            elif name in ('return_on_assets','return_on_equity'):
                key=key_for('net_income');income=rows('net_income',key,inputs)
                beginning=(datetime.date.fromisoformat(key[0])-datetime.timedelta(days=1)).isoformat();balance=names[1]
                average=(rows(balance,(None,beginning),inputs)+rows(balance,(None,key[1]),inputs))/2
                value=income/positive(average,'non_positive_average_balance')
                limitations.append('Return over the exact reported income period,not annualized;requires both beginning and ending balances,not an end-balance proxy.')
            elif name=='debt_to_equity':
                key=key_for('equity',instant=True);equity=positive(rows('equity',key,inputs),'non_positive_equity')
                debt=[rows(component,key,inputs) for component in names[1:]]
                if any(x<0 for x in debt):raise Ineligible('negative_debt_component')
                value=sum(debt)/equity
                limitations.append('Only the three explicit disclosed borrowing/debt components;not total liabilities,lease-inclusive debt or an assumed missing zero.')
            elif name=='current_ratio':
                key=key_for('assets_current',instant=True);value=rows('assets_current',key,inputs)/positive(rows('liabilities_current',key,inputs),'non_positive_current_liabilities')
            elif name=='free_cash_flow':
                key=key_for('operating_cash_flow');cfo=rows('operating_cash_flow',key,inputs);capex=rows('capex',key,inputs)
                if capex<0:raise Ineligible('unsupported_capex_sign_convention')
                value=cfo-capex;limitations.append('Non-GAAP CFO less cash payments for PP&E;excludes acquisitions and other investment/lease definitions.')
            elif name=='cash_conversion':
                key=key_for('operating_cash_flow');value=rows('operating_cash_flow',key,inputs)/positive(rows('net_income',key,inputs),'non_positive_net_income')
            else:
                key=key_for('revenue');revenue=positive(rows('revenue',key,inputs),'non_positive_revenue');value=rows(names[1],key,inputs)/revenue
            if max(value.numerator.bit_length(),value.denominator.bit_length())>4096:raise Ineligible('exact_rational_capacity')
            status='AVAILABLE';reason=None;wire={'numerator':str(value.numerator),'denominator':str(value.denominator)}
        except Ineligible as error:status='UNAVAILABLE';reason=str(error);wire=None
        metrics[name]={'value':wire,'status':status,'quality':'REPORTED_INPUTS_ALIGNED' if wire is not None else 'INELIGIBLE_OR_MISSING','reason':reason,'unit':unit,'formula':formula,'period':{'start':key[0],'end':key[1],'duration_days':days(key),'kind':'duration' if key[0] else 'instant'} if key else None,'as_of_filing_date':as_of,'timestamp':None,'timestamp_reason':'source facts expose filing dates,not reliable intraday availability','source':'SEC companyfacts/us-gaap selected concepts','input_facts':inputs,'limitations':limitations}
    return {'schema':'gig.financial_analytics.v2','metrics':metrics,'selection_policy':'latest reported end;longest duration at equal end;annual growth has separate explicit eligibility','coverage':'selected concepts only;no full accounting statement,IFRS,quarter subtraction or missing-value imputation'}
