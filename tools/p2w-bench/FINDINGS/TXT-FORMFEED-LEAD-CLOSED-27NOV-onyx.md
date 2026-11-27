# txt form-feed lead is CLOSED — the bug was real, is already fixed, and clears 0 documents

**27 Nov 2026 · slot 16:06 · fixer `Onyx-Node` · the lead the previous run left is a dead end. Do not chase it.**

The previous run's lead, verbatim:

> txt reader: `verify_txt.py` `_txt_lines` dropped the form-feed separator line (`l.strip()` is empty for
> U+000C), so every multi-page `.txt` is missing its page separators | next run: the .docx half

## What was measured

A three-page fixture written the way `TxtWriter` writes it, run through the **real** `_txt_lines`:

    pre-fix reader : ['Page one line', 'Page two line', 'Page three line']                      3 lines
    HEAD reader    : ['Page one line', '\x0c', 'Page two line', '\x0c', 'Page three line']      5 lines

So the bug was real: `"\f".strip()` is `""`, so the separator line vanished. Single-page files were
never affected; a trailing form feed was dropped pre-fix and is kept at HEAD, with or without a trailing
newline; CRLF survives.

## It is already fixed, and it was never the writer

- Fixed at `verify_txt.py:944` by commit `0d45ff6` (27 Nov 00:17 UTC). Smallest remaining patch, if
  anyone touches it again: test `PAGE_BREAK in l` rather than the literal.
- **Not a writer bug.** `TxtWriter.java:87` emits `"\f\n"` per boundary; the only control scrub (`:119`)
  deliberately omits `\u000C`; `PdfToWord.java:10014` is the sole call site. The corpus confirms the
  bytes are there: `041122-Account_Opening_Form.pdf` is 9 pages, its row is `applicable=10` including
  `t11_page_breaks`, and `t11` was judged and passed — so exactly 8 U+000C are present.

## It clears nothing — measured, not estimated

A/B with the same real files under both readers: **verdict diffs = NONE** on a 3-page and a 10-page
source. `t11` counts raw bytes, so the reader cannot move it; the other eleven checks are indifferent
to the separator. The recorded re-score agrees: 12 before / 12 after, 0 worse, 0 better.

## The premise was stale, which is the finding

`HISTORY-TXT.jsonl`: **186 clean / 27 failing was 20–21 Nov.** Since 26 Nov the `.txt` half reads
**205 clean / 8 failing**, and none of the current 8 fails `t11`. The "27" in the hand-off is three days
old and nothing in the pipeline refreshes it.

**Risk of any further edit here:** only `t04_structure` can move (it fails when `N-1 > L/2`, near-blank
multi-page documents). Measured headroom 1.08 and 1.01 against a 1.5 ceiling; no pass→fail found.

**Live hazard, documentary:** `t11`'s comment block (`:1418-1429`) and `t08`'s (`:1257`) still claim the
writer strips U+000C. That claim is false and would send the next agent to "fix" a correct writer.
