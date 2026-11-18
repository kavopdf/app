# content-missing-nothing-in-its-place / A - the engine code path

Asked: what mechanism places the inline image of `415_inline_images` page 1 at the wrong place
       or the wrong size, given share@5px 89.04, text_recall 100.0, chars_missing 0, and a
       reported 92 pt median / 153 pt max displacement?

Claim: nothing is displaced and nothing is the wrong size. The image's ink is not painted at all.
       The engine writes the picture into `word/media/image1.png` with the image's own grey
       sample in the ALPHA channel, so every dark pixel of a DeviceGray image becomes fully
       transparent and the checkerboard disappears. The "92 pt displacement" is the distance
       from that vanished ink to the nearest ink that survives - the two text lines below it.

       File/function/line:
         app/src/main/java/com/kavopdf/app/engine/PdfToWord.java:6160, inside
         `RuleCollector.decodeImage(PDImage, float[])` - `android.graphics.Bitmap b =
         img.getImage();` (returned at 6161). That bitmap is ARGB_8888 with `hasAlpha=true` and
         alpha == the grey sample. `collectImage` (6069) folds a mask in only when the PDF
         declares one (6118, `withMask`), and this page declares none, so the alpha survives
         untouched into `encodePng(bmp, frame)` at 6125, whose `Bitmap.compress(PNG)` writes a
         colour-type-6 PNG carrying it. `DocxWriter.java:734-736` then copies those bytes
         verbatim into the zip.

Mechanism (one paragraph): The page paints its picture with an *inline* image -
       `q 120 0 0 120 56 620 cm BI /W 8 /H 8 /CS /G /BPC 8 /F /AHx ID <64 hex bytes> EI Q` -
       i.e. 8x8 samples of DeviceGray with no /Decode, no /Mask and no /SMask, so every pixel is
       opaque by construction and black is simply 0. pdfbox-android's `PDImage.getImage()` packs
       that one-component sample into all four ARGB lanes instead of only the three colour lanes
       (`g<<24 | g<<16 | g<<8 | g`, where it should be `0xFF000000 | g<<16 | g<<8 | g`), so a
       black sample 0x00 arrives as 0x00000000 - alpha 0 - and a white sample 0xFF arrives as
       0xFFFFFFFF. The engine takes that bitmap at face value: `decodeImage` returns it
       unmodified, `collectImage` has no "this image declared no transparency, so force alpha
       opaque" step (it only ever *adds* a mask, never removes a spurious one), and `encodePng`
       preserves the alpha it was given. The .docx therefore carries an 8x8 RGBA PNG whose alpha
       equals its luminance: black ink is 100% transparent, white is opaque white. LibreOffice's
       PDF export round-trips that alpha faithfully (it writes an /SMask with data 255-at-black
       plus `/Decode [1 0]`, i.e. net alpha = luminance), and the mupdf render the bench measures
       composites black-on-transparent over white paper and produces nothing. Placement, scale and
       the media-box origin are all correct - the picture is pinned at exactly the right rectangle
       and simply not visible inside it.

Evidence (numbers, probe output):

  1. The page's content stream, read whole (381 bytes), is the entire page:
         q 120 0 0 120 56 620 cm BI /W 8 /H 8 /CS /G /BPC 8 /F /AHx ID 00FF00FFFF00FF00... EI Q
         BT /F1 11 Tf 56 580 Td (The checkerboard above is an inline image - BI ... ID ... EI.) Tj ET
         BT /F1 11 Tf 56 560 Td (It has no object number and lives inside the content stream.) Tj ET
     MediaBox [0 0 595 842], CropBox the same, /Rotate 0, `page.get_images()` returns [] (it is
     inline, so there is no XObject to find).

  2. Placement is right, so CTM/scale/origin are not the defect. Our render's image XObject sits
     at bbox (56.0, 101.95, 176.0, 221.95) - the source's `120 0 0 120 56 620 cm` puts it at
     56..176 x 102..222 in top-down coordinates. Same rectangle to 0.05 pt, same 120x120 pt size,
     same 8x8 pixel data. The text is byte-identical in position too.

  3. The ink is gone, not moved. Rendering both pages at 150 dpi and counting ink (<68):
         source total ink 34,954 px;  inside the image block (x 110-370, y 200-470) 31,000 px
         ours   total ink  3,921 px;  inside the image block                          0 px
     share@5px (source ink px with no render ink within 5 px) = 89.04%, median 85.46 pt,
     p90 139.50 pt, max 153.23 pt - reproduces the census figures.
     Of the 31,124 missing source ink pixels, 31,124 (100.00%) lie inside the image block, and
     **0** missing pixels lie outside it. Nothing else on the page is displaced by even 5 px.

  4. The alpha is the grey sample. Raw PNG from the delivered docx, `word/media/image1.png`:
     80 bytes, IHDR (8, 8, 8, colour-type 6 = RGBA), all 8 rows identical:
         row 0 = (0,0,0,0) (255,255,255,255) (0,0,0,0) (255,255,255,255) ...
     Source sample row is 00 FF 00 FF FF 00 FF 00 - so alpha == luminance, black -> alpha 0.

  5. It comes from pdfbox, not from the engine. A standalone probe (`ImgProbe.java`, subclass of
     `PDFGraphicsStreamEngine`, compiled against the same `libs/aar/classes.jar`, no engine code
     involved) prints for this page:
         class=PDInlineImage  isStencil=false  w=8 h=8 bpc=8 cs=DeviceGray
         bmp 8x8 hasAlpha=true config=ARGB_8888
         row0 = (00000000) (FFFFFFFF) (00000000) (FFFFFFFF) (FFFFFFFF) (00000000) ...
     A second fixture built for the purpose (same 8x8 grey as an ordinary `/Im1 Do` XObject)
     gives the identical poisoned row, so this is the DeviceGray decode path generally, not an
     inline-image-only quirk. A third fixture, the same 8x8 painted `/CS /RGB`, comes back
     `hasAlpha=false`, `(FFFF0000)` - the RGB path is clean, which is why only grey images die.

  6. Causal proof - change the alpha and nothing else. Copy of the delivered docx with every
     pixel of `word/media/image1.png` rewritten to (r, g, b, 255); same RGB, same size, same
     anchor, same XML, re-zipped and converted through the same soffice -> PDF -> mupdf pipeline:
         as delivered         ours ink  3,921   share@5px  89.04%   median 85.46   max 153.23
         alpha forced opaque  ours ink 35,045   share@5px   0.00%   median  0.00   max   0.48
     One byte per pixel of one media file takes the page from 89% to 0%.

  7. Independent confirmation that the PDF side is LibreOffice being faithful, not a second bug:
     the exported PDF's SMask stream is the *inverse* of the PNG alpha with an inverting
     `/Decode [1 0]` on the dictionary, so net alpha == luminance. Forcing the SMask opaque in
     place (`xref_set_key(6, "Decode", "null")` or `xref_set_key(4, "SMask", "null")`) restores
     all 31,000 px in the image block - i.e. the PDF says exactly what the PNG said.

How to test it: `PdfToWord.java:6160` should not hand back an alpha the PDF never declared. The
       narrow fix is in `collectImage`/`decodeImage`: when the source image declares no /SMask,
       no /Mask, no /SMaskInData and is not stencil (6118 already knows all four facts), replace
       the returned bitmap with an opaque copy - `Bitmap.createBitmap(w, h, ARGB_8888)` filled
       with `0xFF000000 | (px & 0xFFFFFF)` - before `encodePng` at 6125. Rebuild, then
       `python3 benchmarks/p2w.py --diagnose 1` and re-measure: 415_inline_images should go to
       share@5px 0.00 / max 0.48 and text_recall must stay 100.0. A cheaper one-line variant is
       to pack the grey sample in the RGB lanes only when `img.getColorSpace() instanceof
       PDDeviceGray`, but the alpha-normalising fix also protects against any other decode path
       that invents alpha.

Ruled out (each checked, not assumed):
  - The CTM / image matrix / `/Im` scaling / MediaBox origin. The picture lands at
    56,101.95..176,221.95 against a source of 56,102..176,222; 120x120 pt both sides. There is no
    `/Im` here at all (inline BI/ID/EI), and `collectImage:6086-6100` transforms the unit square's
    four corners through the current matrix, which is the correct construction.
  - Rotation. Page `/Rotate 0`; both renders are taken with rotation forced to 0.
  - ReadingOrder.java. One page, two text lines, both already in the right order and the right
    place (0 missing pixels outside the image block); the file is 3.3 KB and has nothing to do
    with image placement.
  - DocxWriter.java as the cause. It is a carrier: 734-736 writes `ctx.media.get(i)` to
    `word/media/imageN.png` unchanged, and `Picture` (2323) only holds the bytes plus the anchor.
    Rewriting those bytes fixes the page with no other change (evidence 6).
  - `/Decode`, `/Mask`, `/SMask`, `SMaskInData`, stencil on the source image - none is present.
  - `withMask` (6040) as the cause - it is never called here; there is no mask to fold in.
  - Fonts / text path - text_recall is 100.0 and 0 text pixels are missing.
  - A second-order effect of `encodePng`'s retry ladder (6211) - it succeeded on attempt 1, and
    the PNG it wrote is a valid 80-byte RGBA file, not a truncated one.
  - Instrument error in the bench itself - the same measurement read on a page where only the
    alpha byte changed went 89.04 -> 0.00, so the ruler is reading the alpha.

Confidence: high. Six independent lines of evidence, and a one-byte-per-pixel edit that flips the
       score to 0% without touching geometry.

What would prove me wrong: a DeviceGray image that survives the same pipeline with
       `hasAlpha=true` and ink still on the page - i.e. a case where alpha == luminance renders
       as ink - or a 415_inline_images conversion in which `word/media/image1.png` is opaque and
       the page still scores 89% share@5px. Either would mean the alpha is a symptom and the ink
       is being lost somewhere downstream of the .docx.

Scope note: this is the DeviceGray decode path, so it should not be read as specific to
       415_inline_images or to inline images. Any picture the engine carries out of a DeviceGray
       image (an ordinary grey XObject too - evidence 5) loses its dark ink the same way; a
       corpus-wide count of DeviceGray images would size the class.

Status: complete
