# The t02 ruler pairs runs with lines by text, and a table repeats its text

## The measurement

332_bom_on_drawing, current engine, 52 runs and 52 .txt lines, fitted mid = 3.907 pt per character. Eleven
of the 52 pairs fail, and the failures are not small:

    x= 77.9  col= 81   expected= 20   err= 61
    x=167.9  col= 81   expected= 43   err= 38
    x=314.9  col= 81   expected= 81   err=  0
    x=638.9  col=164   expected=164   err=  0
    x=117.9  col=164   expected= 30   err=134

The same column 81 is returned for x = 77.9, 167.9 and 314.9. One .txt line cannot be in three places, so the
pairs are not describing the document.

## The cause

_ruler() builds `by_text[ln.strip()].append(_column(ln))` and then pops the first match for each run. A bill of
materials numbers its rows 1, 2, 3; a price list repeats a dash or a currency symbol. Measured on this
document: '1' appears twice, '2' three times, '8' twice, '3' twice, '4' twice. Each duplicate makes the
pairing arbitrary, and the fitted ruler is then fitted to the pairing rather than to the page.

## The fix, measured but not landed

Excluding any text that appears more than once from the fit - it simply does not enter, rather than being
paired wrongly:

    332_bom_on_drawing                   FAIL -> PASS   (8/12, 8 passed)
    price-list-2col-dense-right-aligned  FAIL -> PASS   (10/12, 10 passed)
    334_patent_document                  still FAIL     (32 pairs, 69 %)
    74_balance_sheet_indented_subitems   still FAIL     (50 pairs, 80 %)

Two of the four clear, and the other two stay failing because their ruler still disagrees with the width the
.txt was written with - a separate fault in the writer, not in the pairing.

## Why it was not committed

restamp_txt.py --report answers "213 unchanged", which is a cached-score comparison: it does not re-run
verify_txt, so it cannot show whether this change flips a passing document to failing. Removing text from the
fit changes the fitted mid on every document with repeated text, and some of those are currently PASS.

The user's rule is that no commit lands without a full-corpus regression. The change was reverted rather
than committed on a check that did not actually re-verify.

## To land it

Run verify_txt against all 213 documents twice - once at HEAD, once with the patch - and diff the verdicts.
Land only if nothing goes PASS -> FAIL. The four documents above are the expected gain; the risk is a
document whose ruler was held up by the mispaired duplicates.
