# Phase5 architecture

October26,2026 America/New_York. Exact baseline2d4db35ef91f23eb79875282ba067cd1bd004fb8;
branch feat/atlas-phase5-integration. No main/prior-branch modifications.

Priority implementation:existing provider gates/fixed HTTPS fetch → bounded IEX pages →
exact provider normalization → neutral canonical historical dataset → immutable SQLite
revision → pinned inspection/descriptive risk. Acquisition does not replace the current
stock quote/bar cache. This separation avoids silently mixing mutable quotes with archived
research data. Snapshot read and its derived analysis share an explicitly checked revision.

Existing history-v2 schema and schema1 database retained. Multi-page core validation
checks aggregate observations,ordered source digests and page-count metadata without
inventing source page boundaries;old single-page canonical bytes remain compatible.
Source page hashes are preserved;row-to-page boundaries/timing and resumable cursor state
are not retained. Current-source cache and immutable stored revisions remain separate.

Other integrated milestones:seven added SEC metric families and exact selected-component
checks;explicit-weight portfolio covariance/risk;training-only likelihood scoring and
bounded expanding-window evaluation. No full accounting presentation model,live Alpaca
wire driver or native journal redesign is claimed.

New proof-protected POST paths:stocks/history-ingest,stocks/portfolio,stocks/evaluation.
Existing history-store path adds fixed backup/restore/delete-backup actions. No wildcard
proof targets,caller file paths,arbitrary destinations or credential-bearing responses.
All existing Origin/Host/CORS/proof limits remain. No production dependency added.
