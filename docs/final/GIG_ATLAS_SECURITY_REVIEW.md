# Security and operational review

Preserved exact-origin/Host rules,private Codespaces authentication,one-use endpoint-bound
proofs,body/rate limits,server credentials,provider permissions,no-cost gate and private
storage. Added only exact proof targets live,dataset-analysis,garch-optimization. Forged
forwarding headers/foreign origins remain rejected;no wildcard CORS or local-Origin bypass.

IEX endpoint fixed;redirects denied;inherited WebSocket proxy/TLS path retained,certificate
verification never disabled. Upstream frames32KiB/128 messages,queue4,symbols4,dedup256;
finite reconnect ceiling. Control/error payloads never logged verbatim. Deterministic
reason/code diagnostics avoid credentials. HTTP errors do not expose provider body/key.
Unknown semantics fail closed;one invalid message cannot publish earlier rows of its
frame. Socket/cancellation cleanup exercised with fake async transport.

New endpoints do not accept URLs,file paths or credentials. Retained revisions recheck
hash/schema/expiry/origin permission before analysis. Explicitly conflicting price units
rejected. Only authored derived research can be exported by the UI;observed export is
disabled. No private ZIP,market rows,databases,credentials or generated binary screenshots
in tracked changes. SQLite access limits are access-expiry/purge-on-write policies,not a
physical erasure guarantee or cross-process HA system. Original backup limitations remain.

Executed46 security checks,8 verified-TLS/WSS proxy checks,new endpoint proof/forgery
regressions and real browser blocked-start test. Not a professional penetration test,
network infrastructure audit or externally authenticated Codespaces acceptance. Small
msgpack dependency is pinned;no comprehensive current CVE database claim. No workflows,
paid services,broker activity or real-data requests launched.
