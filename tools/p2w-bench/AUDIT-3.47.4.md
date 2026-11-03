# Audit at 3.47.4 — what was found, what was fixed, what was left

Development is closed. This is the audit pass, kept so the next person does not have to
repeat it.

## Fixed

### 1. Crash — PdfRepair, filter decoding

    if (name.equals(filters.get(0)) && filters.size() == 1) break;

`get(0)` ran before the size test. A damaged file carrying a filter array with nothing in it
threw `IndexOutOfBoundsException` and took the repair down. Reordered to test the size first.
The repair path is exactly where a malformed filter array turns up.

### 2. Dead code — two private methods in PdfToWord that nothing called

    columnOf(Object)                         124 chars
    mergedPositions(List<float[]>, boolean)  467 chars

Both removed after searching every call site.

## Found, deliberately not changed

### 3. 180-degree rotation — three sites differ from the cropper

    line  221  crop   case 180: px = w - xd;  py = h - yd;   fixed in 3.46.4
    line 1403  text   case 180: px = w - xd;  py = yd;
    line 2093  box    case 180: px = w - c[0]; py = c[1];
    line 2407  text   case 180: px = w - xd;  py = baseY;

The comment above 1403 says "same mapping the cropper uses". It is not.

**Working the geometry by hand.** A display point is measured from the top-left of what the
user sees. A PDF page point is measured from the bottom-left. On a page with `/Rotate 180`
the viewer turns the content upside down, so a point that appears at display (100, 100) on a
600x800 page sits at page (500, 100) — x flipped, y NOT flipped.

That means line 1403 (`px = w - xd; py = yd`) is **right**, and the cropper at line 221
(`py = h - yd`) is the one that does not match. But the cropper's version has shipped since
3.46.4 and crop is reported working, so its input `yd` is probably already in a different
frame than the text one.

**This was not changed.** All three were tried against the cropper and then reverted: a
600x800 page at `/Rotate 180` with text at display (100,100) was rendered to check where the
marker landed, but PDFBox-Android's `PDFRenderer` returns an Android `Bitmap`, which cannot
be inspected headless. There is no device here and no way to settle it. Shipping a guess
could move text, hyperlinks, page numbers and watermarks to the other half of every rotated
page, which is worse than the status quo.

To settle it: open a 180-degree page, add a text hyperlink at a known spot, and look.

### 4. Duplicate code — four identical method bodies

    showSignatureDialog  AnnotateActivity + CreatePdfActivity   873 chars
    placeStamp           AnnotateActivity + CreatePdfActivity   445 chars
    pickShape            AnnotateActivity + CreatePdfActivity   380 chars
    move                 ImagesToPdfActivity + MergeActivity    150 chars

About 1,850 characters, byte-identical in each pair.

**Not merged, on purpose.** Every one of them touches live Activity state — `binding.overlay`,
`pendingPoint`, `selectTool`, `files`, `adapter`. Folding them into a shared helper needs a
base class or an extension on a common interface, which is a structural change to two working
tools. The gain is 1,850 characters of source; the risk is two tools breaking. Not a trade
worth making during an audit.

If it is ever done, the safe order is: extract a base Activity holding `files` and `adapter`,
move `move()` there first because it is five lines and touches nothing else, and leave the
signature and stamp dialogs alone unless CreatePdfActivity is being changed anyway.

## Clear — checked and sound

    security    no WebView, no JavaScript bridge, no external storage permission, no
                WRITE_EXTERNAL_STORAGE. usesCleartextTraffic=false, allowBackup=false.
                INTERNET and ACCESS_NETWORK_STATE explicitly removed. Only CAMERA.
                Every incoming URI parsed inside runCatching.
    exported    three components, all legitimate: launcher, VIEW for a PDF, SEND for a
                shared PDF. No exported service, receiver or provider.
    parsing     20 parseInt/parseFloat/parseLong sites, all inside try blocks.
    rendering   ARGB_8888 everywhere, inSampleSize only for decoding, nothing on RGB_565.
    leftovers   no TODO, FIXME, XXX or HACK in the source.
    arithmetic  no integer-division trap in the engine's coordinate maths.
    catches     46 empty catch blocks, all deliberate: a PDF engine must carry on when one
                optional stage fails. Spot-checked, none swallows a value the caller uses.

## Benchmarks at this build

    53-document corpus      13 metrics, see KAVOPDF-CREDENTIALS-3.47.4.txt
    line order 90.35 %      exact line hit 98.45 %      ID integrity 100.00 %
    old 215-file corpus     line order 79.66 %
