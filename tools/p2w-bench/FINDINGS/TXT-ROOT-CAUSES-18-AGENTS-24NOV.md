# The six failing .txt checks, root-caused by 18 parallel investigations

**24 Nov 2026.** Six classes, 21 document-failures. Eighteen agents, three approaches each: read the
check, work from the output, read the engine. Every one that reported built the engine and reproduced
its numbers, so these are measurements, not opinions.

## The headline

**Most of the .txt "failures" are the check's fault, not the engine's.** Of the 21 document-failures,
13 are false positives, 5 are real engine defects, and 3 are real defects the check is not measuring.

| class | docs | verdict | who is wrong |
|---|---:|---|---|
| t09_page_furniture | 2 | **false positive, 4 of 4 agents agree** | check |
| t02_position | 4 | **false positive, 3 of 3 agree** | check |
| t01_word_accuracy | 3 | 2 false positives, 1 mixed | check (39, 601) · both (77) |
| t12_word_invention | 8 | 5 false positives, 3 real | check (5) · engine (3) |
| t06_encoding | 2 | real, but the reference hides it | engine + reference together |
| t08_line_order | 2 | not yet reported | — |

## t09_page_furniture — the check counts two different populations

`owed` is counted in the top/bottom 12 % band of each page; `present` is a Counter over **every line of
the whole file**. Any furniture key that also occurs in body text therefore makes present > owed
unconditionally. On 041122: owed 29, present 125, over a file that carries its page numbers once each,
in order.

What it calls furniture on that form is the date field — the page draws `D D M M Y Y Y Y` as eight
one-character spans, three date boxes fall in the band on three pages, and `Y`, `D`, `M` each clear
FURNITURE_MIN_PAGES. The document's only real furniture is the page number `1`–`9`, which
`_furniture_key` folds to `#` and the `any(ch.isalpha())` filter then discards.

**Fix, written and unit-tested:** `FINDINGS/t09-FIX-band-scoped-present-and-no-one-char-keys.patch`.
- one-character keys are no longer furniture
- `present` is counted in the same band, recovered from the writer's U+000C page segments

Falsifiability test on a synthetic 3-page file: intact reports 3 copies of the header and 3 of the
footer; deleting the footer reports 0; deleting the header reports 0. Caught a bug in the first version
of the patch on the way — `chr(12)` is whitespace in Python, so `_ln.strip() == chr(12)` never matches
and the file never splits into pages.

**Not committed**: the rule is no commit without a full-corpus regression check, and 213 .txt outputs
cannot be regenerated from here. The fixer must run the corpus pass.

## t02_position — three false assumptions

1. It pairs spans to .txt lines in **content-stream order**, which is not reading order. `t08` already
   fixed this for itself and its comment says so; `t02` still reads the old order.
2. It keeps `span.bbox[0]` after stripping the text, so a span beginning with spaces reports the space's
   x, not the ink's (74_balance_sheet: x=56.00 for ink at 73.40).
3. It fits one character width from `median(x/col)`, which collapses under integer rounding: 334 gets
   5.60 where the engine's own `TxtWriter.documentCharWidth()` returns 5.10, a 9.8 % error against an
   8 % tolerance.

Correcting the three takes the four documents to **100 %, 100 %, 96 %, 98 %**, all above the 90 % bar.
Underneath, two small real faults exist that t02 does not catch: two paragraph-path sub-items indented 3
columns short in 74, and one merged cell row in the price list.

## t01_word_accuracy — it compares words, not characters

`Counter(words(src)) - Counter(words(txt))`, so any disagreement about where a word boundary falls is
scored as a lost word. On 39 and 77 the non-space character multisets are **identical on both sides**.

- **39** — PyMuPDF inserts spaces at 0.15 em, the engine breaks at 0.18 em, and this document's letter
  spacing sits between them. The page draws `570 005`; the .txt says `570 005`; the reference says
  `57 0 0 05`. The .txt is right.
- **601** — two ZapfDingbats check marks decoded as the digit `3` through `/WinAnsiEncoding`. No correct
  .txt can pass: a file carrying `✓` would still lose 2 of 82 words.
- **77** — the reference is in visual (pre-bidi) order and fuses runs the .txt correctly separates. There
  IS a real bidi defect: `logicalOrder()` moves the colon past the number, because
  `Character.isWhitespace('\u00A0')` is false in Java so the NBSP is swept into the LTR run.

## t12_word_invention — token multiset, so re-flow invents words

In 5 of the 8 documents the .txt has **exactly the same non-space character multiset** as the source —
0 extra, 0 missing — and every "invented" word is a fragment of a source token: a letter-spaced pincode
(`57 0 0 05`), a superscript footnote digit welded to its word (`incorrectly.2`), an RTL cell number
welded to its label, a curved seal drawn glyph by glyph.

**Proposed comparison** (measured: 0 invented on all five, 83 and 14 on the three that are real):

    src_c = Counter(re.sub(r"\s+", "", src_text));  txt_c = Counter(re.sub(r"\s+", "", txt_text))
    invented = sum((txt_c - src_c).values())

The 3 real ones: `600_reviewed_invoice_with_annotations` emits annotation text twice (+83 characters),
and both account forms emit `(Authorised signatory)` twice (+14). For 600 the code path is named:
`PdfToWord.pageText()` builds `pageOwn` then calls `readAnnotationAppearances()`, which appends into the
same `glyphs` list the de-duplication guard was built from — so the guard can never match.


## t12, third approach: the one path that ADDS characters, named to the line

The engine-writer investigation converted all 8 documents, dumped the engine's own model (table rows,
paragraph lines) for the failing pages, and compared characters rather than words:

| document | invented chars | missing chars |
|---|---|---|
| 05 seal, 311 fir, 39 small-caps, 77 arabic, journal-2col | **none** | none |
| 600_reviewed_invoice | **+83** | none |
| 041122 / Fillable | +13 | 8 / 13 |

Five of the eight carry **not one character the PDF does not draw**. Their invented words are the same
characters grouped into different tokens - which settles the t12 fix: compare characters, not tokens.

**The only path that adds characters is `PdfToWord.annotationRuns`, line 2456, called at 956.**

It takes `getContents()` from **every** annotation with no subtype filter and appends it as a body
paragraph at `top = 0`. Its only guard is `flat.contains(...)` against the content stream - but a
FreeText's words are drawn by its `/AP`, not by the content stream, so the guard can never match.

Proof, on 600_reviewed_invoice_with_annotations: the first line of its .txt is
`Rate for HSN 8536 confirmed with PO.` - a `/Text` sticky note whose appearance stream draws **no text
at all** (PyMuPDF returns an empty string for it). Seven words that exist nowhere on the page.

The same loop then duplicates the FreeText's sentence (13 more characters) because it lacks the
`drawnByAppearance(apDrawn, ...)` guard that the `/V` loop at line 947 already has.

**So 600 has one fix with two halves, both in the same function:** stop hoisting `/Text` sticky notes
(they draw nothing, so their body is a comment, not page content), and add the same
`drawnByAppearance` guard the sibling loop already uses.

## t12's other real faults, by mechanism

- **Table-cell welding - 3 of 8** (311, 041122, Fillable). Glyphs are bucketed into columns by x, so a
  value that overruns its cell lands in the neighbour's cell, and `glyphText` welds it there because it
  only inserts a space on a *positive* gap. Engine model dump for 311:
  `row3: [Address] [12/3, ... Bengaluru 5] [60067Mobile] [+91 98450 11223]` - the page draws the address
  at x 141 to 312.5 and the label `Mobile` at x 291, so `60067` was bucketed into Mobile's cell and
  welded, orphaning the `5`.
- **041122's signatory duplication, at output level:** `p4 TABLE row0: [D][D][M][M][Y][Y][Y]
  [(Authorised signatory)Y]` **plus** `p4 PARA line1: (Authorised signatory)`. The paragraph is absorbed
  into a cell *and* emitted again, and a stray `Y` glyph 0.5 pt lower is welded on.
- **Token-boundary rules, no character invented - 4 of 8** (05, 39, 77, journal), four different rules:
  `ringLines` emits one Line per seal character (05), the 0.18 em space threshold (39), `logicalOrder`
  RTL reversal (77), superscript baseline clustering (journal).


## t08_line_order — one real engine defect and one check artefact

The check builds its expected order as `sorted(page lines, key=(round(y,1), x))` where `y` is the **top of
the line's bbox**, then compares within column buckets by LCS.

**305_vaccination_certificate — the .txt is wrong, and the engine defect is named.** The inversion:
the footer at y=776.95 is written 504.3 pt *before* a body line at y=272.68. Cause, proven with an engine
probe: the "words inside the ring" rule (`PdfToWord` ~1259-1284) tests only a line's **midpoint x and y**
against the seal ring's bounding box, with no width or containment test. On this page the ring spans
x 81.22-158.78 and the 244 pt-wide `Issued: 18-03-2022 14:22 IST | Certificate ID: ...` line spans
x 28-271.9, so its **midpoint 149.95 falls inside the ring** and it is swallowed into the 48-line seal
paragraph. That paragraph is appended at the end of the page's block list (`ordered.add(ringPara(ring))`,
line 1629) - after the footer. Replaying the predicate in Python reproduces exactly those 48 lines.

**Fix: give the ring rule a width test** - a line wider than the ring cannot be seal centre text.

**39_small_caps_letter_spacing — the check is wrong.** The inversion is between a 1 pt **white invisible**
duplicate of the title and the 15 pt visible title, drawn at the same x on the **identical baseline**
(user-space y 775.89), one after the other in the content stream. The engine has both at `top = 66.0` and
keeps drawing order. The check's key is bbox top, which for a 15 pt caps line sits 12.5 pt above a 1 pt
line on the same baseline - so it invents a top-to-bottom relation between two pieces of text that are
one visual line.

Decisive test, same predicate, only the vertical key changed:

    document                       key=bbox_top          key=baseline
    305_vaccination_certificate    33/32 FAIL            33/32 FAIL
    39_small_caps_letter_spacing   22/21 FAIL            22/22 PASS

So 305 fails whatever defensible key you use; 39 fails only because the key is bbox top.
**Fix: key on baseline, not bbox top.** The invisible 1 pt layer being emitted at all is a separate real
fault, owned by t01/t12, not by line order.


## t02_position — the whole population, and three corrections that clear it

Corpus-wide measurement: **these four are the only documents that fail t02** (213 converted, 4 fail), so
this is the entire population, not a sample.

Each document flips on exactly one correction and is untouched by the other two:

| x model | ruler | pairing | 332 | 334 | 74 | price-list |
|---|---|---|---|---|---|---|
| x0 (today) | median | text (today) | 78.8 F | 68.8 F | 81.5 F | 86.1 F |
| x0 | median | **nearest column** | **100.0 P** | 68.8 F | 81.5 F | **98.4 P** |
| x0 | **least squares** | text | 78.8 F | **100.0 P** | 81.5 F | 86.1 F |
| **first inked glyph** | median | text | 78.8 F | 68.8 F | **96.3 P** | 85.8 F |

- **332** - the page draws `1` both as a drawing callout (x 77.91, col 20) and as the table's Item
  (x 314.93, col 81). The .txt has both, both right. The check pairs callout to table-cell (+61) and
  table-cell to callout (-61).
- **price-list** - the column multiset per text is identical on both sides (`Nos`: {43x14, 100x18} both).
  The mirrored +-56/57 failures are the two columns swapped, because the writer orders cells row-major
  while the PDF's block order is column-major.
- **74** - every failure is a space-indented line at x0 = 56.0; first ink is at 73.40 (col ~14.5) and
  92.98 (col ~18.4), which is what the .txt has. The check wants 11.
- **334** - 22 of 32 pairs are (28, 5), so the median returns 5.600 where the writer used 5.100
  (= 0.6 x 8.5, per `TxtWriter.documentCharWidth`). A single width of 5.100 explains all 32 pairs.

**All three together: 213/213 pass, 0 regressions** - and it still fails a .txt with randomised indents
(3.6-13.8 % against 96-100 % clean), so it is not a weakening.

**The guards are not optional.** Sorted-multiset pairing alone newly fails 23 documents; first-ink applied
to rotated or RTL lines newly fails 4 (in RTL the first glyph in the array is the rightmost). Both must be
restricted: first-ink on upright, non-RTL lines only, and least-squares over columns of at least 3.

Candidates disproved: right-alignment is not the cause (a right-aligned cell still has an x0 the writer
pads to); rotation is not the cause (0 non-upright lines on all four pages).

**A stale ranking cell, found in passing:** `RANKING-TXT.csv` records 74 as also failing
`t13_amount_columns`, which does **not** reproduce on HEAD - that cell was measured on an older engine
(`b97d8172ce642eb0`). Worth a full rescore, not a hand edit.

## t06_encoding — real, but fixing it alone makes t01 and t12 worse

127 U+FFFD in each account form, which are exactly the ligature inventory: ff 13, fi 89, ffi 23, ffl 2.
Effra's subset has no cmap and no glyph names, and its `/ToUnicode` maps those CIDs to U+FFFD.

**But `glyph_truth()` deliberately rewrites those same CIDs to U+FFFD** ("because that is what the writer
emits for the same glyph"), so both sides carry 127 and t06 fails on the .txt count alone. Measured
counterfactual: deleting the U+FFFD passes t06 and takes t01 from 100 to 98.2, t03 from 8 to 7, t07 from
723 to 596, and t12 from 5 to 132.

**So the U+FFFD is load-bearing, and the reference must be repaired with the engine, never before it.**

## What the fixer should do, in order

1. Apply the t09 patch, run the corpus, confirm 2 documents clear and nothing regresses.
2. Rewrite t02's pairing and ruler; expect 4 documents to clear.
3. Change t12 to a character multiset; expect 5 to clear, 3 to remain for the real reason.
4. Leave t06 until the engine's ligature naming can be fixed — and fix `glyph_truth` in the same commit.
5. t01's 601 needs an engine fix (tick glyphs in checkbox appearance streams never reach the .txt).

Every one of these is a measurement change. None may land without the full-corpus regression pass.
