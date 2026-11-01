# Sprint 4 durable implementation progress

Baseline `4522948d94770ea94a6e152b68a695063d711fd4`.
Branch `feat/atlas-sprint-4-market-data-paper`,isolated worktree from that exact SHA.
Sprint3/release/main/audit worktrees and commits preserved.

## Historical core checkpoint

New `terminal/alpaca_wire.py` and `terminal/stocks/historical_v2.py` implement a default-disabled fixed-host transport boundary and explicit-feed exact-time historical client. Credentials are obtained only by a supplied future HTTP callback after authorization;no credential source was read or real HTTPWire invocation made during this task. FixtureWire is explicitly synthetic.

28 authored tests pass,0failures/skips. Coverage: exact timezone/nanosecond normalization,invalid timestamps,SIP900second boundary including1ns negative control,feed permissions,query bounds,redacted HTTP statuses,body/JSON budgets,pages,cursor loops,429bounded retry,ordered observations/identical-row dedup,conflicting identities,cancellation,cache expiry and permission rechecks. Initial test failures exposed an incorrectly authored fixture clock and bar-close `c` being mistaken for trade conditions;both corrected without weakening assertions. Source receipts retain physical counts;deduplicated records do not claim exactly-once tape completeness.

Limits:4pages×64records,512KiBwire/result,one active query,30second operation budget,16in-memory query results,60secondTTL,explicit deletion. No observed disk retention enabled. No automatic startup acquisition,no feed fallback,no session/calendar completeness claim. Official API profile references exist in the repository;no fresh official-doc retrieval or real-provider qualification is claimed.

Next exact action:implement paper-only adapter/normalization and durable-engine integration with deterministic broker fixtures;then historical/research API+browser workflows,streaming regressions,guides and complete affected validation. No Alpaca/provider/account/order operation is authorized.
