# t02_position fails on four documents for two reasons, and neither is position

Measured on the four documents the check charges, current engine 981ff1fa35e2cf67:

    332_bom_on_drawing                   source= 52  txt= 79    +27
    334_patent_document                  source= 32  txt= 69    +37
    74_balance_sheet_indented_subitems   source= 54  txt= 81    +27
    price-list-2col-dense-right-aligned  source=252  txt= 86   -166

The check reports the source and render line counts and compares them before it fits anything. Three
documents have MORE .txt lines than the PDF has - the writer is splitting one visual line into two or more,
which is the same construct as t08_line_order and t13_amount_columns. One has far FEWER: 252 lines become
86, so two thirds of the document's lines are not in the .txt at all.

Neither is a position failure. A line that does not exist cannot be in the wrong column, and a line split
in two produces a ruler fit that describes nothing.

## Why the name matters

The check is called t02_position and its description is "a line's x survives as its leading spaces". A run
reading the ledger sees t02_position on four documents and goes looking at the indent arithmetic, which is
not where the fault is. The population is two different bugs wearing one check name, so neither gets fixed:
the split is a line-building fault and the loss is a different one, and the .txt writer needs both.

## What to measure before touching the writer

For the three that split: which rows in the PDF become two rows in the .txt, and what did the writer key on
- a gap between spans, a column boundary, or a table cell edge. t13_amount_columns already names that
construct for .txt and 18_displacement names the .docx side of it.

For the one that loses: whether the 166 missing lines are off-page, inside a table the writer skipped, or
dropped by a cap. price-list-2col-dense-right-aligned is a dense two-column price list, so the likely
suspect is the second column, not a global cap - but that is a hypothesis, and the .txt has to be diffed
against the PDF before anything is changed.

## Not changed

The .txt writer was not touched. Its line building is the engine, and a blind edit there loses text on 213
documents rather than fixing four. Recorded so the fix starts from the right fault.
