# FONT-MAP — measured font-substitution table for the kavopdf PDF→Word engine

**Task.** One row per (source font family, point size): which Google-Docs-available face the engine must
declare in `w:rFonts` so that Google's render has the same advance widths as the source PDF, and therefore
lands the text column's right edge where the page drew it (`60_text_column_right_edge`).

**Date.** 28 Nov 2026 · clone of `kavopdf/app` at HEAD (`--depth 1`), corpus = the 214 PDFs that
`tools/p2w-bench/corpus-fetch.sh` assembles (213 scored in `RANKING.csv`, 0 missing).
Nothing under `/scratch/input` touched, no engine code changed, nothing written to or deleted from Drive.

---

## 1. What the engine writes today

`DocxWriter.faceName(String font)` (`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:7534`)
strips the 6-letter subset tag, strips the foundry suffixes `PSMT`/`PS`/`MT`, strips the style suffixes
(`" Bold"`, `"-Bold"`, `"-Italic"`, …), then looks the base up in `BASE14` (`:7600`). The map holds only:

| key | value |
|---|---|
| `times` | Times New Roman |
| `helvetica` | Arial |
| `courier` | Courier New |
| `arial`, `timesnewroman`, `couriernew` | identity |
| `liberationsans`, `liberation sans` | Arial |
| `liberationserif`, `liberation serif` | Times New Roman |
| `liberationmono`, `liberation mono` | Courier New |

So for the DejaVu families the lookup misses and the stripped name is returned verbatim:
`DejaVuSans`, `DejaVuSerif`, `DejaVuSansMono` are written into `w:ascii`, `w:hAnsi` and `w:cs` as-is
(`:4772`, `:7079`, `:7366`), with bold and italic carried by `w:b` / `w:i` instead of by the name.
That is the whole defect: **Google Docs has no DejaVu**, so it substitutes, and the substitute it picks is
~13 % narrower. The two documents that were round-tripped through Drive confirm both halves — the export
carries `ArialMT` / `Verdana` / `Calibri`, not the declared name.

---

## 2. Which documents are at stake, and which families they use

59 of the 214 stored Google results fail `60_text_column_right_edge` (`benchmarks/gverify/*.json`).
Reading each source PDF's spans with PyMuPDF and grouping by family:

| source family | docs using it | of those, failing `60` |
|---|---:|---:|
| DejaVuSans | 68 | **28** |
| DejaVuSerif | 35 | **25** |
| DejaVuSansMono | 13 | **6** |
| Liberation Sans / Serif / Mono | 5–72 each | 0–19 — but `BASE14` already maps these to metric-identical faces, so their `60` failures have some other cause and no row below touches them |
| Helvetica / Times / Courier | 16 / 4 / 1 | 1 / 1 / 0 |

Every DejaVu document is exposed; the Liberation documents mostly are not, because `BASE14` already sends
them to metric-identical faces. That is the shape of the problem: **three unmapped families, 59 documents.**

---

## 3. Method — how the required ratio was measured

1. **The source's drawn width.** For every text span in all 214 PDFs I summed the span bounding boxes and
   divided by the same string's advance width computed from the real DejaVu font program
   (`/usr/share/fonts/truetype/dejavu/`, correct style per span: Bold / Oblique / BoldOblique).
   Result over the **5509 spans** that carry the table below: median `drawn / natural = 1.0000`, and
   per-bucket it is 1.000 ± 0.001 for **74 of the 78 buckets**. **The PDFs were drawn with the DejaVu metrics**, so the
   width the check compares against is exactly DejaVu's advance width at that size, and
   **the required ratio for a substitute is 1.000**.
2. **The candidate's width.** Same strings, same sizes, measured from the font program of each candidate.
   Faces whose metrics are genuinely known to this sandbox are marked *verified*:

| Google face | font used to measure it | status |
|---|---|---|
| Arial | `LiberationSans-{Regular,Bold,Italic,BoldItalic}` | verified — Liberation is the metric-compatible Arial clone (same claim the engine's own `BASE14` relies on) |
| Times New Roman | `LiberationSerif-*` | verified (same basis) |
| Courier New | `LiberationMono-*` | verified (same basis) |
| Georgia | Gelasio 400/700 (variable, instanced) | clone — Gelasio is designed metric-compatible with Georgia; **not** the real Georgia |
| Calibri | Carlito | clone — metric-compatible with Calibri; not the real Calibri |
| Cambria | Caladea | clone — metric-compatible with Cambria; not the real Cambria |
| Verdana | — | **proprietary, not installed, not readable.** Modelled as **1.139 × Arial**, a ratio measured inside Google's own render (see §5) |
| Tahoma, Trebuchet MS, Lucida Console, Consolas, Palatino, Book Antiqua, Garamond, Comic Sans, Impact | — | not available; not used below |

3. **Cross-check that the clones are honest.** Google's own render of `313_power_of_attorney` with `Georgia`
   declared put the widest line at 421.01 pt. Gelasio predicts 0.862–0.867 × the source's 481.93 pt =
   **415.4–417.8 pt**, i.e. within 1.3 %. Gelasio ≈ Georgia holds to about 1 % on this text.

---

## 4. The mapping table

One row per (family, style, size) bucket that actually occurs in a document failing `60`.
`required` = the width ratio the substitute must have, measured from the source PDF (§3.1) — it is 1.000
everywhere, which is the finding, not a placeholder. `rec` = the recommended face, `its ratio` = that face's
measured (or modelled) width ratio on the same strings, `resid` = `its ratio − required` in %, so **negative
means the line still stops short**, positive means it runs long.

| source family | style | size pt | spans | docs | of which fail 60 | required | rec. Google face | its ratio | resid | confidence |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| DejaVuSans | Regular | 6.5 | 110 | 35 | 19 | 1.0001 | **Verdana** | 1.008 | +0.8% | inferred (model) |
| DejaVuSans | Regular | 7.5 | 535 | 41 | 18 | 1.0000 | **Verdana** | 1.011 | +1.1% | inferred (model) |
| DejaVuSans | Regular | 7.0 | 216 | 34 | 17 | 1.0001 | **Verdana** | 1.034 | +3.4% | inferred (model) |
| DejaVuSans | Regular | 8.0 | 342 | 27 | 17 | 1.0000 | **Verdana** | 1.021 | +2.1% | inferred (model) |
| DejaVuSans | Bold | 8.0 | 118 | 29 | 14 | 1.0000 | **Verdana** | 0.980 | -2.0% | inferred (model) |
| DejaVuSans | Bold | 13.0 | 33 | 26 | 13 | 1.0001 | **Verdana** | 1.015 | +1.5% | inferred (model) |
| DejaVuSans | Regular | 8.5 | 90 | 16 | 10 | 1.0000 | **Verdana** | 1.017 | +1.7% | inferred (model) |
| DejaVuSans | Bold | 7.0 | 113 | 23 | 9 | 1.0000 | **Verdana** | 1.006 | +0.6% | inferred (model) |
| DejaVuSans | Bold | 8.5 | 29 | 12 | 8 | 1.0000 | **Verdana** | 0.973 | -2.7% | inferred (model) |
| DejaVuSerif | Regular | 8.5 | 111 | 11 | 8 | 1.0001 | **Verdana** | 0.985 | -1.5% | measured @10 pt, scaled |
| DejaVuSans | Bold | 5.5 † | 13 | 9 | 6 | 1.0001 | **Verdana** | 0.957 | -4.3% | inferred (model) |
| DejaVuSans | Regular | 5.5 | 134 | 13 | 6 | 1.0000 | **Verdana** | 1.037 | +3.7% | inferred (model) |
| DejaVuSans | Bold | 9.0 | 26 | 15 | 5 | 1.0000 | **Verdana** | 1.003 | +0.3% | inferred (model) |
| DejaVuSans | Bold | 10.0 † | 14 | 11 | 5 | 0.9999 | **Verdana** | 1.015 | +1.5% | inferred (model) |
| DejaVuSerif | Regular | 10.0 | 80 | 5 | 5 | 1.0173 | **Verdana** | 0.991 | -0.9% | MEASURED in Google @10 pt |
| DejaVuSans | Bold | 9.5 † | 10 | 7 | 4 | 1.0001 | **Verdana** | 0.985 | -1.5% | inferred (model) |
| DejaVuSans | Bold | 11.0 | 41 | 10 | 4 | 1.0000 | **Verdana** | 0.999 | -0.1% | inferred (model) |
| DejaVuSans | Bold | 12.0 † | 4 | 4 | 4 | 0.9999 | **Verdana** | 1.026 | +2.6% | inferred (model) |
| DejaVuSerif | Regular | 9.0 † | 12 | 4 | 4 | 1.0000 | **Verdana** | 0.986 | -1.4% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 9.5 | 62 | 4 | 4 | 1.0144 | **Verdana** | 0.987 | -1.3% | measured @10 pt, scaled |
| DejaVuSansMono | Regular | 7.0 † | 10 | 6 | 3 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSerif | Bold | 9.0 † | 8 | 3 | 3 | 0.9999 | **Verdana** | 0.957 | -4.3% | inferred (model) |
| DejaVuSerif | Bold | 10.0 † | 9 | 3 | 3 | 0.9999 | **Verdana** | 0.960 | -4.0% | inferred (model) |
| DejaVuSerif | Bold | 11.0 † | 4 | 3 | 3 | 0.9999 | **Verdana** | 0.956 | -4.4% | inferred (model) |
| DejaVuSerif | Bold | 13.0 † | 3 | 3 | 3 | 1.0000 | **Verdana** | 0.967 | -3.3% | inferred (model) |
| DejaVuSans | Bold | 11.5 † | 2 | 2 | 2 | 1.0001 | **Verdana** | 0.980 | -2.0% | inferred (model) |
| DejaVuSans | Regular | 9.5 † | 5 | 2 | 2 | 0.9998 | **Verdana** | 1.029 | +2.9% | inferred (model) |
| DejaVuSans | Regular | 10.0 † | 3 | 3 | 2 | 1.0001 | **Verdana** | 1.126 | +12.6% | inferred (model) |
| DejaVuSansMono | Regular | 6.5 † | 13 | 4 | 2 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSerif | Bold | 9.5 † | 7 | 2 | 2 | 0.9999 | **Verdana** | 0.950 | -5.0% | inferred (model) |
| DejaVuSerif | Bold | 12.0 † | 2 | 2 | 2 | 0.9999 | **Verdana** | 0.962 | -3.8% | inferred (model) |
| DejaVuSerif | Bold | 24.0 † | 2 | 2 | 2 | 1.0000 | **Verdana** | 0.988 | -1.2% | inferred (model) |
| DejaVuSerif | Italic | 7.5 † | 3 | 3 | 2 | 1.0000 | **Verdana** | 0.987 | -1.3% | inferred (model) |
| DejaVuSerif | Italic | 8.5 † | 2 | 2 | 2 | 1.0000 | **Verdana** | 0.993 | -0.7% | inferred (model) |
| DejaVuSerif | Italic | 9.0 † | 2 | 2 | 2 | 1.0000 | **Verdana** | 0.990 | -1.0% | inferred (model) |
| DejaVuSerif | Regular | 6.5 † | 7 | 2 | 2 | 1.0000 | **Verdana** | 0.994 | -0.6% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 7.0 † | 5 | 2 | 2 | 1.0000 | **Verdana** | 0.981 | -1.9% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 7.5 | 20 | 3 | 2 | 1.0000 | **Verdana** | 0.984 | -1.6% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 8.0 | 61 | 3 | 2 | 1.0000 | **Verdana** | 0.983 | -1.7% | measured @10 pt, scaled |
| DejaVuSans | Bold | 6.0 † | 13 | 4 | 1 | 1.0001 | **Verdana** | 0.999 | -0.1% | inferred (model) |
| DejaVuSans | Bold | 7.2 | 26 | 3 | 1 | 1.0000 | **Verdana** | 0.966 | -3.4% | inferred (model) |
| DejaVuSans | Bold | 20.0 † | 4 | 4 | 1 | 1.0000 | **Verdana** | 0.986 | -1.4% | inferred (model) |
| DejaVuSans | Regular | 7.2 | 144 | 3 | 1 | 1.0000 | **Verdana** | 1.015 | +1.5% | inferred (model) |
| DejaVuSansMono | Regular | 6.8 † | 3 | 1 | 1 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 8.5 † | 12 | 1 | 1 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 9.5 † | 2 | 1 | 1 | 1.0000 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 11.0 † | 2 | 2 | 1 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 12.0 † | 1 | 1 | 1 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSerif | Bold | 8.5 † | 1 | 1 | 1 | 0.9999 | **Verdana** | 0.955 | -4.5% | inferred (model) |
| DejaVuSerif | Bold | 10.5 † | 1 | 1 | 1 | 0.9999 | **Verdana** | 0.937 | -6.3% | inferred (model) |
| DejaVuSerif | Bold | 18.0 † | 1 | 1 | 1 | 1.0000 | **Verdana** | 0.957 | -4.3% | inferred (model) |
| DejaVuSerif | Bold | 20.0 † | 1 | 1 | 1 | 1.0000 | **Verdana** | 0.963 | -3.7% | inferred (model) |
| DejaVuSerif | Italic | 7.0 † | 5 | 4 | 1 | 1.0000 | **Verdana** | 1.000 | +0.0% | inferred (model) |
| DejaVuSerif | Italic | 8.0 † | 1 | 1 | 1 | 1.0000 | **Verdana** | 0.997 | -0.3% | inferred (model) |
| DejaVuSerif | Italic | 10.0 † | 1 | 1 | 1 | 1.0173 | **Verdana** | 0.979 | -2.1% | inferred (model) |
| DejaVuSerif | Regular | 6.2 † | 2 | 1 | 1 | 1.0001 | **Verdana** | 0.990 | -1.0% | measured @10 pt, scaled |
| DejaVuSans | Bold | 5.0 † | 4 | 1 | 0 | 1.0000 | **Verdana** | 0.979 | -2.1% | inferred (model) |
| DejaVuSans | Bold | 5.4 | 21 | 1 | 0 | 1.0000 | **Verdana** | 0.998 | -0.2% | inferred (model) |
| DejaVuSans | Bold | 5.6 | 35 | 1 | 0 | 1.0002 | **Verdana** | 0.927 | -7.3% | inferred (model) |
| DejaVuSans | Bold | 6.2 † | 12 | 1 | 0 | 1.0000 | **Verdana** | 0.987 | -1.3% | inferred (model) |
| DejaVuSans | Bold | 6.8 | 42 | 2 | 0 | 1.0001 | **Verdana** | 0.962 | -3.8% | inferred (model) |
| DejaVuSans | Bold | 14.0 † | 1 | 1 | 0 | 0.9999 | **Verdana** | 0.997 | -0.3% | inferred (model) |
| DejaVuSans | Regular | 5.0 | 22 | 2 | 0 | 0.9999 | **Verdana** | 1.047 | +4.7% | inferred (model) |
| DejaVuSans | Regular | 5.4 | 378 | 1 | 0 | 0.9997 | **Verdana** | 0.999 | -0.1% | inferred (model) |
| DejaVuSans | Regular | 5.6 | 420 | 1 | 0 | 1.0000 | **Verdana** | 1.164 | +16.4% | inferred (model) |
| DejaVuSans | Regular | 5.8 | 168 | 1 | 0 | 0.9999 | **Verdana** | 1.006 | +0.6% | inferred (model) |
| DejaVuSans | Regular | 6.2 | 313 | 2 | 0 | 1.0097 | **Verdana** | 1.022 | +2.2% | inferred (model) |
| DejaVuSans | Regular | 6.8 | 1440 | 1 | 0 | 0.9997 | **Verdana** | 0.996 | -0.4% | inferred (model) |
| DejaVuSans | Regular | 9.0 † | 2 | 1 | 0 | 1.0002 | **Verdana** | 1.016 | +1.6% | inferred (model) |
| DejaVuSansMono | Regular | 5.8 | 84 | 1 | 0 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 6.2 † | 6 | 1 | 0 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSansMono | Regular | 6.6 | 19 | 1 | 0 | 0.9999 | **Courier New** | 0.997 | -0.3% | MEASURED (font program) |
| DejaVuSerif | Bold | 14.0 † | 2 | 2 | 0 | 0.9999 | **Verdana** | 0.953 | -4.7% | inferred (model) |
| DejaVuSerif | Bold | 26.0 † | 1 | 1 | 0 | 0.9998 | **Verdana** | 1.020 | +2.0% | inferred (model) |
| DejaVuSerif | Italic | 6.0 † | 1 | 1 | 0 | 1.0001 | **Verdana** | 0.961 | -3.9% | inferred (model) |
| DejaVuSerif | Regular | 6.8 | 24 | 1 | 0 | 1.0000 | **Verdana** | 0.986 | -1.4% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 18.0 | 30 | 1 | 0 | 0.9996 | **Verdana** | 0.996 | -0.4% | measured @10 pt, scaled |
| DejaVuSerif | Regular | 24.0 † | 3 | 1 | 0 | 1.0002 | **Verdana** | 1.109 | +10.9% | measured @10 pt, scaled |

### 4b. The same measurement for every face I could read, pooled per family and weight

Ratio = width in that face ÷ width the source drew. **1.000 is the target.** Best value in each row in bold.

| source family | style | spans | Arial | Georgia (Gelasio) | Times New Roman | Calibri (Carlito) | Cambria (Caladea) | Courier New | Verdana *(modelled)* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DejaVuSans | Regular | 4322 | 0.899 | 0.890 | 0.817 | 0.805 | 0.774 | 1.076 | **1.024** |
| DejaVuSans | Bold | 561 | 0.866 | 0.951 | 0.836 | 0.739 | 0.792 | 0.921 | **0.986** |
| DejaVuSerif | Regular | 417 | 0.868 | 0.864 | 0.790 | 0.794 | 0.782 | 1.164 | **0.988** |
| DejaVuSerif | Bold | 42 | 0.842 | 0.930 | 0.834 | 0.707 | 0.765 | 0.882 | 0.960 |
| DejaVuSerif | Italic | 15 | 0.870 | 0.885 | 0.799 | 0.783 | 0.775 | 1.122 | **0.991** |
| DejaVuSansMono | Regular | 152 | 0.870 | 0.854 | 0.816 | 0.774 | 0.744 | **0.997** | 0.991 |

The mono row's Verdana figure is a trap worth naming: Verdana is **proportional**, so its aggregate on
monospace text can look close to 1.000 while every individual column of a monospace grid moves — that is
exactly what `FINDINGS/47_margins-DEJAVU-MONO-GOOGLE-SUBSTITUTES-VERDANA-081500-f1x.md` measured (a 29-char
mono run 34.1 pt short in Google's render). An aggregate ratio is only evidence for a face when the face
has the same pitch structure as the source; for the mono family only a monospace face can pass.

Read across: **Courier New is exact for the mono family and wrong for everything else** (a monospace
advance is 0.600 em, DejaVu Sans Mono is 0.602 em — that is the whole of the 0.997). **Verdana is the only
face in the neighbourhood of 1.000 for the proportional DejaVu families.** Every face that Google already
substitutes by itself — Arial, and the Calibri/Georgia-looking defaults its export shows — sits 10–25 % low.

---

## 5. Evidence for the Verdana rows (the only rows that are not read from a font program)

Verdana is proprietary and not installed here, so it cannot be measured offline. Two facts anchor it:

1. **Measured in Google, `313_power_of_attorney`, `DejaVuSerif` 10 pt** (recorded in
   `FINDINGS/60-JUSTIFY-PIN-REFUTED-IN-GOOGLE-28NOV-fixer.md`, a real upload→Doc→export→compare run):
   source widest line 481.93 pt; declared `DejaVuSerif` → 420.66 pt; declared **`Verdana` → 479.15 pt**;
   declared `Georgia` → 421.01 pt. So **Verdana ÷ DejaVu Serif = 0.994** and **Verdana ÷ ArialMT = 1.139**,
   and the document went 41/42 → **42/42** on nothing but the font name.
2. **`302_radiology_report`** (DejaVuSerif + DejaVuSans + DejaVuSans-Bold) likewise went 41/42 → **42/42**
   with both families declared as Verdana. That is the 2-document probe the brief mentions, and it is the
   only Google-measured Verdana evidence that exists.

Everything else in the Verdana column is the model `Verdana = 1.139 × Arial`, applied to the measured Arial
ratio for the same strings. **The model reproduces both Google measurements it can be checked against:**

| document | quantity | model | Google, measured | error |
|---|---|---:|---:|---:|
| 313_power_of_attorney | widest-line shortfall, Arial | 61.1 pt | 61.27 pt (481.93 − 420.66) | 0.2 pt |
| 313_power_of_attorney | widest-line shortfall, Verdana | 2.6 pt | 2.78 pt (481.93 − 479.15) | 0.2 pt |
| 313_power_of_attorney | widest-line shortfall, Georgia | 72.6 pt | 60.92 pt (481.93 − 421.01) | 11.7 pt |
| 302_radiology_report | Verdana verdict | pass (5.5 pt short) | **42/42 pass** | agrees |

The Georgia row is the one that misses, and it misses for a reason worth recording: Google's real Georgia is
~1.3 % wider than Gelasio on this text, and that 1.3 % of a 482 pt line is 6 pt. It does not change any
verdict (Georgia fails by 60 pt, not by 6).

---

## 6. Does the point size matter? No — and that is a measured result, not an assumption

The brief keys the mapping on (family, size). Measured, **the size is not load-bearing**: advance widths
scale linearly with em size in every one of these fonts, so the *ratio* between two faces on the same text
is size-independent. What actually moves the ratio is the **character mix**, and the table's apparent
size-dependence is that in disguise — each size bucket is a different set of documents and therefore a
different set of strings:

| family + style | face | spread of the ratio across its size buckets |
|---|---|---:|
| DejaVuSans Regular | Arial | 0.885 – 0.911 (0.026) over the 7 buckets holding ≥50 spans |
| DejaVuSans Regular | Georgia | 0.883 – 0.909 (0.026) over the same 7 |
| DejaVuSerif Regular | Georgia | 0.861 – 0.870 (0.009) over the 5 buckets holding ≥20 spans |
| DejaVuSerif Bold | Georgia | 0.926 – 0.942 (0.016) over the 4 buckets holding ≥3 spans |
| **DejaVuSansMono Regular** | **Courier New** | **0.997 – 0.997 (0.000) over all 10 buckets** |

Two aggregations appear in this document and they differ by ~1.5 points, on purpose. §4 is
**span-width-weighted** (total advance in the face ÷ total advance drawn), which is the quantity the check
measures on a long line; §4b is the same weighting pooled over all sizes. A **median over lines** instead
gives Arial 0.874 for DejaVu Sans Regular rather than 0.899, because short lines — table cells, labels —
carry proportionally more digits and capitals, where Arial is relatively narrower. The weighted figure is
the one to trust for a column edge; the median is the one to trust if you care about a typical line.

† marks a bucket with fewer than 15 spans. Those rows are reported for completeness and their ratios are
noisier than the rest — the 10.0 pt DejaVu Sans bucket (+12.6 %) rests on **three** spans of digits.

The mono row is the proof: a fixed-pitch face has no character-mix term, and its ratio is *identical* at
6.5, 6.8, 7.0, 8.5, 9.5, 11.0 and 12.0 pt. The proportional rows vary by ±2 %, and that variation is
string content, not size. **So the mapping is a family-and-weight decision; the size key can be carried for
bookkeeping but does not change the answer at any size the corpus contains (5.0–24.0 pt).**

What *does* change with weight: **the ratio shifts by 2–3 points between regular and bold**, because
DejaVu's bold step is heavier than Arial's — DejaVu Sans Bold is 2.7 % wider than Arial Bold relative to
the regular pair (0.899 regular vs 0.866 bold; the same comparison for the serif is 0.868 vs 0.842, i.e.
2.4 %), so a bold row and a regular row genuinely need separate verdicts. Georgia is the surprise, and it
is a 7-point shift: 11 % narrow for DejaVu Sans **Regular** (0.890) but only **5 % narrow for DejaVu Sans
Bold** (0.951) — the closest any readable face gets to a DejaVu bold row.

---

## 7. Per-document prediction, and what it says about the 59

Offline model of the check itself (`verify_google.py:2743–2830`): cluster each page's lines into columns
by left edge (±10 pt, ≥3 lines), take the column's **widest** line, and compare its right edge; a column
passes if the render is not more than `RIGHT_UNDERRUN 8.0 + one word` (median word width, capped at 40)
short, and not more than `RIGHT_OVERRUN 6.0 + one word` long. Substituting a face scales each line by the
ratio measured in §4. Predicted verdicts:

| face declared for the DejaVu families | documents passing `60` (of 59) |
|---|---:|
| Arial | 33 |
| Georgia | 33 |
| Times New Roman | 32 |
| Calibri | 31 |
| Cambria | 31 |
| Courier New | 32 |
| Verdana | 57 |

`Courier New` scores well only because it is *over*-wide for proportional text, and the overrun branch
punishes it on the documents where a wide line matters — it is right for the 6 mono documents and wrong
for the rest. The two faces worth comparing are **Verdana (57/59)** and **everything Google substitutes by
itself (31–33/59)**. The two documents the model says Verdana still fails:

- **310_court_judgment** — worst column still short by 29.2 pt with Verdana (Arial 84.5, Georgia 76.1).
- **383_api_docs_page** — worst column still short by 50.6 pt with Verdana (Arial 91.9, Georgia 78.9).

Both are worth one measurement of their own: they are **not** among the three letter-spaced documents in
§8, so either Verdana genuinely is not wide enough for their widest column, or their widest column is
justified and the shortfall is a justification artefact rather than a face one. That distinction decides
whether a face map can ever close them.

---

## 8. Rows I am confident about, and rows I am not

**Confident — measured from a font program whose metrics are the real ones:**

- **DejaVuSansMono (all sizes, both weights) → `Courier New`.** 0.997 at every size bucket, spread 0.000,
  and the arithmetic behind it is exact and checkable: DejaVu Sans Mono advance 1233/2048 = 0.6020 em,
  Courier New 600/1000 = 0.6000 em, and the widths are style-independent. Residual −0.3 %, i.e. a 500 pt
  line lands 1.5 pt short. **This row is also the biggest win in the table**: Google currently substitutes
  *Verdana*, a proportional face, for `DejaVuSansMono`, which destroys a monospace grid outright.
- **Arial / Georgia / Times New Roman / Calibri / Cambria are all 10–25 % too narrow for every DejaVu
  family.** Whatever the right answer is, it is not any of these, at any size.
- **The required ratio is 1.000**, not "roughly 1.0": measured `drawn / DejaVu natural = 1.0000` (median)
  over 5,509 spans (5,900+ lines), per-bucket 1.000 ± 0.001 for 74 of 78 buckets.
- **The size key is inert** (§6).

**Confident — measured in Google's own renderer, but on one document:**

- **DejaVuSerif Regular → `Verdana`** at 10 pt: 0.994, 42/42. Generalised to 8.5–10 pt by the linear-scaling
  argument in §6, which is solid for a TTF-backed renderer.

**Not confident — inferred from the `Verdana = 1.139 × Arial` model, never measured for these strings:**

- **DejaVuSans Regular → `Verdana`.** The model says 1.008–1.037 (width-weighted 1.024), i.e. **1–4 % too wide**, which on a
  480 pt line is 10–19 pt long — inside `RIGHT_OVERRUN 6 + one word` for most columns (the model still
  passes 57/59) but not for all of them. The honest statement is: *Verdana is the only face within 4 % of
  the target, and it errs long rather than short for sans and short rather than long for serif.* If a
  sans-specific face is wanted, Tahoma is the plausible next candidate (narrower than Verdana, wider than
  Arial) and I could not measure it at all — **unverified**.
- **DejaVuSans Bold → `Verdana`** (model 0.986; Georgia-Bold measures 0.951 width-weighted, 0.94–1.02
  across buckets) — the measured Georgia-Bold number brackets the Verdana model, so
  the answer is *probably* Verdana, but Verdana Bold's own advance widths are unverified. **If bold
  fidelity matters more than regular fidelity, Georgia Bold is the measured choice for bold sans** —
  the model can't settle it.
- **DejaVuSerif Bold → `Verdana`** (model 0.960). Georgia-Bold measures 0.926–0.942 here, so both candidates
  leave a 4–7 % shortfall. DejaVu Serif Bold is simply wider than any face Google has.
- **DejaVuSans / DejaVuSerif Italic → `Verdana`.** 14 italic serif lines and 0 italic sans lines in the
  corpus; the italic rows are arithmetic, not measurement.

**Not fixable by any face choice:**

- `305_vaccination_certificate`, `352_certificate_ornate_border`, `371_experience_certificate` draw their
  text **17 %, 37 % and 35 % wider than the face's natural advance** — letter-spacing or a horizontal text
  scale in the source, not a face. No substitution reaches 1.35; these three need `w:spacing` (letter
  spacing), and they will fail `60` under any mapping in this table. Their buckets are excluded from the
  table above by the `|required − 1| < 0.03` filter.

---

## 9. The Google Drive half — attempted, and closed

The probe was built (`probe-fontwidth.docx`: the same 64-character string in Verdana, Tahoma,
Trebuchet MS, Georgia, Arial, DejaVuSans, Courier New and Lucida Console at 6.5, 8, 10 and 13 pt) to
measure the unreadable faces inside Google's own renderer. The upload failed on the first call, exactly as
`tools/p2w-bench/BLOCKERS.md` records for 28 Nov:

> `GOOGLEDRIVE_CREATE_FILE` → HTTP 403, *"The file key does not belong to this project or session… use a
> file uploaded by this project"* — the tool needs an `s3key` minted by the platform's upload staging, and
> this sandbox cannot mint one. A `/scratch/work/...` path is not an s3key.

`GOOGLEDRIVE_UPLOAD_FROM_URL` would work (it is the workaround that succeeded once, by publishing the file
to a public branch), but that means writing to the user's GitHub to measure a font, which is outside a
measurement task's licence. **No probe round trips were run — 0 of the 4 allowed.** Everything above is
offline measurement, except the two Verdana results that a *previous* run measured in Google and recorded
in `FINDINGS/`, which I cite rather than claim.

---

## 10. The single most valuable next measurement

**One Drive round trip on `316_contract_with_schedules` with the mapping applied as
`DejaVuSans → Verdana`, `DejaVuSerif → Verdana`, `DejaVuSansMono → Courier New`.**

Why that one: it is the only document in the corpus whose source mixes **all three** DejaVu families
(DejaVuSans 8.0, DejaVuSerif 9.5, DejaVuSansMono in the schedule tables), so a single export tests every
row of the table at once, including the mono row that has never been tested in Google and that the table
rates most confidently. My model predicts Verdana leaves it 3.8 pt short (pass) and that Courier New is
exact; if the export disagrees on the mono column, the whole table's most solid row is wrong and I want to
know that before anyone writes it into the engine.

Second, if the upload path is fixed: the `probe-fontwidth.docx` probe above, which measures Verdana, Tahoma,
Trebuchet MS, Georgia and Lucida Console directly and would replace every "inferred" row in §8 with a
measured one in a single round trip.

---

## 11. Reproducing this

This document is the only deliverable; the working data stays in the sandbox. Everything in it is
regenerated by three scripts, in this order, from a `corpus-fetch.sh` corpus and the DejaVu TTFs:

1. `measure3.py` — walks all 214 PDFs, groups every span by (family, style, size), and emits
   `buckets.json`: span count, documents, failing-document count, the required ratio, and all six
   candidate ratios. This is the source of §4.
2. `lines.py` — the same measurement per **line** rather than per span, for the size-independence
   evidence in §6.
3. `predict.py` — the offline model of `60_text_column_right_edge`, emitting the per-document verdicts
   summarised in §7.

Candidate widths come from `LiberationSans/Serif/Mono` (installed), `Gelasio`, `Carlito` and `Caladea`
(Google Fonts, metric-compatible with Georgia, Calibri and Cambria), and the DejaVu TTFs (installed).
Verdana is the only face in the table that is neither installed nor readable, and every row that depends
on it is marked as inferred.

