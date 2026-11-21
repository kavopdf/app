# t08_line_order — the structural mechanism behind the failing documents

Repo: `https://github.com/kavopdf/app` @ depth-1 clone, 2026-11-21. Nothing in the clone was
edited, committed or pushed; the engine was built with `tools/p2w-bench/build-engine.sh`
and the corpus taken from the `corpus-v1` release.

---

## 1. The answer, in one sentence

**The `.txt` line order is a purely *geometric* order — the model's paragraphs and their
lines, sorted by baseline `y` — while `t08_line_order`'s ground truth is the page's
*drawing sequence* (PyMuPDF block order, never sorted); the engine throws the drawing
sequence away at `PdfToWord.toLines`' baseline sort (`PdfToWord.java:3733`), so every
document whose content stream does not run strictly top-to-bottom in the same granularity
as the model necessarily fails, and those are exactly the failing documents.**

Single structural condition on the document side: *at least one line whose position in the
content stream differs from its position in the vertical order* (a note/stamp/widget block
drawn last but sitting mid-page, chart axis labels drawn bottom-up, a drop cap drawn
separately, speech bubbles drawn bubble-by-bubble, or a straight line absorbed into a
seal-ring paragraph that has no `y` at all).

It explains **all 8 of the 8** the brief names, and in fact **all 10** rows of
`RANKING-TXT.csv` that carry `t08_line_order` — see §3 for the 8-vs-10 bookkeeping.

---

## 2. What the check actually compares

`tools/p2w-bench/verify_txt.py`:

* `_src_pages()` (**lines 775–846**) builds the source model. It walks
  `pg.get_text("dict")["blocks"]` and appends one record per non-empty line **in the order
  PyMuPDF returns them** (`lines.append(...)` at **line 835**) and stores the page at
  **line 843**. **There is no sort anywhere in this function.** The order it produces is
  therefore the order the page's content stream draws its text — not vertical order.
* The `t08_line_order` block (**lines 1082–1174**):
  * source lines = the above, filtered to `upright` ones;
  * `.txt` side = `(stripped text, column)` per non-blank line, `column = len(line) - len(line.lstrip(" "))`;
  * a source line is a **partner** only if its text is unique on *both* sides
    (`src_occ == 1 and txt_occ == 1`) and its text appears in the `.txt` at a column within
    `POS_TOLERANCE` of `round(x / mid)` — `mid` is the characters-per-point ruler fitted by
    `_ruler()`;
  * partners are grouped **by column bucket**, and each bucket is compared with
    `difflib.SequenceMatcher(...).get_matching_blocks()` (**line 1167–1170**);
  * verdict: `in_order == partners` (line 1172), applicable only when `partners >= 3`.

So the question it asks is: *within one column, do the source's unique lines appear in the
`.txt` in the same relative order as the source lists them* — and the source lists them in
**draw order**. The check's own prose describes reading order ("the order a reader
follows", column scoping), but its implementation takes draw order as truth. On 203 of 213
documents the two coincide; on exactly the failing documents they do not.

## 3. The 8 vs 10 bookkeeping

`tools/p2w-bench/txt/RANKING-TXT.csv` has **10** documents whose `failed_ids` contains
`t08_line_order`, not 8:

```
09_stamp_font_not_embedded            305_vaccination_certificate
330_cad_drawing_sheet                 400_comic_page_speech_bubbles
46_chart_coloured_labels_body_text    65_two_col_full_width_figure_caption
70_magazine_drop_cap_photo_caption    itr-computation-with-slab-table
041122-Account_Opening_Form           Account_Opening_Form_Fillable_filled
```

The last two live in `benchmarks/realworld/`, not in the `corpus-v1` zips, which carry 211
PDFs; the remaining **8** are the 8 the brief names. All 10 were converted and measured
here, so both counts are reported.

## 4. Where the `.txt` order comes from

* `TxtWriter.write` walks `pageOrder(page)` (**`TxtWriter.java:95`**) and writes each block
  with `appendPara` (**line 507**) or `appendTable` (**line 568**).
* `pageOrder` (**line 189**) is *not* a re-sort: it only cuts two-column pages into
  left-piece-then-right-piece, and it **returns `page.blocks` untouched** as soon as the
  page carries a `Table` (line 193), has fewer than 6 paragraphs (line 196), or fails the
  gutter tests. So the `.txt` order is the model's block order.
* The model's order is geometric. `PdfToWord.toLines` sorts glyphs by baseline only —
  `Collections.sort(sorted, new Comparator<Glyph>() { … Float.compare(a.y, b.y); })` at
  **`PdfToWord.java:3733–3735`** — then `toParagraphs` sorts lines by
  `(segment, column, row-band, x)` (**`PdfToWord.java:5018`**).
* **`Glyph` has no stream index** (`PdfToWord.java:1819–1822`: `text, x, y, width, size`).
  Once the baseline sort has run, the drawing order is *unrecoverable* — the information
  the check asks for is destroyed at conversion time, not at write time.

One exception inside the model is worth naming because it produces one of the failures:
the seal-ring path leaves `lineY` empty on purpose ("x only, deliberately. lineY is left
empty so the ring keeps the vertical layout it has today" — `PdfToWord.java:4113–4126`,
`p.lineX.add(ln.x)` at line 4125). A paragraph with no `y` has no place in a vertical
order, so it is emitted wherever the block list leaves it.

## 5. Evidence, per document (all measured, this run)

Reproduced first: converting all 213 documents and running the check gives **exactly the
10 rows in `RANKING-TXT.csv` — no more, no fewer** (`t08_line_order` set equality).

| document | partners | in_order | lines out of place | what the page drew out of vertical order |
|---|---|---|---|---|
| 09_stamp_font_not_embedded | 16 | 15 | 1 | the "Note: stamp applied…" line is drawn **last** in the stream but sits at y=513, above the footer at y=799 |
| 305_vaccination_certificate | 33 | 32 | 1 | "Issued: 18-03-2022 …" is drawn at its own y=272.7 but is **absorbed into the seal-ring paragraph** (`lineY` empty), so it is written in ring position |
| 330_cad_drawing_sheet | 33 | 32 | 1 | "ALL DIMENSIONS IN MILLIMETRES…" is drawn last but sits above the title block |
| 400_comic_page_speech_bubbles | 20 | 19 | 1 | bubbles are drawn bubble-by-bubble (RAVI+text, then MEENA+text, …), not row by row |
| 46_chart_coloured_labels_body_text | 43 | 37 | 6 | y-axis labels drawn **20 → 70** (bottom-up); the `.txt` writes 70 → 20 |
| 65_two_col_full_width_figure_caption | 47 | 43 | 4 | axis labels drawn 80, 90 and 110, 120 |
| 70_magazine_drop_cap_photo_caption | 21 | 20 | 1 | the drop cap "T" is drawn separately from its paragraph |
| itr-computation-with-slab-table | 89 | 88 | 1 | footer "Computation prepared on 12 August 2026 · AY 2027-28" drawn at rank 112, y=811 |
| 041122-Account_Opening_Form | 461 | 421 | 40 | widget/annotation text drawn after the page body (draw ranks 515, 543–546 …), written by y |
| Account_Opening_Form_Fillable_filled | 461 | 421 | 40 | same |

## 6. Counterfactual 1 — order alone, proven

Take the engine's own `.txt`, keep every line's text and leading spaces **byte for byte**,
and reorder only the *sequence* so the lines follow the source's drawing order. Re-run the
check:

| document | partners | in_order | verdict |
|---|---|---|---|
| 09_stamp_font_not_embedded | 16 | 16 | **pass** |
| 305_vaccination_certificate | 33 | 33 | **pass** |
| 330_cad_drawing_sheet | 33 | 33 | **pass** |
| 400_comic_page_speech_bubbles | 20 | 20 | **pass** |
| 46_chart_coloured_labels_body_text | 43 | 43 | **pass** |
| 65_two_col_full_width_figure_caption | 47 | 47 | **pass** |
| 70_magazine_drop_cap_photo_caption | 21 | 21 | **pass** |
| itr-computation-with-slab-table | 89 | 89 | **pass** |
| 041122-Account_Opening_Form | 461 | 461 | **pass** |
| Account_Opening_Form_Fillable_filled | 461 | 461 | **pass** |

Identical partner counts, `in_order == partners` everywhere. **Nothing about the content,
the columns, the words or the symbol counts is wrong in any of the 10 — only the sequence
is.** This is the mechanism, isolated.

## 7. Counterfactual 2 — sorting the *source* instead (the one-line check fix)

Sorting each page's source lines by `(round(y,1), x)` inside `_src_pages` and re-measuring
all 213 documents:

* **8 of the 10 flip to pass** — every one of the 8 named in the brief except
  `305_vaccination_certificate`;
* `305_vaccination_certificate` still fails, and now for the *right* reason: its `.txt`
  really is out of vertical order, because the ring paragraph has no `y` and swallowed the
  "Issued: …" line (§4);
* **`39_small_caps_letter_spacing` flips from pass to fail** — a true positive: its heading
  "THE MYSORE CHAMBER…" (y=65.1) is written before the letter-spaced line at y=52.6,
  i.e. that `.txt` is in draw order and out of vertical order. Today it passes only because
  the check also reads draw order.

So one line in the check clears 8 of the 10 and converts the remaining two into
correctly-attributed engine faults; it does not make the table vacuously green.

## 8. How many of the 8 it explains

**8 of 8** (and 10 of the 10 rows in the table). Necessary condition, honestly stated: a
document has to draw at least one unique-text line out of vertical order to be able to fail
this way — but that is not sufficient, because the check's own scoping (unique text on both
sides, ±2-column partner test, per-bucket LCS) masks it. A crude proxy run found ~18 of the
203 *passing* documents also draw some text out of vertical order; on those the offending
lines are masked by repeated text (abstained) or by a column that is not a partner. So the
mechanism is the cause of every failure, but its presence does not predict failure.

## 9. The single next action

**`tools/p2w-bench/verify_txt.py`, `_src_pages`, one line inserted immediately before
`pages.append({"number": pg.number, …})` (line 843)** — sort the page's lines into the
order the rest of the suite assumes:

```python
        lines.sort(key=lambda l: (round(l["y"], 1), l["x"]))   # new, before line 843
        pages.append({"number": pg.number, "height": pg.rect.height,
```

Rationale: the engine's vertical order is the one `t02_position`, `t04_structure` and
`t13_amount_columns` already require and the one a reader wants; asking the writer to
reproduce content-stream order instead would be a much larger change (it needs a stream
index on `Glyph`, `PdfToWord.java:1819`) and would regress the checks that depend on
geometry. The check's own body is written for reading order (column scoping, "the order a
reader follows" for ring text); its `_src_pages` is the one place that never adopted it.

Measured effect of that one line: 8 of the 10 rows clear; `305_vaccination_certificate`
stays red (ring paragraph, `PdfToWord.java:4124–4126`, needs its `lineY` restored or the
ring para split), and `39_small_caps_letter_spacing` goes red as a genuine ordering fault
to be fixed in the engine. Both follow-ups are engine work, and both are one-cause each.

If the project's decision is instead that the `.txt` must literally reproduce draw order,
the change is the opposite one and much larger: add a stream index to `Glyph`, stop sorting
by baseline alone in `toLines` (`PdfToWord.java:3733`) and re-sort in `pageOrder`
(`TxtWriter.java:189`). That is not recommended — it would contradict `t02`/`t04`/`t13`.

## 10. What was and was not measured

Measured: 213/213 documents converted with the built engine; `t08_line_order` recomputed
for all 213 (exact match with `RANKING-TXT.csv`); per-document partner/in_order/diff
breakdown; the drawing-order permutation counterfactual on all 10; the source-y-sort
counterfactual on all 213; the model dump of `305_vaccination_certificate`'s block order.

Not measured: the other 11 checks were not re-run on all 213 (only on the 10 while
reproducing); the "~18 passing documents also draw out of vertical order" figure comes from
a crude `round(x)` bucket proxy, not from the check itself; no fix was applied, so the
counterfactual numbers are simulations of the one-line change, not a re-measured baseline.

## 11. Reproduction

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
gh release download corpus-v1 --repo kavopdf/app -p '*.zip'     # 4 zips, 211 PDFs
bash /scratch/work/CS/tools/p2w-bench/build-engine.sh           # JDK fetched if absent
cd /scratch/work/CS/tools/engine-verify
java -Xmx700m -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne <doc>.pdf <outdir>                              # ONE document per JVM
python3 ../../tools/p2w-bench/verify_txt.py <doc>.pdf <outdir>/<doc>.txt --json /tmp/j.json
```

`ConvertAll` over more than ~15 documents on a 700–1200 MB heap dies with a SIGSEGV in the
JVM's own error reporting on this image; chunks of 10 with `ConvertOne` fallback work.
