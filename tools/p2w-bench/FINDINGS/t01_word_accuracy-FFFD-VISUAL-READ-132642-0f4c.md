# FINDINGS — t01 / FFFD — VISUAL READ of U+0123 / U+0124 / U+0126 / U+0127

- **File under test:** `041122-Account_Opening_Form.pdf` (9 pages)
- **Pages inspected:** 1 and 2
- **Method:** rendered at 300 DPI with PyMuPDF, cropped and upscaled 3x, read by eye
- **Timestamp (IST):** 2026-11-21 13:26:42

## Asked

At the places on pages 1 and 2 where the text extractor reports U+0123 (ģ), U+0124 (Ĥ),
U+0126 (Ħ) or U+0127 (ħ), what letters are *visibly drawn* on the page?

Specifically: are these (a) accented Latin letters — g-cedilla, H-circumflex, H-stroke,
h-stroke — or (b) typographic **ligatures** (`ff`, `fi`, `ffi`, `ffl`) sitting inside
ordinary words?

This had to be answered from a rendered image, not from the extractor, because the
extractor is the thing under suspicion.

## Claim

The four code points are **not** accented letters. They are typographic **ligature
glyphs** of the embedded subset font `Effra-Regular` (and `Effra-Medium`) whose
ToUnicode CMap maps them to the wrong Unicode values:

| Code point | Extractor says | Actually drawn | Visually confirmed word |
|---|---|---|---|
| U+0123 | ģ (g with cedilla) | **ff** | `Staģ` → **Staff**, `Diģerently` → **Differently** |
| U+0124 | Ĥ (H with circumflex) | **fi** | `Ĥll` → **fill**, `QualiĤcation` → **Qualification** |
| U+0126 | Ħ (H with stroke) | **ffi** | `aĦx` → **affix**, `OĦce` → **Office** |
| U+0127 | ħ (h with stroke) | **ffl** | `Oħine` → **Offline** |

Consequence: any consumer of this PDF's text layer — search, extraction, RAG, redaction
matching, screen readers, form-field mapping — sees corrupted words. A grep for
"Office", "Staff", "fill", "verified", "Qualification", "Financial", "Offline",
"affix", "Self-certified", "Unspecified" **will not match** this document.

This is a text-layer defect only. The printed/rendered page is correct and readable.

## Evidence

Extraction pass: `page.get_text("rawdict")` over pages 1–2, collecting every character
in a span whose code point is one of the four targets — **38 occurrences** in total.
Each was recorded with its character bbox, its span text and its full line text.
Eight well-separated occurrences were then chosen (all four code points represented,
both pages, spread from top to bottom of each page), rendered at 300 DPI
(`page.get_pixmap(dpi=300)`), cropped with 40 px vertical padding (110 px horizontal,
to keep the whole word in frame) and upscaled 3x with LANCZOS resampling.

### What I could actually SEE in each crop

| # | Page | Surrounding word as extracted | What is VISIBLY drawn | Crop file |
|---|---|---|---|---|
| 1 | 1 | `Ĥll` in "Please Ĥll up in BLOCK letters" | **fill** — plain `f` `i` `l` `l`, no circumflex, no diacritic | `crops/p1_fi_fill.png` |
| 2 | 1 | `aĦx` in "Branch to aĦx rubber stamp of" | **affix** — plain `a` `f` `f` `i` `x`, three separate strokes of `f`-`f`-`i` | `crops/p1_ffi_affix.png` |
| 3 | 1 | `Diģerently abled` | **Differently** — plain `D` `i` `f` `f` `e` `r` `e` `n` `t` `l` `y`, no cedilla under the `g` (there is no `g` at all) | `crops/p1_ff_Differently.png` |
| 4 | 1 | `QualiĤcation:` | **Qualification:** — plain `f` `i` between `Quali` and `cation` | `crops/p1_fi_Qualification.png` |
| 5 | 2 | `Oħine` | **Offline** — plain `O` `f` `f` `l` `i` `n` `e`, no stroke through the `h` (there is no `h`) | `crops/p2_ffl_Offline.png` |
| 6 | 2 | `Staģ` | **Staff** — plain `S` `t` `a` `f` `f`, no cedilla (there is no `g`) | `crops/p2_ff_Staff.png` |
| 7 | 2 | `Registered OĦce` | **Office** — plain `O` `f` `f` `i` `c` `e` | `crops/p2_ffi_Office.png` |
| 8 | 2 | `veriĤed` in "In person veriĤcation carried out … veriĤed." | **verification / verified** — plain `f` `i`, no circumflex (there is no `H`) | `crops/p2_fi_verified.png` |

**Reading of the images:** in every crop the letterforms are the ordinary lowercase
shapes of the word. There is no cedilla, no circumflex, no stroke bar, and no
uppercase `H` anywhere near the reported position. The accented-letter hypothesis
predicts a visible `g`/`H`/`h` with a diacritic; the page shows none — because the
glyph is a two- or three-letter ligature (`ff`, `fi`, `ffi`, `ffl`) that a Latin
reader perceives simply as the letters it stands for.

### Consistency across the whole document

The mapping is perfectly consistent over all 38 occurrences — the same code point
always sits at the same kind of ligature, never once at a real accented letter:

- U+0124 (`fi`) — 22 occurrences: `Ĥll`(fill), `QualiĤcation`, `IdentiĤcation`,
  `VeriĤcation`, `veriĤed`, `CertiĤed`, `certiĤcation`, `Ĥnancial`(Financial),
  `beneĤt`(benefit), `UnspeciĤed`(Unspecified), `Self-certiĤed`, `Ĥce`(fice), `Ĥed`(fied).
- U+0126 (`ffi`) — 11 occurrences: `aĦx`(affix), `oĦce`(office), `OĦcers`(Officers),
  `OĦcials`(Officials), `OĦcially`(Officially), `oĦcial`, `OĦcial Name`, `Registered OĦce`.
- U+0123 (`ff`) — 4 occurrences: `Staģ`(Staff, pages 1 and 2), `Oģ`(Off), `Diģerently`.
- U+0127 (`ffl`) — 2 occurrences: `Oħine`(Offline, both on page 2).

Every single context resolves to a real English word once the ligature is substituted,
and to a nonsense word if read as an accented letter. That is the signature of a
ToUnicode CMap defect, not of accented content.

## How to test it

Reproduce independently — no trust in my crops required:

```python
import pymupdf
d = pymupdf.open("041122-Account_Opening_Form.pdf")
p = d[0]
# 1. See the corrupted text layer
print(p.get_text())          # "Please Ĥll up in BLOCK letters" , "Staģ" , "aĦx"
# 2. Look at the page itself
p.get_pixmap(dpi=300).save("page1.png")
# 3. Crop around any reported bbox and zoom in
for b in p.get_text("rawdict")["blocks"]:
    for l in b.get("lines", []):
        for s in l["spans"]:
            if any(ord(c["c"]) in (0x123,0x124,0x126,0x127) for c in s["chars"]):
                print(s["text"], s["bbox"])
```

Then confirm the visual read three more ways, each independent of my eyes:

1. **Search the rendered image text.** Run OCR (Tesseract) on `page1.png` and
   `page2.png`. OCR reads glyphs, not the CMap, so it returns "Staff", "Office",
   "fill", "Offline", "Qualification". If OCR disagrees with `get_text()`, the
   text layer is at fault.
2. **Search for the words that should be there.** `pdftotext -layout` and then
   `grep -c "Office\|Staff\|verified"` → 0 hits. `grep -c "OĦce\|Staģ\|veriĤed"`
   → non-zero. Then `strings`/`qpdf --qdf` on the page content stream: the
   ligature glyphs are drawn from a subset font, and the CMap (`/ToUnicode`)
   maps those glyph codes onto U+0123/U+0124/U+0126/U+0127.
3. **Cross-check glyph widths.** Measure the reported bbox width of each
   occurrence. At 6 pt the measured widths are ≈3.8 pt for U+0123, ≈3.2 pt for
   U+0124, ≈5.1 pt for U+0126 and ≈5.2 pt for U+0127. The two `H`-based code
   points (U+0126, U+0127) are each about 5 pt wide — too wide for a single 6 pt
   letter and the right size for a three-letter ligature — while the `fi` case
   (U+0124, ≈3.2 pt) is narrow, as `fi` should be. Widths are a supporting
   signal here, not a proof; the decisive evidence is the crop images.

## Confidence

**Very high** on the visual read itself — 8 independent crops across both pages,
all four code points, every one unambiguous at 3x upscale. The letters are large
and clean; there is nothing marginal about them.

**High** on the mechanism (ToUnicode CMap mis-mapping of ligature glyphs in the
embedded `Effra-Regular` / `Effra-Medium` subset). The consistency of the mapping
over 38 occurrences and the fact that every substitution yields a real word is
strong circumstantial proof.

**Not verified:** I could not read the embedded font's internal glyph-name table
(the font stream was not retrievable in a form `fontTools` would parse), so I am
inferring the ligature *glyph names* rather than quoting them. The visual evidence
does not depend on this — the letters on the page are what they are regardless of
what the font calls them.

**Not in scope:** pages 3–9 were not visually inspected. Given the mapping is
100 % consistent on pages 1–2, the same defect almost certainly runs through the
whole document, but that is an inference, not an observation.

## Ruled out

- **Accented Latin letters (g-cedilla, H-circumflex, H-stroke, h-stroke).** Ruled
  out visually: no diacritic appears in any of the 8 crops, and in most cases the
  base letter (`g`, `H`, `h`) is not drawn at all — `Differently` has no `g`,
  `Offline` has no `h`, `fill` has no `H`. An accented letter cannot be present
  where its base letter is absent.
- **Genuine multilingual / non-English content in the form.** Ruled out: every
  affected word resolves to ordinary English banking-form vocabulary
  (Staff, Office, Qualification, verified, Financial, benefit, Offline, affix).
- **A rendering / font-substitution problem on my side.** Ruled out: the PDF
  carries its own embedded subset fonts (`Effra-Regular`, `Effra-Medium`,
  `Effra-Bold`), so what I rendered is what any conforming viewer renders. This is
  a property of the file, not of my viewer.
- **A scanning / OCR artefact.** Ruled out: page 1 and 2 have a real text layer
  with positioned glyphs and a clean vector render; this is not a scanned image.
- **Deliberate obfuscation or hidden text.** Ruled out: the affected glyphs sit
  inline at normal size, colour and baseline inside visible sentences, with no
  render-mode trickery. It is a plain encoding bug.

## Status

**CONFIRMED — no fix applied, nothing committed or pushed.**

- Verdict: on pages 1 and 2, U+0123 / U+0124 / U+0126 / U+0127 are **`ff` / `fi` /
  `ffi` / `ffl` ligatures**, not accented letters. The rendered document is correct;
  the extractable text layer is wrong.
- 38 affected characters on pages 1–2; 8 visually verified.
- Crops preserved at `crops/` (`p1_fi_fill.png`, `p1_ffi_affix.png`,
  `p1_ff_Differently.png`, `p1_fi_Qualification.png`, `p2_ffl_Offline.png`,
  `p2_ff_Staff.png`, `p2_ffi_Office.png`, `p2_fi_verified.png`).
- Suggested next step (not done here): rebuild the ToUnicode CMap so those glyph
  codes map to the two- and three-character sequences `ff`, `fi`, `ffi`, `ffl`, or
  regenerate the PDF from source with a writer that does not emit ligature glyphs
  without correct Unicode mappings.
