import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validateAlignedStatements} from './alignedStatementContract.ts';

const fixture = JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON || 'python3', ['-c', `
import json
from terminal.stocks.sec import facts
from terminal.stocks.statements import aligned

value = {'val': 125, 'start': '2023-01-01', 'end': '2023-12-31',
         'filed': '2024-02-01', 'form': '10-K', 'accn': '0000000123-24-000001'}
original = {'cik': '0000000123', 'facts': {'us-gaap': {'Revenues': {'units': {'USD': [value]}}}}}
result = facts(original, '0000000123', '2024-02-01')
print(json.dumps({**aligned(result), 'instrument': {'symbol': 'AAPL'}}))
`], {cwd: fileURLToPath(new URL('../../../', import.meta.url)), encoding: 'utf8', timeout: 10000}));

const admit = (value: unknown) => validateAlignedStatements(value, 'AAPL', 'income', 'annual');

test('accepts reported and missing fields from the real aligned statement producer', () => {
 const row = admit(fixture).periods[0];
 assert.equal(row.fields.revenue.value, '125');
 assert.equal(row.fields.net_income.status, 'MISSING');
});

test('rejects stale requests, false period bindings and mismatched amounts or units', () => {
 const changes = [
  (reply: typeof fixture) => {reply.statement = 'cash';},
  (reply: typeof fixture) => {reply.period_filter = 'quarter';},
  (reply: typeof fixture) => {reply.periods.push(reply.periods[0]);},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.value = '126';},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.unit = 'shares';},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.source_facts[0].end = '2023-12-30';},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.source_facts[0].duration_days++;},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.source_facts[0].form = '10-Q';},
  (reply: typeof fixture) => {reply.periods[0].fields.revenue.source_facts[0].filed = '2024-02-30';},
  (reply: typeof fixture) => {reply.periods[0].fields.net_income.status = 'AMBIGUOUS';},
 ];
 for (const change of changes) {
  const reply = structuredClone(fixture);
  change(reply);
  assert.throws(() => admit(reply), /Invalid aligned statement/);
 }
});
