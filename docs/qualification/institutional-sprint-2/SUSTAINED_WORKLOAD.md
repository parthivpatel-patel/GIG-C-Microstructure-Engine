# Four-symbol bounded sustained workload

Measured on clean implementation `c9c75c486cf6ef44b1556bf3858eaaff53578aa0`. Candidate `b91de9e0189a6a4ebbcb1c1cbcc583945495e297` changes only browser-test instrumentation and progress documentation afterwards; runtime, benchmark and native source are byte-identical. Environment metadata and the complete measurements are bound in EVIDENCE.json.

## Method and actual envelope

One measured run, 900 authored batches, nominal 100 ms producer cadence and the actual 250 ms `MarketEvents` projection cadence. No warmup; this includes startup, forced reconnects, storage failure, cleanup and full ledger recovery. This is a bounded roughly 90-second qualification, **not** a full-session soak or an arrival-rate SLA. Earlier 300-batch exploratory runs are retained separately and are not the final measurement.

The production `LiveIEX` state machine, MessagePack parsing, shared subscription lifecycle, history/deduplication, SQLite store and ASGI streaming responses run unchanged. The connector is a bounded fake transport; credentials are authored fixture strings, and a socket guard prohibits non-loopback network access. AAPL, AMZN, MSFT and NVDA are fixture identities. No provider or observed data is used.

Eight consumers run with real send delays (0, 20 ms, 400 ms and one 2.25 s consumer). The production two-second send deadline terminates the slow consumer. A ninth client is refused. One active consumer is canceled and replaced. Quote-only and quote/trade channel sets exercise unsubscribe/subscribe. One socket exception exercises actual automatic reconnect/backoff; two explicit stop/start cycles and one storage-failure restart exercise cleanup. Queue capacity is four frames, each at most 32 KiB. An independent test fills all four slots and verifies the fifth producer blocks and cancels safely.

| Observation | Measured result |
|---|---:|
| Wall time, including recovery | 92.874206 s |
| Parent process CPU | 68.011113 s (73.23% of one core over this run) |
| Accepted observations | 6,600 |
| Independently matched recovered observations | 6,600 |
| Identified duplicate observations | 388 |
| Accepted observations marked out of order | 344 |
| Bounded history / deduplication limit | 256 each |
| History evictions / persisted prefix evictions | 6,344 / 0 |
| Source connections opened / closed | 5 / 5 |
| Upstream fixture queue peak / limit | 1 / 4 |
| Subscription control messages | 9 |
| ASGI snapshot send attempts / independently validated deliveries | 1,972 / 1,971 |
| Timed-out sends | 1 |
| Delivered encoded body bytes | 125,533,994 |
| Peak simultaneous encoded send bodies | 1,059,586 bytes |
| Final clients / sends / bytes / application backlog | 0 / 0 / 0 / 0 |
| Final SQLite database | 13,889,536 bytes |
| Process peak RSS, including full recovery and harness | 164,192 KiB (160.34 MiB) |

CPU: Intel Xeon Platinum 8573C, five logical CPUs visible; Debian 13 x86_64, Python 3.12.14, Release native module built with GCC 14.2.0. Tracemalloc is enabled, so this is not an uninstrumented throughput benchmark. Approximately 71.06 accepted events/s over the whole run reflects the configured offered workload and barriers, **not maximum ingestion throughput**. Per-event p50/p95/p99 and unthrottled burst loss were not measured.

At batches 180/360/540/720, traced current memory was 11,046,192 / 11,179,526 / 12,112,494 / 12,769,005 bytes; history was capped at 256. The bounded independent oracle grows with offered events, and the final full recovery materializes up to the admitted ledger budget. Consequently total RSS is not demonstrated flat: the final recovery increases peak RSS to the value above. This run does not prove day-long leak freedom. Serialized caps are not a managed-heap cap. There is no new universal latency or memory SLA.

## Accounting, faults and limits

The declared recipe produces 3,600 quotes and 3,000 trades. All 6,600 accepted semantic records match independently authored expectations in receipt order after restart. There are 388 duplicate candidates and eight extra event candidates in the deliberately rejected ENOSPC batch; that batch is reoffered only after a clean restart. Its first failed attempt changes neither accepted receipts nor ledger count. Control/authentication messages are not included in market-event counts. Programmed recovery gaps offer no events, so no exchange completeness or source-loss claim follows. Late events are classified and accepted according to the existing policy, not silently discarded.

The workload injects `OSError(28)` at the commit boundary; it does not fill the host disk. The separate admission regression triggers actual `SQLITE_FULL` by freezing page capacity, then proves rollback/restart. Client snapshots intentionally coalesce current state rather than queue every source event. The application queue ends empty; the real provider's transport queue metric remains unavailable. This is post-authorization ASGI transport qualification, not GitHub authentication or TCP-network backpressure evidence.

Semantic SHA256: `73242669f75340e2979363c672c800338a82f28352f07cc0911c510b8d6d7791`. Recipe SHA256: `1d711150377d7d636e6f10092a62862a7794d58c1211f17b61ca6fd114db85ac`. The semantic fingerprint binds receipt, symbol, kind and exact data; runtime source/receipt clocks remain in the ledger but are excluded from this deterministic semantic fingerprint. Timing, encoded byte counts and memory are expected to vary.

## Reproduction

With runtime dependencies and the native module already installed, from the repository root:

```bash
.venv/bin/python scripts/qualify_sustained_workload.py --batches 900 --output build/sprint2-workload-new.json
```

The output must not already exist. The driver owns temporary private synthetic state and removes it after completion. It asserts bounds and independent semantic agreement; assertions must remain enabled (do not use Python `-O`). The driver permits 300–3,000 CLI batches, bounds the reference suffix at 10,000 records and verifies persisted receipt continuity even when retention evicts a prefix. The 900-batch run's cooperative acquisition deadline is 110 seconds plus cleanup; no hard OS or filesystem deadline is claimed. The 3,000-batch envelope was not measured here.
