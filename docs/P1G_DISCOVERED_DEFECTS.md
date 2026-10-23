# P1G reproduced native first-insertion atomicity defect

Baseline book source: `1855a2f7a4d4ef472b61ffa5fd3b6b1a76acf282`.
This report supplements the preserved institutional audit and remediation reports;
it does not rewrite their historical findings or claim their tests covered this case.

## Reproduction and root cause

The new real allocation-failure sweep applied an initial native A after the source
S/R/R prefix. On the sixth reached allocation request (zero-based site5), native
replay returned `resource_exhausted` / `book.mutation`; its journal/cursor and source
context stayed uncommitted, but the native book canonical state had changed.

`OrderBook::State::insert_staged` staged a level, FIFO node and extracted index node,
then checked only `after_count > index.bucket_count()` before reserving buckets.
An empty libstdc++ unordered map reports a sentinel bucket even though its first
insertion can still allocate real buckets. The condition missed that first insertion.
The final `index.insert(node)` could therefore throw after level/list transfer.
This violated the intended strong semantic exception guarantee and could leave a
level without a matching ID index.

The regression was independently relinked with the exact original book source in
`/tmp`, without modifying/resetting the repository. Running its allocation group
returned exit1:

```
direct first-add failure leaves no transferred FIFO/level/index/ledger state
```

Exact local command/source/exit evidence is retained in
`build/p1g/evidence/development/original-book-regression.json`. The earlier adapter
failure is also retained under the development evidence directory. A failed
preliminary budgets test used invalid test BookLimits (orders1,levels128); the
fixture was corrected to1/1/1. No native capacity rule or assertion was weakened.

## Small repair and regression

Before transferring nodes, reserve insertion capacity when the target index is
empty as well as when its current capacity is insufficient. Use `reserve(desired)`
to establish the element-capacity contract. Remaining transfer/erase operations
keep their existing staged architecture. This changes failure safety and potentially
bucket allocation/capacity behavior, not accepted order/FIFO/ledger semantics.
No journal representation, matching, TCA or execution behavior was redesigned.

The new direct native regression checks every first-add allocation failure leaves
zero orders/remaining/revision/ledger, intact invariants, and supports exactly one
subsequent retry. Coordinated adapter tests additionally compare context summary,
book canonical state, replay cursor, receipt count and derived sequence counts for
every reached A/U allocation site. Destruction must release all tracked bytes.

Focused GCC results after repair:

- Direct native first add:5 reached fault sites.
- Adapter creation:6 sites; native first add through adapter:6; replacement:5.
- Armed native E/X/external commits:3 accepted operations, zero allocation requests.
- Separate isolated restart:32 reached allocation failpoints.

Final compiler/sanitizer and package evidence must be read from
`P1G_VALIDATION_REPORT.md`, not inferred from these focused tests. Bucket capacity
is a noncanonical resource diagnostic; semantic state, journal and accepted cursors
are the atomic boundary. PMR resources must obey their lifetime/allocation contract.
