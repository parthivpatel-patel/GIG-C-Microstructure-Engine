# Historical and authored replay integration

The catalog distinguishes an interactive native-authored event scenario,an interactive
provider-shaped aggregate L2 fixture,two authored native diagnostics and blocked
observed datasets. Only declared authored sources may be selected by API/UI.

Interactive controls:play/pause,step,restart,speed1/2/4/8,bounded timeline seek.
Native L3 seek reconstructs from the authored empty boundary; aggregate seek starts
with no accepted snapshot and applies the authored source prefix. No aggregate
state is imported as invented L3 identities. Source hashes and separate replay clock
remain visible. Authored L3 fixture v2 makes exchange EventTimestamp unavailable;
its logical display/replay clock is separate. Native EventTimestamp currently
rejects simulation-clock domain,so the adapter does not mislabel that clock as UTC.
This intentionally versions the new terminal fixture;all8 frozen engine hashes stay.

ITCH diagnostic executes existing bounded gzip/BinaryFile/typed decode/context/L3
restart demo. LOBSTER diagnostic generates existing independently authored toy CSV
in a temporary directory and executes the native unknown-state comparator. Both
are actual C++ runs. They are not imported interactive source replay and do not
process private observations. Full interactive ITCH/LOBSTER import remains future
work; no arbitrary upload/path endpoint is provided.

Recording archives only the fixed authored event source after explicit enablement.
It checksums bounded JSONL+manifest in private staged files,atomic rename/no overwrite,
max512records/2MiB,8datasets,24h replay validity. Verify reconstructs native state;
load resets the verified authored source;delete validates identity before removal.
No continuous observed recorder,compressed archive acquisition or external storage.
Authorized observed replay requires provider rights,integrity/profile evidence and
valid initialization;these are not inferred from catalog or filenames.
