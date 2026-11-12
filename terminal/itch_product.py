"""Explicit authored full-ITCH product sessions. No feeds or implicit recovery.

An immutable bundle carries the full native/context artifact and a bounded authored
continuation. The owner pins the bundle digest outside it. Unknown schema/code or
binary changes require explicit migration; no fallback to a different dataset.
"""
import base64,dataclasses,hashlib,json,os,stat
from fractions import Fraction
from pathlib import Path
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,MAX_BYTES
from terminal.native_recovery import native_binary_identity
from terminal.verification.artifacts import read_bytes,decode
from terminal.session_recovery import _private_parent
from terminal.itch_recovery import publish_new
MAX_BUNDLE=48*1024*1024;MAX_TAIL=2*1024*1024;MAX_RECORDS=256
class ItchProductError(ValueError):pass

def implementation_identity():
    root=Path(__file__).resolve().parent
    data={name:hashlib.sha256(read_bytes(root/name,128*1024)).hexdigest()for name in('itch_product.py','itch_recovery.py','server/engine.py')}
    data['native_binary']=native_binary_identity()
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def encoded(value):
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    if len(raw)>MAX_BUNDLE:raise ItchProductError('itch_product_byte_budget')
    return raw
def digest(raw):return hashlib.sha256(raw).hexdigest()
def _b64(text,limit):
    if type(text)is not str or len(text)>4*((limit+2)//3):raise ItchProductError('itch_product_field_budget')
    try:raw=base64.b64decode(text,validate=True)
    except (ValueError,UnicodeError):raise ItchProductError('itch_product_base64')from None
    if len(raw)>limit or base64.b64encode(raw).decode()!=text:raise ItchProductError('itch_product_base64')
    return raw
def frames(raw):
    if type(raw)is not bytes or len(raw)>MAX_TAIL:raise ItchProductError('itch_product_tail_budget')
    result=[];at=0
    while at<len(raw):
        if len(raw)-at<2:raise ItchProductError('itch_product_partial_frame')
        size=int.from_bytes(raw[at:at+2],'big');at+=2
        if not size or size>len(raw)-at:raise ItchProductError('itch_product_partial_or_terminal_frame')
        if len(result)>=MAX_RECORDS:raise ItchProductError('itch_product_record_budget')
        result.append(raw[at:at+size]);at+=size
    return tuple(result)
def _packet(records):return b''.join(len(p).to_bytes(2,'big')+p for p in records)
def _admit(raw,expected_sha256,*,migration=False):
    if type(raw)is not bytes or not 1<=len(raw)<=MAX_BUNDLE or type(expected_sha256)is not str or digest(raw)!=expected_sha256:raise ItchProductError('itch_product_digest_or_budget')
    v=decode(raw)
    keys={'schema','version','image','admission','tail','tail_sha256','selected_book','speed','native_binary_sha256','migration_history'}
    if set(v)!=keys or v['schema']!='gig.itch.product_session'or type(v['version'])is not int or v['version']!=1:raise ItchProductError('itch_product_schema')
    try:
        if type(v['admission'])is not dict or set(v['admission'])!={f.name for f in dataclasses.fields(ItchAdmission)}:raise ValueError()
        a=ItchAdmission(**v['admission']);a.validate()
    except (ValueError,TypeError):raise ItchProductError('itch_product_admission')from None
    if type(v['selected_book'])is not int or not 0<=v['selected_book']<2 or type(v['speed'])is not int or v['speed']not in(1,2,4,8):raise ItchProductError('itch_product_controls')
    if type(v['native_binary_sha256'])is not str or len(v['native_binary_sha256'])!=64 or any(c not in '0123456789abcdef'for c in v['native_binary_sha256']):raise ItchProductError('itch_product_binary_identity')
    history=v['migration_history']
    if type(history)is not list or len(history)>4:raise ItchProductError('itch_product_migration_budget')
    for row in history:
        if type(row)is not dict or set(row)!={'from_bundle_sha256','from_image_sha256','from_implementation_sha256','from_native_binary_sha256'}or any(type(x)is not str or len(x)!=64 or any(c not in '0123456789abcdef'for c in x)for x in row.values()):raise ItchProductError('itch_product_migration_lineage')
    if not migration and(a.implementation_sha256!=implementation_identity()or v['native_binary_sha256']!=native_binary_identity()):raise ItchProductError('itch_product_explicit_migration_required')
    image=_b64(v['image'],MAX_BYTES);tail=_b64(v['tail'],MAX_TAIL)
    if digest(tail)!=v['tail_sha256']:raise ItchProductError('itch_product_tail_digest')
    return v,a,image,tail

def build_bundle(image,admission,tail=b'',*,selected_book=0,speed=1,history=()):
    if type(image)is not bytes or not 56<=len(image)<=MAX_BYTES or type(tail)is not bytes or len(tail)>MAX_TAIL:raise ItchProductError('itch_product_field_budget')
    if type(admission)is not ItchAdmission:raise ItchProductError('itch_product_admission')
    admission.validate();frames(tail)
    if type(history)not in(list,tuple)or len(history)>4:raise ItchProductError('itch_product_migration_budget')
    value={'schema':'gig.itch.product_session','version':1,'image':base64.b64encode(image).decode(),'admission':dataclasses.asdict(admission),'tail':base64.b64encode(tail).decode(),'tail_sha256':digest(tail),'selected_book':selected_book,'speed':speed,'native_binary_sha256':native_binary_identity(),'migration_history':list(history)}
    raw=encoded(value);ItchProduct.restore(raw,digest(raw));return raw

class ItchProduct:
    @classmethod
    def restore(cls,raw,expected_sha256,*,resource_budget_bytes=128*1024*1024):
        value,a,image,tail=_admit(raw,expected_sha256);records=frames(tail)
        owner=ItchRecovery.restore(image,a,resource_budget_bytes=resource_budget_bytes)
        description=owner.describe()
        if value['selected_book']>=len(description['books']):raise ItchProductError('itch_product_book')
        # Verify the entire authored suffix in isolation before selecting it. No
        # committed prefix transitions are applied;owner is not this probe object.
        probe=ItchRecovery.restore(image,a,resource_budget_bytes=resource_budget_bytes)
        for payload in records:
            s=probe.status();step=probe.process(payload,frame_offset=int(s['next_frame']),ordinal=int(s['next_ordinal']))
            if not step['committed']:raise ItchProductError('itch_product_tail_rejected')
        obj=cls.__new__(cls);obj.owner=owner;obj.description=description;obj.selected_book=value['selected_book'];obj.speed=value['speed'];obj.records=records;obj.offset=0;obj.playing=False;obj.base_image=image;obj.base_admission=a;obj.history=value['migration_history'];obj.minimum=int(owner.status()['source_records'])
        # Exact source quanta are validated by the native reconstruction binding.
        # Present source Price(4)/shares;retain the underlying native rules/metrics.
        if int(description['source_price_quantum'])<=0 or int(description['source_lot_size'])<=0:raise ItchProductError('itch_product_source_units')
        obj.owner.book(obj.selected_book,obj.depth);return obj
    @property
    def depth(self):return min(10,int(self.description['books'][self.selected_book]['limits']['max_snapshot_depth']))
    @property
    def position(self):return self.minimum+self.offset
    @property
    def total(self):return self.minimum+len(self.records)
    def seek(self,position,*,resource_budget_bytes=128*1024*1024):
        if type(position)is not int or not self.minimum<=position<=self.total:raise ItchProductError('itch_product_seek_boundary')
        # Explicit historical seek from the selected checkpoint,not restart replay
        # of the checkpoint's committed source/native events.
        candidate=ItchRecovery.restore(self.base_image,self.base_admission,resource_budget_bytes=resource_budget_bytes)
        count=position-self.minimum
        for payload in self.records[:count]:
            s=candidate.status();step=candidate.process(payload,frame_offset=int(s['next_frame']),ordinal=int(s['next_ordinal']))
            if not step['committed']:raise ItchProductError('itch_product_source_rejected')
        candidate.book(self.selected_book,self.depth)
        self.owner,self.offset,self.playing=candidate,count,False
    def step(self,*,resource_budget_bytes=128*1024*1024):
        if self.offset==len(self.records):self.playing=False;return False
        # A step resumes the current hot boundary,not the original selected
        # checkpoint. Already committed suffix records must never be reapplied.
        image=self.owner.checkpoint();admission=dataclasses.replace(self.owner.admission,artifact_sha256=digest(image))
        candidate=ItchRecovery.restore(image,admission,resource_budget_bytes=resource_budget_bytes)
        status=candidate.status();result=candidate.process(self.records[self.offset],frame_offset=int(status['next_frame']),ordinal=int(status['next_ordinal']))
        if not result['committed']:raise ItchProductError('itch_product_source_rejected')
        candidate.book(self.selected_book,self.depth);next_offset=self.offset+1
        self.owner,self.offset=candidate,next_offset;return True
    def capture(self):
        raw=self.owner.checkpoint();a=dataclasses.replace(self.owner.admission,artifact_sha256=digest(raw))
        return build_bundle(raw,a,_packet(self.records[self.offset:]),selected_book=self.selected_book,speed=self.speed,history=self.history)
    def control(self,action,value=None):
        if action=='book':
            if type(value)is not int or not 0<=value<len(self.description['books']):raise ItchProductError('itch_product_book')
            self.owner.book(value,min(10,int(self.description['books'][value]['limits']['max_snapshot_depth'])));self.selected_book=value
        elif action=='seek':self.seek(value)
        elif action=='restart':self.seek(self.minimum)
        elif action=='step':self.playing=False;self.step()
        elif action=='play':self.playing=self.position<self.total
        elif action=='pause':self.playing=False
        elif action=='speed':
            if type(value)is not int or value not in(1,2,4,8):raise ItchProductError('itch_product_speed')
            self.speed=value
        else:raise ItchProductError('itch_product_control_restricted')
    def view(self,session):
        data=self.owner.book(self.selected_book,self.depth);s=self.owner.status();b=self.description['books'][self.selected_book];r=b['rules'];book=data['snapshot']['data']['book'];native=data['metrics']['data']['result']['metrics']
        metrics={k:native[v]['value']for k,v in {'spread':'spread','midprice':'midpoint','microprice':'microprice','imbalance':'depth_imbalance','top_imbalance':'top_imbalance','bid_depth':'bid_depth','ask_depth':'ask_depth'}.items()}
        quantum=int(self.description['source_price_quantum']);lot=int(self.description['source_lot_size'])
        book={**book,**{side:[{**row,'price_ticks':str(int(row['price_ticks'])*quantum),'quantity':str(int(row['quantity'])*lot)}for row in book[side]]for side in('bids','asks')}}
        for name,factor in [('spread',quantum),('midprice',quantum),('microprice',quantum),('bid_depth',lot),('ask_depth',lot)]:
            if metrics[name]is not None:
                f=metrics[name];value=Fraction(int(f['numerator'])*factor,int(f['denominator']));metrics[name]={'numerator':str(value.numerator),'denominator':str(value.denominator)}
        result={'schema_version':'1','mode':'HISTORICAL_REPLAY','origin':'HISTORICAL_SYNTHETIC','instrument':b['stock'].rstrip(),'provider':'authored-itch','venue':'AUTHORED','feed_type':'L3_AUTHORED','price_scale':'10000','quantity_scale':'1','book':{'bids':book['bids'],'asks':book['asks']},'revision':book['revision'],'metrics':metrics,'position':self.position,'event_count':self.total,'replay_min_position':self.minimum,'playing':session.playing,'speed':session.speed,'source_timestamp_ns':None,'replay_time_ns':None,'received_at_ns':None,'feed':{'state':'REPLAYING'if session.playing else'PAUSED','reason':'Restored full authored ITCH context;complete-record continuation only. Not observed exchange data.','real_time':False,'stale':False,'sequence_complete':True,'capture_complete':False},'provenance':{'category':'HISTORICAL_SYNTHETIC','dataset':'itch-checkpoint-v1','source':self.description['source'],'source_session':self.description['session'],'capture':s['capture'],'generation':s['generation'],'fixture_sha256':self.description['fixture_sha256'],'generator_seed':self.description['generator_seed'],'complete_initialization':True,'initialization_scope':'authored complete seed'if self.description['seeded']else'authored empty boundary','unit_projection':'ITCH Price(4)/shares;exact native-unit conversion','native_tick_size':r['tick_size'],'native_lot_size':r['lot_size'],'clock':'ITCH intraday fields;no UTC date inferred','recording_enabled':False,'permission':'independently-authored'},'capabilities':{'native_replay':True,'simulation':False,'live':False,'observed_itch':False,'recording':False,'itch_book_selection':self.description['books'],'selected_itch_book':self.selected_book,'itch_checkpoint_available':True},'engine':{'native':True,**gig.native_build_info()},'diagnostics':{'connected_clients':session.clients,'queue_capacity':1,'queue_occupancy':0,'stream_timeouts':session.stream_timeouts,'rejected_requests':session.rejected,'native_status':s},'notifications':list(session.notifications),'simulation':None}
        from terminal.server.concentration import calculate
        result['research_metrics']={'concentration':calculate(result)};return result

def migrate(raw,expected_sha256):
    value,a,image,tail=_admit(raw,expected_sha256,migration=True)
    if len(value['migration_history'])>=4:raise ItchProductError('itch_product_migration_budget')
    if a.implementation_sha256==implementation_identity()and value['native_binary_sha256']==native_binary_identity():raise ItchProductError('itch_product_no_migration_needed')
    new,new_a=ItchRecovery.migrate(image,a,implementation_identity())
    history=value['migration_history']+[{'from_bundle_sha256':expected_sha256,'from_image_sha256':a.artifact_sha256,'from_implementation_sha256':a.implementation_sha256,'from_native_binary_sha256':value['native_binary_sha256']}]
    return build_bundle(new,new_a,tail,selected_book=value['selected_book'],speed=value['speed'],history=history)

def save_new(path,raw,expected_sha256,**hooks):
    ItchProduct.restore(raw,expected_sha256);publish_new(path,raw,**hooks);return expected_sha256
def read_private(path):
    path=Path(path).absolute()
    if not path.parent.is_dir():raise ItchProductError('itch_product_private_file')
    path=_private_parent(path);info=path.stat()
    if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise ItchProductError('itch_product_private_file')
    return read_bytes(path,MAX_BUNDLE)

def load(path,expected_sha256):return ItchProduct.restore(read_private(path),expected_sha256)
def select_product_session(environment):
    from terminal.server.engine import NativeSession
    kind=environment.get('GIG_TERMINAL_SESSION','authored')
    if kind not in('authored','itch'):raise ItchProductError('itch_product_session_kind')
    if kind=='authored':
        if any(environment.get(k)for k in('GIG_ITCH_SESSION_PATH','GIG_ITCH_SESSION_SHA256')):raise ItchProductError('itch_product_explicit_selection_required')
        return NativeSession()
    path=environment.get('GIG_ITCH_SESSION_PATH');expected=environment.get('GIG_ITCH_SESSION_SHA256')
    if type(path)is not str or not path or type(expected)is not str or len(expected)!=64:raise ItchProductError('itch_product_pinned_configuration_required')
    return NativeSession.restore_checkpoint(read_private(path),expected,implementation_identity())
