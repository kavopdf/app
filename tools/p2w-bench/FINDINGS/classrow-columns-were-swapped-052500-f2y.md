# `classrow.py` wrote `share1` into the `share5` column and `share5` into `max_pt` — fixed in this run

The class file is the queue every fixer run reads to decide what to work on. For every row this tool
has ever written, its two number columns carried the wrong two numbers, and `max_pt` — the column the
class paragraph says is "reported but never ranks" — was never written at all.

## What it looked like

    | 2 | `mobile-bill` | content-present-partly-displaced | 43.87 | 1.55 | 1 | OPEN | share@5 1.55 |

Read as the header names them, that row says **44 % of the ink is more than 5 px from where the page
drew it, and no ink is more than 1.55 pt from it.** Both cannot be true of one page — if 44 % of the
ink had moved, something would have moved far. An agent sent to explain that contradiction spent its
budget establishing that the page is fine, and the table is not.

The numbers were right. Their labels were wrong: 43.87 is **share@1px**, 1.55 is **share@5px**, and
the real `max_pt` is 16.80, which nobody had ever seen.

## The cause

`load_rank()` returned `(share1, share5, problem)` and the row writer consumed it as if it returned
`(share5, max_pt, ...)`:

    newrow = "| %s | `%s` | %s | %.2f | %.2f | %s | %s | %s |" % (
        c[0], doc, c[2], s1, s5, c[5], new_status, new_note)
    #                     ^^ share5 column   ^^ max_pt column

Two independent repairs, both in `classrow.py`:

1. `load_rank()` now also reads `max_pt` and the writer emits `(s5, mpt)` into the columns the header
   names.
2. **The clean-row branch threw the corrected row away.** `c[2] = prob` corrected the problem name
   from `RANKING.csv` (the comment above it says so), and then the branch did `out.append(line)` —
   the row exactly as found — so the correction never reached the file, and every FIXED-and-clean row
   kept whatever numbers it was born with. Both branches now write the row. The class the row was
   **measured** with is preserved on those rows (`measured_problem`), because the paragraph under the
   summary is right that the file is a record of what was wrong there, not only a work queue.

## Measured, before and after

    rows checked against benchmarks/RANKING.csv     212
    rows whose share5/max_pt disagreed with it      212  ->  0
    rows whose STATUS changed                         —  ->  0   (checked row by row)
    rows whose DOCUMENT changed                       —  ->  0   (checked row by row)
    class summary counts          12/1 6/16 6/4 6/0 23/0 7/1 130  ->  identical

Nothing computes a status from those two cells — `new_status` is computed from `s5` in the dict, never
from the row — so no FIXED/OPEN claim was ever affected by the swap. That is why this went unnoticed:
the wrong numbers were in the column nobody's logic read, on the file everybody's eyes read.

## What it means for the next run

The queue is unchanged (same classes, same counts, same statuses) and its numbers now mean what they
say. **`content-present-partly-displaced` is still the largest class at 23 open, and its documents are
at share@5 of 1.0–4.0 with `max_pt` of 13–17** — not the sub-2 pt figures the table showed. A document
with share@5 of 1.55 and `max_pt` 16.80 is a page with most of its ink in place and a few things
thrown 14–17 pt away, which is a different defect from the one the old numbers described.
