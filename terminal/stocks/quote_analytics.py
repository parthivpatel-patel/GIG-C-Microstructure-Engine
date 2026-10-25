"""Native single-quote analytics;source sizes never inferred to be orders or shares."""
from fractions import Fraction
import gig_microstructure as gig
from terminal.providers.kraken import decimal_wire,PRICE_MAX,UINT64_MAX

def analyze(quote):
    scale=100000000
    try:
        b=decimal_wire(quote['bid'],maximum=PRICE_MAX,scale=scale)[0];a=decimal_wire(quote['ask'],maximum=PRICE_MAX,scale=scale)[0]
        bs=decimal_wire(quote['bid_size'],maximum=UINT64_MAX,scale=scale)[0];az=decimal_wire(quote['ask_size'],maximum=UINT64_MAX,scale=scale)[0]
        if not all(int(v)>0 for v in (b,a,bs,az)):return {'status':'UNAVAILABLE','reason':'positive_two_sided_quote_and_reported_sizes_required'}
        native=gig._native.AggregateDepth(1,1048576)
        gig._checked(native.snapshot([{'price_ticks':b,'quantity':bs}],[{'price_ticks':a,'quantity':az}],None))
        state=gig._checked(native.state());metrics={}
        for name,v in state['metrics'].items():
            if v is None:metrics[name]=None;continue
            n=Fraction(int(v['numerator']),int(v['denominator']))
            if name!='depth_imbalance':n/=scale
            metrics[name]={'numerator':str(n.numerator),'denominator':str(n.denominator)}
        return {'status':'AVAILABLE','engine':'native_C++20_AggregateDepth','level':'L1_SINGLE_VENUE_ONLY','metrics':metrics,'locked':state['locked'],'crossed':state['crossed'],'price_representation_scale':str(scale),'quantity_scope':'provider-reported size units scaled exactly;not share/lot conversion or individual orders','pmr_peak_bytes':state['pmr_peak_bytes']}
    except (ValueError,gig.EngineError):return {'status':'UNAVAILABLE','reason':'quote_not_exactly_representable_by_native_contract;source_values_preserved'}
