import {ArrowIcon} from './WorkspaceIcon';
import { useState, useEffect } from 'react';
import { request, readDirectoryStatus } from './api';
import { validateMarketState } from './marketContract';
import type { DirectoryStatus } from './directoryContract';
import { validateDirectoryStatus } from './directoryContract';
import type { Feed } from './LiveMarket';
export default function ResearchDesk({ selected, onOpen, onNavigate, nativeOrigin }: {
    nativeOrigin: string;
    selected: string;
    onOpen: (s: string) => void;
    onNavigate: (s: 'Securities Universe' | 'Live Markets' | 'Multi-Stock Comparison' | 'Historical Replay') => void;
}) {
    const [watch, setWatch] = useState<string[]>([]), [feed, setFeed] = useState<Feed | null>(null), [directory, setDirectory] = useState<DirectoryStatus | null>(null), [error, setError] = useState('');
    useEffect(() => { let active = true; const c = new AbortController(); try {
        const a = JSON.parse(localStorage.getItem('gig.stock.watch.v1') || '[]'), b = JSON.parse(localStorage.getItem('gig.iex.watch.v1') || '[]');
        setWatch([...new Set([...(Array.isArray(a) ? a : []), ...(Array.isArray(b) ? b : [])])].filter((s): s is string => typeof s === 'string' && /^[A-Z][A-Z0-9.-]{0,13}$/.test(s)).slice(0, 20));
    }
    catch { } const load = () => { void request('/stocks/live').then(v => { if (active)
        setFeed(validateMarketState(v)); }).catch(() => { if (active)
        setError('Equity feed status unavailable'); }); void readDirectoryStatus(c.signal).then(v => { if (active)
        setDirectory(validateDirectoryStatus(v)); }).catch(() => { }); }; load(); const t = setInterval(load, 5000); return () => { active = false; c.abort(); clearInterval(t); }; }, []);
    return <section className="research-desk" aria-label="Research command desk">
 <div className="desk-research-header"><div><span className="eyebrow">YOUR RESEARCH,CONNECTED</span><h2>Pick up where your questions begin.</h2></div><button onClick={()=>onOpen(selected)}>Continue {selected} research <ArrowIcon/></button></div>
 <div className="desk-body"><section className="desk-watch"><header><div><span className="eyebrow">SAVED IDENTITIES / NO AUTOMATIC ACQUISITION</span><h3>Research watchlist</h3></div><button onClick={()=>onNavigate('Live Markets')}>Manage monitoring</button></header>{watch.length?<div className="atlas-table-scroll" tabIndex={0}><table className="watchlist-table"><caption className="sr-only">Saved research identifiers and their available quote receipts</caption><thead><tr><th>Security</th><th>Retained bid / ask</th><th>Observation state</th><th>Research</th></tr></thead><tbody>{watch.map(s=>{const q=feed?.observations.find(r=>r.symbol===s&&r.kind==='quote');return <tr key={s}><th>{s}</th><td>{q?`${q.data.bid} / ${q.data.ask}`:'Not acquired'}</td><td><span className="tag">{q?.state||'UNAVAILABLE'}</span>{q&&<small>{q.timestamp}</small>}</td><td><button onClick={()=>onOpen(s)}>Open {s} <ArrowIcon/></button></td></tr>})}</tbody></table></div>:<div className="desk-empty"><span className="empty-symbol" aria-hidden="true">＋</span><h4>Your next company starts here.</h4><p>Save identifiers in Stock Intelligence or Live Markets. A saved symbol never starts a provider connection.</p><button onClick={()=>onOpen(selected)}>Open {selected} company</button></div>}</section>
 <aside className="desk-session"><span className="eyebrow">SOURCE READINESS</span><h3>Evidence before activity.</h3><dl><div><dt>Equity source</dt><dd>{feed?.readiness.ready?feed.state:'Not authorized / configured'}</dd></div><div><dt>Accepted catalog</dt><dd>{directory?.actual_official_count?`${directory.actual_official_count} listing identities`:directory?.asset_reference?.accepted_count?`${directory.asset_reference.accepted_count} provider references`:'Not acquired'}</dd></div><div><dt>Native lab</dt><dd data-testid="origin-label">{nativeOrigin}</dd></div><div><dt>Retention</dt><dd>Permission-gated</dd></div></dl><p>Configuration readiness is not live-data qualification. No broker order submission.</p></aside></div>
 <div className="desk-workflows">{[['01','Discover & identify','Securities Universe','Identity, issuer coverage and feed rights are separate.'],['02','Monitor observations','Live Markets','Authorized quotes and prints. Honest quiet and missing states.'],['03','Compare with context','Multi-Stock Comparison','Retained source windows with per-symbol attribution.'],['04','Investigate mechanics','Historical Replay','Native authored L3. Kept separate from observed Level 1.']].map(([n,title,target,description])=><button key={n} onClick={()=>onNavigate(target as Parameters<typeof onNavigate>[0])}><span>{n}</span><strong>{title}</strong><small>{description}</small><i aria-hidden="true"><ArrowIcon/></i></button>)}</div>{error&&<p role="status">{error}</p>}
 </section>;
}
