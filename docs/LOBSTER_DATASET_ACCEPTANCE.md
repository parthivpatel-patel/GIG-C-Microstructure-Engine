# LOBSTER AAPL sample acceptance

Status: **integrity/schema inspection PASS; empirical processing CONDITIONAL/BLOCKED
pending usage terms**. Source: owner-uploaded attachment, not a newly downloaded
provider artifact. No publisher signature/official checksum match established.

Archive LOBSTER_SampleFile_AAPL_2012-06-21_5.zip,4791006bytes,
SHA25646419dd0d6106be5fcf43600ccd08b2baa5d4cfb76284f1c58773537a3adac50.
Three ordinary unencrypted files: message CSV12495010bytes, reference CSV35129588bytes,
README4790bytes. All ZIP structural/path/type/ratio/count/size checks and per-member
CRC/hash reads pass. No absolute/parent/backslash/drive paths, duplicate names,
symlinks or overlapping ZIP members accepted. Bounded64KiB streaming extraction,
32MiB archive/64MiB member/128MiB aggregate/32 members/200x ratio/30s ceilings.
Actual inspection0.234s. Private0700 directory outside Git,0600 files; no CSV rows
printed, transmitted or committed. Hashes/CRC metadata are in the JSON evidence.

Included README read completely; version01 Sept2013. Six columns: seconds after
midnight (decimal up to9 digits), event code, assigned order reference, shares,
USD price x10000, side1 buy/-1 sell. Documented codes1 new,2 partial cancel,3 full
delete,4 visible execution,5 hidden execution,7 halt/quoting/resume indicators.
Execution direction is resting-order side, not aggressor side. Code6 is not defined
here: no auction/cross behavior is invented. Hidden/admin are not ordinary visible
mutations. Halt7 has ID/size0,side-1 and price-1/0/1; reference duplicates prior state.

Reference is Nx20, interleaved ask price/size,bid price/size at five occupied levels.
Asks ascend,bids descend; empty ask sentinel9999999999/bid-9999999999 with size0.
Levels need not be adjacent ticks. README implies corresponding event/book rows;
actual post-event alignment and counts remain unmeasured until permitted processing.
Timezone and complete initial resting history are not established. Filename denotes
AAPL/date2012-06-21 and theoretical34200000..57600000ms after midnight, not proof of
a complete session-start state. Five-level aggregates contain no queue/order-ID seed.

No license/use grant appears in README. User explicitly requires inspection-only /
synthetic fallback if permitted scope is unclear. Clarification requested while
independent development continues; no CSV event counts, price/quantity distributions,
reference anomalies or empirical agreement are fabricated. These fields stay null.
See LOBSTER_DATA_USAGE_RESTRICTIONS.md. No repeated blocked LOBSTER requests.

Feasibility: parsing, row alignment, aggregate/best/depth/transition checks can be
attempted after rights confirmation; full identity/FIFO/full-initialization claims
cannot be established from five-level reference alone. Constrained components need
explicit eligible denominators and unknown-order/depth-boundary exclusions.

ARM run5: official public run40151444307 independently confirms exact3461a5e,
Success, six completed jobs and8m22s; owner confirms6/6. Raw logs require sign-in.
This qualifies only3461a5e, not subsequent adapter changes. No workflow launched.
