"""Fixed official SEC ticker-directory contract;never inferred from company names."""
import hashlib,re
from .identity import SYMBOL_PATTERN
URL='https://www.sec.gov/files/company_tickers.json'
MAX_ISSUERS=50000

# This is a reference-text admission bound,not an exchange/provider ticker grammar.
# Safe but non-routable forms are explicit exclusions,never aliases or URL inputs.
REFERENCE_SYMBOL=r'[A-Za-z0-9]+(?:[.\-/$^][A-Za-z0-9]+)*'

def parse_reference(payload):
    if type(payload) is not dict or not 1<=len(payload)<=MAX_ISSUERS:raise ValueError('sec_directory_budget')
    rows={};seen=set();excluded=0;examples=[]
    for key,row in payload.items():
        if type(key) is not str or not re.fullmatch(r'\d{1,6}',key) or type(row) is not dict or set(row)!={'cik_str','ticker','title'}:raise ValueError('sec_directory_schema')
        cik,ticker,title=row['cik_str'],row['ticker'],row['title']
        if type(cik) is not int or not 1<=cik<=9999999999:raise ValueError('sec_directory_cik')
        if type(ticker) is not str or not 1<=len(ticker)<=64 or not re.fullmatch(REFERENCE_SYMBOL,ticker):raise ValueError('sec_directory_symbol')
        if type(title) is not str or not 1<=len(title)<=256 or any(ord(c)<32 for c in title):raise ValueError('sec_directory_title')
        if ticker in seen:raise ValueError('sec_directory_duplicate_symbol')
        seen.add(ticker)
        if not re.fullmatch(SYMBOL_PATTERN,ticker):
            excluded+=1
            if len(examples)<16:examples.append({'record_key':key,'ticker_sha256':hashlib.sha256(ticker.encode()).hexdigest(),'reason':'unsupported_routing_symbol'})
            continue
        rows[ticker]={'symbol':ticker,'company_name':title,'cik':str(cik).zfill(10)}
    if not rows:raise ValueError('sec_directory_no_supported_symbols')
    return rows,{'input_rows':len(payload),'accepted_rows':len(rows),'excluded_rows':excluded,
                 'excluded':{'unsupported_routing_symbol':excluded},'excluded_examples':examples,
                 'examples_truncated':excluded>len(examples),
                 'coverage':'ACCEPTED_ROUTABLE_SUBSET' if excluded else 'ALL_SOURCE_ROWS_REPRESENTABLE',
                 'normalization':'NONE_EXACT_SOURCE_SYMBOLS'}

def parse(payload):
    """Legacy all-rows contract:callers cannot silently lose unsupported references."""
    rows,integrity=parse_reference(payload)
    if integrity['excluded_rows']:raise ValueError('sec_directory_symbol')
    return rows
