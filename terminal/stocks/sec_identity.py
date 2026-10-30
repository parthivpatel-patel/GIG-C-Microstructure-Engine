"""Fixed official SEC ticker-directory contract;never inferred from company names."""
import hashlib,re
from decimal import Decimal
from pathlib import Path
from .identity import SYMBOL_PATTERN,symbol as validate_symbol
URL='https://www.sec.gov/files/company_tickers.json'
MAX_ISSUERS=50000

# This is a reference-text admission bound,not an exchange/provider ticker grammar.
# A single terminal marker is opaque reference text,not a missing class to infer.
# Safe but non-routable forms are explicit exclusions,never aliases or URL inputs.
REFERENCE_SYMBOL=r'[A-Za-z0-9]+(?:[.\-/$^][A-Za-z0-9]+)*[.\-/$^]?'
PARSER_PROFILE='sec.reference.terminal-marker.v3'


def symbol_condition(value):
    if type(value) is not str:return 'NON_STRING'
    if not value:return 'EMPTY'
    if len(value)>64:return 'TOO_LONG'
    if not re.fullmatch(REFERENCE_SYMBOL,value):return 'REFERENCE_PATTERN'
    return None


class SECReferenceSymbolError(ValueError):
    """Public metadata stores no raw field,header,CIK,title or contact value."""
    def __init__(self,payload,key,ordinal,ticker,condition,requested_symbol=None,*,path='reference_admission'):
        super().__init__('sec_directory_symbol')
        kind={str:'string',int:'integer',float:'number',Decimal:'number',bool:'boolean',list:'array',dict:'object',type(None):'null'}.get(type(ticker),'other')
        text=ticker[:64] if type(ticker)is str else ''
        separators='.-/$^'
        flags=[]
        for name,found in (
            ('CONTROL',any(ord(c)<32 or ord(c)==127 for c in text)),
            ('WHITESPACE',any(c.isspace()for c in text)),
            ('NON_ASCII',not text.isascii()),
            ('UNDERSCORE','_'in text),
            ('DISALLOWED_ASCII',any(c.isascii()and not(c.isalnum()or c in separators)for c in text)),
            ('LEADING_SEPARATOR',bool(text and text[0]in separators)),
            ('TRAILING_SEPARATOR',bool(text and text[-1]in separators)),
            ('REPEATED_SEPARATOR',bool(re.search(r'[.\-/$^]{2}',text)))):
            if found:flags.append(name)
        relation='NOT_REQUESTED'
        if requested_symbol is not None:
            if type(ticker)is not str:relation='NON_STRING'
            elif ticker==requested_symbol:relation='EXACT'
            elif len(ticker)<=64 and ticker.strip(' \t\r\n')==requested_symbol:relation='ASCII_WHITESPACE_VARIANT'
            elif len(ticker)<=64 and ticker.isascii()and ticker.upper()==requested_symbol:relation='ASCII_CASE_VARIANT'
            elif len(ticker)<=64 and ticker.isascii()and ticker.strip(' \t\r\n').upper()==requested_symbol:relation='ASCII_CASE_WHITESPACE_VARIANT'
            else:relation='OTHER_STRING'
        try:profile_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        except OSError:profile_hash=None
        self._context={'parser_profile':PARSER_PROFILE,'parser_source_sha256':profile_hash,
            'parser_path':path,'condition':condition,'record_key':key,'record_ordinal':ordinal,
            'input_records':len(payload),'field':'ticker','value_type':kind,
            'string_length':len(ticker)if type(ticker)is str else None,
            'shape_flags':tuple(flags),'shape_scope':'FIRST_64_CODEPOINTS',
            'requested_symbol':requested_symbol,'requested_relation':relation,
            'requested_exact_records':sum(type(r)is dict and type(r.get('ticker'))is str and r['ticker']==requested_symbol for r in payload.values())if requested_symbol is not None else None,
            'publication':'REJECTED_NO_NEW_SNAPSHOT','source_sha256':None}

    def attach_source_digest(self,digest):
        if type(digest)is str and re.fullmatch(r'[0-9a-f]{64}',digest):self._context['source_sha256']=digest

    def diagnostic(self):
        return {**self._context,'shape_flags':list(self._context['shape_flags'])}

def parse_reference(payload,*,requested_symbol=None):
    if requested_symbol is not None:validate_symbol(requested_symbol)
    if type(payload) is not dict or not 1<=len(payload)<=MAX_ISSUERS:raise ValueError('sec_directory_budget')
    rows={};seen=set();excluded=0;examples=[]
    for ordinal,(key,row)in enumerate(payload.items(),1):
        if type(key) is not str or not re.fullmatch(r'\d{1,6}',key) or type(row) is not dict or set(row)!={'cik_str','ticker','title'}:raise ValueError('sec_directory_schema')
        cik,ticker,title=row['cik_str'],row['ticker'],row['title']
        if type(cik) is not int or not 1<=cik<=9999999999:raise ValueError('sec_directory_cik')
        condition=symbol_condition(ticker)
        if condition:raise SECReferenceSymbolError(payload,key,ordinal,ticker,condition,requested_symbol)
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
    if integrity['excluded_rows']:
        key=integrity['excluded_examples'][0]['record_key']
        raise SECReferenceSymbolError(payload,key,list(payload).index(key)+1,payload[key]['ticker'],'LEGACY_EXCLUSIONS_NOT_ALLOWED',path='legacy_all_rows')
    return rows
