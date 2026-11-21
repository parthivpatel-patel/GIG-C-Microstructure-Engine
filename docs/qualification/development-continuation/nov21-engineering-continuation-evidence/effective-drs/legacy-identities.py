import sys,json
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from terminal.stocks.test_xbrl_dimensions import entry
from terminal.stocks.test_xbrl_open_dimensions import opened
from terminal.stocks.test_xbrl_inherited_dimensions import inherited
from terminal.stocks.test_xbrl_negative_dimensions import negative
from terminal.stocks.test_xbrl_negative_only_dimensions import only
from terminal.stocks.test_xbrl_typed_hypercubes import fixture
from terminal.stocks.test_xbrl_cross_role import fixture as cross_fixture
from terminal.stocks.xbrl_dimensions import corroborate,PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE,TYPED_PROFILE,CROSS_ROLE_PROFILE
from terminal.stocks.xbrl_instance import parse_instance,selected_financials,digest
from terminal.stocks.xbrl_dts import discover
from terminal.stocks.xbrl_binding import bind_declarations
import terminal.stocks.xbrl_dimensions as module
assert Path(module.__file__).resolve().is_relative_to(root)
cases=[(PROFILE,entry()),(PROFILE,entry(None,default=True)),(OPEN_PROFILE,opened()),(OPEN_PROFILE,opened(default=True)),(INHERITED_PROFILE,inherited()),(INHERITED_PROFILE,inherited(member=None,default=True)),(NEGATIVE_PROFILE,negative()),(NEGATIVE_PROFILE,negative(closed=True)),(NEGATIVE_ONLY_PROFILE,only()),(NEGATIVE_ONLY_PROFILE,only(member=None,positive_default=True)),(TYPED_PROFILE,fixture()),(TYPED_PROFILE,fixture(explicit=True,default=True)),(CROSS_ROLE_PROFILE,cross_fixture()),(CROSS_ROLE_PROFILE,cross_fixture(None,default=True))]
rows=[]
for profile,e in cases:
 p=parse_instance(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);p=bind_declarations(p,g);args={'documents':e['documents'],'instance_uri':e['instance_uri']}if profile in(TYPED_PROFILE,CROSS_ROLE_PROFILE)else{};out=corroborate(p,g,profile=profile,**args)
 rows.append({'profile':profile,'artifact_sha256':out['canonical_sha256'],'selected_sha256':digest(selected_financials(out))})
from terminal.stocks.test_xbrl_inherited_cross_role import fixture as inherited_cross_fixture
from terminal.stocks.xbrl_dimensions import INHERITED_CROSS_ROLE_PROFILE
for e in (inherited_cross_fixture(),inherited_cross_fixture(member=None,default=True),inherited_cross_fixture(inherited=False,cubes=3),inherited_cross_fixture(diamond=True),inherited_cross_fixture(cubes=1)):
 p=parse_instance(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);p=bind_declarations(p,g)
 out=corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 rows.append({'profile':INHERITED_CROSS_ROLE_PROFILE,'artifact_sha256':out['canonical_sha256'],'selected_sha256':digest(selected_financials(out))})
print(json.dumps(rows,sort_keys=True))
