# The two Account Forms fail t06 because every ligature in them is written as U+FFFD

## The measurement

    t06_encoding   source=47477 glyphs   txt=127 defects   FAIL
    t09_page_furniture  source=29 lines  txt=125          FAIL

127 is not a character count on the .txt side - t06 stores `fffd + bom + enc_err` as its defect count. So the
.txt carries 127 U+FFFD replacement characters.

## What they are

Reading the context around the first ten:

    'lease \ufffdll '     -> "Please fill up"
    'h to a\ufffdx r'     -> "affix"
    '(For o\ufffdce '     -> "office"
    '   Sta\ufffd'        -> "Staff"
    'ii. Di\ufffdere'     -> "Different"
    ' Quali\ufffdcat'     -> "Qualification"
    'Identi\ufffdcat'     -> "Identification"
    'tary O\ufffdcer'     -> "Officer"
    'arty O\ufffdcia'     -> "Official"

Every one is a ligature: fi, ff, ffi. The .txt writer emits U+FFFD for the ligature glyph instead of expanding
it to its letters, so 127 words in each form are corrupted.

## Blast radius, measured across the corpus

    documents whose .txt carries U+FFFD:  2 of 213
    total replacement characters:       254
      Account_Opening_Form_Fillable_filled  127
      041122-Account_Opening_Form           127

Only these two. Their embedded font carries ligature glyphs with no ToUnicode entry for them, so the writer
has nothing to map the glyph to and writes the replacement character. Other documents' fonts either have the
mapping or do not use ligature glyphs.

## This is the engine, not the verifier

t06 is doing its job: it asks whether the bytes decode as the UTF-8 the writer declares, and 127 replacement
characters is a real corruption. Changing the check would hide 254 corrupted words from a user.

The fix belongs in the .txt writer: when a glyph has no Unicode mapping and the font's glyph name or the
GSUB table says it is a ligature, expand it to its component letters (fi -> f, i; ffi -> f, f, i) rather than
writing U+FFFD. PDFBox exposes the glyph name, and the standard ligature names - fi, fl, ff, ffi, ffl - are a
closed set, so this is a lookup, not a guess.

## Why it was not landed here

It is the .txt writer's glyph handling, on the engine side, and a wrong change there corrupts text on
documents that currently pass. It needs the same treatment as the annotation fault: fix, then verify the whole
corpus, and only these two documents should move.

## What this does NOT explain

t09_page_furniture fails on the same two documents with 29 source lines against 125 in the .txt. That is a
separate symptom with the same population - two sibling forms - and it should be measured on its own rather
than assumed to follow from the ligatures. It may well be the same root (the form's field appearances being
read as page furniture), but that is a hypothesis and is not established here.
