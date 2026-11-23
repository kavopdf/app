# `60_text_column_right_edge` + `59_shape_anchor` — one construct or two?

Run B1, 2026-11-23 13:34 IST. Repo `kavopdf/app` @ depth-1 clone, HEAD as cloned.
Google Docs is truth; nothing here was verified through Google (no corpus, no JDK, no renderer on this pod).

---

## 1. VERDICT: TWO constructs, not one

They are two different questions that happen to fire on the same documents.

| | what the check asks | where |
|---|---|---|
| `60_text_column_right_edge` | Does the render's **text column end where the source's did**? Reads only the text layer: lines grouped into columns by left edge, each column's right edge = its **widest line**; fails if the render's widest line is >`RIGHT_OVERRUN` (6.0 pt) + one word past the source's, or >`RIGHT_UNDERRUN` (8.0 pt) + one word short. | `tools/p2w-bench/verify_google.py:2597-2673` (`BAND`/`RIGHT_OVERRUN`/`RIGHT_UNDERRUN`/`SLACK_CAP` at `:2538-2543`, `edge()` at `:2597`) |
| `59_shape_anchor` | Does the text **sit at the same place inside its enclosing drawn rectangle**? For each source run enclosed by a shape, compares `dx`/`dy` of the text's offset from its box's own corner (`:2398-2415`), convicting only when the two boxes are the same object (`_same_box`, `:2254`) or when the source's box is provably reproduced elsewhere (`_box_moved`, `:2313`). | `tools/p2w-bench/verify_google.py:2216-2472` |

60 never looks at a shape; 59 never looks at a column edge. A document can fail either alone — and does:
56 documents fail 60, 45 fail 59, only **16 fail both** (measured over the 190 `ok` rows in
`benchmarks/gverify/`). The "travel together" is not a shared cause, it is a shared **document
population**: both checks fire on documents whose text the writer puts in an **anchored text box**
instead of the flow (forms, tables, bills of lading, air waybills, fact sheets). One writer decision,
two independent consequences, two independent verdicts.

---

## 2. What in the .docx writer emits the offending width

The anchored text box. `DocxWriter.anchorBox()` writes one text box per line it cannot put in the flow,
and it does **not** size the box to the page's line — it inflates it:

    app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:2793
        float wPt = Math.max(4f, advance) * 1.12f + b.size * 1.5f;

and the same expression a second time, on the rotated/stamp path, at

    DocxWriter.java:3138
        : Math.max(4f, advance) * 1.12f + b.size * 1.5f;

`advance` is `b.right - b.x`, the source line's own advance. So for a line of advance **A** at font size
**s**, the emitted box is

    box_width = 1.12·A + 1.5·s        i.e.   A + (0.12·A + 1.5·s)

The box's left inset is 0 (`bodyPr lIns="0"`, `DocxWriter.java:5625-5630`), the box is anchored at
`b.x` on the page, and `wrap="none"` is written — but `wrap="none"` is **measured dead**: LibreOffice
7.4.7.2 wraps at the box width regardless (`tools/p2w-bench/FINDINGS/content-missing-partly-replaced-B-1300.md`,
variants V0 vs V2: byte-identical line breaks). **The width we emit IS the width the text gets.**

That single number explains both failures:

* **60 — overrun.** The box gives the line `0.12·A + 1.5·s` more room than the page gave it, so a
  re-break pulls the next word (or three) up onto the widest line, and that line's right edge lands
  past the source's column edge. Measured arithmetic: over 647 source body lines wider than 125 pt in
  the five corpus PDFs shipped in the repo, the median excess is **+51.2 pt**, and **568 of 647** exceed
  60's own overrun budget of `6.0 + one word (median 24.0 pt) = 30 pt`. (The check's slack is measured
  per column in `edge()`, p50 = 24.0 pt.)
* **59 — anchor.** The render's enclosing rectangle is no longer the source's rectangle: it is wider
  by the same `0.12·A + 1.5·s`, against `ANCHOR_RECT_TOL = 2.0 pt` (`verify_google.py:2217`). A form
  field box drawn 9.0 pt wide is emitted 21.1 pt wide — measured on
  `benchmarks/corpus-extra/601_fillable_admission_form.pdf` (a document that fails 59), the emitted
  width is **+12.1 pt** off the page's own box. `_same_box` therefore fails on essentially every
  anchored line, and the run is decided by `_box_moved` instead — see §3.

Secondary width site, same family, not the offender here: `sectPrXml` writes
`w:pgMar ... w:right="0"` (`DocxWriter.java:2391`) and `flowFromBox` writes
`w:ind ... w:right="0"` for a left-aligned line (`DocxWriter.java:3724-3725`), so a flowed paragraph's
text area is the whole paper. **That lever is already refuted for 60 — see §3.**

---

## 3. Already measured / already refuted — do not redo

1. **Right indent from the source margin is REFUTED for 60.** `patches/right-margin-from-source.patch`
   was built, converted, rendered and measured on all 211: `47_margins` 82 → 82 (no movement at all),
   total passes **fall by 11**, 7 documents worse, 1 better, and **`60` 43 → 45** — i.e. it makes 60
   *worse*. Recorded in `tools/p2w-bench/REMAINING-DEFECTS.md:197` and
   `patches/README-2026-11-13.md` §"right-margin-from-source.patch". Do not retry it for 60.
   (The mechanism claim in that README — a docx built with `w:ind right=0` rendered at x1 = 591.2
   against a 539 pt column — is real, but the lever does not move the check.)
2. **59's live defect is in the CHECK, not the writer.** `REMAINING-DEFECTS.md:199`: `_box_moved()`
   asks only whether a shape of the source box's **size** exists anywhere on the page, never whether
   it is **where the source put it** — so **992 runs on 42 documents are charged `moved` with the box
   present within 2 pt on all four edges.** Code confirms it: `_box_moved`
   (`verify_google.py:2313-2338`) reduces to `_class_count(a, gshapes) >= _class_count(a, sshapes)`,
   a size-class population count with no position term. A uniform table is nothing but shapes of one
   size, so every cell run passes that test. Measured illustration: on
   `601_fillable_admission_form.pdf` page 1, **11 of 11** qualifying shapes sit in a size class with
   ≥2 members — `_box_moved` is trivially true there.
3. **59 on the stamp documents has a separate, proven cause** — `PdfToWord.java:4231`
   `if (ctmRotated()) return;` drops every preset shape under a rotated CTM (`ctmRotated()` at
   `:4153` is true for 90° and 180°, not just 15°). `patches/README-2026-11-13.md`, §"rotated-shape-dropped".
   That is the 01–15 stamp population, not the 16 co-travelling documents.

---

## 4. Documents affected

Measured directly from `benchmarks/gverify/*.json` (190 `ok` rows; 23 `page_count_refused` rows carry
no `failed` list and are not counted).

* fails `60`: **56** · fails `59`: **45** · fails **both**: **16**
  (matches `benchmarks/DEFECT-CLASSES-GOOGLE.md`: 60 → 56 Google / 18 LibreOffice; 59 → 45 / 9.
  Both are overwhelmingly **Google-only** failures — the construct survives LibreOffice, which is why
  a LibreOffice-only pass has been hiding them.)

**Would go CLEAN (all 42 checks) if 60 alone were fixed — 4 documents**
`302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report`
(all: `failed == ["60_text_column_right_edge"]`).

**Would go CLEAN if 59 alone were fixed — 2 documents**
`48_form_coloured_border_coloured_values`, `52_one_cm_margin_wide_body`.

**Would go CLEAN if both were fixed — 1 document**
`393_spectrum_peak_table` (`59` + `60` only).

**Total prize: 7 documents**, not the 16.9 + 11.5 the request cites — those figures are a weighted
leverage score, not a document count; the raw count of documents that become clean is 7.

The 16 co-travelling documents, with their full failure sets (nothing else here becomes clean on this
fix alone):

| document | fails | failed set |
|---|---:|---|
| 393_spectrum_peak_table | 2 | 59, 60 |
| 340_bill_of_lading | 3 | 18, 59, 60 |
| 343_air_waybill | 3 | 18, 59, 60 |
| 56_table_indented_from_margin | 3 | 18, 59, 60 |
| 373_leave_application_form | 4 | 18, 23_line_pitch, 59, 60 |
| 79_inr_indian_digit_grouping_table | 5 | 05, 18, 32, 59, 60 |
| salary-slip-factory-wages | 5 | 05, 18, 32, 59, 60 |
| 28_value_overflows_cell_txtpos | 6 | 04, 43, 45, 47, 59, 60 |
| 344_customs_declaration | 6 | 04, 13, 18, 25, 59, 60 |
| 371_experience_certificate | 6 | 04, 13, 17, 45, 59, 60 |
| 383_api_docs_page | 7 | 04, 18, 25, 47, 59, 60, 66 |
| 65_two_col_full_width_figure_caption | 7 | 04, 13, 17, 44, 45, 59, 60 |
| 77_arabic_rtl_document | 7 | 17, 18, 26, 43, 47, 59, 60 |
| 318_court_summons_form | 8 | 04, 13, 17, 43, 45, 47, 59, 60 |
| 322_mutual_fund_factsheet | 10 | 04, 13, 17, 18, 25, 26, 44, 45, 59, 60 |
| policy-2col-spanning-section-heading | 10 | 04, 05, 10, 13, 17, 32, 44, 45, 59, 60 |

---

## 5. Proposed minimal change (two changes, one per construct — they are not one fix)

**A. For 59 — repair the instrument, not the writer (highest value per line changed).**
`verify_google.py:2313-2338`, `_box_moved()`: require the surviving same-size shape to be **at the
source rectangle's own position**, which is what the check's own docstring says the defect is ("text
where it was, box somewhere else"):

    def _box_moved(a, gshapes, sshapes):
        here = sum(1 for s in gshapes
                   if abs(s.width - a.width) <= ANCHOR_RECT_TOL
                   and abs(s.height - a.height) <= ANCHOR_RECT_TOL
                   and abs(s.x - a.x) <= ANCHOR_RECT_TOL and abs(s.y - a.y) <= ANCHOR_RECT_TOL)
        if here: return False                       # the box is still where the page put it
        return _class_count(a, gshapes) >= _class_count(a, sshapes)

This is a **tightening** of the check (it makes the conviction harder, on the check's own stated
definition), not a loosening — it can only convert `moved` charges into `anchored`/`unjudged`. It
should retire the 992 false `moved` runs on 42 documents named in `REMAINING-DEFECTS.md:199`, and with
them the 2 solo documents (`48_…`, `52_…`) plus `393`'s 59. **Accept on:** those documents' `59`
flips and *no* document gains a new failure; `59`'s count must not rise on any of the 190.

**B. For 60 — size the anchored box to the page, not to 112 % of it.**
`DocxWriter.java:2793` and `:3138`. The 12 % + 1.5 em inflation was added to stop a substitute face
wrapping and clipping the last word (the comment at `:3116-3125` records that reason: file 69's
"8. The job worker…" became "8. " in a 19 pt box). The inflation buys clipping insurance and pays
for it in overrun — and overrun is exactly what 60 charges. The narrow proposal: keep the anti-clip
floor but bound the width by the page's own line box, e.g.

    float wPt = Math.max(Math.max(4f, advance) * 1.12f, advance + 0.5f * b.size);
    // and never wider than the source line's own drawn box, where the page drew one

i.e. 1.12·A + 1.5·s → A + 0.5·s. On the same 647 wide lines the emitted excess over the advance
falls from a median **+51.2 pt** to **+3.2 pt** (0.5·s, s ≈ 6.4 pt median on these lines), which puts
**0 of 647** over 60's 30 pt budget instead of **568 of 647**. **Accept on:** `60` count falls on the 56, `04_chars_missing`
and `17_matched_runs` do not rise (the anti-clip reason is real — check file 69 and
`69_two_col_legal_numbered_clauses` explicitly), and no document regresses.

---

## 6. What was MEASURED and what was only INFERRED

**MEASURED (script, this run):**
* the 56 / 45 / 16 split, the 4 + 2 + 1 = 7 clean-on-fix document list, and the 16-document table —
  computed from `benchmarks/gverify/*.json`.
* the writer's emitted width and its excess: 2,545 box-enclosed lines and 647 wide (>125 pt) lines
  across the five corpus PDFs in the repo (`benchmarks/corpus-extra/*`, `benchmarks/realworld/*`),
  via PyMuPDF. Median excess **+14.9 pt** on all box-enclosed lines, **+51.2 pt** on wide ones;
  568/647 over 60's 30 pt budget. `601_fillable_admission_form`: source box 9.0 pt → emitted 21.1 pt.
* `_box_moved` reduces to a size-class count with no position term (read at `:2313-2338`); 11 of 11
  qualifying shapes on 601 page 1 sit in a size class with ≥2 members.
* the check constants (`RIGHT_OVERRUN` 6.0, `RIGHT_UNDERRUN` 8.0, `ANCHOR_TOL_PT` 3.0,
  `ANCHOR_RECT_TOL` 2.0, `ANCHOR_WIDTH_TOL` 1.5, `SLACK_CAP` 40.0) read from source.

**INFERRED, NOT MEASURED (no renderer available on this pod):**
* that a re-wrapped line in a 112 %-wide box actually lands past the source's column edge **in Google
  Docs**. The arithmetic says the budget is exceeded; the render is not in hand.
* the before/after of proposal A and proposal B. `verify-change.py` and `measure_gate.py` were **not
  run**: they need `/scratch/work/p2w/corpus` (fetched by `corpus-fetch.sh` from four release assets)
  plus a built engine (`build-engine.sh` fetches a JDK), and there is no JDK and no corpus on this pod.
  Neither was attempted past inspection — reporting a number I did not get would be worse than
  reporting none.
* the two proposals are therefore **proposals, not passes**, which is what the charter asks for a
  change that has not been measured.

---

## 7. One-line answer

Two constructs. 60 is a text-layer column-edge question; 59 is a text-inside-its-rectangle question.
They co-travel because both fire on the documents whose lines the writer puts in an **anchored text
box** — and the box is emitted **`0.12·A + 1.5·s` wider than the page's line**
(`DocxWriter.java:2793`, repeated at `:3138`), which is simultaneously the overrun 60 charges and the
box mismatch 59 can only convict through `_box_moved`, itself a size-only test
(`verify_google.py:2313`). Fixing 59 properly means fixing that test; fixing 60 means sizing the box
to the page. Neither is the right-indent lever — that one is already measured and refuted.
