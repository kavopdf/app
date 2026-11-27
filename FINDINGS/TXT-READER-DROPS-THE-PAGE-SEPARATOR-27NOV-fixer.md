# The .txt reader drops every page separator — and fixing it moves nothing, because no check reads pages

**Measured 27 Nov 2026, twice: once in the code, once over the whole corpus.**

## Fact 1 — the writer emits the separator, deliberately

`TxtWriter.java:86-88` appends `"\f\n"` at every page boundary, on its own line, and its own comment
records the measurement that forced the newline (glued to the next line, `t02_position` fell from
198/211 to 196/211).

## Fact 2 — the reader throws it away

`verify_txt.py`, `_txt_lines`:

```python
return [l.rstrip("\n") for l in f if l.strip()]
```

`U+000C` is whitespace to Python, so a line holding only a form feed has `l.strip() == ""` and is
filtered out. Every multi-page `.txt` is therefore handed to the checks as **one segment**.

## Fact 3 — the fix is inert, and that is the finding

The reader was patched to keep the separator line (`if l.strip() or "\f" in l`) and the whole corpus
was re-scored with `txt_rank.py --all`:

| | documents | failing check-instances |
|---|---|---|
| before the patch | 213 | 12 |
| after the patch | 213 | 12 |

**0 documents worse, 0 better, the same 12 failing checks.** The patch is kept because it is
correct — a reader that cannot see a page boundary cannot ever be asked a question about one — but
it unblocks nothing on its own. No check in the twelve consumes the segmentation: `t11_page_breaks`
counts `U+000C` in the raw bytes, and every other check works on the flattened line list.

## The correction this forces on the t09 lead

`t09_page_furniture`'s band arm reads **0 of 29** and the ledger recorded that as "blocked on an
aligner plus a full 213-document .txt re-measure". The first half of that was right and the second
half was not: the separators are there, the reader drops them, and **keeping them changes no
document's score**. So the band arm is not blocked on a reader at all — it is blocked on a check
that has never been written to consume page segments. That is a different job with a different cost,
and it should be stated that way before the next run spends a slot on it.

## What a future run should do with it

Write the page-segment-consuming check first, against the patched reader, and measure it on the 29
documents that carry page furniture. If it fires on documents that are currently clean, the check is
wrong, not the documents — page furniture is the construct with the most false positives in this
corpus.
