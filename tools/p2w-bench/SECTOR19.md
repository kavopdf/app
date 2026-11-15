# SECTOR 19 — writer side effects

**The .txt must be a function of the PDF. It was a function of the call order.**

Status: fixed, measured on all 211 corpus documents. Nothing committed.

---

## 0. The root cause in one paragraph

`ConvertAll` runs `DocxWriter.write(r, docx)` and then `PdfToWord.writeTxt(r, txt)` on **one**
`Result`. `DocxWriter.write` edited that `Result`: its stamp pass (`orderStamps`,
`DocxWriter.java:4381` / `:4395` at HEAD) removed the turned stamp paragraphs from `page.blocks`
and re-inserted each one at the index its own `y` falls at. `TxtWriter.write` walks
`page.blocks` in order (`TxtWriter.java:69`) and writes one .txt line per drawn line, so it read
the .docx writer's relocation instead of the page. The same PDF therefore produced two different
.txt files, and the difference was invisible to every check because all seven text checks pair by
text — and a reordering of the same lines pairs exactly as well one way as the other.

The move itself is not the bug. Placing a stamp line where its `y` falls is what lets `w:ind` and
`w:before` put the line inside its own frame instead of 200 pt below it. The bug is that the move
was made **in the shared model**, where a second consumer could see it.

---

## 1. Every place a writer mutates shared state

Line numbers are the pristine tree (HEAD `2ee3596`) unless marked *now*. "Consumer" is who can
see the mutation; "seen" is how many of the 211 documents show it.

| # | Mutation | Site (HEAD) | Consumer that can see it | Seen |
|---|----------|-------------|--------------------------|------|
| 1 | `page.blocks` **reordered** — stamp paragraphs removed and re-inserted at their `y` | `DocxWriter.java:4381` (`blocks.removeAll(stamps)`) and `:4395` (`blocks.add(at, p)`), inside `orderStamps`, called from `:1051` | `TxtWriter.write` — walks `page.blocks` in order; a reorder is a different line order in the .txt. **This is the SECTOR 19 bug.** | 11 of 211 .txt differ; block order is the *first* difference on 10 of them |
| 2 | `Para.column = home[i]` — the column band the writer's geometry put a paragraph in | `DocxWriter.java:1753` | no .txt reader today (`TxtWriter` never reads `column`), but every later reader of the `Result` sees a paragraph tagged with a band it was not given by `PdfToWord`, and a second `write` call starts from that state | 13 of 211 |
| 3 | `Para.pinned = true` — "this line is anchored, not flowed" | `DocxWriter.java:3024` | same as #2: a writer finding stored on the document | (counted with #2) |
| 4 | `Result.report.zeroGap`, `.zeroGapAnchored`, `.zeroGapInCol`, `.zeroGapNoRoom`, `.zeroGapWorstPt` | `DocxWriter.java:674–678` | `ConvertAll`'s printed line (`zeroGap=…`), any verifier reading `Report`, and any .txt written afterwards "on behalf of" a document whose report carries .docx-only numbers | 34 of 211 |
| 5 | `Shape.stampFrame`, `Shape.mergedHost`, `Shape.mergedShape` on the page's own shapes | `DocxWriter.java:4755`, `:4758`, `:4759` (inside `stampFrames`, called from `:1048`) | `TxtWriter` ignores shapes, but the document is left describing a stamp frame as folded into a box the document does not have, and `containerOf` reads `consumed` — so the *next* write is not the same write | 28 of 211 |
| 6 | `Shape.consumed` restored from a per-write mark | `DocxWriter.java:1118` (`outlines.get(i).consumed = consumedMark.get(i)`) | the mark is taken at the start of *this* write and re-applied between attempts, so the last attempt's values survive the call — a second `DocxWriter.write` on the same `Result` then differs. Measured: `322_mutual_fund_factsheet`, `word/document.xml` | 1 of 211 |

The "seen" column counts the documents where that mutation was the **first** difference the
per-document fingerprint reported (rows 1–5 add to the 85 of §3); most documents carry more than
one, which is why the .txt itself only moves on the 11 that carry row 1.

Checked and **not** guilty:

* `TxtWriter` writes nothing back. It reads `Para.lines/lineX/lineY/lineSize`, `Table.rows`,
  `Table.cellXPage` and the page box, and assigns no field of any model object.
* `PdfToWord.classifyHeadings` (`:5133`) does write `Para.heading` — but it is a *model* pass, run
  once before both writers, and its output is part of the document, not a writer's finding.
* `mergeClusterTails` / `readPage` mutate during `convert`, i.e. while the model is being built.

---

## 2. The fix

The rule now is: **a writer renders from its own copy; only the model decides what the document
is.** Every one of the six mutations above is either written on a copy or moved into a model pass.

| # | Fix | Where |
|---|-----|-------|
| 1 | The stamp relocation is no longer a writer decision. It is a model pass, `ReadingOrder.apply(Result)`, run once after `classifyHeadings` and before either writer. `DocxWriter.write` no longer calls `orderStamps`; the page it walks is a copy, so even a stray call could not reach the document. | new `app/src/main/java/com/kavopdf/app/engine/ReadingOrder.java`; `DocxWriter.java:1075–1083` (the call site is gone, with the reason written where it was) |
| 1,2,3,5,6 | `DocxWriter.write` takes `PdfToWord.Page.copyForWrite()` at the top of its page loop and does all of its work on that. The copy carries its own block list, its own `Para` objects (`column`, `pinned`, `heading`, `top`, …) and its own `Shape` objects (with `mergedHost`/`mergedShape` remapped to the copies). | `PdfToWord.java:612` (`Page.copyForWrite`), `PdfToWord.java:183` (`Para.copyForWrite`), `DocxWriter.java` (`Shape.copyForWrite`/`remap`), `DocxWriter.java:986` (the copy is taken) |
| 4 | `DocxWriter.write` returns its own `DocxWriter.Stats` instead of writing five fields into the shared `Report`. `ConvertAll` prints from the returned object. `Report.zeroGap*` are documented as no longer written. | `DocxWriter.java:677` (`class Stats`), `:685` (`public static Stats write`), `ConvertAll.java` |

`Table` is deliberately **shared**, not copied: no writer writes a table, and the new independence
test asserts that per document rather than trusting the note.

Why a copy and not "just restore it afterwards": restoring is a promise each future edit has to
keep, and the restore itself is a mutation visible to anything that runs in between. A copy makes
the boundary structural — a writer physically cannot reach the document.

---

## 3. The proof

Two trees, same corpus, same JDK: the pristine tree at HEAD (`2ee3596`) and the fixed tree. Each
run is one JVM over all 211 PDFs. `.txt` compared byte for byte; `.docx` compared by the SHA-256
of every entry inside the archive (a zip's timestamps make the file bytes useless).

| # | Comparison | Result |
|---|------------|--------|
| A | **.txt, BEFORE**: docx-then-txt vs txt-only | **11 of 211 differ** |
| B | **.txt, AFTER**: docx-then-txt vs txt-only | **0 of 211 differ** |
| C | **.txt, AFTER with the model pass switched off**: docx-then-txt vs txt-only | **0 of 211 differ** — independence is structural, not a property of the model pass |
| D | **.docx, AFTER vs BEFORE** | **0 of 211 differ** — the .docx is member-identical, so the fix costs the document output nothing |
| E | .docx, AFTER-without-model-pass vs BEFORE | 11 of 211 differ — dropping the relocation would change 11 .docx |
| F | .docx, model pass ON vs OFF | 11 of 211 differ (same 11 as E) |
| G | .txt, AFTER vs BEFORE (both docx-first) | **0 of 211 differ** — the .txt the pipeline ships today is byte-for-byte what it shipped before |
| H | .txt, AFTER-without-model-pass vs BEFORE | 11 of 211 differ — this is what a .txt-only run used to produce |

The 11 documents of A (and H) are, exactly, the stamp documents:

```
01_stamp_rotated_15deg_upright      07_stamp_over_table
02_stamp_rotated_15deg_upleft       08_two_overlapping_stamps
03_stamp_vertical_90deg             09_stamp_font_not_embedded
04_stamp_180deg_upside_down         11_stamp_with_signature_image
06_rect_paid_stamp_red_transparent  13_stamp_non_english
43_red_stamp_over_black_text
```

Same line multiset, different order — e.g. on `01_stamp_rotated_15deg_upright` the .txt with the
.docx write in front moves `AUTHORISED SIGNATORY` and `SUNRISE FASTENERS` up to where the stamp
sits, and pushes the footer down.

**Count note.** The brief records one agent measuring 12. This measurement is 11, and it is 11 in
both directions: the corpus-level two-run comparison (A) and the in-process per-document test
(`TestWriterIndependence`, §5) name the same eleven files. `15_stamp_on_scanned_page` is the one
document that moves in the .docx but not in the .txt (its stamp lines are not in its text layer),
so a count taken on .docx members is 12 while a count taken on .txt bytes is 11.

Model-level proof, per document, on all 211 (`tools/engine-verify/TestWriterIndependence.java`):

| | HEAD | fixed |
|---|---|---|
| documents where the model moved across `DocxWriter.write` | **85 of 211** (block order 10, `Para` flags 13, `Report` 34, `Shape` flags 28 — counted by each document's first difference) | **0** |
| documents whose .txt changed when the .docx write was inserted | **11** | **0** |
| documents whose *second* .docx write differed from the first | **1** (`322_mutual_fund_factsheet`) | **0** |
| documents clean on all three | **126 of 211** | **211 of 211** |

---

## 4. Should the stamp relocation live in the model? — yes, and here is the measurement

The relocation is a statement about **reading order**: a stamp line belongs where its `y` falls,
not after the page's last line. Reading order is a property of the document, exactly like
`classifyHeadings`' heading levels, and both writers are entitled to it. Keeping it in the writer
was the only reason one consumer could see it and the other could not.

What the numbers say:

* **Keeping it in the model costs nothing measurable.** With `ReadingOrder.apply` in front of both
  writers, the .docx is member-identical to HEAD on **211/211** (row D) and the .txt is
  byte-identical to HEAD on **211/211** (row G). The shipped output does not move.
* **Dropping it is a real change.** With the pass off, 11 .docx change (row E) and 11 .txt change
  (row H) — a different document from the one the pipeline ships, for no gain.
* **Neither output's checks can tell the two apart**, which is the whole reason this survived:
  * .txt checks: identical on all four variants — **191/211 all-pass**, and every one of the seven
    checks has the same count (table in §6).
  * .docx checks on the 11 documents that change: **456/473 either way** (identical per document).

So: the relocation stays, but as a model pass. `-Dp2w.readingOrder=false` reproduces the
PDF-drawn order for measurement; it is not the default.

The one thing the pass must not do is re-derive itself per consumer. `ReadingOrder.apply` is
idempotent (a stamp already at its `y` is re-inserted at the index it already holds), so a caller
that runs it twice gets the same page — which is what lets `DocxWriter` still fold stamp frames
(`stampFrames`) on its own copy without changing the answer.

---

## 5. The check that fails if the .txt changes when the .docx write is skipped

Two guards, at two levels.

### 5.1 Per document, in process — `tools/engine-verify/TestWriterIndependence.java`

```
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     TestWriterIndependence /scratch/work/pdfs [limit]
```

For each PDF it converts, takes a fingerprint of the whole `Result` (every page's block order with
object identity, every `Para` field, every `Box`, every `Table`'s contents, every `Shape`'s flags
and frame references, and the `Report`), writes the .txt, writes the .docx, and then re-takes the
fingerprint, re-writes the .txt, and writes the .docx a second time. It fails on:

1. **MODEL MOVED** — any field, list or order changed by the write (prints the first differing
   line, with the field values either side);
2. **TXT CHANGED** — the .txt bytes before and after the write differ;
3. **SECOND WRITE DIFFERS** — the second .docx is not member-identical to the first.

Exit 0 only when every document is clean. It catches a *new* writer mutation the day it is
written, on the first document that triggers it.

Run against the pristine tree (with the `ReadingOrder` call removed so it compiles at HEAD):
`126/211 documents clean (model moved 85, .txt changed 11, second write differed 1)`.
Run against the fixed tree: `211/211 documents clean (model moved 0, .txt changed 0, second write
differed 0)`.

### 5.2 Whole corpus, two runs — `tools/p2w-bench/check-writer-independence.py`

```
python3 tools/p2w-bench/check-writer-independence.py <pdfDir> [--limit N] [--work DIR]
python3 tools/p2w-bench/check-writer-independence.py --compare-only <A> <B>
```

It converts the same corpus twice — once through `ConvertAll` (docx, then txt) and once through
`ConvertAll -Dp2w.noDocx=true` (txt only, no .docx write at all) — and compares every .txt byte
for byte. Exit 1 if a single document differs, and it prints the differing files with their
hashes.

Validated both ways:

| corpus state | result |
|---|---|
| HEAD's output trees (`--compare-only`) | **FAIL, exit 1**, 11 of 211 differ |
| fixed output trees (`--compare-only`) | **PASS, exit 0**, 211 of 211 identical |
| fixed engine, end-to-end, first 110 documents | PASS, 110/110 identical |
| fixed engine, end-to-end, last 101 documents | PASS, 101/101 identical |
| the bug put back by hand (`page = model` + `orderStamps` in `write`, model pass off) | **FAIL, exit 1**, 9 of the first 12 documents differ |

It is wired into `tools/precommit.sh` tier 2: `TestWriterIndependence` on 12 corpus documents
(seconds, runs on every engine change) — a `FAIL` there reads *"a writer edits the document it
renders"*.

---

## 6. The measurement on all 211, before and after, per check

Corpus: the four `corpus-v1` release archives, unzipped flat — **211 PDFs**. Engine built with
`tools/p2w-bench/build-engine.sh`. `.docx` rendered with `soffice --headless --convert-to pdf` in
batches of 110. Scores: `verify_txt.py` (7 checks) and `verify_google.py` (43 checks, `--docx`).

### 6.1 .txt — `verify_txt.py`

| check | BEFORE (docx-first) | AFTER (docx-first) | BEFORE (txt-only) | AFTER (txt-only) | AFTER, model pass off |
|---|---|---|---|---|---|
| t01_word_accuracy | 205/211 | 205/211 | 205/211 | 205/211 | 205/211 |
| t02_position | 198/211 | 198/211 | 198/211 | 198/211 | 198/211 |
| t03_symbols | 211/211 | 211/211 | 211/211 | 211/211 | 211/211 |
| t04_structure | 211/211 | 211/211 | 211/211 | 211/211 | 211/211 |
| t05_completeness | 211/211 | 211/211 | 211/211 | 211/211 | 211/211 |
| t06_encoding | 211/211 | 211/211 | 211/211 | 211/211 | 211/211 |
| t07_symbol_counts | 210/211 | 210/211 | 210/211 | 210/211 | 210/211 |
| **documents all-pass** | **191/211** | **191/211** | **191/211** | **191/211** | **191/211** |

Five variants, one column of numbers. **That is the finding**: the .txt checks are blind to the
reordering. 11 documents had genuinely different bytes and every one of the seven checks scored
them identically in both orders — which is why nothing caught this for as long as it ran.

### 6.2 .docx — `verify_google.py` (43 checks × 211 documents)

Measured on the fixed tree's .docx. These are also the BEFORE numbers, because row D of §3 proved
the .docx is member-identical on 211/211 — re-rendering the same bytes would only re-measure the
same file.

Totals: **8923/9073 checks = 98.35 %, 134/211 documents all-pass** — identical to the figure
recorded at HEAD in commit `2ee3596` (`8923/9073 = 98.35 %, 134 all-pass`), which is an independent
confirmation that this harness reproduces the baseline exactly.

| check | pass | check | pass | check | pass |
|---|---|---|---|---|---|
| 01_page_count | 210/211 | 26_text_overlap | 205/211 | 43_within_10pt_x | 206/211 |
| 04_chars_missing | 207/211 | 27_text_off_page | 209/211 | 44_header_footer | 210/211 |
| 05_chars_extra | 208/211 | 28_clipped_at_edge | 209/211 | 45_char_accuracy | 208/211 |
| 08_image_count | 211/211 | 31_pages_lost_their_text | 211/211 | 46_text_crossing_rule | 211/211 |
| 10_font_sizes | 211/211 | 32_stroke_lines | 210/211 | 47_margins | 194/211 |
| 13_text_colours | 211/211 | 34a_span_size_match | 208/211 | 48_image_area | 211/211 |
| 14_filled_shapes | 208/211 | 34b_span_colour_match | 211/211 | 49_page_size | 211/211 |
| 17_matched_runs | 204/211 | 34c_span_weight_match | 211/211 | 50_annotation_text | 211/211 |
| 18_displacement | 176/211 | 35_rotation | 199/211 | 51_field_values | 210/211 |
| 22_reading_order | 211/211 | 36_underline_rules | 211/211 | 52_outline | 210/211 |
| 23_line_pitch | 211/211 | 37_super_subscript | 210/211 | 53_embedded_faces | 207/211 |
| 24_page_breaks | 210/211 | 38_list_markers | 209/211 | 54_image_dpi | 211/211 |
| 25_invisible_text | 211/211 | 39_image_position | 211/211 | 55_orientation_mix | 210/211 |
| 40_link_targets | 210/211 | 42_justification_edges | 210/211 | 59_shape_anchor | 198/211 |
| 60_text_column_right_edge | 192/211 | | | | |

Note `22_reading_order` (the .docx side of this very question): 211/211 both before and after, so
the .docx checks could not see the relocation either.

The engine's own suite is unchanged too: `TestPdfToWord` — **29 passed, 0 failed**.

---

## 7. How to reproduce

```bash
# build
bash tools/p2w-bench/build-engine.sh

# corpus
gh release download corpus-v1 --repo kavopdf/app     # 4 zips, 211 PDFs, unzip flat

# the two guards
cd tools/engine-verify
javac -nowarn -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
      -d out TestWriterIndependence.java
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     TestWriterIndependence <corpusDir>
cd ../..
python3 tools/p2w-bench/check-writer-independence.py <corpusDir>

# the same pair by hand, if you want the trees to keep
CP="out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertAll <corpusDir> out-both                     # docx, then txt
java -Dp2w.noDocx=true -cp "$CP" ConvertAll <corpusDir> out-txt    # txt only
python3 tools/p2w-bench/check-writer-independence.py --compare-only out-both out-txt
```

`-Dp2w.readingOrder=false` gives the page as the PDF drew it (the before-side of §4);
`-Dp2w.noDocx=true` skips the .docx write.

---

## 8. What this does not fix

* The .docx still has 27 checks failing somewhere in the corpus (150 of 9073 check-instances).
  That is the pre-existing state, unchanged by this work — `8923/9073` before and after.
* `Para.column` and `Para.pinned` are still *fields on the model*, written by the writer — on the
  writer's copy. They would be cleaner as writer-local maps; the copy makes that unnecessary, and
  the independence test will fail if anyone reads them from the document by mistake.
* `Table` is shared between the model and the writer's copy. No writer writes one today and the
  test asserts it, but a future writer that edits a table would be caught by the test rather than
  by construction.
