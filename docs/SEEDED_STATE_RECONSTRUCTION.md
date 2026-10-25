# Seeded-state L3 reconstruction

Additive API: `SyntheticReconstructor::create_seeded(config,SeedState,trusted_digest,PMR)`
in reconstruction.hpp/seed.hpp. Existing create remains authored-empty-only and
still rejects complete_seed. New factory is **synthetic-only**: observed origin is
rejected by the established provenance factory. It is not an observed snapshot
verifier, arbitrary native restore API or a new entitlement/publication path.

SeedState borrows directories (exact39-byte R layout), active OrderState + explicit
native priority, retired source references, match history, lifecycle stage, optional
last wire timestamp and exact first-continuation Location. No span is retained.
Directory decoding/bindings, nonzero identities, B/S, positive remaining/Price4,
unique IDs/arrival ranks/priority, arrival-before-boundary, per-symbol FIFO rank
consistency, exact integer tick/lot conversion, context capacities, native limits
and snapshot validity are checked. Retired references have their own typed vector:
no fake order side/stock/price/history is invented. They count against lifetime
capacity and reject future reuse/references. Matches preserve kind/locate/broken
state; no broken trade automatically restores displayed liquidity.

Hard seed limits:2 directories,128 active orders (64/book),4096 retired IDs and4096
matches, additionally constrained by actual configured context/native budgets.
Canonical SHA256 uses versioned `gig.typed_seed.v1` binary preimage, length-prefixed
text and unsigned64 big-endian numbers; identity-sorted directory/order/retired/
match collections, every supplied state/priority/boundary included. Independent
Python encoder in check_seeded_reference.py implements the same declared format.
This digest is distinct from the manifest's JSON snapshot digest and source-artifact
digest. Integrity is not proof of publisher authority or omitted-history completeness.

Factory constructs isolated temporary context/books using the established factory,
then validates/populates seed context and uses existing ReplayEngine::recover with
complete order-level snapshots. Failure destroys all temporary state; destination
is never exposed. PMR failures are swept through full success and must leave zero
live allocations. After success, existing prepared-context/native transaction path
handles every source event; no second book mutation algorithm or matcher is added.
Unknown/duplicate/over-quantity/unsupported/unit/cap failures preserve accepted state.

Explicit native accounting: one derived recovery record at sequence0 per book;
source-native events start at sequence1, while native_counts/native_committed count
only subsequent source events. Seed journal count is exposed separately. Snapshot
metadata uses an authored boundary-predecessor capture token, **not an observed
wire record**; event/receive times stay unavailable. Native provenance retains raw
continuation dataset and adds exact seed SHA256 parent plus seed-import lineage.
Stored ReconstructionConfig binds seed digest; no source origin is changed.

Active priority ranks are preserved. Future native priority allocation starts at
max active rank+1, as defined by existing native recovery. This is a declared native
ranking convention, not the historical exchange's absolute counter (not supplied
by ITCH). If an application needs retired-order absolute priority high-water values,
this factory does not supply that behavior. Native ledger records initial liquidity
as recovered, not fabricated past adds/trades; historical execution analytics cannot
be reconstructed from this seed alone. Aggregated depth or unordered partial L3
cannot establish supplied FIFO ranks or completeness.

Restart: restart_seeded_prefix takes trusted typed seed and independently retained
seed/prefix hashes, re-creates both states and replays exact complete BinaryFile
frames from declared continuation boundary.128MiB prefix/100000 records upper caps;
context/native limits may stop sooner. Corrupt hash, partial frame or refused event
returns no reconstruction. Result is active accepted prefix, not full-session or hot
recovery. No serialized journal parser, fsync/crash durability or gzip seeking added.
Existing canonical replay format and old checkpoint API remain unchanged; old
checkpoint APIs explicitly do not accept seeded reconstruction. No silent migration.

Full observed seeding remains blocked on authenticated complete initial context,
order/FIFO/match/retired history, source profile and independent observed reference.
The caller's complete_history assertion is sufficient only inside the explicitly
authored fixture contract; it never proves historical exchange completeness.
