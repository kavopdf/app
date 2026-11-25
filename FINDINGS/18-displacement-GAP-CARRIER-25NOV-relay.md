# `18_displacement` — the gap-carrier rule, measured live in Google on four documents, and what it does not fix

**25 Nov 2026 · relay slot 23:24 IST · repo `kavopdf/app` @ `afad8076` · engine `981ff1fa35e2cf67`
(the committed tree) and `c1b9eb8604fea319` (the patched tree) · Google Docs, not LibreOffice.**

> **Provenance.** The eight Google renders in this file were produced by a delegated sub-agent of this
> run (Drive upload → copy as Google Doc → export PDF → `verify_google.py`), and their raw result
> JSON is archived beside this finding as `res/*.json` in the run's own output. Every number below was
> **re-read by this run from those JSON files**, not copied from the sub-agent's prose — so the table
> is MEASURED, while the mechanism sentences are the sub-agent's reading of it. The sub-agent's
> `DocxWriter.java` javadoc cites `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`;
> **no such file exists in this repo** (4 files in `FINDINGS/` at `afad8076`). Treat that citation as
> unsupported until a run produces it; the probe numbers it quotes are not in this file.

## The rule that was tested

*A vertical length the page drew is never written on a property Google reads as a line box — not
`w:before` at a page top, not `w:line` on an empty paragraph — but as a 1×1 table row with
`w:trHeight w:hRule="exact"`, zero borders and zero cell margins.*

Two sites, gated by `-Dp2w.gapcarrier`:
`=1` the row replaces `w:before` on every page a break opened; `=2` page 1 as well, preceded by a
one-twip hairline paragraph so a table is never `<w:body>`'s first element.

## The measurement — Google, before and after, same documents

| document | base | gap-carrier v1 | gap-carrier v2 | `18` med / worst, base → v2 |
|:--|--:|--:|--:|:--|
| `68_journal_wide_table_spanning` | 41/42 | 40/42 ⚠ `59` | 41/42 | −114.3 / 115.0 → **−2.7 / 3.5** |
| `bank-statement-5-pages` | 42/47 | 46/47 | 46/47 | −55.2 / 355.5 → **+9.1 / 36.0** |
| `mobile-bill` | 46/47 | 46/47 | 46/47 | −6.7 / 10.0 → **+7.7 / 33.8** |
| `insurance-policy-schedule` | 46/47 | 46/47 | 46/47 | −7.7 / 47.8 → **+7.2 / 29.4** |

Read the sign, not only the size. `med_dy = render − source`, so a negative median is content sitting
**too high** and a positive one is **too low**. Every document in the table starts negative, which is
the page-top `w:before` being dropped; every document except `68` ends positive, which is the row
delivering **more** than the page drew.

## What it establishes

1. **The page-top drop is real and the row carries the gap.** `bank-statement-5-pages` recovers four
   checks (`25_invisible_text`, `27_text_off_page`, `44_header_footer`, `59_shape_anchor`) and its
   `worst_dy` falls 355.5 → 36.0. A construct that recovers four checks on one document is a real
   defect and a real fix.
2. **The refused spacer is real too.** `68_journal`'s 144 pt spacer is charged to `w:before` instead
   of `w:line` exact and its median falls 114.3 → 2.7 pt.
3. **No document becomes CLEAN.** All four still fail `18_displacement`. The dominant magnitude is
   gone and a 2–9 pt residual with a ramp is left. Under the charter's own question — *if this works,
   which documents become CLEAN?* — the answer for this patch alone is **none**.
4. **`hRule="atLeast" → "exact"` on the content rows is refuted, a third time.** Byte-patching every
   row moved `68` by 0.0 pt, `mobile-bill` by 0.0 pt and `bank5` by 0.0 pt. It agrees with
   `18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`, which falsified the declared row box on the
   0.75 pt grid, and it closes the remaining variant of that family.
5. **The residual is an over-delivery, not an under-delivery.** Three of four documents land at
   **+7.2, +7.7, +9.1 pt** after the patch. The spread of 1.9 pt over three documents of different
   shapes and lengths says a near-constant is being added per carried gap — not a ramp, and not the
   pixel grid. The candidate constants in the `.docx` are ruled out by inspection: `topGapRow()` writes
   `w:tblCellMar` top/bottom/left/right = 0 and `w:tblBorders` = none, and the cell paragraph is
   `w:sz="2"` with `w:line="1" w:lineRule="exact"`, so the surplus is in **Google's own minimum line
   box for a cell paragraph**, not in a margin the engine forgot.

## What would prove this wrong

* A Google render of a document whose only change is one `topGapRow` of a **known** height, with the
  laid y of the first body line read before and after: if the surplus is not ~7–9 pt there, item 5 is
  wrong and the surplus is per-document.
* Zero the surplus by lowering `gapTw` by the observed constant and re-measuring: if `med_dy` goes to
  0 **and** the LibreOffice render moves 8 pt up, the surplus is Google's minimum line box (a finding).
  If the LibreOffice render does **not** move, the row is not the carrier at all.
* A document in the corpus whose page top carries no gap and which still shows a positive `med_dy`
  under the patch: that would mean the row adds the surplus even where it carries nothing.

## Why nothing was committed

`regress.py --check` **PASSES** on the committed tree at `981ff1fa35e2cf67` (both formats, google-safe
included, no document worse than baseline), so the gate is not what refuses this patch. What refuses it
is the charter: `mobile-bill`'s `worst_dy` goes 10.0 → 33.8 under the patch, a Google regression on a
document that already passes 46 of 47 checks, and no document becomes clean to buy it with. The patch
stays in this run's output as a design, not in `main`.

## The next run should

1. Read the surplus in item 5 first — it is one document and one row, and it is now the whole of the
   remaining magnitude on three documents.
2. Only then re-open the pixel-grid question (census rank 2, per-cell-line snap): the row box is
   falsified twice and the line box is still untested.
