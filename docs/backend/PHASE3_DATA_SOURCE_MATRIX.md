# Phase 3 data source and authorization matrix

|Source|Actual status in this task|Authority/provenance|Limit|
|---|---|---|---|
|SEC company facts/submissions|BLOCKED_CONFIGURATION|Owner authorizes bounded official read-only reconciliation if existing valid UA is available|Current GIG_SEC_USER_AGENT absent;SEC review gates disabled;no request made|
|Curated company identities|AVAILABLE_SEEDS|identity.py eight manually curated routes|Not a current official listing directory|
|Authored SEC/IEX/options bodies|AVAILABLE_SYNTHETIC|test_repair.py,test_workspace.py,atlas fixture servers;injected fetchers|Never relabelled observed,never empirical reconciliation|
|Alpaca IEX|BLOCKED_PERMISSION|Existing fixed-domain REST adapter and server-side credentials policy|Support381230 pending;no gates or credentials changed|
|Alpaca indicative options|BLOCKED_PERMISSION|Separate indicative-only profile|Not OPRA,NBBO or full depth;no feed activation|
|NASDAQ historical samples|NOT_ACQUIRED_THIS_PHASE|Prior project records/user-provided permission distinguish use from redistribution|No new network request/download;valid complete initialization not inferred|
|LOBSTER attached sample|RESTRICTED|Owner explicitly withheld cloud processing absent authorization|Not opened,extracted,processed or redistributed|
|Kraken/Coinbase|UNVERIFIED_HERE|Existing separate provider gate infrastructure|No external request,connectivity or licensing claim|

No fallback fabricates observations. Fixed-source response SHA256 proves bytes
received by the acquisition path,not independent exchange correctness or legal rights.
Historical HTTP responses never become LIVE merely because they were just downloaded.
