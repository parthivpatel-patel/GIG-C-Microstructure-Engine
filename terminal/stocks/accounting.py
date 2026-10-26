"""Exact selected-component diagnostics,not full accounting reconciliation."""
from fractions import Fraction

RECIPES={'balance':(('assets',1),('liabilities',-1),('equity',-1)),
         'gross_profit':(('revenue',1),('cost_of_revenue',-1),('gross_profit',-1)),
         'cash_change':(('operating_cash_flow',1),('cash_investing',1),('cash_financing',1),('cash_fx',1),('cash_change',-1))}

def checks(normalized):
    history=normalized.get('history',{});results={}
    for name,fields in RECIPES.items():
        keys=set((r['start'],r['end']) for metric,_ in fields for r in history.get(metric,[]));rows=[]
        for start,end in sorted(keys,key=lambda k:(k[1],k[0] or ''),reverse=True)[:12]:
            if (name=='balance')!=(start is None):continue
            selected=[];missing=[]
            for metric,sign in fields:
                candidates=[r for r in history.get(metric,[]) if (r['start'],r['end'])==(start,end)]
                if len(candidates)!=1 or candidates[0]['unit']!='USD':missing.append(metric);continue
                selected.append((candidates[0],sign))
            if missing:rows.append({'start':start,'end':end,'status':'UNAVAILABLE_OR_AMBIGUOUS','missing_components':missing,'residual':None});continue
            residual=sum((Fraction(r['value'])*sign for r,sign in selected),Fraction())
            rows.append({'start':start,'end':end,'status':'SELECTED_COMPONENTS_EQUAL' if residual==0 else 'SELECTED_COMPONENT_RESIDUAL','residual':{'numerator':str(residual.numerator),'denominator':str(residual.denominator)},'unit':'USD','source_facts':[r for r,_ in selected]})
        results[name]=rows
    return {'schema':'gig.accounting.checks.v1','checks':results,'method':'Exact same-start/end USD components;no missing zeros,no inferred quarterly subtraction','limitations':['A zero residual is not proof of complete statement/context reconciliation','StockholdersEquity may omit noncontrolling interests;cash scopes and expense taxonomy may differ','Nonzero residuals require source/context investigation,not an automatic engine-defect or fraud claim','EPS USD/shares and weighted shares are separately retained;no inferred EPS numerator or rounding adjustment']}
