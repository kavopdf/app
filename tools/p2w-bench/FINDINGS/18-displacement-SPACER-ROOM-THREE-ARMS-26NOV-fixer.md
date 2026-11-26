# 18_displacement — the table-gap spacer's room guard, three arms measured in Google

**Run:** fixer, 26 Nov 2026, slot 19:27 IST · **engine built from HEAD** `e85e20b9` ·
**instrument** `verify_google.py`, 42 renders scored against 7 source PDFs in one run.

## The one thing this run establishes

The room guard that decides how much of a table-gap spacer may be spent into `w:before` charges the
unspent remainder at one twip per twip. Google draws only **0.2156 of a twip carried by `w:line`**
(`2.5873 · max(L/240, 0.06)` pt for a declaration of `L/20` pt), so the guard refuses gap the page
can actually hold. Three ways of correcting it were built and each was measured in real Google Docs
on the same seven documents, in the same run, from the same corpus PDFs.

**All 42 renders are first-hand.** Every arm went through the same path: `ConvertAll` on the engine
built from that arm → `GOOGLEDRIVE_UPLOAD_FILE` → `COPY_FILE_ADVANCED(mimeType=google-apps.document)`
→ `EXPORT_GOOGLE_WORKSPACE_FILE(application/pdf)` → `verify_google.compare()`. No number below is
modelled, and none is copied from the store.

## The three arms

| arm | change to `roomTw` at `DocxWriter.java:6282` |
|---|---|
| **HEAD** | `max(0, slackTw - spacerSplitTw - rowExcessTw)` — one twip of before costs one twip of page |
| **HALF** | `room + (want - room) / 2` — spend half of the refused remainder |
| **FULL** | `want` — spend the whole gap into `w:before`, no guard |

## The measurement

`med_dy` / `worst_dy` are the 18_displacement instrument's own numbers, in points, negative = the
render sits higher than the source. `p/t` is checks passed of applicable.

| document | HEAD med/worst, p/t | HALF med/worst, p/t | FULL med/worst, p/t |
|---|---|---|---|
| `403_crossword_puzzle` | −10.2 / 12.2, 41/42 | −4.5 / 6.6, 41/42 | **−0.6 / 2.2, 42/42** |
| `68_journal_wide_table_spanning` | −92.4 / 93.1, 40/42 | −47.9 / 48.6, 40/42 | −3.1 / 3.9, 40/42 |
| `marksheet-subject-left-marks-right` | −1.4 / 10.0, 45/47 | 1.9 / 5.2, 45/47 | 6.0 / 13.0, 45/47 |
| `two-tables-stacked-with-no-gap` | 1.7 / 7.3, 46/47 | 2.9 / 8.4, 46/47 | 4.2 / 9.8, 46/47 |
| `electricity-bill` | −7.2 / 10.4, 46/47 | **−0.1 / 7.9**, 46/47 | 8.8 / 31.9, 46/47 |
| `insurance-policy-schedule` | −6.3 / 9.8, 46/47 | **−0.1 / 7.5**, 46/47 | 7.3 / 29.4, 46/47 |
| `mobile-bill` | −6.0 / 9.2, 46/47 | **0.8 / 8.9**, 46/47 | 7.8 / 33.9, 46/47 |

Page count 1→1 on every arm of every document. No check changed verdict on any arm except 403 under
FULL, which gained one.

## What the three arms say

1. **FULL is the only arm that finishes a document, and it is not safe.** `403_crossword_puzzle`
   goes 41/42 → **42/42 CLEAN** at `med_dy −0.6`, `worst 2.2`, one page. That is the first
   first-hand proof this class can be cleared by this construct. But the same arm drives `worst_dy`
   from 10.4 → **31.9**, 9.8 → **29.4** and 9.2 → **33.9** on the three bills. Those documents keep
   their verdict (46/47) and are much further from the original than they were. A rule that trades
   one clean document for three wrecked tails is refused by non-negotiable 3, not by taste.
2. **HALF is strictly better on six documents and marginally worse on one.** On the three bills it
   puts the median at −0.1, −0.1, +0.8 — dead on — and *reduces* `worst_dy` on all three
   (10.4→7.9, 9.8→7.5, 9.2→8.9). It halves the error on 403, 68_journal and marksheet. The single
   document it moves the wrong way is `two-tables-stacked-with-no-gap`, by 1.2 pt of median and
   1.1 pt of worst, on a check it fails on both arms. **It completes no document.**
3. **The residual after HALF is not a constant offset any more.** With the median at zero the check
   still fails on the three bills, and it fails on the tail clause
   (`n_out > max(2, 5% of runs)`) at `worst 7.5–8.9 pt` against a 4.2 pt tolerance. A spacer spend
   error produces a constant offset; what is left is per-run variation. **The class's next mechanism
   is the tail, not the median, and it is a different defect.**

## Why the engine was not committed

The charter's question is *if this works, which documents become CLEAN?*

- FULL: one document (403), at the cost of 30 pt tails on three others.
- HALF: none.

So neither is a fix. Both are recorded here as measurements, and the engine is unchanged at `e85e20b9`.

## Blast radius, measured independently of the engine's own report

HEAD vs patched `word/document.xml`, converted on the same pod:

| document | document.xml identical | spacing pairs differing |
|---|---|---|
| `72_bank_statement_no_rules_right_amounts` | yes | 0 |
| `bus-timetable-station-left-times-right` | yes | 0 |
| `table-with-no-header-row` | yes | 0 |
| the other six | no | **1** |

One spacer per affected document, and three of nine documents byte-identical. The change cannot
reach a document whose guard was not binding.

## What the next run should do

1. Take HALF as the starting point — it is the safest arm and it puts five documents' median within
   1 pt — and attack the **tail**: at `worst 7.5–8.9 pt` with the median at 0, some runs are still
   displaced while the page as a whole is right. That is a per-run question (which runs, what font
   size, what precedes them), not a spacer question.
2. `403_crossword_puzzle` is one arm away from CLEAN and FULL proves it. A rule that spends the
   whole gap **only where the page has real slack beyond the guard's own figure** would keep 403 and
   spare the bills — but that discriminator is not visible in the guard's inputs today, so it has to
   be measured, not assumed.
3. Do not spend another run proving `w:before` is 1:1 in Google. It is, and it was re-measured here
   (the two `w:before` anchors reproduce to 0.9 pt).

## The refutation this run inherits

An agent hypothesis earlier in this slot predicted 403 at `med_dy −2.2` and **42/42 CLEAN** from a
constant `2.5873/12` on the room test. Measured: **−0.9 pt, still 41/42** — the prediction was right
about the median and wrong about the verdict, because the check's tail clause is what fails, not its
median. A modelled "predicted CLEAN" is not a CLEAN, and this is the second time the same modelling
error has been caught by measuring it.
