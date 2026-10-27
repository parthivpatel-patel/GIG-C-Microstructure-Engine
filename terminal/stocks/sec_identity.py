"""Fixed official SEC ticker-directory contract;never inferred from company names."""
import re
URL='https://www.sec.gov/files/company_tickers.json'
MAX_ISSUERS=50000

def parse(payload):
    if type(payload) is not dict or not 1<=len(payload)<=MAX_ISSUERS:raise ValueError('sec_directory_budget')
    rows={}
    for key,row in payload.items():
        if type(key) is not str or not re.fullmatch(r'\d{1,6}',key) or type(row) is not dict or set(row)!={'cik_str','ticker','title'}:raise ValueError('sec_directory_schema')
        cik,ticker,title=row['cik_str'],row['ticker'],row['title']
        if type(cik) is not int or not 1<=cik<=9999999999:raise ValueError('sec_directory_cik')
        if type(ticker) is not str or not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?',ticker):raise ValueError('sec_directory_symbol')
        if type(title) is not str or not 1<=len(title)<=256 or any(ord(c)<32 for c in title):raise ValueError('sec_directory_title')
        if ticker in rows:raise ValueError('sec_directory_duplicate_symbol')
        rows[ticker]={'symbol':ticker,'company_name':title,'cik':str(cik).zfill(10)}
    return rows
