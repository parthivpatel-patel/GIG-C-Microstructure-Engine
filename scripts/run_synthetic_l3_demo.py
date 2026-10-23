#!/usr/bin/env python3
"""Run the actual standalone native reconstruction driver on an authored fixture."""
import json
import subprocess
import sys
import check_itch_l3_reference as reference

payloads = [reference.system('O'), reference.directory(), reference.directory(2),
            reference.add(101, 10), reference.add(201, 20, 20000, b'S', 2),
            reference.add(102, 20), reference.execute(102, 4, 1),
            reference.cancel(101, 3), reference.cancel(101),
            reference.replace(102, 103, 15, 10100),
            reference.print_trade(2), reference.cross(3), reference.broken(2)]
case = reference.session(payloads, 1)
command = ' '.join(map(str, [case['flags'], *case['tick'], *case['lot']]))+' '+case['digest']+' '+' '.join(p.hex() for p in payloads)+'\n'
actual = json.loads(subprocess.check_output([sys.argv[1]], input=command, text=True))
assert reference.first_difference(case['expected'], actual) is None
print('SYNTHETIC ONLY; authored empty start; fixture SHA256='+case['digest'])
for ordinal, (wire, step) in enumerate(zip(payloads, actual)):
    print(f"source={ordinal} type={chr(wire[0])} outcome={step['category']} context={step['accepted']} native={step['native']} external={step['external']}")
for i, book in enumerate(actual[-1]['books']):
    print(f"book={i+1} journal={book['journal']} revision={book['revision']} remaining={book['remaining']}")
    print('  orders [id,side_ascii,ticks,lots,FIFO_ticket]='+json.dumps(book['orders']))
    print('  bids [ticks,lots,orders]='+json.dumps(book['bids'])+' asks='+json.dumps(book['asks']))
    print('  ledger [added,cancelled,executed,discarded,recovered,replacement_in,replacement_out,total_in,total_out]='+json.dumps(book['ledger']))
print('Independent every-event comparison passed. Source/session is an incomplete bounded synthetic prefix; no observed-market validation.')
