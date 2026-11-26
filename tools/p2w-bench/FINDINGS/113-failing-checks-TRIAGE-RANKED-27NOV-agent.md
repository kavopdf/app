# p2w-bench — ranked triage of the 113 failing Google check-instances

Read-only investigation of `kavopdf/app` @ HEAD (shallow clone). Nothing was modified, committed or pushed.

---

## 0. How the 113 were established (so the numbers are checkable)

The headline is reproducible from the repo alone:

| quantity | value | where |
|:--|:--|:--|
| check-instances passing | **2462 of 2575 (95.6%)** | recomputed, matches `tools/p2w-bench/report.py:1433` |
| check-instances failing | **113** | 2575 − 2462 |
| documents in the row | **61** | `report.py:551-579` `check_instances()` |
| engine the row is stamped with | `a4d8fca469bba636` | `report.py:487-528` `engine_now()` |

`check_instances()` (`report.py:551-579`) is the only place that number comes from: it globs
`benchmarks/gverify/*.json` and keeps rows whose `engine` equals `engine_now()`. I re-ran that
exact filter and got 61 documents / 2462 passed / 113 failed — identical. Per-check tallies below
are computed from the same 61 rows.

**Three limits on the denominator, stated up front.**

1. **Only 61 of 213 documents are on the current engine.** Across all 213 `gverify` rows the engine
   stamp splits `a4d8fca4`: 61, `025fe9de`: 147, `d85db0a9`: 5. So the 113 describe 29% of the
   corpus; the other 152 documents may pass or fail differently on this engine and **cannot be
   established without re-measuring them through Google**.
2. **One of the 61 is not scored at all.** `Account_Opening_Form_Fillable_filled` is
   `status: page_count_refused` with no `passed` and no `failed` key, so `check_instances()` adds
   0/0 for it and counts it as a clean document. 60 documents are actually scored. (See §C.3.)
3. `classpick.py --leverage` reports a different ranking because **it does not filter by engine**
   (`classpick.py:214-267` iterates every `gverify` file). Its "18_displacement is worth 52.2 clean
   documents" is measured over a mixed-engine store; over the current-engine 61 it is **9.31**. Both
   numbers are real; only the second describes the code in the tree.

Tools run (all read-only, none compiled or converted anything): `status.py`, `report.py`, `gaps.py`,
`pending.py`, `allreports.py --unread`, `classpick.py --leverage`. Not run, as instructed:
`pod-prep.sh`, `attempt.py`, `measure_gate.py`, `build-engine.sh`.

---

## A. The ranked table

`docs` = documents failing that check among the 61 current-engine rows.
`→ clean` = documents that would become **fully clean** if that check alone were fixed (i.e. it is
their only failure). This is the only count that moves the charter's goal.

| # | check-id | docs | → clean | converter file / function responsible | one-line proposed change |
|--:|:--|--:|--:|:--|:--|
| 1 | `18_displacement` | 18 | **5** | `app/.../engine/DocxWriter.java:6631` `w:trHeight hRule="atLeast"` at the page's own pitch (`rowHeightTw` `:6541`); page-top gap as `w:before` (`flowFromBox :4525`, `flowRow :3635`) under `w:pgMar w:top="0"` (`sectPrXml :2448`) | Accumulate the residual when declaring each row's `w:trHeight`, so Google's 0.75 pt re-quantisation of the *cumulative* target never sums down the table |
| 2 | `60_text_column_right_edge` | **20** | **5** | `DocxWriter.java:4665-4680` `flowFromBox` — a left-aligned line gets `w:ind w:right="0"` and **no `w:jc`** (`:4671-4674`), so its right extent is whatever the substitute face makes it | No converter change: all 5 sole documents are DejaVu, which Google cannot render (§C.1). Engine-side only for the other 15, which have 0 sole |
| 3 | `04_chars_missing` | 13 | 0 | `DocxWriter.java:5622` `anchorShape()` → text written into `wps:txbx/w:txbxContent` inside `wp:anchor` | No construct: the writer's own comment (`DocxWriter.java:408-415`) records that Google returns an anchored textbox as pixels with no text layer |
| 4 | `59_shape_anchor` | 11 | **0** | *instrument*: `tools/p2w-bench/verify_google.py:2426` `_box_moved()`; engine: `DocxWriter.java:2849` `anchorBox()` | Add a **position** term to `_box_moved` (it compares extent only, via `_class_count` `:2420`) — see §C.2 |
| 5 | `47_margins` | 11 | **2** | `DocxWriter.java:4677-4680` `flowFromBox` writes a box's runs back-to-back with **no tab**; the field split is `PdfToWord.java:5185` `sameRow()` (gap floor `Math.max(1.5f, size*0.15f)` at `:5225`) | Emit `<w:tab/>` with a stop at the second run's measured x when two runs share a baseline and a real gap — the machinery already exists in `flowRow` (`DocxWriter.java:3805-3832`) |
| 6 | `13_text_colours` | 7 | 0 | `DocxWriter.java:5622` `anchorShape()` (colour inside a rasterised drawing) + `runXml` | Same construct as #3; no colour is recoverable from a rasterised box |
| 7 | `45_char_accuracy` | 7 | 0 | `DocxWriter.java:5622` `anchorShape()` | Same construct as #3 |
| 8 | `17_matched_runs` | 6 | **1** | `verify_google.py:5799` (verdict: `matched >= ceil(0.9·len(s_runs))`); engine side is run/Line assembly in `PdfToWord.java` | Not established — no finding names a mechanism for `391_survey_questionnaire_grid` |
| 9 | `43_within_10pt_x` | 5 | 0 | `DocxWriter.java:4671` `w:ind w:left`; `flowRow` tab stops `:3805-3832` | — |
| 10 | `35_rotation` | 4 | 0 | `DocxWriter.java:5622` `anchorShape()` (rotation carried by the DrawingML transform) | OOXML has no other construct for a rotation angle (`FINDINGS/04_chars_missing-REAL-WRITER-DEFECT-1115-fixer.md` §Verdict) |
| 11 | `26_text_overlap` | 3 | **1** | declared row height `DocxWriter.java:6631` (a row that grows lays the next row on top) | `374_org_chart` grows **18.3 pt per row** over 3 rows (`benchmarks/DISP-TABLE.csv`) — same construct as #1 |
| 12 | `44_header_footer` | 2 | 0 | `DocxWriter.java:5622` `anchorShape()` — same anchored boxes as #3 | — |
| 13 | `05_chars_extra` | 1 | 0 | run emission, `DocxWriter.runXml` | — |
| 14 | `27_text_off_page` | 1 | 0 | `DocxWriter.java:4671` `w:ind` / `sectPrXml :2448` | — |
| 15 | `10_font_sizes` | 1 | 0 | `runXml` `w:sz` | — |
| 16 | `32_stroke_lines` | 1 | 0 | `DocxWriter` rule/shape emission (`c["32_stroke_lines"]` verdict at `verify_google.py:2993`) | — |
| 17 | `23_line_pitch` | 1 | 0 | `DocxWriter.java:149` `spacing()` + `hairlinePt` `:4113` | — |
| 18 | `66_table_cell_width` | 1 | 0 | `DocxWriter.tableBody` cell width | — |

**Check-family yields (computed over the same 61 rows).** Because only 14 documents are one check
away, the useful number is the *combination*:

| family | documents that become clean |
|:--|--:|
| `18` + `60` | **12** |
| `47` + `60` | 8 |
| `18` + `59` | 8 |
| `18` + `47` | **7** |
| `59` + `60` | 6 |
| `18` + `59` + `60` | 16 |

`18_displacement` appears in every top-yield combination. That is the strongest structural fact in
the store.

**The 14 one-check-away documents, by owner:**

* `18_displacement` (5): `16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`,
  `362_price_list_dense`, `36_embedded_subset_font`, `402_calendar_month_grid`
* `60_text_column_right_edge` (5): `302_radiology_report`, `313_power_of_attorney`,
  `316_contract_with_schedules`, `321_auditors_report`, `335_msds_safety_data_sheet`
* `47_margins` (2): `380_runbook_terminal_output`, `392_statistical_console_output`
* `26_text_overlap` (1): `374_org_chart`
* `17_matched_runs` (1): `391_survey_questionnaire_grid`

---

## B. The one class to attack first: `47_margins`

**Two documents, and it is the only class on the board where feasibility is already measured rather
than hypothesised.**

The argument, in the order it matters:

1. **The mechanism is named in the emitted XML, not inferred.** On `392_statistical_console_output`
   the source draws one baseline as two runs (`x=28.0 "Multiple R-squared: 0.8412,"` and
   `x=139.2 "Adjusted R-squared: 0.8371"`); the engine writes them as **one `<w:t>` with a single
   space**. That is visible in the code: `DocxWriter.java:4677-4680` emits `b.runs` with no
   separator construct at all. Where the second column lands is then decided by the face's advance —
   `DejaVuSansMono` puts it at 141.1 pt, Google substitutes Verdana (proportional) and lands it
   34.1 pt short. Source: `FINDINGS/47_margins-DEJAVU-MONO-GOOGLE-SUBSTITUTES-VERDANA-081500-f1x.md`.

2. **The fix construct has already been measured through Google Docs and honoured exactly.** A
   `<w:tab w:pos="4320">` asked for 216.0 pt and Google rendered 216.00 pt — error 0.00 pt — and the
   origin is the left margin, not the page edge (probe C: 72 + 216 = 288.00).
   Source: `FINDINGS/47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`. **No Google round trip is
   needed to establish that the construct works; only to establish its reach.**

3. **The machinery already exists in the tree.** `DocxWriter.flowRow` (`:3591`) already emits exactly
   this: a paragraph indented to the first field's x with `<w:tabs>` at every later field's measured
   x (`:3805-3832`), gated on the paragraph having ≥2 boxes (`isRow` `:3570-3581`). The gap for
   `392` is that the two mono fields never become two boxes, because `PdfToWord.sameRow()`
   (`:5185`) requires a gap of `max(1.5f, size*0.15f)` at `:5225` and the mono pair is separated by
   one space. So the change is: **let `sameRow` admit a field separated by a single mono space, and
   `flowRow` pins it.** One threshold, plus reusing the emission that is already there.

4. **It carries none of the cost that killed the previous attempt.** The 21 Nov run tried a font
   *rename* (`DejaVuSansMono → Courier New`) and `regress.py --check` refused it, correctly: the
   0.325% narrower advance accumulated to +1.30 on `392`'s `share5` and +0.60 on
   `406_passport_mrz_page`. A tab stop is absolute and does not move with the face, so the
   LibreOffice metric should not move at all — and `392` is a clean single-defect test for it
   (`margin_bad: []`, `indent_bad: [{page 1, unregistered 2, worst_pt 34.1}]`).

5. **It is on the critical path to more than its own two documents.** `18 + 47` = 7 clean
   documents; `47` alone = 2. It is the cheap half of the largest *reachable* pair.

**Why not `18_displacement` first, despite the bigger headline (18 instances, 5 sole).** It is the
larger prize and should be the very next class — but its cheap levers are exhausted and refuted
(spacer spend, guard relaxation, `w:trHeight hRule="exact"`, the 1×1 table, and the section
top-margin patch which is proven in Google and worth **zero** clean documents because all the
sole-`18` documents are single-page). What is left is the 0.75 pt row rung, and the note that
measured it ends: *"Do not implement it before that render exists"* (`FINDINGS/ROW-RUNG-26NOV.md`).
That is a hypothesis, not a lead. `47_margins` is a lead.

**Why not `60_text_column_right_edge` first, despite 20 documents and 5 sole.** All five sole
documents are DejaVu, and four separate measurements say no `.docx` construct can reach them —
including a probe that embedded the actual `DejaVuSans.ttf` / `DejaVuSerif.ttf` into the package and
got a byte-identical substitution back from Google (§C.1). Its 10.08 leverage is the largest single
number in the store and 5 of it is unreachable.

**Falsifier for the recommendation, stated so it can fail fast:** convert `392` and `380` with the
`sameRow` threshold relaxed, and read `47_margins` in Google. If `392` does not pass, or if
`383_api_docs_page` and `360_restaurant_menu` move at all, the change is wrong. If `392`'s `share5`
moves off 1.61, the "tab is face-independent" premise is wrong and the class is parked.

---

## C. Checks failing because the instrument is wrong, not the converter

### C.1 `60_text_column_right_edge` — 5 of its 20 documents are a renderer limit, not a defect

All five sole-`60` documents are the DejaVu set, and the converter is *right* on them:

| document | LibreOffice | Google |
|:--|:--|:--|
| `302_radiology_report` | **42/42 PASS** | 41/42, fails 60 |
| `313_power_of_attorney` | **42/42 PASS** | 41/42, fails 60 |
| `316_contract_with_schedules` | **42/42 PASS** | 46/47, fails 60 |
| `321_auditors_report` | **42/42 PASS** | 41/42, fails 60 |

The measurement: `302`'s `.docx` declares `w:ascii="DejaVuSans"` (27 runs) / `DejaVuSerif` (6 runs).
LibreOffice has DejaVu and renders the source's first line to 0.2 pt (257.41 vs 257.62). **Google has
no DejaVu**, substitutes a face **+4.8% wider** (270.00 pt), which re-breaks page 0 from 33 lines to
35 and moves a column right edge by up to **28.6 pt**. `60`'s slack is *one word of the column's own
text*, and a wider face widens the word too — so the slack **grows with the fault instead of
absorbing it**. That is an instrument that cannot pass the document by construction.

Three attempts to fix it converter-side are all measured and all fail:
* rename to a face Google has → LibreOffice has no Verdana either, substitutes Noto, render is
  **11.6% narrower** than the source;
* embed the real DejaVu faces in the package → Google's export is the **same render** (same three
  substituted families, same 35 lines, same 270.00 pt; the exported PDF differs by 5 bytes of
  container metadata);
* `79_inr_indian_digit_grouping_table`, the one document in the five whose faces Google *does* have,
  is also the one that fails in LibreOffice — so it is the engine's, and it is not one of the five.

Source: `FINDINGS/60_text_column_right_edge-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md` §2-§4.

The honest close is an **attribution**, not a loosening: a rule about extent-versus-substitution —
a column whose re-break is fully explained by a face the renderer does not have is not a
displacement — re-measured on the whole class, not on these four documents in isolation. Worth
**5 clean documents**, the largest instrument-correctable prize in the store.

### C.2 `59_shape_anchor` — the check never compares position

`verify_google.py:2426-2450`, `_box_moved()`, is a **size-class count**:
`return _class_count(a, gshapes) >= _class_count(a, sshapes)` where `_class_count` is at `:2420`.
It asks "does the page still have as many boxes of this size?" and **never asks where they are**.
A box that keeps its size and slides 40 pt reads as *not moved*. Adding the position term was
measured to turn `_box_moved` **True → False on all 332 real boxes** on the three sole-`59`
documents (`FINDINGS/18-60-59-THREE-CLASSES-ROOT-CAUSED-AND-THE-LEVER-THAT-CANNOT-REACH-1900-fixer.md`
§3). Verdict written at `verify_google.py:2585`.

**But its leverage today is zero**, and that is the thing to know before spending a run: there are
**0** sole-`59` documents in the current-engine store, so a perfect `59` cannot flip a single
document to clean. The same file that proposed it as "the single cheapest large move on the board,
worth 15.1 clean documents" was measured against the 190-document mixed-engine store. On the 61
rows that describe this engine it is worth **3.50 clean documents of partial progress and 0 flips.**
The later, first-hand note `FINDINGS/59-shape-anchor-IS-NOT-ITS-OWN-CONSTRUCT-26NOV-relay.md` reaches
the same conclusion: on 4 converted documents the `.docx` reproduces the source's drawings to within
0.75 pt, so the shape writer is not the defect. **Fix it as an instrument change, do not schedule it
as a fix.**

### C.3 `check_instances()` counts a refused document as a clean one

`report.py:551-579` adds `int(j.get("passed") or 0)` and `len(j.get("failed") or [])`. For
`Account_Opening_Form_Fillable_filled` both are absent (`status: page_count_refused`, `pages: 11`,
`want: 9`), so it contributes **0/0** and is counted as one of the "61 documents". The same file's
`google_fixed()` (`report.py:606-611`) deliberately counts refused documents as defects and says so
in a comment. Two functions in one report disagree about the same row. Effect on the 113: none — but
the denominator is "60 scored", not 61, and the document that Google reflowed from 9 pages to 11 is
invisible in the row that a reader trusts first.

### C.4 `classpick.py --leverage` does not filter by engine

`classpick.py:214-267` reads every `benchmarks/gverify/*.json` with no engine check. Its table
therefore mixes 61 rows of `a4d8fca4`, 147 of `025fe9de` and 5 of `d85db0a9`. Consequence: it says
`18_displacement` is worth **52.2** clean documents and `60_text_column_right_edge` **24.0**; on the
current engine the same two are **9.31** and **10.08**. The ordering it prints (18 first) is not the
ordering of the code in the tree (60 first, and 5 of those unreachable). This is the same class of
fault `report.py`'s own `engine_now()` docstring (`:487-528`) was written to end, one tool further
out.

### C.5 Candidate, not established: `17_matched_runs` on `391_survey_questionnaire_grid`

It fails with 17 runs matched, `worst_dy 2.6`, `med_dy -1.3`, `bad_pages []`, and LibreOffice
`worst_dy 0.44` (`benchmarks/DISP-TABLE.csv`). A document that is essentially perfect in both
geometry records and fails a *matching count* is the shape of an instrument asymmetry — the verdict
is `matched >= ceil(0.9·len(s_runs))` (`verify_google.py:5799`), so one render-side split of one
source run into two pieces that the matcher will not re-pair costs the document. **I could not
establish this without the source PDF and the Google export**, and no finding in `FINDINGS/` names a
mechanism for this document. Listed as a candidate only.

---

## D. What could not be established without the compiled engine

* **Which of the other 15 `60`-failing documents are DejaVu.** Only `302`, `313`, `316`, `321` are
  established (`...-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md` §2) and `335` is asserted in
  `LAST-MESSAGE.md`. The declared faces of the other 15 are **not stated** in any committed artefact;
  reading them needs the emitted `.docx`, which this clone does not carry.
* **Whether the 0.75 pt row-rung lever actually moves any of the five sole-`18` documents.** The
  attribution is committed (`benchmarks/DISP-TABLE.csv`: `16` 13 rows @ 19.0 pt, `362` 29 rows @
  8.4 pt, `36` 7 rows @ 20.0 pt, `402` 6 rows @ 62.0 pt, all `table-row`), but the effect needs a
  Google render of a patched build.
* **The per-document verdict for 152 of the 213 corpus documents** on this engine.
* **Whether `47_margins` clears on `383_api_docs_page` and `360_restaurant_menu`** under the tab
  construct — `360`'s failure is a different mechanism entirely (a table cell selling its inset to
  buy a line, `FINDINGS/47_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md`) and is not reachable by
  this change.
* **Any `share5` / LibreOffice consequence of any change.** `measure_gate.py` and `regress.py
  --check` both need the corpus built; that needs the JDK and a compile, which was out of scope.
