# Market initialization contract

`scripts/check_initialization_manifest.py` validates a bounded machine-readable
initialization manifest (example:tests/fixtures/market_seed_manifest.json). This is
an input/policy contract, not a publisher signature, observed factory or proof that
an arbitrary snapshot is complete. Existing BinarySourceAdapter observed mode
remains context-only. Its complete/seeded observed declarations never create a book.

| Mode | Necessary evidence | Implemented assessment |
|---|---|---|
|complete|Authorized source, gap-free complete initial boundary; explicit order/history/match scope|Synthetic fixture requires separately supplied trusted source digest, authored verification, complete/no gaps; observed evidence verifier pending|
|seeded|Complete order-level state with explicit priority, retired IDs/matches and exact continuation boundary|Synthetic fixture additionally requires separately supplied snapshot digest; observed evidence verifier pending|
|unknown|Missing resting history/unknown completeness|Context-only, no complete L3 claim|
|invalid|Known gaps/corruption/invalid declaration|Invalid or refused; never publish complete L3|

A trusted digest parameter binds independently supplied fixture expectations, not
legal/publisher authentication. Self-declared `complete:true` or `validation_status`
never suffices. Missing exchange sequence stays missing; BinaryFile ordinal is an
explicit capture-order namespace. Unknown mode/invalid schema/duplicate JSON keys,
contradictory digest, invalid fields or capacities cause refusal without mutation.

Snapshot contract: <=2 symbols, <=64 active orders/book,128 total; unique nonzero
order references, known locate, explicit B/S, positive uint32 remaining/Price4,
positive distinct priority per symbol and distinct historical arrival ordinal less
than continuation ordinal. Physical vector ordering is not priority. Retired IDs
and matches must be explicit, bounded and noncontradictory; absence is a claim of
complete empty reference history, not permission to infer history. Price levels
are derived from orders; aggregate depth is not accepted as a full L3 seed.

The contract records session lifecycle stage and optional last wire timestamp for
continuation policy; neither creates observed evidence. Timestamp is an exact48-bit
wire value; event boundary has exact frame/payload adjacency and uint64 ordinal.
Native tick/lot/range consistency and contextual invariants remain required by the
seed factory, not proved merely by this JSON validator. No inferred FIFO priority,
missing order, exchange sequence or clock. No hot recovery promise.

Python validator reads at most1MiB, refuses duplicate keys, returns explicit status,
canonicalizes snapshot vector order by identity while retaining priority values,
and has no network or state mutation. C++ native state is not populated by this
phase's Python validation. Subsequent seeded construction must separately validate
its typed seed and construct joint native/context state before exposing a result.
