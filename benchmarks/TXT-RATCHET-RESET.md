# The .txt ratchet was reset, and why

## What forced it

`t09_page_furniture` was fixed (`benchmarks/T09-FURNITURE-FIX.md`). Its
`present += min(count, owed)` cap made `present <= owed` always, so
`present == owed` held whenever there were AT LEAST enough copies, and the check
could only see MISSING furniture. Removing the cap makes it two-sided, which is
what its stated meaning already claimed.

Two documents now fail that previously read as perfect:

    324_loan_amortisation_schedule    owed 66   present 1485
    gst-invoice-multipage-item-table  owed 39   present 43

The stored marks for both said `best 4/5, failed [t04_structure]` -- t09 was
passing for them because of the cap.

## What was done, and what was refused

`ratchet.py --txt --reset --reason "<the above>"` was run. It archived 211 marks
to `RATCHET-TXT-20261115-160404.json` and cleared the store.

The alternative was hand-editing those two rows to add `t09` to `failed` and drop
`best` to 3. **That was refused.** A ratchet edited by hand to accommodate a fix
is a ratchet that can no longer prove anything: the next person cannot tell a
genuine regression from a hand-wave. The reset path exists precisely for this --
it archives the old marks rather than discarding them, so the record of what the
one-sided check used to score is still there to read.

The tool enforces this itself: `--reset` with no `--reason` is refused with
"A reset without a reason erases the record of what the old marks meant."

## Why the marks could not simply be kept

The archive shows `out_of 5` for these documents, not 12. The stored universe is
a partial one from an older run. `ratchet.py` refuses to write a store whose
numbers are counted out of two different universes, because every write would
fold one instrument's number into the other's. Re-measuring is not optional
here; it is the only way to get a store whose denominator is the current one.

## Current state

    RATCHET-TXT.json                     0 marks  -- cleared
    RATCHET-TXT-20261115-160404.json   211 marks  -- archived, readable

Per the reset itself: "every document sets a fresh mark on its next measurement."
The next .txt measurement run rebuilds the store against the corrected check, and
from then on the ratchet compares like with like.

## What this means for the APK gate

The APK cron runs `ratchet.py --txt --check`. With an empty store it will report
no regressions -- correctly, because there is nothing to regress against yet.
It must not be read as "the .txt is clean"; it means "the .txt has not been
re-measured since the yardstick changed". A .txt measurement run is required
before that gate means anything again.
