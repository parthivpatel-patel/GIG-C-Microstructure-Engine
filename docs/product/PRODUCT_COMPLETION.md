# Current provider/history checkpoint — October29,2026

See [Phase Next integration report](PHASE_NEXT_DATA_INTEGRATION_REPORT.md),
[private setup/qualification guide](ALPACA_RESEARCH_DATA_SETUP.md) and
[executed evidence](phase_next_evidence.json). Implementation checkpoint
`89d06adb973c4a3f5cb8f3da3e734721a63bfe02` adds paper-account asset discovery,
source filters,bounded bars/quotes/trades,historical aligned comparisons and non-seed
SEC qualification. Current default actual coverage remains13 fallback identities,
0 imported Alpaca assets,0 official exchange imports and0 accepted official SEC
mappings. The new adapter is fixture-qualified,not live-provider verified.

The latest cohort passes207 stock tests/configuration,274 terminal/native consumers
/configuration,45 frontend tests,151 browser checks,53 security/8 HTTPS-WSS checks,
8 unchanged native references,14 installed-wheel tests,3 packaging cases and an819-member
implementation source inventory. See the report for exact scope,failures preserved,
measurements and remaining external permissions/infrastructure gates.

The previous checkpoints below are preserved historical evidence.

---

# Current product checkpoint — October28,2026

See [product-development report](PRODUCT_DEVELOPMENT_REPORT.md),
[source ledger](SOURCE_ACCESS_LEDGER.md),[visual QA](PRODUCT_VISUAL_QA.md) and
[verified evidence](product_evidence.json). The research desk,all12 workspaces,
SEC startup/cache discovery,company coverage and advanced source-aware 3D work are
implemented and fixture-qualified at `7b28431943d2eb3d63485bf248015242321da32e`.
Official current coverage here remains0 listing identities/0 SEC mappings/13 fallback
identities. Source/provider/actual-candidate ARM64/device qualification remain open.
This supersedes the earlier IN PROGRESS labels below;the original checkpoint record
is preserved as historical evidence,not silently rewritten as current results.

---

# Product completion program — October28,2026

Baseline50b83c581297a200ffc15b6f5a4801b0a60a5d49. Previous engineering acceptance
is not product acceptance. The owner rejected the narrow experience as final.

| Milestone | Engineering | Actual source/product qualification |
|---|---|---|
|Official US listing directory |Two-file bounded parser,index,pagination,fixed HTTPS acquisition,six-hour atomic refresh,last-accepted recovery;process lifetime only |BLOCKED source-use rights;actual official imported count0 |
|SEC identity and financial coverage |Existing authoritative resolver,period-aware facts/ratios/filings;optional background SEC-directory refresh behind ready SEC config |No current SEC config or official reconciliation here;no invented CIKs |
|Market integration |Accepted directory identities route to existing gated stock loaders/IEX subscription manager |No feed activation;unlimited discovery is not unlimited subscriptions |
|Institutional IA and overview |IN PROGRESS |No product-acceptance claim |
|Advanced visualization suite |IN PROGRESS |No fabricated observed depth |
|End-to-end product qualification |PENDING |External provider,source rights,device and exact-candidate ARM64 remain open |

## Official source investigation

Metadata-only requests on October28 returned200 for:
- https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs
- https://www.nasdaqtrader.com/Trader.aspx?id=CopyDisclaimMain

The linked terms restrict alteration,storage and other uses except specified personal
noncommercial copies or prior consent. Public accessibility does not establish rights
for automatic cloud processing/private derived-catalog display. No listing files were
downloaded. Raw official listing data is not included in Git. Source bytes and hashes
in automated tests are independently authored fixtures only.

Fixed acquisition candidates are Nasdaq Trader's HTTPS dynamic/SymDir/nasdaqlisted.txt
and otherlisted.txt. Their actual availability/content has not been tested by download.
Implementation requires server-only GIG_DIRECTORY_USE_APPROVED=1 and a nonempty
GIG_DIRECTORY_PERMISSION_REFERENCE after real use rights are verified. These settings
are declarations,not proof of rights. No flag was enabled in this assignment.

The automatic worker refreshes at startup and every21600s only when approved. Explicit
refresh uses an endpoint-bound same-origin proof;minimum retry interval300s. Both files
must parse and share their declared creation date before one new indexed snapshot
is published. Failure preserves the prior accepted snapshot. Directory retention is
process-lifetime only;restart reacquires when allowed. No licensed raw file is persisted.
SEC mappings can separately refresh with GIG_SEC_DIRECTORY_AUTO_REFRESH=1 and existing
SEC fair-access/identifying configuration. Nasdaq identity never grants SEC mapping,
provider support,tradability or retention rights.

Source parsing excludes declared test issues and symbols outside the native lexical
contract,counts both exclusions,and rejects collisions/malformed enums/truncated footers.
It preserves ACT/CQS/Nasdaq aliases without silently mapping punctuation between vendors.
ETF/NextShares classification comes from source flags;other subtypes remain UNCLASSIFIED
rather than guessed from names. Presence in a directory is not a real-time active/halt
state. Historical delisted coverage is unavailable. Safety ceilings8MiB/file and100000
combined rows reject excess input;they do not truncate an accepted universe.

GET/api/v2/securities supports exact/prefix ticker and word-prefix company search,
offset/limit pagination (up to100/page),source metadata and counts. GET/status reports
actual official count separately from fallback identity count. POST/stocks/directory-refresh
is permission/proof gated. Existing v1 consumers and curated fallback remain supported;
fallback identities are clearly not a full current official universe.

Initial validation:13 directory/catalog tests,164 stock regressions,274 terminal
regressions pass on Debug binding. Full product qualification remains ongoing.

## Financial availability and routing checkpoint

A read-only versioned company availability endpoint now distinguishes unknown identity,
known security/unverified CIK,CIK with unavailable filings,filings without selected facts,
selected facts available,and temporary SEC failure with cached evidence preserved.
An injected synthetic SEC mapping is not labelled current official reconciliation.
No unverified CIK,missing financial zero,provider entitlement or live depth is invented.

The strict stock cohort includes the directory and availability regressions:175 cases
pass under Debug,Release and ASan+UBSan (live LSan check0). This is authored qualification,
not an actual listed-universe import. Source/core C++ expectations remain unchanged.
