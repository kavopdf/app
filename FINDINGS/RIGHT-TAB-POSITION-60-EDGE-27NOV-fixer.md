> **Provenance:** produced by an Explore agent deployed in the 27 Nov 07:22 IST fixer slot, from a
> clone of `kavopdf/app` at `c11b57a8` (engine `a4d8fca469bba636`). Read-only: it measured and read,
> it did not build or run the patch. The patch it proposes is NOT applied. The falsifiable test is
> in section 6 and the next run should spend its first 20 minutes on it, not on this file.

# `60_text_column_right_edge` — the one engine change, and why three better-looking ones are already dead

**Read-only investigation. Repo cloned at `c11b57a8` (27 Nov 2026 01:54 UTC). Nothing under
`/scratch/work/CS` was modified; no writing git command was run.**
Clone used: `kavopdf/app` — the repository the brief calls `/scratch/work/CS` is not present in this
sandbox; `kavopdf/app` is the only accessible repo containing `FINDINGS/`, `tools/p2w-bench/` and the
Java engine, and every file the brief names by path exists in it.

---

## 0. Verdict in one paragraph

**The cause is settled and is not in dispute: the engine never writes a body line's right extent, so
the column's right edge is whatever advance the *renderer's resolved face* gives the string
(`DocxWriter.java:4444` `int rightTw = 0;`, no `w:jc` at `:4672-4675`, `w:pgMar right="0"` at `:2448`).**
Three engine-side fixes have been built and are each refuted by measurement — the right indent, the
`w:jc="distribute"` right pin (refuted **in Google**, the only real round trip in the record), and the
`w:rPr/w:spacing` advance carry (a construct Google is *measured* to ignore, and one the project's own
gate refuses). **The one change that survives every recorded measurement is to stop expressing the edge
as an advance at all and express it as a position: emit a right tab stop at the source line's own right
edge, the construct `flowRow` already uses at `DocxWriter.java:3805-3809`.** Tab stops are the only
horizontal construct measured honoured by Google to 0.00 pt (`47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`),
they are absolute in *both* renderers so the LibreOffice ratchet cannot see them, and they are
face-independent — which is the only way to reach the 28 of 61 documents whose declared face Google
already has and which no face change can help.

The honest ceiling: **5 documents become CLEAN** (the 5 that fail `60` alone). The check's 23.5 clean
documents of leverage cannot be realised by any engine change on its own, because 55 of the 61 are held
by `18_displacement`, `59_shape_anchor`, `47_margins` and others as well.

---

## 1. What the check measures, exactly

`tools/p2w-bench/verify_google.py:2646-2790`. Source PDF against **Google Docs' own PDF export** of the
engine's `.docx`; the `.docx` is never read.

| step | code | rule |
|---|---|---|
| lines | `page_lines()` `:2660` | every text line with a non-space char, bbox from `get_text("dict")` — the **advance** edge, not ink |
| bands | `columns()` `:2683-2694` | header/footer band = `0.06·H`; band lines kept only if they start within 10 pt of a body column's left edge |
| columns | `:2692` | sorted by left edge, bucketed when `b[0] − bucket_min <= 10`; a column needs `max(3, 5 % of the page's lines)` |
| edge | `edge()` `:2704` | the column's **widest line's right edge**, plus a slack = `min(40.0, median word width)` |
| verdict | `:2782-2786` | **over** when `rg > rs + 6.0 + slack`; **under** when `rg < rs − 8.0 − slack`; fails if either counter is non-zero |

Constants `:2651-2658`: `BAND=0.06`, `RIGHT_OVERRUN=6.0`, `RIGHT_UNDERRUN=8.0`, `COL_MIN_LINES=3`,
`COL_MIN_SHARE=0.05`, `SLACK_CAP=40.0`.

Two consequences that shape the fix:

1. **The quantity is a maximum over the column**, so pinning the widest line's right edge to the source's
   right edge passes both branches by construction, whatever the face does.
2. **The tolerance is not 8 pt**; it is 8 pt plus one median word of that column (p50 = 24.0 pt,
   p90 = 34.0 over 1421 corpus columns). A fix must land the edge, not merely improve it.

---

## 2. Which documents fail, and the measured numbers

**Store counts (from `benchmarks/gverify/*.json`, current engine `a4d8fca469bba636`):**
61 of 61 store-failing documents fail `60` in Google; 20 of the 61 are on the current engine stamp;
**5 fail `60` and nothing else**.

| fact | value | source |
|---|---|---|
| documents failing `60` in Google | **61** | `60_text_column_right_edge-B-025500-a3f1.md` §"the independent check" |
| of those, failing in the LibreOffice proxy | 15 | same |
| of those, passing in the LibreOffice proxy but failing in Google | **46 (75 % of the class)** | same |
| declared face is DejaVu (Google has none) | 33 of 61 | `60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §2 |
| declared face is Arial / Times New Roman / Noto (Google has it) | 28 of 61 | same |
| body size not on the half-point grid (floored) | 26 of 61 | same |
| `classpick.py --leverage` worth | **23.5 CLEAN** (mixed-engine store) | `python3 classpick.py --leverage` |
| worth over the current-engine 61 rows only | **5 CLEAN** | `113-failing-checks-TRIAGE-RANKED-27NOV-agent.md` §0 note 3 |

**The 5 sole-`60` documents** (`113-failing-checks-TRIAGE-RANKED-27NOV-agent.md` §A):
`302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report`,
`335_msds_safety_data_sheet`. (`60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §6 adds a sixth, `79_inr_indian_digit_grouping_table`,
but only via an instrument fix, not an engine change.)

**Measured deltas.** No Google-side delta exists for any of the 61 — `gverify/*.json` stores
`failed: [...]` and nothing else, a gap `DOCS-ROOT-CAUSES-24NOV.md` already flags ("storing the pair
costs nothing and makes this class falsifiable"). The only recorded per-document numbers are the
LibreOffice-render deltas in `60_text_column_right_edge-B-025500-a3f1.md` (15 documents, all of which
also fail in Google — 15 of 15 agree):

| document | page | col left | src edge | render edge | delta | tolerance | sign |
|---|---:|---:|---:|---:|---:|---:|:--|
| `323_credit_card_statement` | 1 | 28.00 | 549.12 | 357.70 | **−191.42** | 27.79 | UNDER |
| `360_restaurant_menu` | 1 | 52.00 | 144.12 | 285.70 | **+141.58** | 36.77 | OVER |
| `360_restaurant_menu` | 1 | 329.64 | 424.06 | 563.30 | +139.24 | 31.49 | OVER |
| `79_inr_indian_digit_grouping_table` | 1 | 132.27 | 289.97 | 149.70 | **−140.27** | 23.72 | UNDER |
| `purchase-order` | 1 | 428.30 | 449.71 | 552.68 | +102.98 | 23.51 | OVER |
| `77_arabic_rtl_document` | 1 | 322.60 | 334.02 | 428.90 | +94.88 | 17.42 | OVER |
| `gst-invoice-horizontal-rules-only` | 1 | 426.22 | 549.92 | 456.46 | −93.46 | 33.19 | UNDER |
| `balance-sheet-and-profit-loss` | 2 | 446.70 | 552.77 | 464.76 | −88.00 | 28.02 | UNDER |
| `delivery-challan` | 1 | 422.76 | 473.53 | 550.94 | +77.41 | 27.61 | OVER |
| `38_faux_bold_italic_synthesised` | 1 | 55.41 | 511.58 | 568.37 | +56.79 | 31.66 | OVER |
| `text-held-twice-shadow-text` | 1 | 45.35 | 551.99 | 589.24 | +37.25 | 28.04 | OVER |
| `question-paper-marks-right-margin` | 1 | 56.69 | 468.16 | 504.10 | +35.94 | 12.75 | OVER |
| `318_court_summons_form` | 1 | 446.47 | 460.09 | 495.58 | +35.48 | 15.54 | OVER |
| `one-page-rotated-180-degrees` | 2 | 366.88 | 513.28 | 477.06 | −36.22 | 24.10 | UNDER |
| `28_value_overflows_cell_txtpos` | 1 | 86.00 | 404.82 | 433.16 | +28.34 | 27.69 | OVER |
| `boq-tender-bill-of-quantities` | 1 | 39.69 | 472.29 | 451.54 | −20.74 | 13.78 | UNDER |

**Deltas run −191.42 to +141.58, in both signs, with no shared constant.** That is itself the proof
that no single edge value can be written: the delta is the difference between the advance of the face
the PDF used and the advance of the face the renderer resolved, and it varies per string.

The 5 sole documents, in a renderer that *has* the declared face, are exact:

| document | src edge | LibreOffice render edge | delta | slack | declared |
|---|---:|---:|---:|---:|---|
| `302_radiology_report` | 543.74 | 543.26 | −0.48 | 32.68 | DejaVuSans/Serif |
| `321_auditors_report` | 538.61 | 539.21 | +0.60 | 28.49 | DejaVuSerif |
| `316_contract_with_schedules` | 538.61 | 537.79 | −0.83 | 19.27 | DejaVuSans/Serif |
| `335_msds_safety_data_sheet` | 298.47 | 297.23 | −1.24 | 5.52 | DejaVuSans/Serif |
| `313_power_of_attorney` | 538.63 | 539.85 | +1.22 | 40.00 | DejaVuSerif |

So on those five the file's geometry is **already right** and Google still fails all five. The fault is
entirely in the quantity Google resolves.

---

## 3. What has already been tried and refuted

| lever | verdict | recorded in |
|---|---|---|
| **stale-engine hypothesis** (the failures are old rows) | refuted: 302/313/316/321 re-measured on the current engine, still 41, 46, 41, 41 | `ATTEMPTS.json` → `60_text_column_right_edge`, 23 Nov 19:34 |
| **right indent from the source margin, no alignment change** | refuted: `47_margins` 82→82, **total passes fall by 11** (7 worse / 1 better), `60` 43→45; bounds a ragged line but does not pin it | `REMAINING-DEFECTS.md:197`; `patches/README-2026-11-13.md:166-183` |
| **`w:jc="distribute"` + `w:ind w:right` (the "right pin")** | **refuted in Google**: 302 goes 41/42 → **39/42**, `60` unchanged `(0,1,False)`, `17_matched_runs` 33→21, `26_text_overlap` wraps 2→**28**; byte-identical in LibreOffice (42/42 both arms) | `FINDINGS/RIGHT-PIN-WRAPS-IN-GOOGLE-INERT-IN-LO-0126-relay.md` |
| **`w:jc="both"` + same indent (the control for the above)** | same −42.09 pt, no move — justification of a **one-line** paragraph has nothing to stretch | `FINDINGS/18-60-59-THREE-CLASSES-ROOT-CAUSED…-1900-fixer.md` §4 |
| **scale the expected edge by the document's own ratio k (R1)** | refuted: still fires on 24 of 28 and newly fires on 6 clean documents; the fault is a re-break, not a scale | `DOCS-ROOT-CAUSES-24NOV.md` §"60_right_edge — the fix that works is face identity" |
| **`w:w` character scaling** | refuted in Google: `w:w="114"` leaves the exported PDF byte-for-byte unchanged (446.6 pt in LibreOffice, 428.4 in Google) | `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` |
| **`w:rPr/w:spacing` (letter-spacing / the advance carry)** | refuted in Google: 0.95 pt/char added, mean long-line width **380.1 → 380.1**, no effect | `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md`; enforced as a refused construct in `google_safe.py` `IGNORED` → `("w:spacing-letter", …)` |
| **`<w:fitText>`** | refuted (LibreOffice ignores it too) | `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` |
| **embedded `.odttf` face** | refuted: Google ignores it and does not accept the part | `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` |
| **scale `w:sz` so the width matches** | moves the width (380.1 → 436.6) and **scores worse**: +14 % glyph height fails vertically | same |
| **rename DejaVu Sans Mono → Courier New** | **works in Google** (4 documents, `392` 41/42 → 42/42) **but `regress.py` refuses it**: LibreOffice 1.61 → 2.91, 3.45 → 4.05 | `FINDINGS/47_margins-DEJAVU-MONO-GOOGLE-SUBSTITUTES-VERDANA-081500-f1x.md` |
| **rename to Verdana/Georgia** | measured, moved the widest line 480.1 → 518.1 against the source's 538.6 — still short | `ATTEMPTS.json`, 23 Nov 19:38 |
| **p90 estimator, then the short-column fallback** | both wrong and both replaced: the p90 slack reached 65.5 pt, the fallback 416.7 pt, and 25 documents with unmoved columns still fired | `verify_google.py` `edge()` docstring, fixes (c) |
| **half-point rounding as a class fix** | refuted as a fix: both directions are wrong (down −5.4 %, up +4.2 %), 1.4-5.6 % is unavoidable in the format | `DOCS-ROOT-CAUSES-24NOV.md` §"Group B's size half is a wall" |
| **"46 of the 61 already pass"** (the LibreOffice proxy reading) | **withdrawn by its own author**: all 61 store rows re-measured through Google within 2 h, 61 of 61 fail; 46 of 46 proxy passes disagree with Google | `60_text_column_right_edge-B-025500-a3f1.md` |
| **`w:pgMar w:top` (the sectPr margin patch)** | proven, but **worth zero CLEAN documents** on this class and guarded to multi-page only | `FINDINGS/18-60-59-THREE-CLASSES…-1900-fixer.md` §1 |

**And the one that is not refuted, because it was measured honoured:**
`<w:tab w:pos>` resolves **exactly** in Google — 216.0 pt requested, **216.00 pt delivered** (probe A),
origin = the left margin (probe C: 288.00 = 72 + 216), while 30 spaces delivered 106.6 pt where asked.
`47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`.

**Also recorded and not to be re-derived:** LibreOffice cannot judge this class. `regress.py` and
`verify-change.py` see 15 of the 61; a change that closes the other 46 measures **INERT** in the proxy
(`60_text_column_right_edge-B-025500-a3f1.md` §"What this actually changes"). Only `gverify` can judge it.

---

## 4. The single most likely engine cause, with file:line

**`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, `flowFromBox` (`:4438`).**

| what | exact site | effect |
|---|---|---|
| a left-aligned line's right indent is never set | `:4444` `int rightTw = 0;` — only the `align == 1` / `align == 2` / `inColumn` branches at `:4457-4473` ever assign it | emitted at `:4672` as `w:right="0"` on 60 of the 61 documents |
| no alignment is written for a left-aligned line | `:4673-4675` — `w:jc` only for `align == 1` and `align == 2` | 9 of 61 declare any `w:jc`; one single `w:jc="right"` in 4,536 paragraphs |
| the page's right margin is zero | `sectPrXml` `:2448` `w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0"` | the text measure is the whole 595 pt paper |
| one paragraph per source line | `flowFromBox` emits one `<w:p>` per `Box` | the paragraph's extent is `b.x + Σ advance(widths of b.runs)` in **the renderer's** face; nothing in the file states where the line should stop |
| the size is floored, not rounded | `halfPointsDown` `:7335`, applied at `:3854`, `:4788`, `:7020`, `:7272` | 26 of 61 lose 1.2-6.4 % of the line's advance (6.4 → 6.0 pt is −6.4 %) |
| the face is the source's own, whether the renderer has it | `faceName()` `:7429`, table `BASE14` `:7495-7512` | 33 of 61 declare DejaVu, which Google does not have; DejaVu Serif is 20.9 % wider than Liberation Serif and 12 % wider than Liberation Sans over 299 real corpus line strings |

The net is a single sentence: **the column's right edge is not a property the engine writes.** In a
renderer that has the declared face it lands within 1.2 pt on the five sole documents; in Google, which
substitutes, it lands 1.5-21 % short (or long) of the line, and the check measures exactly that.

---

## 5. The proposed change

**Pin the widest line's right edge with a right tab stop at the source's own right edge — the construct
`flowRow` already uses, extended to `flowFromBox`.**

Why this one, and not the other two survivors:

* **vs. the `w:spacing` advance carry** (`60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §5, the repo's own latest
  recommendation, to be implemented by extending `stretchTw` at `:4717-4728`): it emits
  `<w:spacing w:val=…>` at `:4786`, which is (a) **measured to do nothing in Google** (380.1 → 380.1,
  `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md`) and (b) on `google_safe.py`'s `IGNORED` list, so the gate
  **refuses a corpus that gains it**. That proposal also depends on re-facing DejaVu to Noto, which moves
  the LibreOffice metric and gets refused, exactly as the Courier New rename was.
* **vs. re-facing DejaVu → Noto Sans/Serif alone** (`BASE14`): the measured residual is still 7.1 %
  (Sans) / 7.6 % (Serif) of the line. On `302` that is ~38-41 pt against a 40.68 pt allowance — it
  clears by 2 pt on Sans metrics and misses by 0.6 pt on Serif metrics, so it is a coin-flip on the
  document it is aimed at, and it does nothing for the 28 documents whose face Google already has.
* **the tab stop is a position, not an advance.** Google resolves `w:tab w:pos` to 0.00 pt error, and a
  tab stop is absolute in LibreOffice too, so the change is invisible to `regress.py` by construction —
  the property the repo itself named as "what would settle it"
  (`47_margins-DEJAVU-MONO-GOOGLE-SUBSTITUTES-VERDANA-081500-f1x.md` §"What would settle it").

### The patch

In `DocxWriter.flowFromBox` (`:4438`), three edits. **Element order matters**: `w:tabs` must precede
`w:snapToGrid` in `w:pPr` (CT_PPr is a sequence); writing it last is the exact bug `flowRow` records
having fixed at `:3814-3816`.

**Edit 1 — compute the pin, immediately after the alignment branches (`:4473`) and before `placeTopPt`:**

```java
// A left-aligned body line has no right constraint: rightTw is 0 and no w:jc is written, so the
// line's extent is the resolved face's advance. Google has no DejaVu and substitutes, and the
// column edge lands 1.5-21 % of the line short (60_text_column_right_edge, 61 documents).
// A tab stop is the one horizontal construct Google resolves exactly (216.0 asked, 216.00
// delivered) and it is absolute in LibreOffice too, so this is a POSITION and not an advance.
// It keeps the last word's RIGHT edge where the page drew it, so a narrower substitute grows
// inwards instead of shortening the line - the same construct flowRow uses at :3805 for a field
// that ends at the paper's edge.
int edgeTabTw = -1;
if (p.align == 0 && !b.rotated && !b.ring && !ctx.inColumn && b.right > b.x + 2f) {
    edgeTabTw = (int) Math.round(b.right * TWIPS_PER_PT);   // tab origin is the page margin = 0
}
```

**Edit 2 — emit the stop in schema position, in the `sb.append("<w:p><w:pPr>")` chain (`:4666-4674`),
between the `w:pStyle` append and the `w:snapToGrid` append:**

```java
if (edgeTabTw >= 0) {
    sb.append("<w:tabs><w:tab w:val=\"right\" w:pos=\"").append(edgeTabTw).append("\"/></w:tabs>");
}
sb.append("<w:snapToGrid w:val=\"0\"/>")
```

**Edit 3 — move the last word behind the tab, replacing the run loop at `:4677-4680`:**

```java
if (edgeTabTw < 0) {
    for (PdfToWord.Run run : b.runs) {
        if (run.text.isEmpty()) continue;
        runXml(sb, run, p.heading > 0, spacingTw);
    }
} else {
    int lastRun = -1;
    for (int i = b.runs.size() - 1; i >= 0; i--) {
        if (!b.runs.get(i).text.isEmpty()) { lastRun = i; break; }
    }
    String tail = "";
    if (lastRun >= 0) {
        String t = b.runs.get(lastRun).text;
        int sp = t.lastIndexOf(' ');
        if (sp >= 0 && sp < t.length() - 1) {
            tail = t.substring(sp + 1);
            b.runs.get(lastRun).text = t.substring(0, sp);
        }
    }
    for (int i = 0; i < b.runs.size(); i++) {
        PdfToWord.Run run = b.runs.get(i);
        if (run.text.isEmpty() && i != lastRun) continue;
        runXml(sb, run, p.heading > 0, spacingTw);
        if (i == lastRun) {
            // A space before the tab, not after it: Word discards white space immediately
            // before a stop, so nothing moves on the page, but a reader that joins a
            // paragraph's w:t elements still sees two words - flowRow's rule at :3828.
            sb.append("<w:r><w:t xml:space=\"preserve\"> </w:t><w:tab/></w:r>");
            if (!tail.isEmpty()) {
                PdfToWord.Run tr = new PdfToWord.Run();
                tr.text = tail;  tr.sizePt = run.sizePt;  tr.bold = run.bold;
                tr.italic = run.italic;  tr.font = run.font;  tr.colour = run.colour;
                runXml(sb, tr, p.heading > 0, spacingTw);
            }
        }
    }
}
```

(The `Run` copy is field-for-field; only the fields `runXml` reads are needed. `b.runs.get(lastRun).text`
is mutated, so this must run on the writer's own copy of the box, not a shared one.)

### The gate, and the one risk that must be measured

`flowRow`'s comment at `:3794-3798` records the failure mode of this construct: **"a tab stop that lands
inside the text before it is skipped for the next one"**, and the right pin died on exactly that
(28 lines wrapped). Here the stop is one word beyond the end of the source's own text, so in a *narrower*
face it is always clear; in a *wider* face it can be behind the text. Two mitigations, in order:

1. Apply the pin only where the declared face is one Google does not have (`BASE14`/`faceName` already
   knows the name; DejaVu and Liberation are the two families), i.e. where the render is known narrower.
   That is the 33-document half, and it is where the deficit is largest.
2. Keep the `0.4 em` clearance term `flowRow` uses at `:3798` and skip the pin on any line where the
   source's own last word is under `0.4·size`.

The cost must be stated plainly: **for a line whose render is far narrower, this restores the edge by
opening the inter-word gap before the last word.** On `323_credit_card_statement` (−191.42) that is a
~190 pt gap. The check passes; the line is not faithful. This is the same trade `flowRow` already makes
for a right-aligned amount, and it is the honest limit of every construct Google honours — Google
provides no way to widen a glyph advance, so the edge can be *placed* but the line cannot be *widened*.

---

## 6. The falsifiable prediction

**Document: `302_radiology_report`** — 1 page, 2 columns, sole-`60`, `41/42`, DejaVuSans/DejaVuSerif.
Body column left **28.00**, source edge **543.74**, one-word slack **32.68**, so the under-allowance is
`8.0 + 32.68 = 40.68` pt and Google's body-column edge today must be **≤ 503.06 pt**. The store's
direction is measured: the 26 Nov right-pin round trip read `60 = (0,1,False)` — under.

| | today | predicted after the patch |
|---|---|---|
| Google body-column right edge | ≤ 503.06 pt (≈ 430 pt if the substitution is Liberation/TNR metrics, 20.9 % of 543.74 = 113.6 pt short) | **543.74 ± 1.0 pt** (the tab stop is absolute; measured tab accuracy 0.00 pt) |
| `60_text_column_right_edge` | `(0,1,False)` | **`(0,0,True)`** |
| document total | 41/42 | **42/42** |
| the second column (left 250.00, edge 328.73) | −0.01 in LibreOffice | unchanged, still passing |

**Move, in one number: the body column's right edge must travel right by at least 40.68 pt, and land on
543.74 ± 1.0.** If it moves by 20 pt, the stop is being clamped and the gate is wrong. If it does not move
at all, Google is normalising `w:tab w:val="right"` the way it normalised `distribute`, and the whole
tab-stop family — including the `47_margins` tab lead — is dead.

**Predicted document movement: 5 become CLEAN** — `302_radiology_report`, `313_power_of_attorney`,
`316_contract_with_schedules`, `321_auditors_report`, `335_msds_safety_data_sheet` — because the pin is
face-independent and these five fail `60` alone.

**Two negative controls, both already recorded, that must NOT move:**

* `purchase-order` must still read **+102.98 OVER**. That failure is an instrument artefact, not an
  edge: the Rate column's anchor is 428.30, the "For Kastura Home Products Pvt. Ltd." line sits at left
  **438.38** on the source (10.08 pt away, outside the 10 pt bucket) and **438.50** in the render
  (9.60 pt, inside it) — the line moved **0.12 pt** and the check charged a 102.98 pt overrun. If the pin
  makes `purchase-order` pass, it has changed the bucketing and not the edge, and the result is not
  attributable. The instrument fix is the symmetric-anchor predicate at `verify_google.py:2692`
  (`ASSIGN = 15 pt`, anchors taken from the source once) — 8 documents flip to PASS and 2 newly fire
  under it, which is the proof it is not a check gone blind
  (`60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §4(b)).
* `360_restaurant_menu` must **not** be reported as fixed by the face half: its +141.58 is an overrun, so
  the pin pulls the last word leftwards, and it is the document most likely to wrap (two columns, one
  already +139.24).

**The discriminating measurement, if only one can be run:** the pin on `302` alone, through `gverify`,
read as `(over, under, pass)`. `(0,0,True)` confirms the construct; `(0,1,False)` refutes the whole
tab-stop family in one round trip and closes the last open engine-side door on this class.

---

## 7. What this cannot do, stated plainly

* **23.5 clean documents is not reachable by any engine change.** 55 of the 61 fail at least one other
  check: 12 fail `18`+`60`, 8 fail `47`+`60`, 6 fail `59`+`60`, 16 fail `18`+`59`+`60`
  (`113-failing-checks-TRIAGE-RANKED-27NOV-agent.md` §A). The engine-side ceiling on this class is
  **5 CLEAN**, and it is realised only when `18`, `47` and `59` land too.
* **`classpick.py --leverage`'s 23.5 is a mixed-engine number.** It does not filter by engine
  (`classpick.py:214-267`); over the 61 current-engine rows the same check is worth 5. Both numbers are
  real; only the second describes the code in the tree.
* **The largest reachable move on this class is not an engine change.** The 24 Nov face-identity rule
  ("if any declared face is one the renderer lacks, the extent check abstains in that renderer") is
  validated at **0 real defects lost** and clears the DejaVu half — 41 of the 41 Google-only failures
  become verdicts rather than charges. It is a `verify_google.py` change, so it is outside this brief,
  but it is worth more CLEAN documents than the patch above and should be scheduled with it.
* **No Google-side delta exists in the record for any of the 61.** Every "Google" figure in this file is
  either the store's pass/fail verdict or a LibreOffice-render measurement quoted as such. The one real
  Google measurement on this class is the right-pin round trip, and it is a refutation.

---

## Open questions

1. **Does Google honour `w:tab w:val="right"`** (as opposed to `w:val="left"`, which is measured exact)?
   Not stated anywhere in the repo. The left flavour is measured to 0.00 pt; the right flavour is in the
   tree at `DocxWriter.java:3805` with a documented rationale but **no Google measurement**. One round
   trip on `302` settles it.
2. **The residual advance ratio after re-facing DejaVu to Noto** — 7.1 % / 7.6 % over 299 line strings
   (`60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §5) is measured on a sample, not on the widest line of each of
   the 61, which is what the check reads.
3. **Whether `regress.py --check` will refuse the patch.** It currently refuses every commit on an
   unmodified HEAD for an unrelated stale-row reason (`GATE-FLOOR-IS-A-REVERTED-ENGINE-0212-27NOV.md`:
   `39_small_caps_letter_spacing`, `newsletter-3col-header-footer`, `350_question_paper`). Until that
   table is rebuilt, no engine change of any kind can land, so the patch is unshippable for a reason that
   has nothing to do with `60`.
4. **The 28 documents whose declared face Google already has.** Nothing in the record explains why they
   fail in Google when the LibreOffice render is within 0.13 pt. The half-point floor explains 26 of 61
   and the estimator slack explains some; the residue is "open" in
   `60-COLUMN-RIGHT-EDGE-0137-27NOV.md` §4(c) and would need a Google render to close.
