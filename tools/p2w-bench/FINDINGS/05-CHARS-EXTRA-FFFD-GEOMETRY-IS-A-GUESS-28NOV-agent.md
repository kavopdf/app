# The advance-width route to the four U+FFFD ligatures is a guess, not a decision

**28 Nov 2026. Document: `041122-Account_Opening_Form.pdf` (corpus copy, 9 pages, 230,348 bytes).
Readers used, named on every number below:**

- **R1 - PDFBox-android 2.0.27.0**, the engine's own reader, run on the pod as `WidthProbe.java`
  (built from `tools/engine-verify` with classpath
  `out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar`,
  `JAVA_HOME=/scratch/work/.p2w-jdk/jdk`). Advance = `PDType0Font.getWidth(code)/1000`.
  Occurrences = every `TextPosition` whose unicode contains U+FFFD, counted per `getCharacterCodes()`.
- **R2 - the embedded font program's own `hmtx` table**, read through `TrueTypeFont.getAdvanceWidth(gid)/
  getUnitsPerEm()` (`HmtxProbe.java`). Independent of the PDF's `/W` array.
- **R3 - PyMuPDF 2.1 / MuPDF 1.28.6**, `page.get_text("rawdict")`, advance = `(char bbox x1-x0)/span size`
  (cross-checked against `next_origin.x - origin.x`; the origin delta is contaminated by TJ kerning
  adjustments and varies by 0.02-0.05 em inside one code, so bbox width is the advance used here).
- **R4 - PyMuPDF page text**, used only for the word-context column, which is a *separate* route and
  takes no part in the width verdict.

**R1, R2 and R3 agree to 4 decimals on every width in this document** (e.g. 0x124 Regular: R1 0.5390,
R2 0.5390, R3 0.5390). So the numbers below are the glyphs' real advances, not a reader artefact.

Note on decoding, for whoever repeats this: R1 (PDFBox) reports these codes as U+FFFD; R3 (PyMuPDF)
reports the same four codes as U+0123/U+0124/U+0126/U+0127 (code point = code). Both readers agree on
the **codes** and on the **widths**; they disagree only on the unicode, which is the defect itself.

## 1. The component widths, from the same font, same page (R1, confirmed by R2 and R3)

Advance widths in text space (em), per embedded subset:

| font subset | w(f) | w(i) | w(l) | w(t) | w(f)+w(i) = "fi" | w(f)+w(f) = "ff" | w(f)+w(f)+w(i) = "ffi" | w(f)+w(l) = "fl" | w(f)+w(t) = "ft" |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| REAQAG+Effra-Regular | 0.3300 | 0.2220 | 0.2120 | 0.3840 | **0.5520** | **0.6600** | **0.8820** | **0.5420** | **0.7140** |
| WWLUSW+Effra-Medium  | 0.3400 | 0.2440 | 0.2340 | 0.4020 | **0.5840** | **0.6800** | **0.9240** | **0.5740** | **0.7420** |
| IWIJEY+Effra-Bold    | 0.3560 | 0.2580 | 0.2500 | 0.4180 | **0.6140** | **0.7120** | **0.9700** | **0.6060** | **0.7740** |

The ASCII component glyphs are reachable inside these subsets by inverting `toUnicode` (f = code 0xE9,
i = 0xEC, l = 0xEF, t = 0xF7, gids 233/236/239/247) - the ASCII letters decode fine; only the four
ligature codes are broken. So the components are genuinely measurable, which is the one thing the route
needs and does have.

## 2. The four junk codes, per face, with the match test at ±0.02 em

| font subset | code | gid | advance (em) R1=R2=R3 | occurrences R1 (R3 agrees) | candidates within ±0.02 em | nearest candidate | word context (R4, separate route) |
|:--|:--|--:|--:|--:|:--|:--|:--|
| REAQAG+Effra-Regular | 0x123 | 291 | 0.6370 | 13 | **none** | ff, 0.6600, Δ0.0230 | "ff" - di**ff**erent, o**ff**ered, a**ff**ect, a**ff**orded |
| REAQAG+Effra-Regular | 0x124 | 292 | 0.5390 | 85 | **two: fl (Δ0.0030), fi (Δ0.0130)** | fl | "fi" - **fi**ll, veri**fi**ed, **fi**cation, **fi**ne, **fi**rst |
| REAQAG+Effra-Regular | 0x126 | 294 | 0.8470 | 21 | **none** | ffi, 0.8820, Δ0.0350 | "ffi" - o**ffi**ce, o**ffi**cially, su**ffi**cient, A**ffi**x |
| REAQAG+Effra-Regular | 0x127 | 295 | 0.8580 | 2 | **none** | ffi, 0.8820, Δ0.0240 | "ffl" - O**ffl**ine |
| WWLUSW+Effra-Medium  | 0x124 | 292 | 0.5650 | 2 | **two: fl (Δ0.0090), fi (Δ0.0190)** | fl | "fi" - **fi**ll Form DA-1 |
| WWLUSW+Effra-Medium  | 0x126 | 294 | 0.8760 | 2 | **none** | ffi, 0.9240, Δ0.0480 | "ffi" - o**ffi**cially, o**ffi**cial |
| IWIJEY+Effra-Bold    | 0x124 | 292 | 0.5840 | 2 | **none** | fl, 0.6060, Δ0.0220 | "fi" - **fi**cation, o**ffi**cial |

**Per-code verdict.**

- **0x123 (Regular, 13 occurrences) - no candidate inside ±0.02.** Its own identity "ff" is the nearest
  at Δ0.0230, i.e. *outside* the stated tolerance. Under the stated criterion this code does not resolve
  at all, even though the geometry points at the right pair.
- **0x124 (Regular 85 + Medium 2 + Bold 2 = 89 occurrences) - ambiguous, and the nearest is the wrong
  answer.** "fi" (0.5520) and "fl" (0.5420) are 0.0100 em apart in Regular, and the glyph sits 0.0130
  from fi and 0.0030 from fl: the width says **fl**, the word says **fi**. In Medium the same: 0.0090
  to fl, 0.0190 to fi. In Bold neither is within ±0.02. This is the largest block of the document and
  the route gets it wrong if it takes the nearest match.
- **0x126 (Regular 21 + Medium 2 = 23 occurrences) - no candidate inside ±0.02.** Δ0.0350 / Δ0.0480 from
  "ffi". It is 3-4 glyph widths' worth of compression away, not a rounding.
- **0x127 (Regular, 2 occurrences) - no candidate inside ±0.02** under the brief's candidate set
  (Δ0.0240 from "ffi"). It *would* match uniquely if "ffl" were a candidate (w(f)+w(f)+w(l) = 0.8720,
  Δ0.0140) - so the one code that can be pinned is pinned by a candidate the brief did not list. The
  route is candidate-set dependent as well as width-dependent.

## 3. How many of the 127 occurrences resolve uniquely

Counted over all 127 occurrences on the 9 pages (R1 counts 127 `TextPosition` codes; R3 independently
counts 127 chars: page 0 = 11, 1 = 27, 2 = 12, 3 = 5, 4 = 29, 5 = 12, 6 = 14, 7 = 11, 8 = 6):

| outcome at ±0.02 em, brief's candidate set {fi, ff, ffi, fl, ft} | occurrences | share |
|:--|--:|--:|
| **resolves to exactly one candidate** | **0** | **0 %** |
| ambiguous (two or more candidates inside tolerance) | 87 | 68.5 % |
| no candidate inside tolerance | 40 | 31.5 % |
| total | 127 | 100 % |

Sensitivity - the count does not become decisive at any tolerance, because widening the tolerance to
reach the real identities (Δ up to 0.048) swallows "fi" and "fl" together (gap 0.010):

| tolerance | unique | ambiguous | none |
|:--|--:|--:|--:|
| ±0.02 | 0 | 87 | 40 |
| ±0.03 | 17 | 87 | 23 |
| ±0.04 | 36 | 89 | 2 |
| ±0.05 | 38 | 89 | 0 |

Best case at ±0.05: 38 of 127 unique (30 %), and the other 89 - three quarters of the document's
ligatures - still unresolved between "fi" and "fl".

## 4. Why the route fails: the signal is smaller than the noise

Measured advance minus the sum of the components, for the codes whose identity the word context fixes:

| code / face | identity (context) | component sum | measured | delta |
|:--|:--|--:|--:|--:|
| 0x123 Regular | ff | 0.6600 | 0.6370 | **-0.0230 (-3.5 %)** |
| 0x124 Regular | fi | 0.5520 | 0.5390 | **-0.0130 (-2.4 %)** |
| 0x126 Regular | ffi | 0.8820 | 0.8470 | **-0.0350 (-4.0 %)** |
| 0x127 Regular | ffl | 0.8720 | 0.8580 | **-0.0140 (-1.6 %)** |
| 0x124 Medium | fi | 0.5840 | 0.5650 | **-0.0190 (-3.3 %)** |
| 0x126 Medium | ffi | 0.9240 | 0.8760 | **-0.0480 (-5.2 %)** |
| 0x124 Bold | fi | 0.6140 | 0.5840 | **-0.0300 (-4.9 %)** |

The ligature advance is **not** the sum of its components: every one is 1.6-5.2 % narrower (sidebearings
are shared/overlapped in the ligature, and the subset's `hmtx` - R2 - says the same, so this is the
design, not the PDF). That systematic compression, 0.013-0.048 em, is **1.3 to 4.8 times larger** than
the 0.010 em that separates "fi" from "fl". A rule that cannot measure its own error to better than the
quantity it is trying to discriminate cannot discriminate. The brief's own worry - "`ff` vs `fi` differ
by ~0.1 em in most serif faces" - is optimistic here: in this face `fi` and `fl` differ by 0.010 em and
`fi` and `ff` by 0.108 em, so two of the four candidates are separable and two are not, per face, with
no way to tell which case you are in from the width alone.

## 5. Verdict

**On `041122-Account_Opening_Form.pdf` the advance-width route is a guess, not a decision: 0 of the 127
occurrences resolve to exactly one candidate within ±0.02 em, the only code that has any candidate
(0x124, 89 occurrences, 70 % of the document) is closer to "fl" than to its actual "fi", and the
0.010 em that separates those two candidates is smaller than the 0.013-0.048 em by which this font's
ligatures compress their own component sums.**

Consequence for the class: the geometric fallback cannot be shipped as a mapping table for this
document, and the four codes stay a Google-side (producer-side) finding - the `/ToUnicode` of the
Type0 font maps them to `<FFFD>` on purpose, and nothing inside the file re-states their identity in a
form a reader can verify. Any "fi/ff/ffi/fl" written into the .docx for these 127 positions would be
the engine's assertion, right on 89 of them by word context and wrong on the width test.

What was *not* done, and why: no attempt to decode the glyphs' outlines (rendering the four glyphs and
reading them) - that is a different route with a different error model, and the question asked was
whether the width route decides. No repo file was modified, nothing was committed or pushed; the two
probes live in `/scratch/work/probe/` outside the clone, and `pod-prep.sh` wrote only its own build
output under `tools/engine-verify/{libs,out}` as designed.
