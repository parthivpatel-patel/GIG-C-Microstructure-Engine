"""10,000 authored candidates, independent decimal maps/CRC/Fraction expectations."""
from fractions import Fraction
import json,random,unittest
import gig_microstructure as gig
from .kraken import KrakenBookAdapter,ProviderError
from .test_kraken import crc_reference

class Differential(unittest.TestCase):
    def test_two_symbols_ten_thousand_candidates(self):
        rng=random.Random(1907);models={};adapters={};books={}
        for symbol in ('BTC/USD','ETH/USD'):
            book=gig._native.AggregateDepth(32,1048576);books[symbol]=book
            def callback(*,snapshot,bids,asks,sequence,book=book):
                gig._checked((book.snapshot if snapshot else book.update)(bids,asks,sequence))
            adapters[symbol]=KrakenBookAdapter(callback,symbol=symbol);models[symbol]=[{},{}]
        def wire(symbol,kind,changes,reference):
            sides=[]
            for mapping,reverse in zip(reference,(True,False)):
                sides.append(sorted(mapping.items(),reverse=reverse))
            text=''.join(str(p*100)+str(q*100000000) for p,q in sides[1]+sides[0])
            data={'symbol':symbol,'checksum':crc_reference(text)}
            for key,values in zip(('bids','asks'),changes):
                data[key]=[{'price':f'{p}.00','qty':f'{q}.00000000'} for p,q in values]
            return json.dumps({'channel':'book','type':kind,'data':[data]})
        for symbol in adapters:
            adapters[symbol].feed(wire(symbol,'snapshot',[[],[]],[{},{}]),0)
        rejected=0
        for i in range(1,10001):
            symbol=('BTC/USD','ETH/USD')[rng.randrange(2)];side=rng.randrange(2)
            price=(90+rng.randrange(10)) if side==0 else (101+rng.randrange(10));qty=rng.randrange(20)
            before=[dict(m) for m in models[symbol]];candidate=[dict(m) for m in before]
            if qty:candidate[side][price]=qty
            else:candidate[side].pop(price,None)
            updates=[[],[]];updates[side]=[(price,qty)]
            raw=wire(symbol,'update',updates,candidate)
            if i%97==0:
                bad=json.loads(raw);bad['data'][0]['checksum']^=1
                with self.assertRaisesRegex(ProviderError,'checksum_mismatch'):adapters[symbol].feed(json.dumps(bad),i)
                rejected+=1
                native=gig._checked(books[symbol].state())
                self.assertEqual(native['bids'],[{'price_ticks':str(p*100),'quantity':str(q*100000000)} for p,q in sorted(before[0].items(),reverse=True)])
                # Exact authored reference snapshot is required after corruption.
                restored=[list(m.items()) for m in before]
                adapters[symbol].feed(wire(symbol,'snapshot',restored,before),i)
            adapters[symbol].feed(raw,i);models[symbol]=candidate
            value=gig._checked(books[symbol].state())
            for j,key in enumerate(('bids','asks')):
                expected=[{'price_ticks':str(p*100),'quantity':str(q*100000000)} for p,q in sorted(candidate[j].items(),reverse=j==0)]
                self.assertEqual(value[key],expected)
            if candidate[0] and candidate[1]:
                b,a=max(candidate[0])*100,min(candidate[1])*100
                qb,qa=candidate[0][b//100],candidate[1][a//100]
                f=value['metrics']['microprice'];self.assertEqual(Fraction(int(f['numerator']),int(f['denominator'])),Fraction(a*qb+b*qa,qb+qa))
        self.assertEqual(rejected,103)
        # Deliberately corrupt a reference expectation; comparison must catch it.
        value=gig._checked(books['BTC/USD'].state())
        wrong=[dict(x) for x in value['bids']];wrong[0]['quantity']=str(int(wrong[0]['quantity'])+1)
        self.assertNotEqual(value['bids'],wrong)

if __name__=='__main__':unittest.main()
