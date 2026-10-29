# Authoritative securities-reference source ledger

Review: October28,2026 America/New_York. No paid resource,listing-body or market-data
download. Terms interpretation is recorded conservatively;public accessibility is not
an unrestricted cloud-processing or redistribution license.

| Source | Verified evidence | Unresolved boundary / decision |
|---|---|---|
| Nasdaq Trader definitions | `https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs` GET200,114996 response bytes; official layout documentation read | Format candidate only; not proof of actual current file body or complete security subtype coverage |
| Nasdaq Trader linked terms | `https://www.nasdaqtrader.com/Trader.aspx?id=CopyDisclaimMain` GET200,89749 bytes; linked use restrictions reviewed | Personal noncommercial unaltered-copy exception does not establish derived cloud-catalog use; prior consent may be required. Gate stays off |
| Nasdaq-listed directory | `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt` HEAD200;Content-Length348751;Last-Modified2026-10-28T22:01:37GMT | Body not acquired;header size/date not independently verified content/integrity. Exact daily availability/classification/source rights unqualified |
| Other-listed directory | `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt` HEAD200;Content-Length542893;same Last-Modified | Same boundary; requires BOTH files and validated complete publication for implemented importer |
| SEC company ticker reference | Existing fixed `https://www.sec.gov/files/company_tickers.json` acquisition/parser contract inspected; automatic startup/cache/refresh tested with authored bytes | No ready SEC identifying configuration here;no request attempted. Authoritative issuer/ticker mapping,not complete US-listed universe. Current mappings do not prove historical identity |
| Existing provider reference / Alpaca | Existing gated catalog/import/credential contracts inspected | Account/source permissions and actual credentials required;no source activation or new provider capability invented |
| NYSE directory / Cboe reference candidates | Candidate providers identified only | No request made;current environment policy does not configure those domains. Exact artifact,free access,usage rights,coverage and format UNVERIFIED. No unauthorized mirror used |

Sanitized response-header records,official terms/definitions receipts and hashes are in
the local evidence manifest. Set-Cookie headers were removed before evidence hashing;
no cookie/token or identifying SEC contact is committed. HEAD metadata is explicitly
separate from source-body evidence. No LOBSTER/Nasdaq historical data was inspected or
downloaded in this product checkpoint. An earlier user-provided Nasdaq email covering
ITCH samples is not reinterpreted as permission for a different directory product.

## Implemented safe acquisition boundaries

Nasdaq source use requires server-only `GIG_DIRECTORY_USE_APPROVED=1` plus a nonempty
`GIG_DIRECTORY_PERMISSION_REFERENCE` after actual permission is established. These
declarations are not proof of rights. Fixed HTTPS endpoints,certificate validation,no
redirects,8MiB per source,100000 accepted combined rows,2048-character lines,25-second
operation cap,complete headers/footers and matching declared creation dates protect
publication. Unknown file timezone remains unspecified. Source hash,receipt,exclusions
and classification are preserved. No partial update or silent truncation. No persistent
raw catalog storage;restart reacquires only when authorized. Six-hour refresh and
300-second manual cooldown do not grant provider/retention entitlements.

SEC permission and identifying/fair-access readiness are checked independently.
Automatic ready-server startup and six-hour refresh can be disabled with
`GIG_SEC_DIRECTORY_AUTO_REFRESH=0`;injected fixtures do not acquire implicitly.
Successful reference snapshots may be reused for60 seconds after permission recheck,
with original receipt/hash intact. Read-only discovery GETs do not fetch upstream.
Explicit endpoint-bound-proof refresh controls remain separate for both sources.

## Smallest next source step

Use the already approved identifying SEC configuration in its authorized environment to
qualify registrant discovery separately. For full current listings,obtain a specific
Nasdaq directory-use determination or independently review an official zero-cost
alternative before acquisition. Verify format,exclusions,symbol collisions,coverage,
retention and redistribution rights independently. Until then advertise accepted
identifier counts and source classes,not full US stock coverage.
