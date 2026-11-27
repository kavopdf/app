# The .txt reader drops every page separator, so every .txt check is measured on ONE segment

**Measured 27 Nov 2026. Instrument defect, not an engine defect. Not fixed this run.**

## The two facts

1. The writer emits the separator. `TxtWriter.java:86-88` appends `"\f\n"` at every page boundary,
   deliberately on its own line, and its own comment records the measurement that forced the
   newline (glued, `t02_position` fell 198/211 → 196/211).
2. The reader throws it away. `verify_txt.py:939`:

```python
def _txt_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f if l.strip()]
```

`U+000C` is whitespace to Python, so a line that is only a form feed has `l.strip() == ""` and is
filtered out. **Every document is therefore read as a single segment**, whatever its page count.

Confirmed on this pod: `303_discharge_summary` (1 page) has 0 form feeds — consistent. The t09
relay's finding that "the .txt has no form feeds: segs=1" is the reader, not the writer.

## What it blocks

Any `.txt` check that reasons about page boundaries or page furniture is measuring one segment:
the `t09_page_furniture` band arm reads **0 of 29** because of this line, and that 0 was recorded in
the ledger as evidence that the .txt half of t09 was blocked on an "aligner plus a full 213-document
re-measure". It is blocked on a six-line reader patch instead.

## Why it was not fixed in this run

The fix is small, and that is the problem: `_txt_lines` is the reader behind **every** .txt check.
Restoring the separators changes the segmentation of 213 documents at once, so it needs a full .txt
re-measure and a fresh `RANKING-TXT` stamp before it can be committed — and a fix that lowers a
document's .txt score on the corrected reading is still a regression the gate will refuse. That is a
run's own work, not the last twenty minutes of this one.

Next run: patch `_txt_lines` to keep a separator line (yield `"\f"` rather than dropping it), then
run `benchmarks/p2w.py`'s .txt half over the whole corpus and diff the failing set against
`tools/p2w-bench/txt/RANKING-TXT-BASELINE.csv` before and after. If the failing set grows, the
checks were passing on a segmentation that does not exist and the growth is the correction, not a
regression — say so in the report and stamp it.
