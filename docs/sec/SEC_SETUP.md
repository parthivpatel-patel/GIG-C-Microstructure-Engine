# SEC setup and bounded verification in Codespaces

No paid service/API key is required by this code. SEC request policy acknowledgment and
an owner-provided identifying application/contact User-Agent are still mandatory. Startup,
readiness and requests now share one SEC parser. Accepted true strings(case-insensitive,
outer whitespace ignored):1,true,yes,on. False:0,false,no,off,empty. Missing/unknown values
stay disabled. This is SEC-specific;Alpaca flags/entitlements are unchanged.

## Existing Codespace

Stop the old server with Ctrl+C,preserve local edits,and update the existing final branch:

```bash
git switch feat/atlas-final-release
git pull --ff-only
.venv/bin/python scripts/configure_sec.py --check
```

If approved Codespaces secrets already provide all3 SEC settings and ready:true,skip
configuration. Otherwise use the private helper after the owner's fair-access review:

```bash
.venv/bin/python scripts/configure_sec.py --configure --policy-reviewed
.venv/bin/python scripts/configure_sec.py --check
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Contact is entered at a hidden terminal prompt,not as a shell argument. The helper writes
only SEC settings to ignored `.gig-sec/config.json`(owner directory0700,file0600,atomic
replace/file+directory fsync). No shell code is sourced. App identification is GIG ATLAS;
contact must be the owner's real email,not the authored test addresses. No contact or
User-Agent is printed by the checker,startup log,API or browser. Private contact storage
is not an encrypted secret manager;Codespaces secrets remain an alternative.

Environment variables take precedence for each key,INCLUDING explicit empty/false values.
If an obsolete exported value shadows the private file,fix the Codespaces secret/export,
or intentionally unset that key in this server's terminal to use the file. Changes made
in another terminal do not modify an already running process. Restart after changing
configuration;reopen the terminal/Codespace if new Codespaces secrets were not injected.
Do not paste contact/credential values into chat or screenshots. Never commit private files.

The safe example sec-config.example.json is deliberately disabled and has an invalid
placeholder contact. Do not enable it without review. Symlink,duplicate/unknown-key,
wrong-owner/public-mode,malformed or>4096-byte private files fail closed for SEC. Other
native functionality can still start. Complete explicit environment configuration takes
precedence without reading the unused private file.

## Browser acceptance

Keep8787 PRIVATE and use the existing authenticated Codespaces forwarded HTTPS URL.
Open Stock Intelligence and select AAPL(user action starts the existing gated loader),or
press Refresh SEC disclosures. Inspect /api/v1/stocks/company?symbol=AAPL:

* configuration.sec.ready=true;missing_configuration empty.
* configuration.sec.user_agent_present/user_agent_valid true;no actual contact value.
* instrument.cik=0000320193;fundamentals status AVAILABLE or clearly explained PARTIAL.
* source receipts identify fixed official submissions/companyfacts URLs and hashes;
  financial records preserve concept,unit,actual start/end,filed date and accession.
* sec_refresh reports success,cached reuse,cancellation or sanitized failure accurately.
* UI shows reported/derived/stale/unavailable/error distinctions. Fiscal duration and
  response receipt time are different. Annual,quarter,YTD are not TTM;no subtraction.

A refresh performs at most2 fixed official requests,1second pacing,25s whole-operation
budget,8MiB per source response,redirect/compression/body validation and zero automatic
retries. Accepted SEC responses are reused for60seconds on browser/loader refresh;
repeated clicks do not generate another request pair. HTTP429/503 enforce a60s upstream
cooldown;other failed refreshes impose existing10s cooldown. Read-only UI polling does
not acquire SEC data. No background continual SEC ingestion was added.

Cache is bounded/process-local,NOT persisted financial storage. Restart requires another
explicit selection/refresh. Failed or cancelled requests preserve accepted cache;partial
first-load filings stay visible. A later failed Company Facts component cannot erase
previously accepted financials or relabel old receipts as new. Entire prior SEC packet is
retained in that case;new partial filings are not silently mixed into it. Stale means
cached response age>24h(application disclosure),not a statement about fiscal completeness.

## Optional owner-run official reconciliation

Only when checker says ready:true and approved network access is available:

```bash
.venv/bin/python scripts/qualify_sec_sources.py --symbol AAPL --as-of 2026-10-26 --fetch --output build/sec-owner-reconciliation.json
```

This reads a bounded official Company Facts response and reconciles selected source
records using independent calculations. It also resolves the same private configuration.
Use the intended filing cutoff;do not claim intraday point-in-time/full statements from
this check. On upstream403/proxy/TLS failure,stop,report the sanitized error and resolve
access through supported policy;never disable TLS or bypass restrictions.

This Codex session has NO approved User-Agent or SEC enable/policy flags,so no live SEC
request was attempted. Tests use independently authored data and mocked HTTP,not actual
AAPL financial evidence. Codespaces owner acceptance remains the final external check.
