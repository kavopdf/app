# Text is clipped at the bottom in every document, and the cause is `w:lineRule="exact"`

The user spotted this by eye on `74_balance_sheet_indented_subitems`: **"payables"** loses the bottom of its
`y`, and **"gratuity"** loses the bottom of its `y`. Descenders are cut off across the page. The user's
words: *"almost maximum of the documents me yeh problem"*.

They are right, and it is not a document problem. It is every document.

## Measured

    total docx                       213
    with w:lineRule="exact"          213   (100%)
    with w:lineRule="atLeast"          0
    with w:lineRule="auto"             0
    with no lineRule at all            0

## The mechanism, from the XML of the exact paragraph that clips

The paragraph containing "Trade payables" in that document:

    <w:pPr>
      <w:pStyle w:val="TableText"/>
      <w:snapToGrid w:val="0"/>
      <w:spacing w:before="262" w:after="0" w:line="12" w:lineRule="exact"/>
      <w:ind w:left="348"/>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman"/> <w:sz w:val="17"/></w:rPr>

`w:sz w:val="17"` is **8.5 pt** of text. `w:line="12"` with `w:lineRule="exact"` is **12 twentieths of a
point = 0.6 pt** of line box.

**A 0.6 pt line box cannot hold an 8.5 pt glyph.** Everything outside the box is clipped, and what is outside
is exactly the descender.

## Why the engine does this, and why the obvious fix is wrong

The engine positions every text line **absolutely**: the vertical place comes from `w:before` (here 262
twentieths = 13.1 pt), and `w:line` is set near zero so that one line's height does not push the next line
down. That is a reasonable model for a PDF converter - the PDF gives a baseline, not a line height.

**But `lineRule="exact"` does two things at once: it fixes the height AND clips to it.** There is no OOXML
value that means "zero height contribution, do not clip".

**So the one-word fix - `exact` to `atLeast` - is wrong.** `atLeast` gives the line its natural height
instead of 0.6 pt, so nothing clips, but **every line then contributes ~10 pt of height that it did not
contribute before, and the whole document shifts down and grows.** That trades a clipped descender for a
broken layout, which is worse.

## The fix that actually works

**Raise `w:line` to the font's natural line height and subtract the same amount from `w:before`.** The line
box then contains the glyph, and the line's top stays where it was:

    natural   = font_size * 1.15        (8.5 pt -> 9.8 pt -> 196 twentieths)
    new_line  = natural
    new_before = before - (natural - old_line)

    74's "Trade payables":  before 262, line 12, font 8.5 pt
                            natural 196
                            new before = 262 - (196 - 12) = 78
                            new line   = 196

**The line's position is preserved to the twentieth of a point and the clip is gone.** This is arithmetic, not
a judgement, and it can be verified on one document before it is applied to 213.

## What is not known yet

- **Whether Google and LibreOffice both honour the arithmetic the same way.** They do not agree on everything
  - the whole reason Google is the reference - so this needs one document through a real Google export with
  the two numbers measured before and after: the ink's top edge and the ink's bottom edge, per line.
- **Whether `w:before` can go negative** where `before` is already smaller than `natural - old_line`. It can
  in OOXML, but it needs checking rather than assuming.
- **Whether the same clip happens in table cells**, which carry their own row heights. `74` is a table-shaped
  document and its paragraphs carry `pStyle="TableText"`, so this is not hypothetical.

## Do not

- **Do not switch to `atLeast` and stop there.** It removes the clip and breaks the layout.
- **Do not raise `w:line` without lowering `w:before`.** Same mistake, same result.
- **Do not treat this as a per-document fix.** It is 213 of 213, and the arithmetic is the same everywhere.
