# PROPOSAL, NOT APPLIED: one flag on the .txt reference, measured, waiting for a person

21 Nov 2026, fixer run claimed 00:57. This is a patch a fixer is not allowed to apply and a
measurement that says it should be looked at. `verify_txt.py` is the instrument; the brief forbids
a fixer moving a number by editing the check. So the change is written here, exactly, with its
measured effect over the whole corpus, and it is not in the tree.

## The change

    tools/p2w-bench/verify_txt.py, in the per-page text block (the `declared_page` read, ~line 571)

    -                declared_page = pg.get_text()
    +                declared_page = pg.get_text(
    +                    flags=fitz.TEXTFLAGS_TEXT & ~fitz.TEXT_MEDIABOX_CLIP)

## Why

`fitz.TEXTFLAGS_TEXT` includes `TEXT_MEDIABOX_CLIP`. On that path MuPDF drops any line whose box
crosses the page edge and returns whatever survives as one-character fragments. The page still
draws the glyphs, and the writer still emits the ones inside the page, so the reference ends up
carrying words the page never drew as words.

Measured on `411_nested_xobject_transforms`: both parsers agree on the CTM to the digit,
`[0 1 -1 0 60 700]`, determinant +1; PDFBox returns all 32 glyphs of the rotated line and
pymupdf's `get_texttrace()` also returns all 32. Only `get_text()` returns 2 - the two phantom
tokens `S` and `O` the check then charges the writer for.

## The measured effect, whole corpus

Measured over all 213 documents on engine `cd21104b11ed26c1`, with a harness that first reproduces
the committed `RANKING-TXT.csv` on all 213 rows:

| | documents |
|---|---:|
| rows byte-identical | **211** |
| improved | **2** - `411_nested_xobject_transforms` (4,3,1 -> 4,4,0) and `12_stamp_across_page_break` (10,10,0, charged `U` and `G` by the same path) |
| worse | **0** |

The flag changes the declared word count on exactly those two of 213 documents.

## If it is approved, the sequence is the brief's own

    # the instrument changed, so every .txt row is stale - restamp all of them, do not hand-edit one
    python3 tools/p2w-bench/restamp_txt.py --run
    python3 tools/p2w-bench/restamp_txt.py --report
    python3 tools/p2w-bench/restamp_txt.py --apply
    python3 tools/p2w-bench/txt_gate.py --gate
    python3 tools/p2w-bench/regress.py --check
    python3 tools/p2w-bench/classify_txt.py

## What it does not fix

It does not touch `39_small_caps_letter_spacing`, whose fault is the 1.200 pt gap split and is
written up in `39-small-caps-gap-threshold-0150-fixer.md`. That one needs a decision about which
boundary is authoritative on a letter-spaced line - the drawn space glyphs or the gap - and a
tokenisation that prefers the drawn glyphs without shattering the address welds it correctly but
scores 90.0 on this document, so it is not a straight swap.

Two smaller-looking repairs were built and rejected on measurement, so the next run does not build
them again: a content-order rebuild from `get_texttrace()` fixes `411` and makes **83 of 213**
documents worse; abstaining when a span cannot be aligned moves `t01` on **86 of 213** and is a
separate, larger instrument defect.
