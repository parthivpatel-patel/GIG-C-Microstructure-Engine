"""Offline immutable-run manifest schema. Native validation does not certify artifact authenticity."""
TOKEN = {'type':'string','minLength':1,'maxLength':128,'pattern':'^[!-~]+$'}
TEXT = {'type':'string','minLength':1,'maxLength':4096}
SHA = {'type':'string','pattern':'^[0-9a-f]{64}$'}
U64 = {'type':'string','pattern':'^(0|[1-9][0-9]*)$','maxLength':20}
I64 = {'type':'string','pattern':'^(0|-?[1-9][0-9]*)$','maxLength':20}
def obj(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
INPUT = obj({'identity':TOKEN,'sha256':SHA,'license_reference':TEXT,'origin':{'enum':['synthetic','observed']},'source':TEXT,'transformation':TEXT,'local_file':{'anyOf':[{'type':'null'},{'type':'string','pattern':'^inputs/input-[0-9]{4}\\.bin$'}]}})
OUTPUT = obj({'identity':TOKEN,'sha256':SHA,'schema':TOKEN,'version':{'const':'1.0'}})
ERROR = obj({'code':TEXT,'field':TEXT,'index':{'anyOf':[U64,{'type':'null'}]}})
AVAILABLE_TIME = {'oneOf':[obj({'reason':{'const':'0'},'value':I64}),obj({'reason':{'enum':['1','2','3']},'value':{'type':'null'}})]}
BODY = obj({'run_id':TOKEN,'code':obj({'commit_sha':{'type':'string','pattern':'^[0-9a-f]{40}$'},'dirty':{'type':'boolean'},'source_tree_sha256':SHA}),
 'build':obj({'compiler':TEXT,'flags':TEXT,'architecture':TEXT,'os':TEXT,'dependencies':{'type':'object','additionalProperties':TEXT}}),
 'inputs':{'type':'array','items':INPUT,'minItems':1,'maxItems':4096},'parents':{'type':'array','items':obj({'run_id':TOKEN,'manifest_sha256':SHA}),'maxItems':4096},
 'schema_versions':{'type':'object','additionalProperties':{'const':'1.0'},'minProperties':1},
 'instrument_rules':{'type':'array','items':{'type':'object'},'minItems':1,'maxItems':4096},
 'policies':obj({'ordering':TEXT,'sequence':TEXT,'recovery':TEXT,'clock':TEXT,'precision':TEXT}),
 'parameters':{'type':'object'},'seeds':{'type':'array','items':U64,'maxItems':4096},
 'coverage':obj({'start_ns':AVAILABLE_TIME,'end_ns':AVAILABLE_TIME,'records':U64}),
 'outputs':{'type':'array','items':OUTPUT,'maxItems':4096},'errors':{'type':'array','items':ERROR,'maxItems':4096},'complete':{'type':'boolean'}})
MANIFEST_SCHEMA = {'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:gig.run_manifest:1.0',**obj({'schema':{'const':'gig.run_manifest'},'version':{'const':'1.0'},'data':BODY})}
