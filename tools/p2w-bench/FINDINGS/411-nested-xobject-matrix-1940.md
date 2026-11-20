# 411_nested_xobject_transforms — the words are not lost, the reference invents two of them

**Verdict on the handed diagnosis: wrong.** There is no disagreement between pymupdf and PDFBox
about the nested form's matrix. Both compute the same CTM to the last digit and both place the
rotated line at the same device position; PDFBox returns all 32 glyphs of it, pymupdf returns 2.
The two glyphs `t01` charges the `.txt` for — `S` and `O` — **are not words the page draws**.
They are what MuPDF's mediabox-clipped text declaration leaves behind when a line crosses the page
edge: the line is dropped, and two one-character lines survive in its place.

The `.txt` is correct on this document. `t01` is measured against a broken source side.

The fix is **one flag, one line, in the instrument** — `tools/p2w-bench/verify_txt.py:571`. Applied
to a copy and measured over all 213 documents: **211 rows byte-identical, 2 documents improve, 0 get
worse.** 411 goes `4,3,1` → `4,4,0`.

Nothing under `app/src/main/java/com/kavopdf/app/engine/` was touched. `verify_txt.py` was not edited
in the tree; the patch is text below and was measured on a copy.

---

## 0. How this was measured

    git clone https://github.com/kavopdf/app /scratch/work/CS
    bash tools/install-gate.sh                  # PASS, engine fingerprint cd21104b11ed26c1
    bash tools/p2w-bench/build-engine.sh        # engine built (34s)

Corpus: the four `corpus-v1` release zips + `benchmarks/corpus-extra` + `benchmarks/realworld`
= **213 PDFs**, matching the committed corpus size.

    java ConvertAll <corpus> /scratch/work/txtout      # 213 .txt in 78 s, 0 failed
    python3 verify_txt.py <pdf> <txt>                  # one document
    score.py verify_txt.py base.tsv                    # all 213, one row each

The harness was **validated against the committed table** before it was used: my run of the
*unmodified* verifier reproduces `tools/p2w-bench/txt/RANKING-TXT.csv` on all 213 rows, including
`411_nested_xobject_transforms,4,3,1,1,t01_word_accuracy`.

---

## (a) The measured token diff

`t01_word_accuracy` compares the word multiset of `glyph_truth(pdf)` against the word multiset of the
`.txt`. Measured on this document, unmodified verifier:

    source words 20   txt words 24   accuracy 90.0   (t01 FAIL, threshold 99)

    LOST  (in source, not in txt) : {'S': 1, 'O': 1}
    EXTRA (in txt, not in source) : {'NESTED': 1, 'FORM': 1, '-': 1, 'scaled': 1, 'and': 1, 'rot': 1}

The source side, verbatim:

    'NESTED FORM - scaled and rotated\nS\nO\nAbove: one form placed inside another, scaled 1.6x and rotated 90 degrees.\n'

The `.txt`, verbatim (the runs of `\n` between the lines are the blank lines the writer puts
between blocks):

    '          NESTED FORM - scaled and rotated\n\n\n\n\n\n\n\n\n\n\n          Above: one form placed inside another, scaled 1.6x and rotated 90 degrees.\n          NESTED FORM - scaled and rot\n'

So the document is 1 word short of nothing and 6 words long: the `.txt` carries the rotated line the
source side dropped, and `t01` ignores extra words by design ("Lost words only. Extra words are a
different fault"), so the *only* charge is `S` and `O`.

Two arithmetic facts pin the whole failure to those two tokens:

* remove `S` and `O` from the source side → 18 words, 0 lost → **100.0 % PASS**
* keep `S` and `O` and add the missing rotated line to the source side → 26 words, 2 lost → **92.3 % FAIL**

The failure is not "2 words of 20 lost". It is "the reference holds two words the page does not".

---

## (b) The CTM chain, with numbers

The file is 1338 bytes, 1 page, 9 objects. No `/Matrix` on either form. No `/Rotate`. No `/CropBox`.

    page 3   /MediaBox [0 0 595 842]
             /Resources /Font << /F1 5 0 R /F2 6 0 R >> /XObject << /Fm1 7 0 R >>
    obj 4 (page content)
             q 1 0 0 1 60 700 cm /Fm1 Do Q
             BT /F2 10 Tf 60 560 Td (Above: one form placed inside another, scaled 1.6x and rotated 90 degrees.) Tj ET
    obj 7 (/Fm1, Form, /BBox [0 0 300 60], no /Matrix -> identity)
             q 1.6 0 0 1.6 0 0 cm /Fm2 Do Q
             q 0 1 -1 0 0 0 cm /Fm2 Do Q
    obj 8 (/Fm2, Form, /BBox [0 0 200 20], no /Matrix -> identity)
             BT /F1 10 Tf 0 0 Td (NESTED FORM - scaled and rotated) Tj ET

Yes: the text is inside a Form XObject (`/Fm2`) nested inside another Form XObject (`/Fm1`), and both
instances of `/Fm2` are drawn from `/Fm1` under a `cm` operator. Two levels, two `Do`, no `/Matrix`
anywhere — the entire transform is in `cm`.

**Instance A** (the 16 pt heading).  CTM = T(60,700) · S(1.6) = `[1.6 0 0 1.6 60 700]`

    text origin (0,0) -> device (60.00, 700.00)        size 10 x 1.6 = 16
    advance direction  (a,b) = (1,0)  -> +x, upright
    device bbox        x 60.00 .. 322.30 , baseline y 700
    det = 1.6*1.6 - 0*0 = 2.56  (positive: no flip)

**Instance B** (the rotated copy).  CTM = T(60,700) · `[0 1 -1 0 0 0]` = `[0 1 -1 0 60 700]`

    x' = -y + 60 ,  y' = x + 700                      (a rotation of +90 deg, counter-clockwise)
    text origin (0,0) -> device (60.00, 700.00)        size 10 (unscaled)
    advance direction  (a,b) = (0,1)  -> +y, i.e. UP
    glyph quads        x 52.18 .. 62.18 , y 700.00 .. 863.94
    det = 0*0 - 1*(-1) = +1  (proper rotation, no flip, no negative scale)

**Caption.**  `Td (60,560)`, 10 pt, baseline y 560, device bbox x 60.00 .. 396.30.

So: there is a rotation (a `cm` at the outer form level, applied to the inner form), there is no
negative/flipped matrix anywhere in this file, and the matrix is not in dispute — see (d).

---

## (c) Device-space bbox against the MediaBox

Page: `/MediaBox [0 0 595 842]`, no `/CropBox`, so the visible page is y 0 .. 842.

Instance B runs from y = 700 to y = **863.94** — **21.94 pt past the top of the page**. Glyph by
glyph, in PDF device space (pymupdf's y is 842 minus this):

| glyph # | char | device y (quad) | on the page? |
|--:|:--|:--|:--|
| 0 .. 26 | `NESTED FORM - scaled and ro` | 700.00 .. 841.70 | yes, entirely |
| 27 | `t` | 841.70 .. 844.48 | **origin inside, quad straddles the edge** |
| 28 | `a` | 844.48 .. 850.04 | no |
| 29 | `t` | 850.04 .. 852.82 | no |
| 30 | `e` | 852.82 .. 858.38 | no |
| 31 | `d` | 858.38 .. 863.94 | no |

**28 of the 32 glyphs are inside the visible page. 4 are not.** The page is not wrong and the text is
not "genuinely off-page" as a whole: the line starts at y=700, well inside the page, and runs out of
the top of it. Rendered at 110 dpi, the strip of the rotated line is visible in the left margin from
y=142 up to the page edge, and the last four letters are cut off by the edge — as drawn.

The writer's own rule agrees with that table exactly. `PdfToWord.GlyphCollector.onPage()`
(`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java:1950`) drops a glyph whose **origin** lies
outside the crop box, with 0.5 pt of slack, and says why:

> "The origin is the test rather than the whole advance, because a line that runs off the right edge
> is still visible up to the edge and its first glyphs must not go with it."

Glyph 27 (`t`, origin 841.70) passes; glyphs 28-31 fail. 32 - 4 = **28 glyphs**, which is exactly the
`.txt`'s third line, `NESTED FORM - scaled and rot`.

---

## (d) What each parser returns for the same glyphs

**PDFBox 2.0.27 (`pdfbox-android`), `PDFTextStripper`, sortByPosition — the engine's reader.** Three
lines. The rotated instance is returned **complete, all 32 `TextPosition`s**, `fontSizeInPt` 10.00:

    LINE 32 : NESTED FORM - scaled and rotated
       U+004E 'N' x=700.00 y=60.00 w=7.22 h=5.78 fs=10.00
       U+0045 'E' x=707.22 ...
       ...
       U+0074 't' x=841.70 ...
       U+0061 'a' x=844.48 ...
       U+0074 't' x=850.04 ...
       U+0065 'e' x=852.82 ...
       U+0064 'd' x=858.38 ...   (last glyph ends at 863.94, 21.94 pt past the page top)

(`x`/`y` are `getXDirAdj`/`getYDirAdj`: for a 90° line the pair is swapped into reading order, so the
page-space position is x 52..62, y 700..861.16 — the same place pymupdf puts it.)

**pymupdf 2.1 / MuPDF 1.28.6 — the instrument's reader.**

    get_texttrace()  : span dir=(0,-1) size=10.0 bbox=[52.18, -21.94, 62.18, 142.0]  32 chars
                       -> COMPLETE and correctly placed
    get_text()       : 'NESTED FORM - scaled and rotated\nS\nO\nAbove: ...'         -> 2 of 32 chars
    get_text("dict"):  two one-character lines, dir=(0,-1):
                         'S' bbox=[49.25, 121.44, 62.99, 128.11]   (= glyph 2)
                         'O' bbox=[49.25,  84.77, 62.99,  92.55]   (= glyph 8)
    get_text(flags=fitz.TEXTFLAGS_TEXT & ~fitz.TEXT_MEDIABOX_CLIP)
                     : 'NESTED FORM - scaled and rotated\nNESTED FORM - scaled and rot\nAbove: ...'
                       -> 28 of 32 chars, the on-page set, identical to the writer's

**Where they diverge: not in the matrix.** Both readers put the text origin at (60, 700) with the
advance along +y at 10 pt — the numbers in (b) are the ones both of them computed. PDFBox returns 32
glyphs at those positions; pymupdf's *line builder* returns 2, and its `get_texttrace()` — the same
library, the same page — returns 32 at those positions. The disagreement is inside one library,
between its own two text APIs, and it is switched by `TEXT_MEDIABOX_CLIP`.

### The experiments that isolate it

Generated PDFs, same geometry, one variable changed each time (all measured, this pod):

| variant | what differs | pymupdf, clip ON (default) | pymupdf, clip OFF |
|:--|:--|:--|:--|
| `F_orig` | the file itself | `S` / `O` (2 of 32) | full 28 |
| `A_rot_only` | only the rotated instance drawn | `S` / `O` | full 28 |
| `C_rot_onpage` | rotated instance moved 200 pt down, fully on the page | **line absent entirely** | full 32 |
| `I` | rotated string `SHORT`, fully on the page | `S O` (2 of 5) | `SHORT` |
| `H` | `AAAA BBBB CCCC DDDD`, fully on the page | `C` (1 of 16) | all 16 |
| `G` | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` | `C`,`G`,`J` (3 of 26) | 22 of 26 (4 past the edge) |
| `J` | 270° rotation, line runs off the bottom | **`''` — the page declares nothing** | full 32 |
| `K` | mirrored, `-1 0 0 1 100 0`, at page level | 22 of 32 | full 32 |
| `L` | rotation in the **page content stream**, no form at all | **full 28 — correct** | full 28 |
| `M` | rotation in the **text matrix** inside the form | `S` (1 of 32) | full 28 |
| `N` | rotation in the XObject **/Matrix** instead of `cm` | `S` / `O` | full 28 |
| `E_fits` | no caption | `S` / `O` | full 28 |

What that table says, and what it kills:

* **`L` kills "the rotated line runs off the page".** The identical off-page geometry, drawn with the
  rotation in the page's own content stream instead of a form, extracts **perfectly** with the clip
  on — 28 glyphs, the same set the writer emits. Running off the page is not sufficient to cause the
  loss.
* **`I` and `H` kill it from the other side.** A rotated form instance drawn *entirely inside* the
  page still loses 3 of 5 (`I`) and 15 of 16 (`H`) glyphs. Being off-page is not necessary either.
* **`M` and `N` kill "the nested form's matrix".** Rotation in the text matrix and rotation in the
  XObject's `/Matrix` fail the same way as rotation in a `cm`; and the page-level case `L` — the one
  with no form at all — is the one that works. What the failure tracks is *a line whose glyphs are
  rotated and cross the page boundary*, not any particular way of expressing the transform.
* **`J`** shows how far it goes: a page whose only text is a rotated line running off the bottom
  declares **the empty string** with the clip on.

The surviving explanation, stated so it can be tested: MuPDF's mediabox-clipped text path drops the
glyphs of a line that crosses the page boundary and flushes whatever fragment of it survives as
one-character lines. `TEXT_MEDIABOX_CLIP` off, and the extraction is complete and agrees with PDFBox.

---

## (e) The fix: `tools/p2w-bench/verify_txt.py`, `glyph_truth()`, line 571

**The `.txt` is not produced from pymupdf.** The premise in the brief is inverted, and it matters,
because it points the fix at the wrong side of the pipeline:

    ReadingOrder.java:24-30
        PdfToWord.Result r = PdfToWord.convert(pdf, "", null);   // the model
        DocxWriter.write(r, docx);                               // reads it -> .docx
        PdfToWord.writeTxt(r, txt);                              // reads the same -> .txt
    PdfToWord.java:10012   writeTxt() -> TxtWriter.write()        (TxtWriter.java:59)

The `.txt` is written by the engine (PDFBox) and pymupdf is only the **reference** the `.txt` is
scored against, inside `verify_txt.py`. So:

* pymupdf does drop these glyphs — from the string `t01` uses as its source of truth;
* the writer does not lose them — it emits the 28 on-page glyphs of the line, which is the whole
  visible line;
* therefore **the fix is in the source path of the check, not in the writer.**

`verify_txt.py:571` is the single line where the broken declaration is read. It is the string every
other part of `glyph_truth()` aligns the glyphs against, and the string `_src_text()` returns, and the
string `t01` counts words in:

```python
            try:
                declared_page = pg.get_text()
            except Exception:
                declared_page = ""
```

`pg.get_text()` uses `fitz.TEXTFLAGS_TEXT` (195), which **includes** `TEXT_MEDIABOX_CLIP`. On this
page that returns `'...\nS\nO\n...'`. Without the flag it returns `'...\nNESTED FORM - scaled and
rot\n...'`, the 28 glyphs on the page, and the source side becomes word-for-word the `.txt`.

### The patch (not applied — measured on a copy)

```diff
--- a/tools/p2w-bench/verify_txt.py
+++ b/tools/p2w-bench/verify_txt.py
@@ -568,7 +568,17 @@
             except Exception:
                 trace = []
             try:
-                declared_page = pg.get_text()
+                # THE MEDIABOX CLIP DROPS A LINE, NOT THE GLYPHS OFF THE PAGE.
+                #
+                # 411_nested_xobject_transforms draws the same string twice, the second
+                # time at 10 pt rotated 90 deg by a nested form's cm, and that copy runs
+                # 21.94 pt past the top of the MediaBox. With the clip on, the declaration
+                # for that line is two one-character lines, "S" and "O" - the other 30
+                # glyphs are gone - and t01 then asks the .txt for the words "S" and "O",
+                # which the page never draws. With the clip off the same page declares
+                # "NESTED FORM - scaled and rot", the 28 glyphs that are on the page, which
+                # is exactly what the writer emits.
+                declared_page = pg.get_text(flags=fitz.TEXTFLAGS_TEXT & ~fitz.TEXT_MEDIABOX_CLIP)
             except Exception:
                 declared_page = ""
             # A CODE THE FONT ITSELF SAYS HAS NO UNICODE COMES BACK AS ITS OWN NUMBER.
```

`fitz` is already imported inside `glyph_truth()` (line 528), so no import changes.

### What the patch measures, on all 213 documents

Same engine binary (fingerprint `cd21104b11ed26c1`), same 213 `.txt`, only the verifier changed:

    identical rows : 211 of 213
    moved          : 2, both improved, 0 worse

    12_stamp_across_page_break      10, 9, 1  t12_word_invention   ->  10, 10, 0  -
    411_nested_xobject_transforms    4, 3, 1  t01_word_accuracy    ->   4, 4, 0  -

`12_stamp_across_page_break` is the **same defect, second instance**: measured with the unmodified
verifier it loses `{'U': 1, 'G': 1}` and gains `{'12', 'AUG', '2025', 'KUNIGAL', 'SUB-REGISTRAR'}`
— again two one-character tokens left where a line crossed a page boundary. With the flag off both
documents read `lost={} extra={}` at 100.0.

And the flag's footprint over the whole corpus is exactly those two documents: the declared word
count changes on **2 of 213** pages (411: 20 → 24 words; 12_stamp: 470 → 473). No other document in
the corpus has text that this clip was removing, so the "the clip also lets genuinely off-page text
in" risk is **measured at zero here** — but it is the one risk to keep an eye on, because a document
that deliberately sets text outside the MediaBox would now have it counted in the source side.

`411_nested_xobject_transforms` after the patch:

    source words 24   txt words 24   accuracy 100.0   LOST {}   EXTRA {}

### Why no engine-side fix is possible

`t01` charges the `.txt` for `S` and `O`. Those two tokens are 2 of the 32 glyphs of a line the
`.txt` **already carries in full** (clipped at the page edge by `onPage()`, exactly as drawn). For the
engine to satisfy `t01` it would have to emit the fragments `S` and `O` as separate words somewhere
— that is, corrupt a correct `.txt` to match a broken reference. There is no faithful `.txt` of this
page that contains the word `S`, because the page contains no word `S`. So the engine side is not a
candidate, and no combination of the current two parsers makes the engine side a candidate: PDFBox is
the one that already has it right.

### Two smaller fixes that were measured and rejected

Both were built on copies and run over the corpus. Neither is in the patch above.

1. **Rebuild the source side from `get_texttrace()` in content order** (one line per span, glyphs
   wholly outside the page dropped). Fixes 411 (`4,4,0`) — and **makes 83 of 213 documents worse**,
   because a span boundary is not a line boundary: splitting every span onto its own line cuts words
   in half and `t01` then reads them as lost-and-invented. `411` alone would be bought at the price
   of 83 documents. Rejected on the measurement.
2. **Make `t01` abstain when a span cannot be aligned to the declaration.** That condition is true on
   **86 of 213 documents** (the forward-only cursor search in the substitution loop fails whenever the
   declaration's order is not the content order — two-column pages, RTL, Devanagari, and every
   stamp-heavy document; `76_devanagari_table` cannot align 945 of its 969 glyphs). As a rule it would
   move `t01` on 86 documents. Rejected as a way to fix one.

Both numbers are worth recording for their own sake: **on 86 of 213 documents the declaration cannot
be reconciled with the glyph walk at all**, so the source side is quietly missing spans there too. That
is a separate, larger instrument defect than this document; it is named here and not fixed.

---

## What is not established

* **The exact internal rule inside MuPDF** that keeps `C`,`G`,`J` out of `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
  and `S`,`O` out of this line. The measurement localises it to the `TEXT_MEDIABOX_CLIP` path and shows
  the full glyph set is available without it; the subset it keeps in the clipped path is
  string-dependent and I did not characterise it. Not established.
* **Whether `_src_runs()` has the same artefact.** It calls `pg.get_text("dict")` (line ~700) with the
  clip on, so it is the same code path — but `t02_position` and `t08_line_order` both abstain on 411,
  so nothing here is charged for it. Its corpus-wide reach is **not established**; the same one-flag
  change would be the place to look.
* **Whether the writer should clip at all.** `onPage()` drops 4 glyphs of this line. That is a design
  decision with a documented reason and it agrees with what a reader sees; I did not test the
  alternative (emit off-page glyphs) and I am not proposing it.

## Reproducing

    bash tools/p2w-bench/build-engine.sh
    java -cp out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar \
         ConvertOne <corpus>/411_nested_xobject_transforms.pdf /tmp/o
    python3 tools/p2w-bench/verify_txt.py <corpus>/411_nested_xobject_transforms.pdf /tmp/o/411_nested_xobject_transforms.txt
    #   -> 4/12 applicable, 3 passed, 8 abstained   FAIL
    #      t01_word_accuracy   source=100   txt=90.0

The engine fingerprint at every number above is `cd21104b11ed26c1`, the one `install-gate.sh` printed
on this clone. The `.txt` table has to be re-scored (`txt_gate.py --score`) by whoever lands the patch;
the numbers here are the ones the patch produces on the engine as it stands.
