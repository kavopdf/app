# 18_displacement — where the row height is written, and what the 0.9634 actually is

**24 Nov 2026 · slot 17:47 → · engine `kavopdf/app` cloned at HEAD, built in-sandbox
(`tools/p2w-bench/build-engine.sh`, 39 s), converted with `ConvertAll` · no engine change, no
commit but this file · corpus fetched with `corpus-fetch.sh` (213 PDFs, 0 missing)**

Every number below marked **measured here** was produced in this slot from the emitted `.docx`
and from a LibreOffice render of it. Every number marked **recorded** is quoted from a FINDINGS
file named at that point; none of those was re-run.

---

## 1. The question, and the answer in one line

The row height is computed in `DocxWriter.java` at **6444–6468** and written at **6558–6559**.
The **0.9634 is not in the source** — `grep -rn "0\.963\|1\.038\|9634" app/src/main/java` returns
nothing. It is the ratio **18.40 / 19.10 = 0.96335**: the page's own row pitch (18.40 pt) divided
by the height the row is *laid* at (19.10 pt) on `mobile-bill`. It is an **additive per-row charge
re-expressed as a scale**, and the charge is the row's rule plus whole-pixel rounding, not a
leading factor, not a unit conversion, and not a padding constant.

**And the declaration it was fitted to is already correct.** Measured here, on the `.docx` this
engine emits at HEAD, the `w:trHeight` it writes *is* the page's pitch:

| document | rows (tables) | `w:trHeight` written | page's own row pitch | error |
|:--|--:|:--|:--|--:|
| `mobile-bill` | 24 (3) | 360 / 380 tw = 18.0 / 19.0 | 18.40 (26 of 28 gaps) | 0.0 on the mean |
| `insurance-policy-schedule` | 22 (3) | 360 / 380 tw | 18.40 | 0.0 on the mean |
| `16_right_aligned_amounts_txtpos` | 13 (1) | 380 tw = 19.00 | 19.00 | **0.00** |
| `68_journal_wide_table_spanning` | 7 (1) | 380 tw = 19.00 | 19.00 | **0.00** |
| `bus-timetable-station-left-times-right` | 33 (1) | 328 tw = 16.40 | 16.40 | **0.00** |
| `table-with-no-header-row` | 26 (1) | 360 / 380 tw | 18.40 | 0.0 on the mean |

A declaration that is exact to 0.00 pt on four documents cannot be the thing that is 3.66 % long.
The 0.9634 is a *fitted correction for the renderer*, applied to a number that was already right —
which is why it does not generalise and why it is wrong-signed in the renderer that honours
`w:trHeight`.

---

## 2. Where the row height is computed and written

All line numbers are `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` at HEAD.

| what | where |
|:--|:--|
| the row's pitch from the page, `rowTwHere` | 6380–6386 (the `keepRows`/`paperHPt` cap), set from `rowEdge`/`rowTw` above it |
| the rule this row pays, `ruleTwHere = round((szAbove+szBelow) * 20 / 16)` | **6389** |
| the premise: "the renderer lays a row out at max(w:trHeight, cell content + rule)" | **6391–6401** |
| `pitchTwHere = rowTwHere`; `contentTwHere = rowTwHere − ruleTwHere` | **6402–6404** |
| the cell's line box / the type-size floor, `rowLineTw = max(rowLineTw, round(sz * 1.25 * 20))` | 6444, **6459** |
| the cap a squeezed page puts on the row, `typeFloorTw` | 6466–6467 |
| **`rowHeightTw = max(rowTwHere, rowLineTw)`** | **6468** |
| `ctx.squeeze` scaling (only when a page is squeezed) | 6469–6472 |
| the budget the flow is placed from, `writtenRowsTw += max(pitchTwHere, max(rowTwHere,rowLineTw) + ruleTwHere)` | **6477–6483** |
| **emission: `<w:trHeight w:val="rowHeightTw" w:hRule="atLeast"/>`** | **6558–6559** |
| the second emission site, a column page's single-row table, `hRule="exact"` | 2257–2258 |

So there are exactly two `w:trHeight` appends, and the one 18_displacement's tables go through is
6558. Constants in play: `TWIPS_PER_PT = 20.0` (52), `LINE_BASE = 0.8f` (214),
`LINE_FACTOR = 1.15f` (73), `HAIRLINE_EM = 0.069f` (126–141).

---

## 3. The mechanism, in one paragraph

The engine declares each row at the page's own pitch and then *takes one rule back out of the
cell's line box* — `contentTwHere = rowTwHere − ruleTwHere` (6403) — on the premise, stated at
6391, that the renderer lays the row at `max(w:trHeight, content + rule)`, i.e. that the rule is
charged **inside** the declared height. On `mobile-bill` that premise is false in Google Docs: the
emitted table carries `w:tblBorders` with `insideH`/`top`/`bottom` at `w:sz="4"` = **0.5 pt**
(measured here from the emitted `document.xml`), each row is charged one rule **on top of** the
declared height, and the row is then snapped to a whole pixel (0.75 pt) — so an 18.0 pt row comes
back at 19.10 rather than 18.40 and the surplus is charged again on the next row. That surplus is
**additive, not proportional**: 0.70 pt on a 19 pt row (0.9634 as a scale) but also 0.70 pt on
`362_price_list_dense`'s 8.4 pt rows (a factor of 1.083) and on `bus-timetable`'s 16.4 pt rows
(1.043). The 0.9634 is the additive term divided by one particular pitch, and it only fits pitches
near 19 pt — which is the whole reason it was measured on `mobile-bill`, fitted there, and does not
transfer. The engine's own comment at 6237–6240 already records the same quantum from the other
side ("the subtraction made every w:trHeight-driven row 0.75 pt short").

**The recorded Google evidence is internally inconsistent on one point, and it is stated here
rather than smoothed over.** `18_displacement-TRHEIGHT-HONOURED-LINEBOX-FLOOR-1130-relay.md`
measured `laid = declared + 0.75` on 13 of 13 declarations from 15 to 72 pt (10 pt text, a 0.5 pt
`Table Grid` border). `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` measured the same
document class laying 18.0/19.0/20.0 on rows declared 360/380 and concluded `w:trHeight` is stored
and not laid. Both cannot be literally true. What every recorded Google measurement does agree on
is the sign and the size: **the laid row is the declared height plus a positive 0.5–1.1 pt**, which
is the rule, and it is charged once per row. That is the +0.70, and it is what 0.9634 divides out.

---

## 4. Measured here: what the scale actually does

I did not touch the engine. I scaled `w:trHeight` by 0.9634 **inside the emitted `.docx`** (XML
rewrite, everything else byte-identical) and rendered both versions in LibreOffice, the renderer
that honours `w:trHeight` — where `mobile-bill` is currently **47/47 clean** (`gverify-lo/mobile-bill.json`).

`mobile-bill`, table rows 1–26, LibreOffice:

| | row pitches | bottom rule of the table | "Net amount payable" | "Amount in words…" |
|:--|:--|--:|--:|--:|
| HEAD (360/380 tw) | 18.2 / 17.8 / 19.0 / 18.0 / 19.0 … | 541.25 | 546.2 | 566.0 |
| `w:trHeight` × 0.9634 | 17.6 / 17.1 / 18.3 / 17.4 / 18.3 … | **525.85 (−15.40)** | **530.8 (−15.40)** | **550.0 (−16.00)** |

`insurance-policy-schedule`, LibreOffice:

| | "Net premium payable" | "Authorised signatory" |
|:--|--:|--:|
| HEAD | 509.2 | 605.2 |
| × 0.9634 | **495.2 (−14.00)** | **590.5 (−14.70)** |

15.4 pt over 26 rows is 0.59 pt a row: the scale shortens every row by exactly the amount it was
supposed to remove, and every line below the table inherits the sum. On a document that is
**currently clean in LibreOffice**, that is a 15.4 pt displacement against a tolerance of
`clamp(0.35 × 7.4, 1.5, 4.5) = 2.59` pt — six times the cap, on every run below the table.

---

## 5. Which corpus documents the correction would move

Two different corrections are on the table, and they move different sets. I separate them because
the instruction "correct the factor to 1.0" is ambiguous and the two readings have opposite signs.

### 5a. If "1.0" means *removing the renderer's per-row charge* (rows lay at the page's pitch in Google)

This is the real fix and it is additive, not a scale. It moves every document whose page-1 table
has enough rows for the per-row surplus to exceed `max(2, ceil(0.05 n))` runs and
`clamp(0.35 size, 1.5, 4.5)` pt. Row counts and pitches measured here from the emitted `.docx`:

| document | rows | row pitch | surplus at +0.70/row, at the table's foot | predicted |
|:--|--:|--:|--:|:--|
| `362_price_list_dense` | 29 | 8.4 | **20.3 pt** (and 8 % of every row) | **moves** — the largest per-row ratio in the corpus |
| `bus-timetable-station-left-times-right` | 33 | 16.4 | **23.1 pt** | **moves** |
| `table-with-no-header-row` | 26 | 18.0/19.0 | **18.2 pt** | **moves** |
| `mobile-bill` | 24 | 18.0/19.0 | **16.8 pt** | **moves** (measured clean by the row-pitch patch: `patches/18-spacer-before-rowpitch-rowrule.patch`) |
| `insurance-policy-schedule` | 22 | 18.0/19.0 | **15.4 pt** | **moves**, and does not close on its own (recorded: 41/42 with the patch) |
| `72_bank_statement_no_rules_right_amounts` | 18 | 17.0 | **12.6 pt** | **moves** |
| `22_invoice_four_columns_txtpos` | 16 | 18.0/19.0 | **11.2 pt** | **moves** |
| `balance-sheet-two-columns-of-figures` | 16 | 11.6/12.0 | **11.2 pt** | **moves** |
| `71_invoice_space_aligned_no_rules` | 14 | 18.0/16.0 | **9.8 pt** | **moves** |
| `two-tables-stacked-with-no-gap` | 13 | 18.0/19.0 | **9.1 pt** | **moves** |
| `16_right_aligned_amounts_txtpos` | 13 | 19.0 | **9.1 pt** | **moves** |
| `41_coloured_headings_white_bg` | 12 | 18.0 | **8.4 pt** | **moves** |
| `73_marksheet_subject_marks_grade` | 9 | 19.0/20.0 | **6.3 pt** | **moves** |
| `68_journal_wide_table_spanning` | 7 | 19.0 | **4.9 pt** | **moves**, weakest — and its `w:tblBorders` are all `w:val="nil"` (measured here), so it has no rule to charge; its failure is its own |
| `29_dot_leaders_txtpos` | 5 | 18.0/20.0 | **3.5 pt** | **moves**, marginal |
| `31_times_body_arial_headings` | **0** | — | **0.0 pt** | **cannot move** — no table at all (measured here) |

15 of the 16 documents that fail `18_displacement` alone are row-driven by this arithmetic; the
16th, `31_times_body_arial_headings`, has no table and is out of scope for any row fix. That is a
stronger claim than the recorded patch achieved (3–4 documents), and the difference is that the
surplus is *not* removable by declaring a smaller height where the renderer charges the rule
outside the box.

### 5b. If "1.0" means *the previous run's scale, applied to the declaration*

Then the predicted movers are the opposite set: the documents where LibreOffice honours the
declaration. `mobile-bill` and `insurance-policy-schedule` are both **clean or near-clean in
LibreOffice today** (`gverify-lo/mobile-bill.json` is 47/47), and section 4 measures them going
15.4 and 14.0 pt off the page. Predicted: `mobile-bill` 47/47 → `18_displacement` fails; and
nothing at all changes in Google, where the declaration is not what lays the row.

---

## 6. Why `mobile-bill` and `insurance-policy-schedule` lose content

Both are **single-page A4 (595 × 842 pt) documents that are exactly full**: the table runs to the
foot of the flow and only the footer band (y 811) sits below it, so there is no slack to give. Two
things then move the tail onto a second sheet, and it is the pair that costs the content — the
scale alone does not overflow, it *under*-shoots:

- `mobile-bill`, page 1: the itemised table ends with row 10 "Net amount payable 873.52" at
  y 544.6, then the closing block — "Amount in words: Rupees Eight Hundred Seventy Four Only"
  (y 564.5), "SAC 998413 · This is a tax invoice under rule 46 of the CGST Rules" (y 577.8) and
  "For assistance call 198 from your Vistara number…" (y 591.0). If the table cannot compress, the
  **last four numbered rows (7 SGST 104.76, 8 Total amount payable 1,373.52, 9 Less: advance
  payment (500.00), 10 Net amount payable 873.52 — y 489–552)** go first, then that closing block.
- `insurance-policy-schedule`, page 1: the table's last row "Net premium payable 76,072.20"
  (y 507.7), then "Note: this schedule must be read with the policy wording and the endorsement"
  (y 528.2), then the signature block — "For Sahyadri General Insurance Co. Ltd." (y 549.9),
  "Authorised signatory" (y 603.7), "Underwriting department" (y 613.0). The signature block is
  the part that must not be split from its schedule, and it is the lowest thing on the page.

The recorded outcome of the build that carried the scale *together with the spacer* is
`41/42 → 38/42`, **2 pages, four checks** (`18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md`,
restated in `18_displacement-DITHER-REFUTED-AND-THE-GUARD-THAT-REPLACES-IT-0030-fixer.md`). The
spacer is spent at its true value (~19.5 pt at the page top); the scale buys back 0.6 pt × 24 rows
= 14.4 pt, which is less than the spacer costs, so the page overflows by the difference and the
tail above lands on page 2. That is the content loss — not clipping, **overflow**.

---

## 7. Falsifiable predictions

1. **The 0.9634 is a ratio, not a factor.** If the +0.70 is the row's rule charged outside the
   `w:trHeight` box, then rewriting `mobile-bill`'s `w:trHeight` from 360/380 to **350/370**
   (one 0.5 pt rule less) changes its Google row pitch from 19.10 to 18.40 ± 0.05, while
   rewriting it to **347/366** (× 0.9634) changes it to 18.40 at best and leaves it at 18.35 in
   any row where the cell's line box binds. Two variants, one round trip, different outcomes.
   If both give 18.40, the additive reading is wrong.
2. **The scale is wrong-signed in the renderer that honours `w:trHeight`.** Measured here,
   LibreOffice: `mobile-bill`'s table bottom moves 541.25 → 525.85 and "Net amount payable"
   546.2 → 530.8 with `w:trHeight` × 0.9634 and nothing else changed. Prediction: `mobile-bill`
   goes from `47/47` to failing `18_displacement` in `gverify-lo`. If it stays 47/47, the row box
   is not where the 0.70 lives.
3. **Page count is decided by the row count, not by the scale.** If the surplus is +0.70 per row,
   removing it moves `mobile-bill`'s table foot up 16.8 pt and its page-1 slack from ~0 to ~16.8 pt;
   spending the spacer at its true value (~19.5 pt) then overflows by ~2.7 pt and page 2 appears
   **only** if the spacer is spent in full. Prediction: row fix without spacer → 1 page, 41/42;
   row fix with the spacer capped at 16 pt → 1 page and 42/42; spacer uncapped → 2 pages. That is
   the shape of the recorded 38/42, and it is a prediction, not a restatement.
4. **A document with no table cannot move.** `31_times_body_arial_headings` emits 0 tables
   (measured here). If any row-height change moves its `18_displacement`, the change is reaching
   something other than a row.

---

## 8. Ruled out

- **A twips/points/EMU unit conversion.** `TWIPS_PER_PT = 20.0` (52) is used consistently and the
  emitted numbers reproduce the page's pitch to **0.00 pt** on four documents (section 1). EMU
  (`EMU_PER_PT = 12700.0`, 50) is used only for drawing anchors, never for a row. A conversion
  error would be a fixed ratio (0.05, 20, 1/1440) and would show as a wrong number in the XML; the
  numbers are right.
- **A leading / line-height factor.** `LINE_FACTOR = 1.15` (73) and the `sz × 1.25` floor at 6459
  are both far below the pitch here: `mobile-bill`'s and `insurance-policy-schedule`'s cells are
  `w:sz="14"` = **7.0 pt** (measured here), so 1.15 × 7 = 8.05 and 1.25 × 7 = 8.75 pt against an
  18.4 pt row. `LINE_BASE = 0.8` (214) places a cell's baseline and appears nowhere in the row
  height. **This also corrects the record**: the relay's decomposition `19.10 − 0.75 = 18.35 =
  1.15 × 15.96` requires a 15.96 pt cell, and there is no cell larger than 7 pt in either document.
- **Rounding of the declaration to whole twips.** The alternation 360/380 against a 18.40 pitch is
  a 0.025 pt error per row (0.5 twip), 28× too small to be 0.70.
- **`ctx.squeeze` / `twScale` (576, 6469–6472).** Only runs when `squeeze != 1`, i.e. on a page the
  engine has decided to squeeze; both documents here are one page and emit `rowHeightTw` = `rowTwHere`
  unchanged.
- **A deliberate padding constant.** There is no 0.9634, 0.963, 1.038 or equivalent anywhere in
  `app/src/main/java`; the only constants in the row path are 20.0, 1.25, 1.15, 0.8 and 0.069, none
  of which is within 3 % of 0.9634.
- **The cell-box path (`rowParts > 1`, 6411–6435 and 6747–6750).** Not entered on either cost
  document: every cell carries one paragraph (measured here: one `w:spacing` per cell, no `\n`).

## 9. What was not done

No Google round trip was made by this slot, so no Google number in this file is mine. The
LibreOffice numbers in sections 4 and 5 are mine and reproducible from the emitted `.docx` alone.
The predictions in section 7 are the measurements that would settle it, in the order of cost.
