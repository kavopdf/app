# 18_displacement — the 0.9634 row scale is REFUTED, and the cell-box explanation of the row excess is refuted too. The excess is in the MULTI-PARAGRAPH cell path.

**22 Nov 2026 · slot 09:51–10:35 IST · fixer · attempt 10 · outcome `lead`, 0 of 3 moved**

## What was built

The 10:05 run left an explicit instruction: land the spacer construct **and** the row-height
construct in one build. Three edits went into `DocxWriter.java`:

1. **The table spacer as `w:before` + hairline `w:line`** (the emitter at 5868-5875). The gap moves
   from `w:line` to `w:before`; `w:line` becomes `1` twip `exact`. LibreOffice charges `before + line`,
   which is the same sum it charged before, so soffice cannot move.
2. **The spacer cap raised 2880 → 4320 twips** (5852, 5866).
3. **A hairline cell box for sizeless single-line cells** — the proposed replacement for the
   0.9634 `trHeight` scale, which was *not* built because two independent reads of the code said it
   would be inert (see "Why the 0.9634 scale was not built" below).

## What it did, measured in Google, three documents

| document | before (HEAD) | after | outcome |
|:--|--:|--:|:--|
| `68_journal_wide_table_spanning` | 42/42 | **42/42** | **still CLEAN** — the spacer half still works |
| `mobile-bill` | 41/42 | **38/42** | WORSE — 2 pages, `01_page_count`, `18_displacement`, `32_stroke_lines`, `55_orientation_mix` |
| `insurance-policy-schedule` | 41/42 | **38/42** | WORSE — same four |

Rendered through the real renderer (Drive: upload → copy as Google Doc → export PDF), scored by
`verify_google.py` against the corpus PDF. All three probe Docs were deleted after scoring;
`KavoPDF-Verify` is empty.

## The row excess is still there, and it is not 0.70

Measured directly off the Google export, from the horizontal rule positions in page 1:

| | source | Google (HEAD + all three edits) |
|:--|--:|--:|
| `mobile-bill` median row pitch | **18.40 pt** (24 of 26 gaps exactly 18.4) | **19.00 pt** |
| `mobile-bill` pitch histogram | 18.4 ×24 | 19.0 ×16, 20.0 ×5, 18.0 ×3 |
| `insurance-policy-schedule` median | **18.40 pt** | **19.00 pt** |

The engine writes these rows 360/360/380 twips repeating — 18.0/18.0/19.0, averaging 18.33, the
`floor(18.4k)` quantisation. Google lays them out at 19.0, 19.0 and 20.0. So Google is **growing the
360-twip rows** to 19.0 and 20.0.

## Two mechanisms refuted, with the numbers

**Refuted 1 — the 0.9634 `trHeight` scale.** Under `hRule="atLeast"` the written `w:val` is a FLOOR:
the row is laid out at `max(val, cell content + rule)`. Scaling the floor down cannot cap a row that
is taller than its floor. On `mobile-bill` every row is already at or above its floor, so
`0.9634 × val` is a no-op on 24 of 24 rows and would shrink only the two rows in the corpus whose
`val` genuinely binds (`370_offer_letter` 620 tw, `table-with-rotated-header` 1480 tw). The 08:20
finding's C1 proposal (0.9785) and the 10:05 instruction (0.9634) both target the non-binding half
of the constraint. **Do not build this.**

**Refuted 2 — the cell paragraph is the growth.** The 10:05 hypothesis was that Google prices the
cell's `w:line` as a multiple of the face's line height — `(w:line/240) × 1.164 × size` — and that a
whole-pitch box therefore charges 19.10 pt on an 18.40 pt pitch. That arithmetic does reproduce
19.1003 pt, which is why it was worth building. It is wrong: the cells in these documents were
**already** hairline boxes before the edit —

```
row 0   trHeight 360   cell w:before="194" w:line="10" lineRule="exact"
row 2   trHeight 380   cell w:before="210" w:line="10" lineRule="exact"
```

194 twips = 9.70 pt, and Google's charge on that pair is 9.70 + max((10/240)×1.164×11, 0.069×11)
= **10.23 pt**, less than half the 18.40 pt floor. A cell charging 10.23 pt cannot grow an 18.40 pt
row. The edit changed the emitted pair and moved the rendered pitch by **0.10 pt** (19.10 → 19.00),
not 0.70. The cell box is a 14 % contributor, not the cause.

## What the evidence says the cause is

The growth concentrates on rows that hold a cell with **more than one paragraph**. Counting
`<w:p>` per `<w:tr>` in `mobile-bill.docx`:

| rows | paragraphs in the row | trHeight | Google pitch |
|:--|--:|--:|--:|
| 0–4, 13–23 | 3–4 | 360/380 | 18.0 / 19.0 / 20.0 mixed |
| **5–12** | **6** | 360/380 | **20.0** |

A 6-paragraph row on a 3-column table is two paragraphs per cell — a wrapped line. Those are exactly
the rows the new cell guard skipped (`rowParts == 1`), because there the box IS the line advance and a
hairline would collapse the two lines onto each other. Two paragraphs at ~9.7 pt each is ~19.4 pt of
content, which grows a 360-twip (18.0 pt) row to 20.0. That is the ramp, and it is 20.0 − 18.0 =
**2.0 pt on those rows**, not a uniform 0.70.

**The next build must reach the multi-paragraph path, not the single-line one.** The lever there is
not the box (it is the line advance and must stay) but the paragraph's own `w:before` on the
continuation lines, or the row's `trHeight` floor raised to the true 368 twips so the floor and the
content agree instead of the floor being quantised 8 twips low.

## Why the 0.9634 scale was not built

Two independent reads of the emitter (this run's own, and a subagent given the real
`DocxWriter.java`) both concluded that `w:val` under `atLeast` is a floor and cannot cap growth. The
measurement above confirms it: the rows Google grows are the ones whose `val` is *below* the content,
and the rows where `val` binds already render at `val`. The instruction in `LAST-MESSAGE.md` to
"scale the row height by 0.9634" is therefore withdrawn by this finding.

## What is settled

1. The spacer-as-`w:before` construct still takes `68_journal` to 42/42 with the cell edit alongside
   it. It is not the thing that breaks the two pages.
2. The two blocker documents need the **multi-paragraph cell** path fixed before the spacer can land.
3. The row excess is 2.0 pt on wrapped rows and 0–1.0 pt on single-line rows, not a uniform 0.70 pt.
   A factor cannot describe it; a per-row count of lines can.
4. `screen.py` must not be used on this class: it renders in soffice, which honours `w:line` as a
   length and cannot see any of these states.

## What it cost

Three Google renders, nine Drive calls, three probe Docs created and deleted, ~20 min. The engine is
back at HEAD (`git checkout -- DocxWriter.java`); nothing in the corpus, the tables or the Drive was
touched.
