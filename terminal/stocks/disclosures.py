"""Bounded offline 13F information-table parser. No holder feed or position inference."""
import re,xml.etree.ElementTree as ET
from .sec import date,text

def holdings(raw,*,report_date,filing_date,accession,value_unit,amendment=False):
    date(report_date);date(filing_date)
    if filing_date<report_date or not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):raise ValueError('holdings_provenance')
    if value_unit not in ('USD','USD_THOUSANDS') or type(amendment) is not bool:raise ValueError('holdings_unit_or_amendment')
    if type(raw) is not bytes or len(raw)>1024*1024 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('holdings_xml_budget_or_dtd')
    # Prevent encoding tricks that would bypass the DTD/entity byte guard.
    try:source=raw.decode('utf-8')
    except UnicodeError:raise ValueError('holdings_utf8_required') from None
    if '\x00' in source:raise ValueError('holdings_utf8_required')
    try:root=ET.fromstring(source)
    except ET.ParseError:raise ValueError('holdings_xml') from None
    name=lambda e:e.tag.rsplit('}',1)[-1]
    if name(root)!='informationTable' or len(list(root.iter()))>5000:raise ValueError('holdings_structure')
    rows=[]
    for node in root:
        if name(node)!='infoTable' or len(rows)>=256:raise ValueError('holdings_record_budget')
        fields={}
        for child in node:
            key=name(child)
            if key in fields:raise ValueError('holdings_duplicate_field')
            fields[key]=child
        def leaf(key):
            e=fields.get(key)
            if e is None or len(e):raise ValueError('holdings_field')
            return text(e.text or '',256)
        issuer=leaf('nameOfIssuer');cusip=leaf('cusip');value=leaf('value')
        if not re.fullmatch(r'[0-9A-Z]{9}',cusip) or not re.fullmatch(r'\d{1,18}',value):raise ValueError('holdings_numeric_or_identity')
        shares=fields.get('shrsOrPrnAmt')
        if shares is None:raise ValueError('holdings_shares')
        values={}
        for child in shares:
            key=name(child)
            if key in values:raise ValueError('holdings_duplicate_field')
            values[key]=text(child.text or '',64)
        amount=values.get('sshPrnamt','');unit=values.get('sshPrnamtType')
        if not re.fullmatch(r'\d{1,18}',amount) or unit not in ('SH','PRN'):raise ValueError('holdings_shares')
        put_call=leaf('putCall') if 'putCall' in fields else None
        if put_call not in (None,'Put','Call'):raise ValueError('holdings_put_call')
        rows.append({'issuer':issuer,'cusip':cusip,'reported_value':value,'value_unit':value_unit,'value_usd':str(int(value)*(1000 if value_unit=='USD_THOUSANDS' else 1)),'amount':amount,'amount_unit':unit,'put_call':put_call})
    return {'classification':'OFFLINE_DISCLOSURE_INPUT_NOT_LIVE_POSITIONS','report_date':report_date,'filed':filing_date,'accession':accession,'amendment':amendment,'holdings':rows,'limitations':['Unit is explicitly supplied from the applicable historical filing profile,never inferred','Not a complete company holder registry,beneficial-ownership total or real-time position','Amendments are retained separately,not blindly added or netted','No observed SEC information table fetched in this execution']}
