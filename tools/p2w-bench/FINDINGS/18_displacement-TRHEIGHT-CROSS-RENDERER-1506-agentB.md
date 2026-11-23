# 18_displacement — is there a `w:trHeight` construct that gives Google the source pitch without moving LibreOffice?

**23 Nov 2026 · agent B · engine `kavopdf/app` at HEAD `3b98dce7`, built in-sandbox with
`tools/p2w-bench/build-engine.sh` · corpus fetched with `tools/p2w-bench/corpus-fetch.sh`
(213 PDFs, 0 missing) · every number below is measured in this run.**

**Scope, stated before anything else: there is no live Google round trip in this slot.** Every
Google number quoted is either the committed record in `benchmarks/gverify/*.json` or a prediction
derived from the recorded Google dose-response, and it is labelled as such in every row of the table.
LibreOffice is measured directly, two ways: the repo's own 47-check instrument
(`tools/p2w-bench/verify_google.py <source> <render> --docx <docx>`, the same file that scores the
Google export) run on the soffice render, and an independent reading of the row rules and text
baselines straight out of the soffice PDF with PyMuPDF (`/scratch/work/exp/measure.py`).

The instrument was checked against the record before it was used to judge anything: HEAD
`mobile-bill` measures **share@5 1.55** in `benchmarks/p2w.py measure_doc`, which is the number in
`benchmarks/RANKING.csv` for that document, and **47/47** on the 47-check instrument, which is the
number in `benchmarks/gverify-lo/mobile-bill.json`.

---

## The two models, as measured

| | LibreOffice 7.4.7.2 | Google Docs (recorded) |
|:--|:--|:--|
| row height | `max(w:trHeight, cell content + rule)` — the border box is charged only when the content is what fills the row | `w:trHeight + one rule`, flat, whatever the content is |
| evidence | `DocxWriter.java:6313-6341` (measured on 404_sudoku_grid: 880+880+sz16 → 46.0 pt rows on a 44.0 pt page) and re-measured here | `FINDINGS/18_displacement-ROW-RULE-IS-OUTSIDE-TRHEIGHT-1220-f1x.md`: rows written 360/380 tw laid **19.0 / 20.0 pt**, +1.00 pt on every row; `w:hRule="exact"` is inert (Google rewrites it to `atLeast`), `w:before` never enters the row |

Two models, one number. Writing the pitch `P` into `w:trHeight` makes Google `P + 1`; writing
`P − 1` (the obvious patch) makes every LibreOffice row whose content does not fill it `P − 1`.
That is the whole conflict, and the only algebra that satisfies both is a **pair**:

    w:trHeight                = P − c_g          (c_g = the rule Google charges, 20 tw measured)
    cell content + rule        = P                (so LibreOffice's max() lands on P as well)

The second line is what this run went looking for, because the cell's own text box cannot supply it:
the engine places a cell's baseline at `w:before + 0.8·w:line` (`LINE_BASE`, `DocxWriter.java:214`),
so a box that reaches the pitch puts the baseline at 0.8·P instead of the page's 0.5·P —
`184 = before + 0.8·box` with `before + box = 348` needs `before = −472 twips`. Negative, i.e.
infeasible with one paragraph. (That is the arithmetic the 10:45 relay already wrote down; it is
reproduced here because it is why the construct below is a *margin*, not a box.)

---

## Per-variant table — measured in LibreOffice, predicted for Google

Every variant is the **same `.docx` the engine emitted at HEAD**, rewritten only in
`word/document.xml` (`/scratch/work/exp/variants.py`), rendered with soffice and scored. Nothing else
in the document changes. `P` is the source pitch, 368 twips (18.40 pt) on both documents. Row pitch
is read off the drawn rules; "off" counts interior rows more than 0.2 pt from 18.40.

| # | variant | construct emitted | LO row pitch (pt) | LO share@5 | pages | what Google is predicted to do, and on what evidence | verdict |
|--:|:--|:--|:--|--:|--:|:--|:--|
| 0 | **HEAD** | `w:trHeight` 360/380 `atLeast`; cell `w:before` 190-210 + `w:line` 9-10 `exact`; separators as `w:tcBorders` sz 7 | mb: **18.0 / 19.0** sawtooth, 23/26 rows off; tnhr: **18.0 / 19.0**, 26/26 off | 1.55 / 0.61 | 1 / 1 | **19.0 / 20.0** — recorded, live, `gverify/mobile-bill.json` fails `18_displacement` alone | the defect |
| 1 | **shave** | `w:trHeight` = P − 20 only (354) | **17.9 uniform**, 26/26 off | 31.66 | 1 | 18.9 — the charge is gone, the pitch is 0.5 low | **REFUSED, LO 46/47** (`18_displacement`). Reproduces agentA's 20-26 pt LO move |
| 2 | **exact** | same as 1 with `w:hRule="exact"` | **17.9 uniform** | 31.66 | 1 | unchanged: Google rewrites `exact`→`atLeast` on import (recorded, read back from its own .docx) | **REFUSED, LO 46/47.** Direction (c) is inert on both sides |
| 3 | **pitch** | `w:trHeight` = P (368) uniform, borders untouched | mb: **18.4 × 20 of 26**; tnhr: **18.40 × 26 of 26, 0 off** | 2.70 / (not measured) | 1 | **19.4** — the charge is untouched, so this makes Google 0.4 pt *worse* | LO 47/47 **both**, but LO share@5 rises 1.55→2.70 |
| 4 | **tcmar20** (control) | HEAD's heights, `w:tcMar` bottom = 20 tw | **identical to HEAD**, 47/47 | 1.55 | 1 | n/a | **the margin is inert whenever the `trHeight` floor binds** — so nothing below is the margin's doing |
| 5 | **absorb** | `w:trHeight` = P − charge; `w:tcMar` bottom = P − rule − content | mb: 18.4 × 20/26, 6 off | 4.23 | 1 | 354 + 20 = 374 = 18.7 | LO **46/47** (18_displacement) |
| 6 | **absorb_full** | charge read as the cell's full bottom rule (sz/8), same shape | mb: 18.4 × 20/26 | (not measured) | 1 | 354 + 20 = 374 | LO **47/47** |
| 7 | **absorb_g20** | `w:trHeight` = **P − 20** uniform (348); `w:tcMar` bottom = P − full bottom rule − content (138-154 tw) | mb: **18.4 × 20 of 26**; tnhr: **18.40 × 26 of 26, 0 off** | **2.39 / 0.79** | 1 / 1 | **348 + 20 = 368 = 18.40 exactly**, by the recorded +1.00 pt charge | **47/47 on both documents, 1 page, text_recall 100 %, 0 chars missing** — survives on the stated criteria; LO share@5 +0.84 / +0.18 |
| 8 | **pbdr** (dir. a) | the row rule leaves `w:tcBorders`/`w:tblBorders` and becomes `w:pBdr/w:bottom` on the cell's paragraph; `w:trHeight` = P | 18.3 / 18.8 sawtooth, 20/23 off | (not measured) | 1 | the rule is no longer in any border box, so the charge should vanish — unmeasurable without a round trip | **rejected on placement**: the pBdr draws at the foot of the *text*, measured 7.1 pt above the row's bottom edge (row top→rule 11.3 pt where the page draws 18.40) |
| 9 | **norule** (dir. d) | every horizontal border removed, `w:trHeight` = P | 18.4-ish, but **only 8 rules left of 27** | (not measured) | 1 | charge gone, so trHeight alone should be laid | **rejected**: the rules themselves are lost (`32_stroke_lines`) |
| 10 | **toponly** (dir. a) | each cell's bottom border moved to a top border on the same row, `w:tblBorders/insideH` removed | 8 rules only — **inconclusive** | — | 1 | — | **inconclusive**, and it cannot help: the row's border box still carries one rule per row |
| 11 | **ENGINE BUILD** of `patches/18-trheight-rule-absorb.patch` | 348 uniform (`rowTw` preferred over the snapped `rowEdge`) + `w:tcMar` 138-154, emitted by `DocxWriter` itself | tnhr: **18.40 × 26 of 26, 0 off**; mb: 17.7-23.8, 5 off | 0.76 / **5.82** | 1 / 1 | 348 + 20 = 368 = 18.40 | tnhr **47/47**; **mb 46/47 — REFUSED** (see below) |

*(mb = `mobile-bill`; tnhr = `table-with-no-header-row`. Both 1 page at HEAD and 1 page in every
variant. `text_recall` 100.0 and `chars_missing` 0 in every variant measured.)*

---

## What the numbers say

**1. The construct exists, and LibreOffice measures it at the source pitch exactly.** Variant 7:
`w:trHeight` = 348 tw (the pitch less the 20 tw Google charges) with `w:tcMar` bottom = 146 tw
carrying the rest of the pitch in the cell's content box. On `table-with-no-header-row` LibreOffice
lays **every one of the 26 rows at 18.40 pt** (HEAD: 18.0/19.0, 26 of 26 rows off), 47/47 on the
47-check instrument, one page, text_recall 100 %, and the cell's text does not move — the first
baseline sits 10.75 pt below its row's top rule in both HEAD and the variant. `w:tcMar` bottom is
below the last line, so it can move nothing; the control (variant 4) proves it: a 20 twip margin
under HEAD's heights is byte-for-byte inert in LibreOffice.

**2. The `w:tcMar` half is what carries LibreOffice, and it is doing exactly the arithmetic it was
given.** On tnhr the emitted numbers are `w:trHeight` 348 and `w:tcMar` bottom 154 = 368 − 10 (the
0.5 pt `insideH`) − 204 (the cell's `before` 194 + `line` 10). LibreOffice's
`max(348, 204 + 154 + 10)` is 368, which is the pitch. The same arithmetic on mobile-bill's 0.875 pt
separator rows gives 138-146. Both were measured, not assumed.

**3. But laying the exact pitch costs LibreOffice ink, and the cost is not the construct's.** With
the rows at 18.40 the *rules* land better (per-rule dy vs the source: max 1.63 pt against HEAD's
1.73) and the *text* lands worse: share@5 1.55 → 2.39 on mobile-bill, 0.61 → 0.79 on tnhr, with
median_pt and max_pt unchanged (1.44 / 16.8). Variant 3 isolates it: `w:trHeight` = 368 with **no
shave and no margin at all** already costs 1.55 → 2.70. The cause is that the engine places each
cell's text from `rowEdge[r]` — the page's rules snapped to whole points, i.e. the 18.0/19.0
sawtooth (`DocxWriter.java:6031`, `6032`, and the cell placement at `6364-6369` / `6832-6837`). The
sawtooth is simultaneously the engine's row height *and* its text grid; any uniform pitch moves the
text off the grid the engine wrote it to. So the conflict is not two renderers fighting over one
number — it is that **the number LibreOffice wants is not one number**: its rules want 18.40 and its
text wants the sawtooth. That is a real finding and it is why no construct, however clever, gets
both renderers free.

**4. Implemented in the engine, it holds on one document and is refused on the other.**
`patches/18-trheight-rule-absorb.patch` (117 lines, one file, applies to HEAD) emits variant 7 from
`DocxWriter.table()` — built, converted, and its `word/document.xml` compared against the hand-built
variant: `w:trHeight` 348, `w:tcMar` bottom 138-154, i.e. the same construct. Measured:
`table-with-no-header-row` **47/47, 18.40 on all 26 rows, 1 page, share@5 0.76 (HEAD 0.61)** —
clean. `mobile-bill` **46/47, `18_displacement` failing, share@5 1.55 → 5.82** — a LibreOffice
regression, so the patch must not land as it stands. The engine build differs from the hand-built
variant in one number only (one row comes out 347 rather than 348) and in the page budget, and that
is enough to move mobile-bill's rows to 17.7-23.8 — the construct is on a knife edge there, which is
itself the answer to "is it robust": **not on this document**.

**5. Therefore: no construct satisfies both renderers without cost.** The measured proof is the
table above. Variants 1 and 2 fix Google's arithmetic and cost LibreOffice a check (46/47, share@5
31.66). Variants 3 and 7 fix the pitch in both renderers and cost LibreOffice 0.84 share@5 points on
mobile-bill. Variants 8-10 are refuted on placement, on lost rules, and as inconclusive. What is
left is a genuine trade, and the trade is priced here to two decimal places rather than argued.

---

## What the next run should do with this, in one step

The one thing this slot could not do is the only thing that can decide it. `table-with-no-header-row`
is the document to spend it on, because the construct is **exactly clean there in LibreOffice**
(47/47, 18.40 on every row, one page, share@5 0.76 against 0.61) and it is the cheaper of the two
(1 page, 27 rows, no separator-weight complication):

    # 1. build the construct
    git apply patches/18-trheight-rule-absorb.patch
    bash tools/p2w-bench/build-engine.sh
    # 2. convert the one document and take it through Google, four Drive calls
    java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
         ConvertOne /scratch/work/p2w/corpus/table-with-no-header-row.pdf /scratch/work/out18
    # upload -> GOOGLEDRIVE_CREATE_FILE(mimeType=google-apps.document, parents=[KavoPDF-Verify
    #   11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6]) -> GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(pdf)
    python3 tools/p2w-bench/verify_google.py /scratch/work/p2w/corpus/table-with-no-header-row.pdf \
            <export.pdf> --docx /scratch/work/out18/table-with-no-header-row.docx
    # 3. read the row rules off the export and compare with 18.40 - that, not the check, is the claim
    python3 /scratch/work/exp/measure.py <export.pdf>      # rules y, rule pitch, text baselines

**The prediction the round trip is testing, stated so it can fail:** Google lays
`w:trHeight + 20 tw` = 348 + 20 = 368 = **18.40 pt on every row**, against HEAD's recorded 19.0/20.0
sawtooth, and `18_displacement` passes on the Google side for the first time. The number that would
falsify it is the charge not being a flat 20 tw on a table whose only horizontal rule is a 0.5 pt
`insideH` — the recorded +1.00 pt was measured on mobile-bill's 0.875 pt separators, so a 0.5 pt
table is the untested case, and if Google charges 10 tw there the rows will come back at 17.90 and
the prediction is wrong by 0.5 pt a row.

**And the thing to fix after it:** if the round trip confirms the pitch, the remaining LibreOffice
cost is the engine's text grid, not the construct. The next change is to place each cell's text from
the *same* uniform pitch the row is written at, instead of from the whole-point `rowEdge` sawtooth —
that is `DocxWriter.java:6364-6369` (`rowTopPagePt`) feeding `6832-6837` (`wantPt = cellBaseY −
rowTopPagePt`). Until that lands, every variant in this table trades one renderer for the other, and
this file is the price list.

---

## Where the construct lives in the engine

The patch is `patches/18-trheight-rule-absorb.patch`, 117 lines, `DocxWriter.java` only, applies to
`3b98dce7`:

| what | file:line at HEAD | change |
|:--|:--|:--|
| the charge, named | `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:5742` (beside `TABLE_RULE_SZ`) | new `GOOGLE_RULE_CHARGE_TW = 20` |
| the row's pitch, unsnapped | `DocxWriter.java:6364-6369` (`rowTwHere` from `rowEdge`) | prefer `rowTw` when it agrees to within 20 tw (agentA's hunk 3, reused) |
| `w:trHeight` emission | `DocxWriter.java:6556-6559` | `rowHeightTw − GOOGLE_RULE_CHARGE_TW` |
| the rule LibreOffice charges | after `DocxWriter.java:6559` | `loRuleTwHere` from the cell's own bottom rule (sz/8 pt) |
| the margin | `DocxWriter.java:6869` and `6889` (the two `</w:tcPr>` sites) | `cellMarTw(...)` — `<w:tcMar><w:top 0/><w:bottom (pitch − rule − content)/></w:tcMar>` |
| the helper | beside `szOf()` | `cellMarTw(int pitchTw, int ruleTw, int contentTw)` |

## The commit gate

The finding and the patch are committed; **the engine change is not**, and the gate was not worked
around. `tools/install-gate.sh` is installed and reports
`docx: no document worse than baseline / txt: no document worse than baseline / PASS` on this tree,
because this commit touches no `.java` — the patch is carried in `patches/` as a file, which is how
this repo carries an engine change that has not been measured corpus-wide. When the patch *is*
applied, `regress.py --check` will refuse it for the reason recorded by the 12:20 run: the trHeight
edit reaches every ruled table in the corpus and `p2w.py --budget` cannot measure 213 documents in
one slot. The refusal is expected, it is information, and it is not a reason to land it.

## Cost

One clone, one corpus fetch (6 min), 4 engine builds (37-66 s each), 13 soffice renders, 17
`verify_google.py` runs, 2 `measure_doc` passes per document. The engine tree is back at HEAD;
`DocxWriter.java` is unmodified in the working tree, and the change travels as the patch.
