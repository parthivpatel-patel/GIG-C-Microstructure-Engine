"""Aligned selected reported facts,not fabricated full financial statements."""

GROUPS={'income':('revenue','gross_profit','operating_income','net_income','eps','eps_basic','diluted_shares','cost_of_revenue'),
        'balance':('assets','liabilities','equity','cash','assets_current','liabilities_current','short_term_borrowings','long_term_debt_current','long_term_debt_noncurrent'),
        'cash':('operating_cash_flow','cash_investing','cash_financing','cash_fx','cash_change','capex')}


def aligned(normalized,statement='income',period='annual'):
    if statement not in GROUPS or period not in ('annual','quarter','ytd','all'):raise ValueError('statement_query')
    rows=normalized.get('history',{});keys=set()
    def eligible(r):
        if statement=='balance':return r['start'] is None
        if r['start'] is None:return False
        days=r['duration_days']
        if period=='all':return True
        if period=='annual':return 350<=days<=380 and r['form'] in ('10-K','10-K/A')
        if period=='quarter':return 75<=days<=105
        return 106<=days<=349 and r['form'] in ('10-Q','10-Q/A')
    for name in GROUPS[statement]:
        for r in rows.get(name,[]):
            if eligible(r):keys.add((r['start'],r['end']))
    selected=sorted(keys,key=lambda k:(k[1],k[0] or ''),reverse=True)[:12];packets=[]
    for start,end in selected:
        fields={}
        for name in GROUPS[statement]:
            candidates=[r for r in rows.get(name,[]) if eligible(r) and (r['start'],r['end'])==(start,end)]
            row=candidates[0] if len(candidates)==1 else None
            fields[name]={'value':row['value'] if row else None,'unit':row['unit'] if row else None,
                          'status':'REPORTED' if row else 'AMBIGUOUS' if candidates else 'MISSING',
                          'source_facts':candidates,'reason':None if row else 'multiple_compatible_concepts' if candidates else 'no_reported_fact_for_exact_period'}
        packets.append({'start':start,'end':end,'kind':'instant' if start is None else 'reported_duration','fields':fields})
    return {'schema':'gig.backend.statements.v2','statement':statement,'period_filter':period,'periods':packets,
            'coverage':'SELECTED_REPORTED_FACTS_NOT_COMPLETE_STATEMENTS','truncated_periods':len(keys)>12,
            'method':'exact reported start/end alignment;latest-per-concept as-of normalization;no cumulative-to-quarter subtraction,no missing zeros',
            'missing_capabilities':['Complete XBRL presentation/context reconstruction','Full taxonomy coverage','Independent official reconciliation']}
