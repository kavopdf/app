# 65_table_span_down on `75_merged_header_cell_three_columns` — the check reads a rule the page never drew

Date: 2026-11-19 · Engine HEAD `90193e0` · read-and-measure only: no engine change, no patch, no PR.

Question: what does `65_table_span_down` actually assert, and why does
`75_merged_header_cell_three_columns` still fail it now that the `.docx` carries real
`w:vMerge` restart/continue cells?

Answer in one line: **65 asserts that the `.docx`'s vMerge rectangles equal the rectangles
implied by the page's rules, column by column. On this document the page's rules imply two
merges the page's own caption says do not exist, because the source never draws the
header/body rule except under the Depot cell. Our placement is right; the expectation is
wrong.** Measured, both ways (§5).

---

## 1. The assertion, quoted

`tools/p2w-bench/tablechecks.py:26` states the intent:

```
26|  65_table_span_down    each cell's w:vMerge coverage == the rows its page rectangle encloses
```

The code that decides it — `tablechecks.py:189-190`, inside `measure()`:

```
189|            rec["ok_down"] = (_col_rows(pr, rec["p_cols"])
190|                              == _col_rows(dr, rec["d_cols"]))
```

with `tablechecks.py:147-150`:

```
147|def _col_rows(rects, ncol):
148|    """Per column, the sorted (r0, r1) intervals - the vertical-merge question."""
149|    return [sorted((r["r0"], r["r1"]) for r in rects if r["c0"] <= col <= r["c1"])
150|            for col in range(ncol)]
```

So the comparison is a **list equality, per column, of the sorted `(first row, last row)`
intervals of every cell covering that column** — left side the page, right side the `.docx`.
Nothing about the render is involved: `verify_google.py:6172` calls
`_tables.checks_for(src_path, docx_path)` and the comment above it (`6167-6169`) says so
explicitly — *"the only checks here that never look at the render, because table geometry
is a question about what was WRITTEN"*. The render column in the verifier's printout is a
mislabelled number (§6).

What counts as a span "down" on each side:

* **Page side** (`tablegrid.py:172-273`, `_table_from`): the page's thin rules are turned
  into a lattice; two adjacent slots are **one cell** when the page drew no rule on the
  boundary between them; a cell's `r0/r1` are the bounding box of the connected component.
  The premise is stated at `tablegrid.py:24-26` — *"A merged cell is a cell the page did not
  divide, and the only evidence of the division is the rule. Reading it off the rules is
  reading the page; reading it off the text extent (which is what the engine does today) is
  a guess."*
* **Docx side** (`tablechecks.py:74-132`, `_docx_rects`): the OOXML model from
  `docxtables.py` is re-assembled into rectangles with union-find; the only vertical-merge
  evidence used is `tablechecks.py:102-105`:

```
102|            if cell["vm"] == "continue" and r > 0:
103|                above = owner[r - 1].get(c)
104|                if above is not None:
105|                    union(above, key)
```

  i.e. a `w:vMerge`-continuation cell is welded to whatever owned the slot directly above
  it; the merge's row extent is then the bounding box of the welded set. `w:gridSpan` is
  expanded at 99-101 and is what makes a merge that spans columns appear in several columns
  of `_col_rows`.

Scoring (`tablechecks.py:234-238`): every table with `ok_down is not None` is asked; the
check fails if **any** table is bad — `bad = sum(1 for t in asked if not t[key])`,
`res[cid] = (len(asked), bad, bad == 0)`. One table, one vote. Abstention
(`ok_down = None`, line 202) happens when the page and docx disagree on column or row
*count*, not on the merge.

---

## 2. What the page actually draws (measured)

`/scratch/work/p2w/corpus/75_merged_header_cell_three_columns.pdf`, page 1, via
`tablegrid._segments` — 28 segments, lattice `xs=[56,196,262,328,394,456,518]`,
`ys=[126,143,160,177,194,211,228,245,262]` → 6 columns × 8 rows.

The rules that are **absent**, which is the whole story:

| boundary | drawn where | not drawn where |
|---|---|---|
| `y=143` (row 0 / row 1) | only `x ∈ [196, 394]` (bottom of SCHEDULED) | col 0, cols 4-5 |
| `y=160` (row 1 / row 2) | only `x ∈ [56, 196]` (bottom of the Depot box) | **cols 1-5** |
| `x=456` (col 4 / col 5) | only `y ∈ [143, 262]` | **row 0** |

Everything else is drawn full width / full height. The shaded bands are fills, not rules:
`(196,126)-(394,143)` (SCHEDULED) and `(394,126)-(518,160)` (the Fleet held / Breakdowns
header band).

The source **states its own geometry** in its caption, at `y≈272`:

> "The header cell marked SCHEDULED spans three columns; the depot column and the last two
> columns are merged vertically across the two header rows. Neither merge has a rule of its
> own to find."

Ground truth per the document: Depot = 2 rows (0-1), SCHEDULED = 3 columns, the **last two
columns** (plural — two cells, one per column) = 2 rows (0-1). Nothing in cols 1-3 is
merged; nothing reaches row 2.

## 3. What the check says is wrong, and what it expected (measured)

`python3 /scratch/work/diag.py <source.pdf> <converted.docx>` on the document converted by
`ConvertOne` from this tree. `62`/`63`/`66` pass, `64` and `65` fail; the verifier prints
`44/47` on a LibreOffice render, failing `18_displacement`, `64_table_span_across`,
`65_table_span_down`.

The `.docx` measured on this tree (not the numbers in the brief — see §6):

```
row 0: Depot  vm=restart   | SCHEDULED gridSpan=3 | "Fleet held Breakdowns" gridSpan=2 vm=restart
row 1: Depot  vm=continue  | Services | Km operated | Revenue (Rs. lakh) | gridSpan=2 vm=continue
row 2: Yeshwanthpur | 1,842 | 6,42,180 | 1,284.42 | 184 | 42
```

**`65_table_span_down`, per column — page (expected) vs docx (ours):**

| col | verdict | page expects | docx has |
|---|---|---|---|
| 0 | OK | `(0,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)` | same |
| **1** | **BAD** | `(0,0),(1,2),(3,3),…,(7,7)` | `(0,0),(1,1),(2,2),(3,3),…` |
| **2** | **BAD** | `(0,0),(1,2),(3,3),…` | `(0,0),(1,1),(2,2),…` |
| **3** | **BAD** | `(0,0),(1,2),(3,3),…` | `(0,0),(1,1),(2,2),…` |
| **4** | **BAD** | `(0,2),(3,3),…` | `(0,1),(2,2),…` |
| **5** | **BAD** | `(0,2),(3,3),…` | `(0,1),(2,2),…` |

Two distinct expectations, both traceable to one absent rule:

* cols 1-3 — the check expects `Services` / `Km operated` / `Revenue (Rs. lakh)` to be
  **merged down into the first data row** (`(1,2)`), because the page draws no rule at
  `y=160` in those columns. The caption says those are ordinary one-row header labels.
* cols 4-5 — the check expects the Fleet held / Breakdowns block to run **three rows
  (0-2)**, swallowing `184` and `42`, because the page draws neither `y=160` nor (in row 0)
  `x=456` there. The caption says two rows, two cells. The engine has the right row count
  but one cell for the two columns (`gridSpan=2`).

**Verdict: (c), with (a) as its mechanism — not (b).** The check is not misreading the ink:
it reads it exactly. The page genuinely does not draw the merge/separator boundary the
check is looking for, and the document's caption says the boundary the check infers is not
there. Our vMerge placement — restart on row 0, continuation on row 1, in cols 0 and 4-5 —
is the placement the caption asks for. §5 proves this by changing nothing but the ink.

The one thing in the `.docx` that is genuinely wrong is not a vMerge question: **Fleet held
and Breakdowns are a single `gridSpan=2` cell, not two cells each merged down**, which is
what "the last two columns" means. On this page's ink that defect is invisible — the page
also has no rule between them in row 0 — so 64, 65 and 66 all pass it. §5 experiment B
turns it visible.

## 4. `64_table_span_across` on the same document

`64` compares, per row, the sorted `(c0,c1)` intervals of the cells covering that row
(`tablechecks.py:135-144`, `187-188`) — the same construction one axis over, and it fails on
this document at **exactly one row**: row 2, page `(0,0),(1,1),(2,2),(3,3),(4,5)` vs docx
`(0,0),(1,1),(2,2),(3,3),(4,4),(5,5)`; rows 0, 1 and 3-7 are equal. The cause is the same
single cell the page's lattice produced, `(0,4)-(2,5)`: its bounding box reaches row 2, so
the page says `184` and `42` sit in one 2-column cell with the header, while the docx keeps
them apart. It is therefore the *same* failure as 65 cols 4-5 and has the *same* root cause
— the missing `y=160` rule — not an independent horizontal-merge bug: repairing only that
one rule in the source's ink makes 64 pass with the `.docx` untouched (§5 experiment A). The
horizontal defect that *is* real — `gridSpan=2` where the page has two columns — is the one
row 0 cannot charge, because row 0's page interval is `(4,5)` too; it surfaces only when the
row-0 column separator exists (§5 experiment B, where 64 fails rows 0 and 1).

## 5. Is a fix available in DocxWriter / PdfToWord, or is the check mis-specified?

**For 65 on this document there is no legitimate engine fix, because there is no defect.**
The docx that 65 wants is the docx that contradicts the source's caption. Both directions
were measured on this pod, on the unchanged HEAD `90193e0` conversion:

* **Experiment A — repair only the source's ink.** Copy the PDF, draw one line
  `y=160, x 196→518` (the header/body rule the source omits), keep the `.docx`
  **byte-identical**. All five table checks flip to pass:
  `{'62': (1,0,True), '63': (1,0,True), '64': (1,0,True), '65': (1,0,True), '66': (1,0,True)}`.
  Nothing in the engine changed and 65 stopped failing. That falsifies (b) outright: our
  restart/continue placement satisfies the check the moment the page draws the separator.
* **Experiment B — draw only the row-0 column separator** `x=456, y 126→143`: 65 still fails
  cols 1-3 *and* 4-5; 64 now fails rows 0 and 1 (`page (4,4),(5,5)` vs `docx (4,5)`); and
  **66 fails too** (the docx's `gridSpan=2` cell is 124 pt where the page's cell is 62 pt).
  This isolates the one real defect: the fused Fleet held / Breakdowns cell, invisible until
  the ink is complete.
* **Experiment C — both rules**: 65 passes; 64 fails rows 0 and 1; 66 fails. So with complete
  ink the residual is the fused header cell alone.
* **Experiment D — the converse.** Hand-mutate a copy of the `.docx` to the geometry the
  check's lattice describes (Fleet held/Breakdowns `gridSpan=2` restart on row 0 with
  continuations on rows 1 **and** 2; `Services`/`Km operated`/`Revenue` restart on row 1
  with continuations on row 2): all five checks pass — but only because `1,842`,
  `6,42,180`, `1,284.42`, `184` and `42` have all been swallowed into header merges. The
  check is satisfiable; it is satisfiable *wrongly*.

**Where the real fix lives, if one is wanted:** not in `DocxWriter`. The writer emits one
`w:tc` per cell the model has (`DocxWriter.java:6288-6293`, `6369-6371`, with the
restart/continuation decision derived by `vMergeContinues`, `DocxWriter.java:5708-5716`), and
the model has **one** cell for cols 4-5 — it came from the shaded band
`(394,126)-(518,160)`, whose `c0..c1` is 4..5 because no rule divides it in row 0. Splitting
it needs an interior column edge that exists on the rows below (`x=456`, drawn from
`y=143` down) or the two glyph columns (`Fleet held` at `x=399`, `Breakdowns` at `x=461`,
straddling `456`) — a change in `PdfToWord`'s cell model, not in the vMerge emitter.
`DocxWriter` cannot recover a column its input does not have.

**The check side is where the mis-specification is, and the fix is already in the tree on the
other side of the comparison.** `PdfToWord` distinguishes "the page is missing a separator"
from "the page merged a cell" at `PdfToWord.java:7923-7925`:

```java
7923        boolean[] cellMerge = new boolean[ncells];
7924        for (int i = 0; i < ncells; i++) {
7925            cellMerge[i] = cellBands.get(i).size() < cellCover[i];
```

— a rectangle is a vertical merge only when its own glyphs occupy *fewer row bands than the
rows it covers*. That is exactly the discrimination `tablegrid.py` refuses to make, and on
this document it is the difference between right and wrong: the Depot box and the shaded
band carry one text band over two covered rows (merge), while `Services`/`1,842` carry two
bands over two covered rows (missing separator). Applying the same test to the page side of
`tablechecks` — or to the `_page_rects` used by 64/65 — makes 65 pass on
`75_merged_header_cell_three_columns` **and** leaves `table-with-merged-cells` passing, since
its merges (measured: DOWN col 0 `(2,4)` and `(5,6)`, col 6/7 `(0,1)`) are cells whose text
occupies fewer bands than they cover. That is the change to propose; it is not made here.

**Falsification tests, named.** (i) *Is the failure ours?* Draw the missing `y=160` rule into
a **copy** of the source PDF, keep the `.docx` byte-identical, re-run `checks_for` → 65 must
still fail if our placement is wrong. Measured: it passes. (ii) *Is the failure the check's?*
Mutate only the `.docx` to the check's lattice → the check must fail if it is measuring the
page faithfully rather than a guess. Measured: it passes, at the cost of a table no reader
would accept. (iii) *Does the check see vMerge at all?* `table-with-merged-cells` passes 65
with the page's genuine 2- and 3-row merges reproduced exactly — so a green 65 is
achievable and the check is not blind.

## 6. Two corrections to the brief, both measured

* The brief says the `.docx` "now contains 3 `w:vMerge` restarts and 3 continuations". On
  `90193e0` the converted file contains **2 restarts and 2 continuations**
  (`<w:vMerge w:val="restart"/>` ×2, `<w:vMerge/>` ×2), plus `gridSpan=3` ×1 and
  `gridSpan=2` ×2. Not 3 and 3.
* `verify_google.py` prints the failing table checks as `source=1 render=1`
  (`6189-6191` maps `v[0]→"source"`, `v[1]→"render"`), but for ids 62-66 those are
  *(tables asked, tables bad)*. `source=1 render=1` means "one table asked, one table bad",
  not "the source and the render each score 1". Nothing in 62-66 reads the render.

## 7. Not measured

* Google Docs' own export (unreachable from this pod): the 41/47 in the brief is not
  reproduced here. Only the LibreOffice render was measured — `44/47`, failing
  `18_displacement`, `64_table_span_across`, `65_table_span_down`.
* The rest of the corpus: only `75_merged_header_cell_three_columns` and
  `table-with-merged-cells` were converted and measured. How many other documents fail 64/65
  for this same missing-separator reason is **not measured**.
* The share5 metric (27.31 / 7.62) was not recomputed — not measured here.

## Reproduction

```
git clone https://github.com/kavopdf/app && cd app
bash tools/install-gate.sh && pip install scipy
export JAVA_HOME=/scratch/work/.p2w-jdk/jdk; export PATH=$JAVA_HOME/bin:$PATH
bash tools/p2w-bench/build-engine.sh
python3 -c "import sys;sys.path.insert(0,'benchmarks');import p2w;p2w.corpus()"
cd tools/engine-verify && java -Xmx700m -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
    ConvertOne /scratch/work/p2w/corpus/75_merged_header_cell_three_columns.pdf /tmp/o75
python3 tools/p2w-bench/verify_google.py <source.pdf> <soffice render of the docx> --docx /tmp/o75/<name>.docx
```

The per-cell diagnostic (`_col_rows` / `_row_cols` compared column by column and row by row)
is `tablechecks.measure()` plus the two interval helpers — 40 lines, no repo change.
