# TXT defects

**Every fix in this file goes inside `TxtWriter` and nowhere else.**

If a fix needs a change outside `TxtWriter`, it is not a txt defect - it is a model
defect and belongs in `REMAINING-DEFECTS.md`. Filing a txt problem in that file is
how a cron ends up editing `buildPara` to improve a column, which changes the .docx
and is the one thing the user has ruled out.

## The proof every fix must carry

    python3 tools/p2w-bench/txt-guard.py snapshot --dir OUT --save before.json
    ... apply the fix, reconvert the same documents ...
    python3 tools/p2w-bench/txt-guard.py compare  --dir OUT --against before.json

`identical: N, different: 0` or the fix is reverted.

## Open

| ID | Defect | Document | Tries used |
|----|--------|----------|------------|
| -  | none   | -        | -          |

## Fixed

| ID | Defect | Fix | Date |
|----|--------|-----|------|
| T1 | Column came from each line's own font size, so two lines at the same x landed in different columns and tables never lined up | One character width for the whole document, from the size the page drew most of its characters at, weighted by character count | 6 Nov |
| T2 | Blank lines came from a guessed multiplier on the line's own size | Median of the gaps the page actually left between consecutive lines, measured per page, capped at 10 | 6 Nov |
| T4 | Every amount sat at its cell's left edge, so a column of figures was not a column | A numeric cell drawn flush against its cell's right edge is right-aligned in that cell | 6 Nov |
| T5 | Trailing spaces were kept and the file had no guaranteed final newline | Trailing spaces trimmed, file always ends with a newline, UTF-8 without a BOM | 6 Nov |
| T8 | A row of eight columns produced a two-hundred-character line nobody could follow | Rows wider than the readable width fall back to one cell per line | 6 Nov |

## Closed - cannot fix

| ID | Defect | Why |
|----|--------|-----|
| T3 | Cell column width | Not a defect of its own: it is T1 seen from the table side, and T1 fixes it. Nothing in `buildTables` was touched. |
| T7 | Images | A .txt cannot hold an image. A marker would only say something was there, and it would appear in the middle of copied text. Open the .docx for images. |
