# 18_displacement — `autoflow` + `autoEm=1.2207` does not reproduce: five documents, three the wrong way, none clean

**27 Nov 2026 · fixer slot 17:00 → · engine `d28ca7516c3f9165` · five Google renders, one export each**

## The lead this was pointed at

`FINDINGS/18-displacement-PAGEFIRST-DEAD-CODE-AND-AUTOFLOW-1200-relay.md` §6 (26 Nov, 12:00) recorded
that `-Dp2w.lineRule=autoflow -Dp2w.autoEm=1.2207` made `72_bank_statement_no_rules_right_amounts`
**42/42 PASS** in Google, median dy +0.21, 2 of 80 runs out. That was the only record in the tree of a
construct change producing a *clean* solo-`18` document, and it was the reason the flag pair was still
carried as a live lever rather than a closed one.

Two things have moved under that record since it was written, and both were checked, not assumed:

1. `spacing()`'s `pageFirst` argument is no longer dead. The compensation at `DocxWriter.java:171`
   (`b += (1 - LINE_BASE) * (boxTw - lineTw)`) is now reached: both flow call sites pass `ctx.newPage`
   (`:3825`, `:4676`). The build measured in §6 was described as "both patches" — so this is the same
   code path, not a different one.
2. **Check 18 no longer scores the bbox top.** The 26 Nov 18:00 relay (`18dA-06`) replaced the scored
   quantity with `roy`, the origin projected into reading space, so that a font's ascent cancels. Every
   number in the 26 Nov 12:00 file was measured under the OLD quantity. A 42/42 under the old
   instrument is not a 42/42 under this one.

## What was measured

Five solo-`18` documents, converted from the corpus with
`java -Dp2w.lineRule=autoflow -Dp2w.autoEm=1.2207 -cp <same classpath> ConvertAll` into a scratch
directory, uploaded to `KavoPDF-Test-Outputs`, converted to a Google Doc, exported as PDF, and scored
with `gverify.py --collect`. The flag took effect and is verified in the bytes: 8 flow paragraphs per
document carry `w:line="240" w:lineRule="auto"`, cell paragraphs stay `exact` (that is what `autoflow`
means). `72`'s XML differs from the corpus build's, and so does its render — this was not a no-op.

`dy` is measured by a throwaway script that opens both PDFs and subtracts `span["origin"][1]` after
matching spans on `(page, text)`; it imports nothing from `verify_google.py`.

| document | stored (engine `d28ca7516c3f9165`) | this render | median dy: stored → autoflow | verdict |
|:--|:--|:--|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 41/42, fail 18 | 41/42, fail 18 | **−3.12 → −6.72** | worse 3.6 pt |
| `16_right_aligned_amounts_txtpos` | 41/42, fail 18 | 41/42, fail 18 | −2.63 → −3.12 | worse 0.5 pt |
| `71_invoice_space_aligned_no_rules` | 41/42, fail 18 | 41/42, fail 18 | +1.12 → +0.37 | better 0.75 pt |
| `320_balance_sheet_statutory` | 46/47, fail 18 | 46/47, fail 18 | +6.25 → +6.84 | worse 0.6 pt |
| `electricity-bill` | 46/47, fail 18 | 46/47, fail 18 | (no current-engine dy on record) → +4.20 | unmeasured before |

**No document changed its score.** All five still fail `18_displacement` and nothing else; the failing
set is identical to the stored one on every document.

Per-document detail from this render (`n` matched runs, median, p90 abs, share within 1 pt of the
median):

    72    n= 80  med= -6.72  p90= 8.35  within1pt=48%  min=-8.8  max=-2.9
    16    n= 64  med= -3.12  p90= 4.62  within1pt=48%  min=-6.5  max=-0.7
    71    n= 72  med= +0.37  p90= 5.10  within1pt=50%  min=-4.7  max=+6.0
    elec  n=125  med= +4.20  p90= 5.70  within1pt=87%  min=-2.0  max=+7.5
    320   n= 73  med= +6.84  p90=14.21  within1pt=14%  min=-2.2  max=+21.5

## What this refutes, and what it does not

**Refuted:** the claim that the flag pair is a lever on the solo-`18` set. It moves three of the four
documents with a current-engine baseline in the wrong direction and clears none. The 26 Nov 42/42 does
not reproduce on the instrument this store is measured with, and the honest reading of the two
together is that the old 42/42 was the old quantity, not the construct.

**Not refuted, and still the live question:** `AUTO_LINE_EM` is one number for every document, and the
box it asks for is the *substitute* face's line height. That face is per document — the engine declares
`Arial` on some paragraphs (07's flow lines carry `w:rFonts ascii="Arial"`) and declares nothing on
others, where Google substitutes Calibri → Carlito at `r = 1.220709`. A single global em is therefore
right for at most one of those two populations, which is exactly the shape of the result above: `71`
and `16` (which declare Arial) are the two that moved least badly, and `72` (which declares nothing)
moved worst.

**The untested axis is per-face, not per-document.** The next attempt should make the auto box
`ratio(face) * size` with the ratio read from the face the paragraph declares — `1.15` for the faces
Google owns (Arial, Times New Roman, Helvetica) and `1.2207` for the ones it substitutes (Calibri →
Carlito) — and measure the same five documents. That is a two-line change in `spacing()`'s caller plus a
face lookup, and it is the first version of this construct that is not one number for the whole corpus.

**Do not re-run this exact flag pair.** The measurement is here; repeating it costs five uploads and
returns the table above.
