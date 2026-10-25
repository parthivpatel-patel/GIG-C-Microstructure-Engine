# LOBSTER reference validation

Implemented exact twenty-column parser and independent authored oracle. Columns
are ask price/size,bid price/size repeated5 times. Occupied levels need not be
adjacent ticks. Missing asks9999999999/bids-9999999999 require volume0 and tail
position. Prices/quantities retain integer precision; no tolerance-based matches.

Ordering, field count, range and sentinel contradictions reject. Locked/crossed
books and occupied zero-volume levels remain explicitly flagged, with later
comparison eligibility restricted where semantics are uncertain. Neither aggregate
levels nor their agreement provide observed identities/FIFO/full initialization.
Row alignment requires equal file EOF and per-pair timestamp order, not sorting or
silently truncating the longer file. This does not establish upstream completeness.

Actual attached-reference statistics (locked/crossed/missing/zero-volume frequencies,
row counts/time ordering/price-scale observations) are **not measured**. Owner
explicitly withholds cloud processing until rights are established; values remain
null in evidence, not0 or fabricated passes. No further attached/private-file access
after clarification. All currently executed reference validation is synthetic.
