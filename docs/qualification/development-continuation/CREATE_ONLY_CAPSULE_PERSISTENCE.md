# Create-only completed-source capsule persistence

The explicit SDK methods `ItchRecovery.persist_completion_capsule_file` and
`restore_completion_capsule_file` add bounded POSIX file persistence around the
existing GIGSCAP1 native completion-capsule contract. Every native/source/capture/
generation/resource admission remains independently supplied. No trust metadata
is inferred from a filename or persisted as authority. Existing bytes, formats,
defaults and unsupported-streaming behavior remain unchanged.

Publication validates the complete native capsule before touching the filesystem.
It traverses an absolute path descriptor-relatively without following symlinks,
requires an owned non-group/world-writable final directory, creates private0600
staging with a bounded random-name collision budget, completes writes, fsyncs and
hash-checks the file, then atomically hard-links without replacing any destination.
Only its own staging entry is removed; directory fsync follows publication.
Primary and cleanup errors remain separate. An error after publication explicitly
reports that the complete artifact may remain and whether durability is uncertain.
Completed fsync syscalls do not establish physical hardware crash durability.

Restoration opens a bounded owned regular file without following symlinks or
blocking on special files, verifies stable descriptor/path metadata and exact SHA,
then invokes native restoration with the independent admission. A positive link
count of2 is permitted after a process exits between publication and staging unlink.
This does not establish inode immutability or protection against a concurrently
hostile same-user namespace. Unsupported platforms reject explicitly.

36 focused and69 guarded combined recovery tests pass. Fixtures cover interrupted
writes, fsync/close/unlink failures, umask, bounded short reads, malformed and
re-signed native capsules, no-overwrite preservation, symlinks/path replacement,
concurrent publishers and actual subprocess exits before/after atomic publication.
SDK source/build copies were hash-compared. No C++ source or binary format changed;
REL02 remains PARTIAL. Evidence: `work/engineering-next/capsule-persistence-*.log`
and `capsule-persistence-metadata.json`.
