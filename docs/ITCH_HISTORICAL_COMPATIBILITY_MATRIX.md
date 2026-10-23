# Historical ITCH compatibility matrix — offline H/Y extension

Reviewed October23,2026 against the retained official S1/2023 document and source.
This is a software-contract matrix,not full2019 or observed-market certification.
See [HY_HISTORICAL_COMPATIBILITY.md](HY_HISTORICAL_COMPATIBILITY.md) for exact
specification hash/pages,assumptions,API selection and actual validation evidence.
First observed-prefix inventory remains historical;no new market bytes were read.

Default `DecodeProfile::baseline_v1` retains its12 typed families. Explicit
`status_observations_v2` adds H/Y for14 typed families. Both profiles know the same
23 payload lengths. Unsupported/unknown inputs remain explicit stop outcomes.

| Type | Bytes | v1 /v2 wire support | Context /native behavior and limits |
|---|---:|---|---|
| S |12 |Typed /Typed |System observation,global locate0,configured lifecycle;never an inferred book reset or empty boundary |
| R |39 |Typed /Typed |Directory admission,exact daily locate/symbol mapping;not complete initial state |
| H |25 |Unsupported /Typed |Known-directory status observation;HPQT,exact reserved/reason;external receipt,no native mutation |
| Y |20 |Unsupported /Typed |Known-directory restriction observation;ASCII012;external receipt,no native short-sale enforcement |
| L |26 |Unsupported /Unsupported |Market participant position;known length does not imply typed or semantic support |
| V |35 |Unsupported /Unsupported |MWCB decline levels;explicit stop |
| W |12 |Unsupported /Unsupported |MWCB status;explicit stop |
| K |28 |Unsupported /Unsupported |IPO quotation update;historical price interpretation unresolved;explicit stop |
| J |35 |Unsupported /Unsupported |LULD auction collar;explicit stop |
| h |21 |Unsupported /Unsupported |Operational halt,distinct from H;explicit stop |
| A |36 |Typed /Typed |Known symbol,new order identity,positive admissible quantity/exact units;source-specified add |
| F |40 |Typed /Typed |Attributed add,exact MPID retention |
| E |31 |Typed /Typed |Known eligible order,checked decrement/match identity;no invented aggressor |
| C |36 |Typed /Typed |Execution price/printability distinct from resting price;native use requires explicit existing book-only policy |
| X |23 |Typed /Typed |Checked partial cancellation;equal cancellation policy remains explicit |
| D |19 |Typed /Typed |Known-order deletion/identity retirement |
| U |35 |Typed /Typed |Checked replace-chain identity,new priority;no historical-reference reuse |
| P |44 |Typed /Typed |Non-displayed print observation;not a resting order or inferred aggressor |
| Q |40 |Typed /Typed |Cross observation;full auction integration unsupported,no arbitrary liquidity creation/depletion |
| B |19 |Typed /Typed |Known match correction observation;cross-break semantics unsupported,no automatic liquidity restoration |
| I |50 |Unsupported /Unsupported |NOII;explicit stop |
| N |20 |Unsupported /Unsupported |Retail price improvement indicator;explicit stop |
| O |48 |Unsupported /Unsupported |Later direct-listing capital-raise extension in retained2023 spec;not evidence of2019 occurrence |
| Other type octet |Unknown |Unknown /Unknown |`unknown_type`,not a silent omit or guessed record length |

No actual H/Y enum,reserved or reason payload values survived the earlier
memory-only4KiB inspection. That run established only H2/Y2 lengths plus S/R
acceptance. New v2 compatibility is independently synthetic-validated,not a claim
that the earlier four H/Y payloads now pass. Full-market preludes may still exceed
source-context directory/receipt/journal budgets or encounter unsupported families.

Context-profile selection does not change wire time into a date/UTC clock,
tracking numbers into exchange sequences,or missing history into initial orders.
The synthetic L3 factory remains synthetic-only with explicit authored-empty
evidence. H/Y observations neither establish initialization nor bypass gzip CRC,
terminal,source identity or publication gates. No observed-market adapter is added.
