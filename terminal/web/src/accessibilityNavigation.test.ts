import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {searchKeyboard,searchSignature,activeSearchIndex,searchResultId} from './searchKeyboard.ts';
import type {TerminalState} from './contracts.ts';
async function leaf(name:string){
 const path=new URL(name,import.meta.url),jsx=ts.transpileModule(readFileSync(path,'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
 const compiled=jsx.replace(/from (["'])([^"']+)\1/g,(_,_q:string,target:string)=>`from ${JSON.stringify(import.meta.resolve(target.startsWith('.')&&!target.endsWith('.ts')?target+'.ts':target))}`);
 return import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
}
const {TerminalHeader}=await leaf('./TerminalHeader.tsx'),{OrderBook}=await leaf('./OrderBook.tsx');
const results=[{symbol:'AAPL',company_name:'Apple Inc.'},{symbol:'MSFT',company_name:'Microsoft Corporation'}];
const props=()=>({section:'Stock Intelligence',collapsed:false,onCollapse(){},theme:'dark',onTheme(){},onHelp(){},transport:'DISCONNECTED',query:'tech',onQuery(){},onSearch(){},results:[],message:'',onSelect(){}});
const header=(extra:Record<string,unknown>={})=>renderToStaticMarkup(createElement(TerminalHeader,{...props(),...extra}));
const attributes=(markup:string,element:string)=>markup.match(new RegExp(`<${element}\\b[^>]*>`))?.[0]||'';
const attr=(tag:string,name:string)=>tag.match(new RegExp(`\\b${name}="([^"]*)"`))?.[1];

test('global search is a named collapsed combobox with persistent polite status and keyboard instructions',()=>{
 const html=header(),input=attributes(html,'input');assert.match(input,/role="combobox"/);assert.match(input,/aria-label="Global company search"/);assert.match(input,/aria-autocomplete="list"/);assert.match(input,/aria-expanded="false"/);assert.doesNotMatch(input,/aria-controls=|aria-activedescendant=/);
 const help=attr(input,'aria-describedby');assert.ok(help);assert.ok(html.includes(`id="${help}"`));assert.match(html,/Use Up and Down Arrow/);assert.match(html,/Escape to dismiss results without changing the query/);assert.match(html,/role="status" aria-live="polite" aria-atomic="true"/);assert.doesNotMatch(html,/role="listbox"/);
});
test('actual populated search markup links one listbox and exact named options to its combobox',()=>{
 const html=header({results}),input=attributes(html,'input'),control=attr(input,'aria-controls');assert.ok(control);assert.match(input,/aria-expanded="true"/);assert.ok(html.includes(`id="${control}" class="atlas-search-results" role="listbox"`));
 assert.equal((html.match(/role="option"/g)||[]).length,2);assert.equal((html.match(/aria-selected="false"/g)||[]).length,2);assert.equal((html.match(/tabindex="-1"/g)||[]).length,2);
 for(const [index,r]of results.entries()){assert.ok(html.includes(`id="${searchResultId(control,index)}"`));assert.ok(html.includes(`aria-label="${r.symbol} · ${r.company_name}"`))}
 assert.match(html,/2 company search results for tech/);assert.doesNotMatch(input,/aria-activedescendant=/);
});
test('each concurrently rendered search owns distinct popup and instruction identities',()=>{
 const html=renderToStaticMarkup(createElement('div',null,createElement(TerminalHeader,{...props(),results}),createElement(TerminalHeader,{...props(),results}))),inputs=html.match(/<input\b[^>]*>/g)!;
 assert.equal(inputs.length,2);assert.notEqual(attr(inputs[0],'aria-controls'),attr(inputs[1],'aria-controls'));assert.notEqual(attr(inputs[0],'aria-describedby'),attr(inputs[1],'aria-describedby'));
});
test('one result and empty/error responses have correctly escaped live announcements without phantom options',()=>{
 const one=header({results:[results[0]],query:'AAPL'});assert.match(one,/1 company search result for AAPL/);
 const unavailable=header({message:'Source <unavailable> & no matches'});assert.equal((unavailable.match(/role="status"/g)||[]).length,1);assert.match(unavailable,/Source &lt;unavailable&gt; &amp; no matches/);assert.doesNotMatch(unavailable,/role="option"|role="listbox"|<unavailable>/);
});
test('query and result labels cannot become HTML or change option identities',()=>{
 const html=header({query:'<script>',results:[{symbol:'A&X',company_name:'<iframe> & issuer'}]});assert.doesNotMatch(html,/<script>|<iframe>/);assert.match(html,/&lt;script&gt;/);assert.match(html,/&lt;iframe&gt; &amp; issuer/);
});
test('arrow entry and wrap selection follows only the admitted current result count',()=>{
 assert.deepEqual(searchKeyboard({key:'ArrowDown'},2,-1),{kind:'move',index:0});assert.deepEqual(searchKeyboard({key:'ArrowUp'},2,-1),{kind:'move',index:1});
 assert.deepEqual(searchKeyboard({key:'ArrowDown'},2,1),{kind:'move',index:0});assert.deepEqual(searchKeyboard({key:'ArrowUp'},2,0),{kind:'move',index:1});
 assert.deepEqual(searchKeyboard({key:'ArrowDown'},1,0),{kind:'move',index:0});
});
test('Enter chooses only a valid active result; untouched Enter remains normal form submission',()=>{
 assert.deepEqual(searchKeyboard({key:'Enter'},2,1),{kind:'select',index:1});for(const index of [-1,2,NaN,0.5])assert.deepEqual(searchKeyboard({key:'Enter'},2,index),{kind:'none'});
});
test('Escape dismisses an open result set without supplying a replacement query',()=>{
 assert.deepEqual(searchKeyboard({key:'Escape'},2,1),{kind:'dismiss'});assert.deepEqual(searchKeyboard({key:'Escape'},0,-1),{kind:'none'});
});
test('Tab, text editing and native Home/End navigation remain unhandled',()=>{
 for(const key of ['Tab','Home','End','ArrowLeft','ArrowRight','Backspace','Delete','a',' '])assert.deepEqual(searchKeyboard({key},2,0),{kind:'none'});
});
test('input-method composition and modifier keys never choose or dismiss a result',()=>{
 for(const key of ['ArrowUp','ArrowDown','Enter','Escape'])for(const flag of ['isComposing','altKey','ctrlKey','metaKey','shiftKey'])assert.deepEqual(searchKeyboard({key,[flag]:true},2,0),{kind:'none'});
});
test('no results or invalid result counts cannot activate a phantom result',()=>{
 for(const count of [0,-1,NaN,Infinity,1.5])for(const key of ['ArrowUp','ArrowDown','Enter','Escape'])assert.deepEqual(searchKeyboard({key},count,0),{kind:'none'});
});
test('changed query, replacement labels or reordered results invalidate the old active descendant',()=>{
 const signature=searchSignature('tech',results),cursor={signature,index:1};assert.equal(activeSearchIndex(cursor,signature,2),1);
 for(const next of [searchSignature('other',results),searchSignature('tech',[...results].reverse()),searchSignature('tech',[results[0],{...results[1],company_name:'Changed source label'}])])assert.equal(activeSearchIndex(cursor,next,2),-1);
 assert.equal(activeSearchIndex(cursor,signature,1),-1);assert.equal(activeSearchIndex({...cursor,index:0.5},signature,2),-1);
});
test('successive popup actions preserve one DOM input focus contract and never infer a company',()=>{
 const signature=searchSignature('tech',results);let cursor={signature,index:-1};const picked:string[]=[];
 for(const key of ['ArrowDown','ArrowDown','Enter']){const action=searchKeyboard({key},results.length,activeSearchIndex(cursor,signature,results.length));if(action.kind==='move')cursor={signature,index:action.index};if(action.kind==='select')picked.push(results[action.index].symbol)}
 assert.deepEqual(picked,['MSFT']);assert.equal(cursor.index,1);assert.notEqual(searchResultId('stable',0),searchResultId('stable',1));
});

function state():TerminalState{return {schema_version:'1',mode:'HISTORICAL_REPLAY',origin:'HISTORICAL_SYNTHETIC',instrument:'AUTHORED',provider:'AUTHORED',price_scale:'1000000000',quantity_scale:'1000000000',book:{bids:[{price_ticks:'3',quantity:'18446744073709551615'},{price_ticks:'2',quantity:'18446744073709551615'}],asks:[{price_ticks:'4',quantity:'5'}]},metrics:{spread:null,midprice:null,microprice:null,imbalance:null},position:0,event_count:1,playing:false,speed:1,feed:{state:'REPLAY_READY'},provenance:{},feed_type:'L2_AGGREGATE'}}
const book=(value=state(),extra:Record<string,unknown>={})=>renderToStaticMarkup(createElement(OrderBook,{state:value,...extra}));
test('real order-book markup exposes exact integer values in native keyboard disclosures without hover titles',()=>{
 const value=state(),before=structuredClone(value),html=book(value);assert.deepEqual(value,before);assert.match(html,/0\.00000000…/);assert.match(html,/<details class="book-exact-values">/);assert.match(html,/<summary aria-label="Inspect exact bid level at 3 price ticks">Exact level values<\/summary>/);
 assert.match(html,/<dt>Price ticks<\/dt><dd>3<\/dd>/);assert.match(html,/<dt>Quantity integer<\/dt><dd>18446744073709551615<\/dd>/);assert.match(html,/<dd>36893488147419103230<\/dd>/);assert.doesNotMatch(html,/title="Exact bid/);
});
test('book table scroll regions are named, rows keep native table semantics and no inert row tab stops remain',()=>{
 const html=book();assert.equal((html.match(/role="region" tabindex="0" aria-label="(?:bid|ask) price ladder"/g)||[]).length,2);assert.equal((html.match(/scope="col"/g)||[]).length,6);assert.equal((html.match(/scope="row"/g)||[]).length,3);assert.doesNotMatch(html,/<tr\b[^>]*tabindex/);
});
test('raw disclosures retain accepted ordering, ask identity, origin, scales and displayed-only cumulative scope',()=>{
 const html=book();assert.ok(html.indexOf('at 3 price ticks')<html.indexOf('at 2 price ticks'));assert.match(html,/Inspect exact ask level at 4 price ticks/);assert.match(html,/Displayed cumulative quantity/);assert.match(html,/HISTORICAL_SYNTHETIC/);assert.match(html,/quantity scale 1000000000/);assert.match(html,/Displayed totals only;no inferred hidden orders/);
});
test('empty bid or ask books do not manufacture an exact level or numeric result',()=>{
 const value=state();value.book={bids:[],asks:[]};const html=book(value);assert.match(html,/No accepted bid levels/);assert.match(html,/No accepted ask levels/);assert.doesNotMatch(html,/book-exact-values|Inspect exact .* level/);assert.equal((html.match(/role="region"/g)||[]).length,2);
});
test('compact and expanded book disclosure counts respect existing visible depth bounds',()=>{
 const value=state();value.book.asks=[];value.book.bids=Array.from({length:45},(_,i)=>({price_ticks:String(100-i),quantity:'1'}));
 for(const [extra,count]of [[{compact:true},5],[{},10],[{expanded:true},40]]as const){const html=book(value,extra);assert.equal((html.match(/<details class="book-exact-values"/g)||[]).length,count);assert.ok(html.includes(`showing ${count}/45 bid`));assert.doesNotMatch(html,/at 55 price ticks/)}
});

// The same admission runner below is invoked by App; promises are supplied locally.
import {createSearchRequestGuard,runSearchRequest,runSearchSelection} from './searchRequestGuard.ts';
function deferred<T>(){let resolve!:(value:T)=>void,reject!:(reason:unknown)=>void;const promise=new Promise<T>((yes,no)=>{resolve=yes;reject=no});return {promise,resolve,reject}}
test('replacing the same query admits only the latest result when old success arrives last',async()=>{
 const gate=createSearchRequestGuard('tech'),context=gate.context(),old=deferred<string>(),latest=deferred<string>(),results:string[]=[],errors:unknown[]=[];
 const first=runSearchRequest(gate,context,()=>old.promise,v=>results.push(v),e=>errors.push(e)),second=runSearchRequest(gate,context,()=>latest.promise,v=>results.push(v),e=>errors.push(e));
 latest.resolve('latest source');await second;old.resolve('obsolete source');await first;assert.deepEqual(results,['latest source']);assert.deepEqual(errors,[]);
});
test('query change rejects late success and captured stale search handlers before loading',async()=>{
 const gate=createSearchRequestGuard('AAPL'),oldContext=gate.context(),pending=deferred<string>(),results:string[]=[],errors:unknown[]=[];let staleLoads=0;
 const old=runSearchRequest(gate,oldContext,()=>pending.promise,v=>results.push(v),e=>errors.push(e));gate.changeQuery('MSFT');
 await runSearchRequest(gate,oldContext,async()=>{staleLoads++;return 'stale callback'},v=>results.push(v),e=>errors.push(e));
 pending.resolve('AAPL late');await old;await runSearchRequest(gate,gate.context(),async query=>query,v=>results.push(v),e=>errors.push(e));
 assert.equal(staleLoads,0);assert.deepEqual(results,['MSFT']);assert.deepEqual(errors,[]);
});
test('late source errors cannot replace the current query feedback',async()=>{
 const gate=createSearchRequestGuard('AAPL'),pending=deferred<string>(),errors:unknown[]=[],results:string[]=[];
 const old=runSearchRequest(gate,gate.context(),()=>pending.promise,v=>results.push(v),e=>errors.push(e));gate.changeQuery('MSFT');
 await runSearchRequest(gate,gate.context(),async()=> 'current',v=>results.push(v),e=>errors.push(e));pending.reject(Error('obsolete source failure'));await old;
 assert.deepEqual(results,['current']);assert.deepEqual(errors,[]);
});
test('selection or Escape dismissal invalidates in-flight work and preselection same-query handlers',async()=>{
 for(const dismiss of ['selection','escape']){
  const gate=createSearchRequestGuard('AAPL'),context=gate.context(),pending=deferred<string>(),results:string[]=[],errors:unknown[]=[];let staleLoads=0;
  const old=runSearchRequest(gate,context,()=>pending.promise,v=>results.push(v),e=>errors.push(e));if(dismiss==='escape')gate.changeQuery('AAPL');else gate.invalidate();
  await runSearchRequest(gate,context,async()=>{staleLoads++;return 'stale callback'},v=>results.push(v),e=>errors.push(e));pending.resolve('late');await old;
  assert.equal(staleLoads,0);assert.deepEqual([...results],[]);assert.deepEqual([...errors],[]);assert.equal(gate.matchesContext(context),false);assert.equal(gate.context().query,'AAPL');
  await runSearchRequest(gate,gate.context(),async()=> 'explicit new search',v=>results.push(v),e=>errors.push(e));assert.deepEqual(results,['explicit new search']);
 }
});
test('unmount blocks pending success, errors and old handlers without launching new work',async()=>{
 for(const fail of [false,true]){
  const gate=createSearchRequestGuard('AAPL'),context=gate.context(),pending=deferred<string>(),results:string[]=[],errors:unknown[]=[];let calls=0;
  const run=runSearchRequest(gate,context,()=>pending.promise,v=>results.push(v),e=>errors.push(e));gate.close();
  await runSearchRequest(gate,context,async()=>{calls++;return 'unmounted'},v=>results.push(v),e=>errors.push(e));if(fail)pending.reject(Error('unmounted'));else pending.resolve('unmounted');await run;
  assert.equal(calls,0);assert.deepEqual(results,[]);assert.deepEqual(errors,[]);
 }
});
test('effect cleanup/replay accepts current handlers without resurrecting old requests',async()=>{
 const gate=createSearchRequestGuard('AAPL'),rendered=gate.context(),pending=deferred<string>(),results:string[]=[],errors:unknown[]=[];
 const old=runSearchRequest(gate,rendered,()=>pending.promise,v=>results.push(v),e=>errors.push(e));gate.close();gate.activate();
 assert.equal(gate.matchesContext(rendered),true);await runSearchRequest(gate,rendered,async()=> 'current effect',v=>results.push(v),e=>errors.push(e));pending.resolve('prior effect');await old;
 assert.deepEqual(results,['current effect']);assert.deepEqual(errors,[]);
});
test('current asynchronous or synchronous failures remain announced only for their current request',async()=>{
 const gate=createSearchRequestGuard('AAPL'),errors:unknown[]=[],results:string[]=[];const first=Error('current async'),second=Error('current sync');
 await runSearchRequest<string>(gate,gate.context(),async()=>{throw first},v=>results.push(v),e=>errors.push(e));
 await runSearchRequest<string>(gate,gate.context(),()=>{throw second},v=>results.push(v),e=>errors.push(e));assert.deepEqual(errors,[first,second]);assert.deepEqual(results,[]);
});
test('query mutation is immediate before a React rerender and cannot mutate captured ticket identity',()=>{
 const gate=createSearchRequestGuard('AAPL'),captured=gate.context(),ticket=gate.begin(captured)!;gate.changeQuery('MSFT');captured.query='MSFT';captured.revision=gate.context().revision;
 assert.equal(ticket.query,'AAPL');assert.equal(ticket.isCurrent(),false);assert.equal(gate.context().query,'MSFT');
});

test('actual selection admission refuses captured callbacks after query, dismissal, prior selection or unmount',()=>{
 for(const change of ['query','dismiss','selection','unmount']){
  const gate=createSearchRequestGuard('AAPL'),rendered=gate.context(),picked:string[]=[];
  if(change==='query')gate.changeQuery('MSFT');else if(change==='dismiss')gate.changeQuery('AAPL');else if(change==='selection')gate.invalidate();else gate.close();
  runSearchSelection(gate,rendered,'AAPL',s=>picked.push(s));assert.deepEqual([...picked],[]);
  if(change!=='unmount'){runSearchSelection(gate,gate.context(),'MSFT',s=>{picked.push(s);gate.invalidate()});assert.deepEqual([...picked],['MSFT'])}
 }
});
test('same-query replacement invalidates old rendered option callbacks before rerender',()=>{
 const gate=createSearchRequestGuard('tech'),picked:string[]=[];gate.begin(gate.context());const oldRendered=gate.context();
 gate.begin(oldRendered);runSearchSelection(gate,oldRendered,'AAPL',s=>picked.push(s));assert.deepEqual([...picked],[]);
 const current=gate.context();gate.close();runSearchSelection(gate,current,'AAPL',s=>picked.push(s));assert.deepEqual([...picked],[]);gate.activate();runSearchSelection(gate,current,'MSFT',s=>{picked.push(s);gate.invalidate()});runSearchSelection(gate,current,'AAPL',s=>picked.push(s));assert.deepEqual([...picked],['MSFT']);
});
