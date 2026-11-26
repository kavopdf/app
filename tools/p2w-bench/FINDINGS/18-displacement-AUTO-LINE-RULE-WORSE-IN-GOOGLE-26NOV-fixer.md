# `-Dp2w.lineRule=auto` on 31_times: Google moves the wrong way (2.6 -> 3.3 pt, worst 3.5 -> 8.7)

**26 Nov 2026, fixer slot 10:54.** One document, one construct, measured in Google both ways.

## Why this was worth a measurement

`DocxWriter.java:110-140` carries a second, fully built line construct behind
`-Dp2w.lineRule=auto`: `w:line="240" w:lineRule="auto"` - the reader's own single line height - with
the remainder of the pitch in `w:before`. Its own comment says the `exact` hairline is charged
quadratically in the type size by Google, and that auto is linear in it, so auto looked like the
construct that removes the last few points of `18_displacement` on the documents that sit just outside
the tolerance. `31_times_body_arial_headings` fails by **0.09 pt** (worst run 3.59 pt against a 3.5 pt
tolerance at 10 pt), so a tenth of a point was enough.

## What I measured

Both builds are the same engine at HEAD `a4f8...`, the same source PDF, the same conversion path
(`ConvertOne`), and the only difference is `-Dp2w.lineRule=auto` on the JVM:

| | default (`exact`) | `lineRule=auto` |
|:--|--:|--:|
| Google checks | 41/42 | 41/42 |
| failing | `18_displacement` | `18_displacement` |
| med_dy | **2.6** | **3.3** |
| worst_dy | **3.5** | **8.7** |
| runs matched | 29 | 29 |
| export md5 | 8a002ed5… | 0e6ea0df… (different file, so the construct did reach the export) |

The construct reached Google - the two exports are different bytes - and Google placed the page
**0.7 pt further off at the median and 5.2 pt further off at the worst run.**

## What is now true

1. **Auto is not the construct that closes the marginal `18_displacement` documents.** It is worse on
   the one document chosen because it was closest to CLEAN, and by 5.2 pt on the run the check convicts.
2. The engine's default stays `exact`. Nothing was committed to the engine; the flag was passed on a
   single conversion.
3. This also explains why the flag has never been turned on: it was built, and the corpus it was built
   against already said the hairline is the better of the two.

## What I did not do, and what would prove this wrong

One document is one document. Auto could still be better on the large-type documents (the quadratic
term only bites above `size = 12/r`), and the corpus-wide comparison was not run. What would overturn
this: auto measured on the 8-10 pt body documents that carry 18_displacement *with* a large-type
heading, and found better.

## The ledger was restored

`benchmarks/gverify/31_times_body_arial_headings.json` was overwritten by the auto measurement and
re-collected from the default build's export afterwards; it reads 41/42, `18_displacement`,
med_dy 2.6, worst_dy 3.5, engine `a4d8fca469bba636` - identical to before the experiment except the
timestamp. The two Google Docs the experiment created in the verify folder were deleted; the two
staged copies under `/scratch/output` were removed.
