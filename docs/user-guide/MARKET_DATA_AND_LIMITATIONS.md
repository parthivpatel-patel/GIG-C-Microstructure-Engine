# Market data and evidence boundaries

Identity discovery, SEC issuer financials, venue-limited market data, native synthetic replay and mathematical scenarios are independent capabilities. A searchable symbol does not establish SEC CIK, financial coverage, exchange-listing completeness or feed entitlement. Preserve null identity fields if not authoritatively verified.

- **Retained provider quote:** an actual accepted source observation, carrying source/receipt time and explicit age/state. It does not become current again after a disconnect. Source/receipt clock differences are not measured network latency.
- **Historical observation:** bounded accepted historical records; gaps, adjustments and complete-session coverage must be stated.
- **Native authored replay:** deterministic synthetic book/event fixture. It is useful for independent correctness tests, not empirical exchange validation.
- **Mathematical scenario:** user-declared parameters or returns. Outputs are calculations conditional on those inputs.
- **Unavailable/blocked:** no accepted or authorized input. No synthetic fallback is allowed to impersonate live data.

## IEX readiness

The existing Alpaca integration has independent catalog/history/live/retention gates, bounded symbol counts, one shared upstream connection, subscription handover, source/receipt metadata, bounded recent observations, ordering/correction diagnostics, session evidence and bounded browser-push retry. This sprint exercises these through deterministic fixtures only. No credentials are inspected and no Alpaca connection is made. Free Basic account availability does not itself resolve private cloud/display/history or retention scope. Do not enable flags based on this guide.

IEX is Level 1, not full-US-market NBBO, Level 2 or Level 3. No order identities, queue priority, signed executions or depth are reconstructed from it. Quiet feeds, stale observations and browser failures are distinguished. Coalesced browser history is incomplete, not a lossless tape. Observed-data persistence remains permission-gated; new fake-paper persistence is a separate authored-only store.

## SEC provenance

Selected facts retain source hash/reference, concept, units, filing period, missingness and source time where available. Historical acceptance-time metadata can be absent; it must not be recreated from cache receipt dates. Financial duration filters do not manufacture quarters by subtracting cumulative values. Amendments and as-of queries require explicit availability evidence to avoid look-ahead.

Existing owner-reported 10,429 identities and 1,772-record reconciliation remain owner observations until exact supplied artifacts are bound and verified. This sprint makes no new SEC request or provider-verification claim. The LOBSTER attachment remains inaccessible for processing without confirmed cloud permission; do not inspect or extract it here. No new historical market data is downloaded.

## Qualification still required

Current-commit owner Codespaces private authentication/HTTPS-WSS, provider permissions and read-only qualification, source-bound observed evidence, current native ARM64, physical-device usability and separately authorized real paper account/order tests remain distinct gates. Passing fixtures or displaying a connected local browser does not close them.

## Sprint4 historical and paper permission ledger

The owner reports Alpaca Support affirmed individual personal/noncommercial Basic research/backtesting,local storage,venue-limited real-timeIEX,and historicalSIP with explicit feed=sip/end at least15minutes old. Redistribution,multi-user display and business-entity retail-plan use remain prohibited. Those statements do not independently answer private Codespaces processing/display or historicalIEX scope. No new provider call or fresh official API-document retrieval was made in this sprint;existing repository references are the implementation profile,not live verification.

All provider/history/paper gates remain default-off. Historical v2 adds independent enable/cloud/private-display/protocol/no-cost/reference and IEX/SIP flags;exports require their own permission. Even the legacy v1 real historical path now requires the specific IEX historical permission. Authored transports can never produce OBSERVED origin. Separate paper execution flags do not inherit market-data authorization.

Historical limits:four pages×64physical records,512KiBresponse/result,30second operation,one active query,max2bounded429retries,no retries for other errors,no feed fallback. Exact source nanoseconds and offsets survive normalization. Identical normalized records collapse with physical page counts retained;this is not proof of a complete or corrected tape. Memory cache16queries,logical60secondTTL,access pruning and periodic60second cleanup;physical deletion is not instantaneous at the TTL boundary. Explicit deletion is available. No observed disk cache is enabled. Session evidence remains UNKNOWN unless an explicit schedule supplies limited coverage.

The owner-verified Sprint3 directory count is10,423SEC ticker mappings,not a verified exchange-listed universe. Prior owner-reported10,429identity and1,772reconciliation counts retain their original evidence scopes;they are not replaced or reverified by these authored tests. Provider account/market qualification,private-target authentication,ARM64current candidate and real historical completeness are separate future evidence gates.
