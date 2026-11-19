# PATCH-t13 was measured and REJECTED

The agent wrote this patch on 19 Nov, believing the reasoning was obvious: `TxtWriter.appendTable()`
ended every **cell** with a newline, so a nine-column invoice row came out as nine lines. Option A for
this format is "rows on one line, columns aligned by spaces". The fix made one page row one `.txt` line.

**It was built, run over all 213 documents, and scored. It is wrong.**

    better  0
    worse   101
    same    112

**101 documents got worse and not one got better.** The patch is reverted and must not be applied.

---

## Why the reasoning was wrong

The shape was a real defect — a table row really did arrive as nine lines. What the reasoning missed
is that **`t04_structure` is a line-count check**:

    c["t04_structure"] = (src_lines, len(lines),
                          1.0 / MAX_LINE_DRIFT <= drift <= MAX_LINE_DRIFT, True)

Collapsing nine lines into one changes `len(lines)` by a factor of nine. `drift` leaves
`[1/MAX_LINE_DRIFT, MAX_LINE_DRIFT]` and `t04_structure` fails on every table-heavy document. The
regression list names it first on almost every row.

So the `.txt` format has a constraint the patch did not know about: **the line count has to stay close
to the page's line count.** A table row drawn on one baseline is one line on the page, but the writer
was emitting each cell on its own line and the check was calibrated against that.

**Which means the cell-per-line shape is not simply a bug.** Either the check's model of a line is
wrong, or the shape is right and `t13` is measuring the wrong thing. That is a question about the
instrument, and it must be settled before anyone touches the writer again.

---

## What is still true from the investigation

* `gst-invoice-3line-items` really does emit one cell per line: its amount column at end-column 133
  holds `32,745.00 / 7,522.50 / 13,806.00`, and in the `.txt` they end at 134 / 133 / 134.
* `t13`'s own matching bug was real and is fixed — an amount token that appeared in two columns was
  resolved to its first position. That fix alone made 13 documents newly clean with **0 worse**, and
  it is kept.
* **128 of 213 `.txt` files change** under the t13 patch, which is how far the shape reaches.

## Do not

* Do not re-apply `PATCH-t13-table-row-per-line.patch`.
* Do not "fix" `t04_structure` to make the patch pass. If the line-count model is wrong, that is a
  measurement decision to be made on its own evidence, not a way to rescue a patch that failed.

## The file is kept, not deleted

`PATCH-t13-table-row-per-line.patch` stays where it is, because a rejected patch that says why it was
rejected is worth more than an absence.
