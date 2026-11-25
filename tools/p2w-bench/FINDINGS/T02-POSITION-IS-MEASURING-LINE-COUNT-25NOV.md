# CORRECTED: t02_position is measuring position, and I misread its output

This file claimed that t02_position fails four documents because of line count - three splitting lines and
one losing two thirds of them. That was wrong, and the way it was wrong is worth recording.

## What the output actually says

    print("    %-26s source=%-10s txt=%s" % (cid, s, t))

and the tuple it unpacks is

    c["t02_position"] = (len(pairs), share, share >= 90, True)

So "source=52 txt=79" means 52 (x, column) pairs and a 79 % share of them inside tolerance. It does not mean
52 source lines and 79 .txt lines. 79 is a percentage.

The documents were then "confirmed" by counting blank lines in the .txt: 79-27=52, 58-26=32, 96-42=54, each
equal to a PDF line count I had taken from PyMuPDF. The arithmetic lined up, so the theory looked proven. It
was a coincidence between a percentage and a line count that happened to be near it.

## What is actually true

t02 fits a character width from the (x, column) pairs and asks what share of lines sit within
max(POS_TOLERANCE, POS_DRIFT * col) of the column their x implies. Four documents fall below the 90 % bar.
That is the check working as designed on a proportional-font document where the two estimates of a
non-existent character width disagree on more than a tenth of the lines.

Whether that bar is right for those four is a real question. Whether the check is measuring line count is
not: it is not.

## Why this correction is kept

Third time today. `gverify live` was read as an engine hash when it was a check-set hash; `p2w.py --force`
was read as stale when its comparison was correct; and now a percentage was read as a count. Each time the
symptom matched a disease already in the repo and the code that printed it was not read first.

The real defects this session were found the other way round - read the code, then measure.

## Status

No change made. The .txt writer was never touched, which is the one good consequence: the wrong theory would
have had me editing line building in the engine on the strength of an arithmetic coincidence.
