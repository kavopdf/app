# `32_stroke_lines`: the rule is a floating drawing, and `google_safe.py` already names it

Read-only investigation. No engine file, no `google_safe.py`, no `verify_google.py`, no
`verify_txt.py` was edited. No corpus measurement was run; every number below is read out of
`benchmarks/gverify/*.json` and `benchmarks/gverify-lo/*.json`, which are the committed results of
the 21 Nov 10:17 regeneration of `benchmarks/DEFECT-CLASSES-GOOGLE.md`.

## The answer in one paragraph

A rule the page draws is emitted by the engine as a **floating `<w:drawing>` inside a `<wp:anchor>`**,
in its own one-twip carrier paragraph - `DocxWriter.shape()`, `DocxWriter.java:2772`, with
`<w:drawing>` opened at **`DocxWriter.java:2782`** and `<wp:anchor ... behindDoc="1">` at
**`DocxWriter.java:2783`**. The engine emits no `w:pBdr`, no `w:pgBorders` and no `v:line` anywhere
(`grep -rn "pBdr\|pgBorders\|v:line" app/src/main/java/` returns nothing), so this is the **only**
way a rule leaves this writer. `tools/p2w-bench/google_safe.py` already lists it as a construct Google
does not honour, twice: `("w:drawing", "floating-drawing", re.compile(r"<w:drawing>"))` and
`("wp:anchor", "anchored-object", re.compile(r"<wp:anchor\b"))`, both citing
`FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`. So this is **branch (2) of the question, not
branch (3)**: we already know Google ignores it, and it must be re-expressed. The safe construct that
replaces it is a `<w:pBdr><w:bottom .../></w:pBdr>` on an otherwise empty one-twip paragraph whose
`w:ind` left/right are the rule's x range and whose `w:spacing w:before` is the gap from
`ctx.flowY` - the engine already writes exactly this construct for table sides, at
`DocxWriter.java:5528` (`borders()`) and `DocxWriter.java:6420` (`<w:tcBorders><w:bottom .../>`), so
the pattern is in the file, just not on the rule path.

## The three documents

Picked from the 144 `LibreOffice draws it, Google does not` documents - Google fails
`32_stroke_lines`, LibreOffice does not, both renders present (`status: ok`, i.e. not one of the 21
`page_count_refused`).

| document | Google | LibreOffice | rules on the page |
|---|---|---|---|
| `394_map_with_legend` | fails **only** `32_stroke_lines` (41/42) | 42/42 | **3**, 0 lost |
| `407_id_card_front_back` | fails **only** `32_stroke_lines` (41/42) | 41/42, fails only `14_filled_shapes` | **46**, 0 lost |
| `315_gazette_notification` | fails `32_stroke_lines` + `05_chars_extra` (40/42) | 42/42 | **5**, 0 lost |

Two of the three fail nothing but `32_stroke_lines`; they are the two documents in the whole 144 that
do (`394_map_with_legend`, `407_id_card_front_back` - the same pair `FIXER-BRIEF.md` names as
one check away from clean). The third is the pair case, and it is the more informative one.

**Read the JSON field carefully before you quote it.** `32_stroke_lines` is stored as
`(len(s_rules), len(s_lost), not s_lost)` - `verify_google.py:2837`. The second field is **rules LOST**,
not rules rendered, even though it sits under the key `render`. `{'source': 5, 'render': 0, 'ok': True}`
means five rules on the page and **zero lost**, not five rendered as nothing. This misreading has cost
a wrong verdict before and it is called out in the comment right above the assignment.

What the three say together:

* LibreOffice loses **0 of 3**, **0 of 46**, **0 of 5** rules. The bytes it is given are drawable.
  The rules are not missing, malformed, zero-width or lost in a run property - the instrument that
  can see them sees every one, at the right place, at the right weight.
* Google loses enough of them to fail the check on all three. Nothing about the *geometry* changed
  between the two renders: same `.docx`, same engine, same instrument.
* `394` and `407` have **0 extra characters** in LibreOffice and Google fails them on `32` only -
  no `05_chars_extra`. `315` fails **both** `32` and `05`. That split is the fingerprint:
  `05` failing on a document whose source has no stray character means the render *gained* a
  character, and the character Google leaves behind at a floating drawing's anchor is `U+200B`.
  A rule that is simply mis-drawn does not manufacture a character; a rule whose **anchor** is
  kept while its **shape** is not does.
* `08_image_count` cannot settle this either way and must not be quoted as if it could: it passes
  when `g_imgs >= s_imgs` (`verify_google.py:4745`), so a render that gained one raster image per
  drawing passes, and a render that dropped them all passes too. It fails on **0 of 191** Google
  documents. `394` and `315` carry 0 images on both sides and `407` carries 1 on both sides, so on
  these three the check says nothing at all.

The measured confirmation that Google drops the shape is in
`FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`: on `18_centred_heading_left_body_txtpos` the
`.docx` holds `<w:pBdr> 0`, `<w:tcBorders> 0`, `<w:tbl> 0`, `<w:drawing> 2`, the source draws 2 rules,
the Google render draws 0, and the render's only extra word is one `U+200B`. Two drawings in, two
rules out, one anchor left over.

## (1) The construct, file and line

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`

    2772:  private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
    2779:      sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")                       <- carrier paragraph
    2780:          .append("<w:spacing ... w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
    2781:          .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
    2782:          .append("<w:r><w:drawing>")                                            <- THE CONSTRUCT
    2783:          .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")   <- and its wrapper
    2785:          .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
    2787:          .append("<wp:positionH relativeFrom=\"page\">")                        <- absolute page x
    2789:          .append("<wp:positionV relativeFrom=\"page\">")                        <- absolute page y
    2791:          .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy)
    2793:          .append("<wp:wrapNone/>")
    2823:          .append("</wp:anchor></w:drawing></w:r></w:p>");

The call site is `emitBlock()`, `DocxWriter.java:2281` - `if (!s.consumed) shape(sb, s, ctx);` - so
**every shape that no table side and no stamp frame has claimed goes out as a floating drawing.** A
hairline (`isHairline()`, `DocxWriter.java:2845`: one side <= 1.5 pt, the other > 2 pt) is exactly what
that means for a rule, and it is the same 1.5/2 pt test `verify_google._strokes()` and
`PdfToWord.bandFillStroke()` use, so the writer and the instrument agree on what a rule is.

The two other `<w:drawing>` emitters in the file are **not** the rule path and must not be confused
with it: `DocxWriter.java:2441` is `<wp:inline>` inside `picture()` (`2434`), `2475` is `anchoredPicture()` (`2466`), and
`5447` is `stampBox()` - the rotated text box that carries a stamp and its frame.

What the engine does **not** emit, verified by grep over `app/src/main/java/`:

    w:pBdr        0        w:pgBorders   0        v:line   0        v:rect   0

So a rule is never a paragraph border, never a page border, never a VML line, and never a table-cell
border unless the rule happens to lie on a table side (`borders()` at `5528` writes `w:tblBorders` for
the page's own six sides; `6420` writes a `w:tcBorders` bottom for a row separator). A standalone rule
on blank paper - which is what `394`'s 3, `407`'s 46 and `315`'s 5 mostly are - has exactly one route
out of this engine: `shape()`.

## (2) `google_safe.py` already knows it

Yes, twice, and the entry names this exact finding:

    ("w:drawing", "floating-drawing",
     re.compile(r"<w:drawing>"),
     "FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md: Google does not lay out floating drawings from "
     "an imported .docx. It drops the shape and leaves the anchor."),
    ("wp:anchor", "anchored-object",
     re.compile(r"<wp:anchor\b"),
     "Same as above: an anchored object is the wrapper a floating drawing arrives in."),

The docstring of the same file lists it in the four-construct table: `floating <w:drawing> rules -
Google drops the shape - 143 documents`. `FIXER-BRIEF.md` gives the same verdict in its forbidden
list (`floating <w:drawing>` / `wp:anchor`, "drops the shape, keeps the anchor, 143 documents") and in
the "What to use instead" table, which already prescribes the replacement in one line: *"a rule - a
floating drawing is dropped; give it to the paragraph the page drew it above, as that paragraph's own
border, or to the table row's border."*

So this is not a "written wrong" defect. The width is not zero, the fill is not suppressed, the run
property is not lost: the engine writes a well-formed drawing at the correct page coordinate and
Google declines to lay it out. **The construct is the defect.**

**The safe construct that replaces it**, in the engine's own idiom:

    <w:p><w:pPr><w:snapToGrid w:val="0"/>
      <w:pBdr><w:bottom w:val="single" w:sz="<width*8>" w:space="0" w:color="<rgb>"/></w:pBdr>
      <w:ind w:left="<x*20>" w:right="<(pageW - x - w)*20>" w:firstLine="0"/>
      <w:spacing w:before="<gap from ctx.flowY>" w:after="0" w:line="1" w:lineRule="exact"/>
      <w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr></w:pPr>
      <w:r><w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr><w:t xml:space="preserve"> </w:t></w:r></w:p>

`w:pBdr` is honoured by Word, LibreOffice and Google Docs. It was **measured through Google before it
was written**: a minimal `.docx` with one bottom border renders the rule in both renderers
(`FINDINGS/RULES-PBDR-FIX-MEASURED.md`), and on `18_centred_heading_left_body_txtpos` the conversion
took `rules drawn 0 -> 2` in Google. The construct is not a hypothesis; it has been through Google.

The full implementation, including the two lines that are easy to omit and expensive to get wrong
(`ctx.flowY = s.topPt` after writing the border, or every paragraph below the rule drifts and
`18_displacement` - the second-largest class - gets worse), is
`FINDINGS/RULES-PBDR-IMPLEMENTATION.md`. It is not restated here.

## (3) What is written wrong even though the construct is the defect

Worth recording because it will bite whoever lands the border, and because one of these three
documents fails for a reason the drawing alone does not explain:

* **The carrier paragraph is charged by Google even when the shape is not.** `shape()` wraps each
  drawing in its own paragraph asking for `w:line="1" w:lineRule="exact"` (line 2780). Google's
  advance is not `w:line/20`: it is `w:before + max((w:line/240) * lineHeight(face, size), 0.069 * size)`
  - `DocxWriter.java:79` - so a dropped drawing still costs vertical space. 93 of the 144 also fail
  `18_displacement`. The fix must **remove the carrier**, not just the drawing: a `ruleAsBorder()`
  that returns before line 2779 does exactly that, because it writes its own paragraph instead.
* **A light rule whose fill is suppressed becomes a blank image and counts as a lost rule.**
  `fillXml()` drops any fill within `PAGE_TOL` of the page (`DocxWriter.java:2888`, the `isPageColour()` test at `2833`), and
  `verify_google._stroke_pictures()` explicitly refuses to count a thin band with no ink as a
  surviving rule. This is already guarded for hairlines - `mustPaint` is
  `s.lineRgb < 0 && isHairline(s)` at `DocxWriter.java:2809` - so it is **not** the live cause here,
  but any rewrite of this path must keep that guard.
* **`behindDoc="1"` and `wp:wrapNone`** (lines 2785, 2793) are correct for a rule drawn behind text
  and should not be read as the fault. They are inside the anchor Google ignores.

## What this predicts, and how many of the 144 it clears

`32_stroke_lines` is the largest class and it is one construct, so the ceiling is the whole class:

    documents failing 32_stroke_lines in Google      145   (of 192 with both renders)
    of which LibreOffice draws every rule            144   <- the class
    LibreOffice also fails 32                          1   (Account_Opening_Form_Fillable_filled,
                                                            itr-computation-with-slab-table per
                                                            the raw JSON; the table counts 1)

Counting from the JSON, of the **144**, how many fail *nothing but* the checks this one construct owns
(`32_stroke_lines`, `05_chars_extra` for the anchor, `18_displacement` for the carrier):

| Google failure set among the 144 | documents |
|---|---:|
| `32_stroke_lines` only | **2** (`394_map_with_legend`, `407_id_card_front_back`) |
| `32` + `05` only | **15** |
| `32` + `05` + `18` only | **15** |
| **no other failing check at all** | **32** |
| also fails something else (04, 59, 25, 60, 45, 44, 13, 17, 47, 27 ...) | 112 |
| of the 144, fails `05` too (the anchor is visible) | 124 |
| of the 144, fails `32` **without** `05` | 20 |

**Prediction, stated as a number and as the evidence behind it:**

* **`32_stroke_lines` itself: I predict it clears on at least 124 of the 144, and I expect 144.** The
  124 are the documents that also fail `05_chars_extra` - the leftover `U+200B` proves a floating
  drawing was there and that its anchor outlived it, so the shape and the fix are the same object. The
  other 20 fail `32` without an extra character and this finding does not explain them: they are the
  ones to look at first if the class does not reach zero (a rule in a header/footer, a rule that lies
  on a table side and is already a `w:tcBorders`, or a rule that arrived as a blank raster image).
  The measured residual on the one probe document was exactly one rule at y=797 - a **footer** rule -
  which this change does not reach unless the same path is applied there.
* **Documents that become completely clean: 32, taking the clean count from 7 to up to 39.** These are
  the 32 whose entire Google failure set is `{32, 05, 18}`; the 2 that fail `32` alone are certain if
  the border lands at all, the 30 that fail `32+05` are near-certain, and the `18` in the
  `32+05+18` group clears only if the border is placed from `ctx.flowY` rather than from flow.
  `FIXER-BRIEF.md` says this fix takes clean from 7 to 10; that figure counts only the three
  one-check-away documents (`394`, `407`, `382`) and **understates the class by 29 documents**, because
  it does not count the `32+05` and `32+05+18` documents that this same construct owns.
* **Nothing else should move.** The other 112 keep failing whatever else they fail; the prediction is
  that their `32`/`05`/`18` columns go quiet and their other columns do not change. If any of those
  112 gains a check, the border is in the wrong place - `18_displacement` first, then
  `60_text_column_right_edge` if the `w:ind` range is wrong.

## What would prove this wrong

1. A Google render of `394_map_with_legend` or `407_id_card_front_back` in which `32_stroke_lines`
   passes - i.e. Google does draw those rules - with the `.docx` still carrying `<w:pBdr> 0` and
   `<w:drawing>` equal to the rule count. That would move the defect to the instrument or to a second
   construct and make this finding wrong at the root.
2. A `.docx` for one of the three in which `32_stroke_lines`' rules are **not** drawings - e.g.
   `<w:tcBorders>` on a table side, or a `<v:line>`. There is no output directory in this tree, so this
   was not checked by inspection here and is the single cheapest thing to check before the fix is
   written: `google_safe.py <file.docx>` on the three documents, which prints `<w:drawing>` and
   `<wp:anchor>` counts directly.
3. Landing the border and finding `18_displacement` rises: that means the `ctx.flowY` update was
   omitted, not that the construct is wrong.

## Why this was not fixed here

The rules say not to edit an engine file, and the brief's own discipline says the same for a different
reason: the gate needs the whole corpus re-measured (213 renders) and a change that cannot be measured
is a change that is not committed. This is a finding, which is what the brief asks for when a construct
is understood but the measurement is not yet paid for. `FINDINGS/RULES-PBDR-IMPLEMENTATION.md` holds
the code; what it lacks is a corpus pass.
