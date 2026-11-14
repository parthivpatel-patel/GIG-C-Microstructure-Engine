"""Caller-supplied bounded acquisition intent; never an official SEC assertion."""
import re
from .xbrl_instance import digest

def normalize(value,cik,accession):
 if type(value)is not dict or set(value)!={'schema','issuer_cik','accession','primary_document','documents'}or value['schema']!='gig.sec.inline_acquisition_manifest.v1'or value['issuer_cik']!=cik or value['accession']!=accession:raise ValueError('sec_inline_manifest_scope')
 docs=value['documents']
 if type(docs)is not list or not 1<=len(docs)<=8:raise ValueError('sec_inline_manifest_budget')
 out=[];seen=set()
 for row in docs:
  if type(row)is not dict or set(row)!={'name','sha256'}:raise ValueError('sec_inline_manifest_document')
  name=row['name'];sha=row['sha256']
  if type(name)is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',name)or '..'in name or not name.lower().endswith(('.htm','.html','.xhtml'))or name in seen:raise ValueError('sec_inline_manifest_name')
  if type(sha)is not str or not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('sec_inline_manifest_digest')
  seen.add(name);out.append({'name':name,'sha256':sha})
 if type(value['primary_document'])is not str or value['primary_document']not in seen:raise ValueError('sec_inline_manifest_primary')
 return {**value,'documents':out}

def identity(value):return digest(value)
