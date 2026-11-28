import {decimalFraction, inPeriod} from './financial.ts';
import type {Fact, Period} from './financial.ts';

type Field = {value: string | null; unit: string | null; status: string; source_facts: Fact[]};
type AlignedResponse = {
 statement: string;
 period_filter: Period;
 periods: {start: string | null; end: string; fields: Record<string, Field>}[];
 selected_component_checks?: unknown;
};

const day = (value: unknown): value is string =>
 typeof value === 'string' && /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value) &&
 !value.startsWith('0000') && Number.isFinite(Date.parse(value)) &&
 new Date(value).toISOString().slice(0, 10) === value;

export function validateAlignedStatements(raw: unknown, symbol: string, statement: string, period: Period): AlignedResponse {
 const reply = raw as AlignedResponse & {schema: string; instrument: {symbol: string}};
 const invalid = () => {throw new Error('Invalid aligned statement contract');};
 if (!reply || reply.schema !== 'gig.backend.statements.v2' || reply.instrument?.symbol !== symbol ||
     reply.statement !== statement || reply.period_filter !== period ||
     !Array.isArray(reply.periods) || reply.periods.length > 12) invalid();

 const periods = new Set<string>();
 for (const row of reply.periods) {
  if (!row || !day(row.end) || (row.start !== null && (!day(row.start) || row.start > row.end)) ||
      (row.start === null) !== (statement === 'balance') ||
      !row.fields || typeof row.fields !== 'object' || Array.isArray(row.fields) ||
      Object.keys(row.fields).length > 16) invalid();
  const periodKey = JSON.stringify([row.start, row.end]);
  if (periods.has(periodKey)) invalid();
  periods.add(periodKey);

  const duration = row.start === null ? null : (Date.parse(row.end) - Date.parse(row.start)) / 86400000 + 1;
  for (const field of Object.values(row.fields)) {
   if (!field || !Array.isArray(field.source_facts) || field.source_facts.length > 8) invalid();
   for (const fact of field.source_facts) {
    if (!fact || fact.start !== row.start || fact.end !== row.end || fact.duration_days !== duration ||
        !day(fact.filed) || fact.filed < fact.end || !/^[0-9]{10}-[0-9]{2}-[0-9]{6}$/.test(fact.accession) ||
        typeof fact.concept !== 'string' || !/^[A-Za-z_][A-Za-z0-9_.-]{0,127}$/.test(fact.concept) ||
        !['10-K', '10-K/A', '10-Q', '10-Q/A'].includes(fact.form ?? '') ||
        !['USD', 'USD/shares', 'shares'].includes(fact.unit) || typeof fact.value !== 'string' ||
        (statement !== 'balance' && !inPeriod(fact, period))) invalid();
    decimalFraction(fact.value);
   }
   const [source] = field.source_facts;
   const status = field.source_facts.length === 1 ? 'REPORTED' : source ? 'AMBIGUOUS' : 'MISSING';
   if (field.status !== status || field.value !== (status === 'REPORTED' ? source.value : null) ||
       field.unit !== (status === 'REPORTED' ? source.unit : null)) invalid();
  }
 }
 return reply;
}
