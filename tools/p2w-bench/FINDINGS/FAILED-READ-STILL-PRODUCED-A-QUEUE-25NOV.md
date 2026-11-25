# A failed read refused to state a count, then stated a queue derived from it

The 09:59 report got the hard half right. Its Google row reads:

    "could not be read - 0 of 212 scored were read as current; a failed read, not a measurement, so no
     count is stated"

That is exactly the behaviour this directory has been asking for all week: when the instrument cannot
read, say so, rather than printing a zero that reads as "nothing is fixed". Two earlier runs printed 0
and were believed.

## The half that is not right

The row directly below it says:

    "Who re-measures them: the :20 gverify cron, up to 60 a run - about 4 runs for the 212 outstanding"

If the read failed, there is no 212. The same failed instrument that could not say how many were fixed
still produced a queue size and a run estimate from the same absence of data. A reader takes "212
outstanding, 4 runs" as a measurement, because it is formatted like one.

The store says otherwise: 213 of 213 verdicts carry engine 981ff1fa35e2cf67, 0 refused, and report.py
now prints "42 of the 213 re-measured on this engine". Nothing is outstanding.

## The rule

A failed read must suppress every number derived from it, not just the headline. "Could not be read"
plus "212 outstanding" in the same table is worse than either alone, because the first sentence teaches
the reader to trust the second.

## Verified, not changed

The read works now - google_fixed() returns (42, 213, 42, 213, 0) - so the derived line is correct on a
healthy pod and the defect only appears in the state it was written for. Recorded so the next report
that fails a read does not also invent a queue from it.
