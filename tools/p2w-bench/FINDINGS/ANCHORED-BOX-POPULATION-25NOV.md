# The anchored-text-box population, measured for the first time

**25 Nov 2026 · engine 981ff1fa35e2cf67 · 213 documents · measured with `tools/p2w-bench/anchors.py`**

## Why this measurement exists

The charter's summary, and `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` before it, name one construct as the
largest engine defect anyone has found:

> `DocxWriter` routes body text into an anchored DrawingML text box once a page's flow enters
> `ctx.positioned`, triggered by a vertical gap wider than `gapCapTw()` = 120 pt. Google rasterises
> every anchored box on import, so that text leaves the exported text layer. That single threshold
> is ~166 document-failures across `04_chars_missing`, `45_char_accuracy`, `13_text_colours`,
> `44_header_footer` and `17_matched_runs`.

Every fixer run since has been pointed at that sentence. Nobody had measured the population it
describes. This is that measurement, and the sentence does not survive it.

## What was measured, and with what

Two instruments, deliberately independent of each other:

1. **The engine's own census** — `-Dp2w.census=<file>`, one line per page, counting which writer
   wrote the page's lines (`flow`, `row`, `col`, `tbl`, `anchor`, `stamp`, `anchorRule`,
   `anchorPos`). This counts *writer calls*.
2. **`anchors.py`, new this run** — reads `word/document.xml` out of each `.docx` and counts the
   characters that are actually inside a `<w:txbxContent>`. This counts *output*, and it cannot be
   fooled by which counter a writer incremented.

They agree on the shape of the answer and disagree on the exact count for a known reason (below).

## The measurement

```
census, 213 documents, 570 pages
  flow lines        5007        rows   933      table   273
  anchor boxes       690        of which:
      anchorPos      652   (94.5 %) - written because the page was already in positioned mode
      anchorRule      13   ( 1.9 %) - written by the gap threshold the charter blames
  documents with >=1 anchor box      20

anchors.py, 213 documents
  total characters                 463,228
  characters inside an anchored box 27,501  (5.94 %)
  documents with any boxed text         47
```

**The gap threshold writes 13 boxes in the whole corpus.** `anchorPos` — the propagation of
`PAGE_POSITION_ON_ANCHOR`, where one anchored line turns every later box on the sheet into a box —
writes 652. The census finds 20 documents; `anchors.py` finds 47, and the extra 27 are stamps and
other text-carrying boxes that the census files under `stamp` rather than `anchor`. Both are correct
answers to different questions; `anchors.py` answers the one that matters, because it counts the text
that can leave the Google text layer whoever wrote the box.

The documents carrying the most boxed text are not the class members the charter names:

```
041122-Account_Opening_Form          6840 of 50416 chars  13.6 %
Account_Opening_Form_Fillable_filled 6840 of 50495       13.5 %
policy-2col-spanning-section-heading 3046 of  3328       91.5 %
academic-paper-ieee-2col-abstract    2942 of  6410       45.9 %
magazine-2col-pullquote-spanning     2182 of  2387       91.4 %
```

These are forms, two-column magazine layouts and diagrams. They are the documents where a page's
flow genuinely cannot reach a line.

## What this overturns

**The construct cannot be the explanation for ~166 document-failures.** Only 47 of 213 documents
contain a single character inside an anchored box. Arithmetic, not opinion: a construct present in 47
documents cannot be the mechanism of 166 failures. The five classes named in that sentence have to be
re-measured for this construct one document at a time before any run spends another hour on it.

This is not a claim that the 24 Nov work was wrong. It root-caused real text loss and its mechanism
is exactly as described. The error is in the *size*, and the size is what a run acts on. The 24 Nov
numbers were taken on a different revision — that document cites `place()` at `:4124-4157`, and the
same code is `flowFromBox` at `:4406` today — and the engine has moved twice since.

## The A/B: what the propagation flag is worth

`PAGE_POSITION_ON_ANCHOR` is on by default (`-Dp2w.pagepos=0` turns it off). Converted all 213 both
ways and diffed `word/document.xml`:

```
document.xml changed : 8 of 213
boxed characters     : 27,501 -> 22,476  (-5,025, -18 %)
total characters     : 463,228 -> 463,265 (+37)
```

Eight documents, 5,025 characters moved out of boxes and back into flowed text. The +37 characters
are text that was being dropped, not moved.

That is the whole lever inside the construct, and it is worth 8 documents. It is **not landed**: the
flag's own doc comment says turning it off puts two positioners on one page (flow and boxes) whose y
models then disagree by the miss, measured at 21 overlaps and median |dy| 105.7 pt on
`policy-2col-spanning-section-heading`. 5,025 characters is not worth a `26_text_overlap` regression,
and this run had no Google verification path to prove otherwise. It is a lead with a number on it.

## The `!ctx.inColumn` asymmetry: real in code, empty in the corpus

`flowFromBox` guards the wide-gap branch with `!ctx.inColumn` (`:4474`); `flowRow` does not
(`:3591`), so a row inside a column cell could anchor to the page and land outside its cell. Patched,
rebuilt, converted all 213, diffed `word/document.xml`:

```
document.xml changed: 0 of 213
```

The branch is unreachable inside a column on this corpus. The patch was reverted rather than
committed: an unmeasurable change is a finding, not a commit. The asymmetry is still a latent fault
for a document the corpus does not contain.

## Method notes a later run should not have to rediscover

- **Compare `word/document.xml`, never the `.docx` bytes.** The archive is not byte-deterministic
  (zip timestamps). Measured: 213 of 213 differ at the byte level and 0 of 213 differ in
  `document.xml`, between two runs of the *same* engine. A byte diff reports a false positive on
  every document.
- **`corpus-convert.py` needs `--ensure` or `--force`.** With no flag it prints its docstring and
  returns 2; it looks like a successful no-op and converts nothing.
- **The census file is opened in append mode**, so it must be removed between passes or the pages of
  two engines are summed together.
- `corpus-fetch.sh` + `build-engine.sh` + a full 213-document conversion is **about 5 minutes** on a
  2-core pod at `-j 4`. The cost that stopped earlier runs from measuring is gone; measure.
