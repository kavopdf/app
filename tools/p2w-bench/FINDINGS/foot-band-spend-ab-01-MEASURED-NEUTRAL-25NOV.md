# The foot-band gap spend: fires on 2 of 12, removes 128 boxed chars, neutral on the pixel instrument

**Fixer slot 25 Nov 07:02. Engine HEAD 49fd3b98. Patch: `04_chars_missing-GAPCAP-PATCH-0225-agent.patch`
(written 02:25, never measured on a corpus, never applied).**

## What I believed

The 24 Nov census says the anchored-box mechanism is ~8 documents, not 166, and that the 120 pt cap is
16 % of the boxed characters while the `ZERO_GAP_ANCHOR` latch is 70 %. The written-not-kept patch
(`SPEND_FOOT_GAP`, `FOOT_BAND = 0.90`) spends a wide gap in the foot band as `w:before` instead of
anchoring the line, and its author recorded one Google render at 40/42 -> 42/42 on
`27_two_column_left_short_txtpos`. If that generalises, the boxes on the pages the guard fires on leave
the text layer in Google, which is the mechanism behind `04_chars_missing`, `45_char_accuracy` and
`13_text_colours`.

## What I measured

Applied the patch, compiled, converted the same 12 documents twice - `-Dp2w.spendfoot=0` (HEAD rule) and
the default (patch) - and compared.

**1. The engine is deterministic at `word/document.xml`, not at the `.docx` byte.** Two runs of the SAME
engine differed in `.docx` bytes on 12/12 documents and were identical in `word/document.xml` on 12/12.
So the patch's own reviewer checklist item 1 ("`-Dp2w.spendfoot=0` must reproduce HEAD's
`word/document.xml` byte for byte") is satisfiable only at the XML level; an A/B on the file hash
reports 12/12 "changed" when nothing changed. Anyone repeating this must unzip first.

**2. The patch fires on 2 of 12.** Boxed characters (`<w:txbxContent>` text), `spendfoot=0` -> default:

| document | box chars | page count |
|---|---:|---|
| `27_two_column_left_short_txtpos` | 57 -> **0** | 1 -> 1 |
| `46_chart_coloured_labels_body_text` | 71 -> **0** | not measured |
| `20_numbered_list_separate_column_txtpos` | 232 -> 232 | - |
| `54_two_column_body_full_width_header_footer` | 92 -> 92 | - |
| `55_sidebar_box_beside_body` | 65 -> 65 | - |
| `61_two_col_abstract_spanning` | 84 -> 84 | - |
| `66_two_col_footnotes_bottom` | 448 -> 448 | - |
| `69_two_col_legal_numbered_clauses` | 1358 -> 1358 | - |
| `330_cad_drawing_sheet` | 75 -> 75 | - |
| `12_stamp_across_page_break`, `373_leave_application_form`, `mutual-fund-statement` | 0 -> 0 | - |

The other ten are identical at the XML level. **This is the finding that matters: the foot-band condition
is rare.** The census's 70 % is the `ZERO_GAP_ANCHOR` latch and this patch does not touch it, exactly as
its author said.

**3. On the pixel instrument the change is neutral.** `benchmarks/p2w.py` `measure_doc`, both arms, same
source PDF: `27_two_column_left_short_txtpos` **share5 1.62 -> 1.62**, pages 1 -> 1, signature
`displacement`, problem `content-present-partly-displaced`. No document was made worse on the one
document measured in both arms; the second changed document was not measured (slot).

## What is now true

* The patch is a **two-document construct**, not a corpus-wide one, and it is not a regression on the
  document it changes.
* The Google evidence for it stays what the repo already had: **one** render, 40/42 -> 42/42 on
  `27_two_column_left_short_txtpos` (`RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md`). I did
  not re-render it; Google was unreachable from this pod (`403`, `s3key belongs to another project`).
* It **cannot be committed from a 90-minute slot as things stand**: the commit gate needs a full-corpus
  `RANKING.csv` stamped for the new engine, and `p2w.py --budget 250` measures ~26-48 documents per
  250 s pass, so a cold stamp is ~8 passes / ~35 minutes of measurement on top of a ~13 minute corpus
  build. That is the whole slot for one two-document change.

## What would prove this wrong

* A Google render of both changed documents showing `04_chars_missing` still failing (the box was not the
  cause) or a page count that moved.
* A corpus-wide `document.xml` A/B showing the guard fires on documents outside this 12.

## The lead, stated as work

Run the full-corpus A/B of `-Dp2w.spendfoot=0` vs default at the `word/document.xml` level (cheap: 213
conversions, ~3 minutes at 4 workers), get the exact changed set, and then measure only that set with
`p2w.py` - not the corpus. If the set is two documents, the honest conclusion is that this patch is worth
at most one Google check on one document, and the box work belongs to `ZERO_GAP_ANCHOR` (20,024 of 23,794
boxed characters on 11+1 pages), not to the cap.
