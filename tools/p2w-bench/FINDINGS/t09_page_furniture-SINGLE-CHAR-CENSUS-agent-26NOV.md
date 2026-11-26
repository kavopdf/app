# t09_page_furniture — census of the single-character lines

**Date:** 26 Nov 2026
**Engine:** HEAD `51c3b64a` (compiled by `tools/p2w-bench/pod-prep.sh`, step 6, 12 engine sources)
**Documents:** `041122-Account_Opening_Form.pdf` and `Account_Opening_Form_Fillable_filled.pdf`,
converted with `ConvertOne` (9 pages each, 480 / 489 paragraphs), scored with
`tools/p2w-bench/verify_txt.py`.

## Verdict

**Instrument asymmetry. The writer is not at fault, and the number cannot be fixed in the writer.**

| | count | what it is |
|---|---|---|
| single-character `.txt` lines in the file | **274** | 264 artifacts of a letter-spaced run cut into pieces, 10 genuine one-glyph draws |
| of which fall in t09's own top/bottom band | **26** | all 26 are class (b); they are the owed `D`/`M`/`Y` occurrences |
| t09 `present` (whole file) | **125** | 29 in the band + **96 outside it** |
| t09 `owed` (band only) | **29** | `Y` 12, `D` 8, `M` 6, `Date` 3 |
| writer's share of the 125 | **0** | every one of the 29 owed occurrences is present, once, on the right page |
| instrument's share of the 125 | **96** | the entire surplus, produced by counting the whole file against a band-restricted owed |

Restricting the `present` side to the same band yields **29 against 29 owed — PASS — on both
documents**, and the match is exact per `(page, key)`, not merely in total.

The premise in the brief ("the Y/D/M ones are the date box, drawn as eight separate one-glyph
lines on one baseline") **does not hold at the content-stream level**. The date box is drawn by
**one** text-showing operator with letter-spacing:

```
/Fm0 (bbox 448.458 739.621 550.182 748.738)
  /TT0 1 Tf
  1.45 Tc -1.45 Tw 0 Ts 100 Tz 0 Tr 6 0 0 6 448.458 743.7373 Tm
  (DDMMYYYY)Tj
```

One `Tj`, eight characters, `Tc = 1.45` at 6 pt type. Across page 0's own content stream and its
17 form XObjects there is exactly **one** single-character `Tj` — `(1)Tj`, the footer page number —
plus 13 single-space `( )Tj` runs and **no `TJ` array at all**. That single `(1)Tj` is exactly what
the census classes as (a): the footer digits are the only genuinely one-glyph draws in the
document, and they are not furniture keys. Every letter-spaced run on the page has that same
shape — 17 form XObjects, one `Tj` each:

| XObject | Tc | text |
|---|---|---|
| Fm0, Fm1 | 1.45 | `DDMMYYYY` |
| Fm9, Fm10 | 1.5 | `STD` |
| Fm11, Fm14, Fm6 | 1.5 / 1.563 | `FIRSTNAME` |
| Fm12, Fm15, Fm7 | 1.502 | `MIDDLENAME` |
| Fm13, Fm16, Fm8 | 1.502 | `LASTNAME` |
| Fm2 | 1.563 | `SALUTATION FIRST NAME` |
| Fm3 | 1.502 | `MIDDLE` |
| Fm4 | 1.502 | `NAME` |
| Fm5 | 1.502 | `LAST NAME` |

So "eight one-glyph lines" is what **PyMuPDF's `get_text("dict")` line model** makes of one
8-character run whose glyph advances are ~12.96 pt at 6 pt type. `_src_pages()` inherits that
model, and `t09`'s `owed` is computed from it. The writer produced one `.txt` line per glyph
because the source model says there are eight lines there.

---

## 1. t09 as it stands (re-measured this run, not read from a file)

```
041122-Account_Opening_Form.txt          10/12 applicable, 7 passed, 2 abstained  FAIL
    t06_encoding               source=47477      txt=127
    t09_page_furniture         source=29         txt=125
    t12_word_invention         source=48845      txt=14
Account_Opening_Form_Fillable_filled.txt 10/12 applicable, 7 passed, 2 abstained  FAIL
    t06_encoding               source=47562      txt=127
    t09_page_furniture         source=29         txt=125
    t12_word_invention         source=48944      txt=14
```

Per key, both documents identical:

| key | owed (band) | present (whole file) | surplus |
|---|---|---|---|
| `Y` | 12 | 41 | 29 |
| `D` | 8 | 33 | 25 |
| `M` | 6 | 45 | 39 |
| `Date` | 3 | 6 | 3 |
| **total** | **29** | **125** | **96** |

`owed` is per drawn occurrence, not per page: the date box is in the top band of pages 0, 1 and 2
only (`Y` 4+4+4, `D` 4+2+2, `M` 2+2+2, `Date` 1+1+1). Page 0 owes four `D`s, not two, because
the bottom band of page 0 carries two `STD Tel.` runs that PyMuPDF also splits into `S`/`T`/`D`
glyph lines — the owed set already contains writer-shaped single-glyph lines.

## 2. The census

Method — no guessing about which drawn line a `.txt` line came from. A diagnostic dumper
(`tools/engine-verify/DumpLines.java`, new file, **not committed**, not part of the engine) walks
`PdfToWord.Result` and writes one row per **model line** — every `para.lines[i]` and every table
cell paragraph — with the x and y `TxtWriter` places it at. The `.txt` page is then aligned to
the model line-for-line with `difflib.SequenceMatcher` (every one of the 1193 non-blank `.txt`
lines of `041122-Account_Opening_Form` pairs; on `Account_Opening_Form_Fillable_filled` 9 of 1202
do not — the filled field values `12/01/2000`, `jalapur`, `89`, `hsjw862`, `Gautam`, `25/10/1999`
and four similar, which the `.txt` carries and my dumper does not walk; none of the nine is a
single-character line or a furniture key). Each single-character `.txt` line therefore carries the
model's own x and y. Finally the drawn glyph at that (x, y) is read from `page.get_texttrace()`, and the
question asked is: **how many characters did the show operation that drew this glyph carry on
this baseline?**

* span of 1 character → **(a) genuinely a one-glyph line the page drew**
* span of 2+ characters → **(b) a letter-spaced run that the line assembly cut into pieces**

| | `041122-Account_Opening_Form` | `Account_Opening_Form_Fillable_filled` |
|---|---|---|
| single-character `.txt` lines | 274 | 274 |
| (a) genuine one-glyph draw | **10** | **10** |
| (b) artifact of a cut letter-spaced run | **264** | **264** |
| distinct (page, run) instances cut | 36 | 36 |
| distinct run texts | 29 | 29 |

Per page: 90 / 20 / 10 / 32 / 1 / 1 / 9 / 13 / 98 (pages 0-8), identical on both documents.

The 264 class-(b) lines come from 36 letter-spaced runs — `DDMMYYYY` (87 lines), `LASTNAME` (48),
`FIRSTNAME` (39), `MIDDLENAME` (38), `SALUTATION FIRST NAME` (10), `MIDDLE` (6), `LAST NAME` (6),
`STD` (6), and 21 smaller ones. 249 of the 274 come through the **table** path (`appendTable`, one
cell per line), 25 through the **paragraph** path (`appendPara`).

The 10 class-(a) lines are the only genuinely one-glyph draws in the document: the page-number
footers `1`…`9` (each its own `Tj`, x = 584.1) and one `#` at x = 131.5. None of them is a
furniture key.

**Band split of the same census:** 26 of the 274 single-character lines are inside t09's band —
`Y` 12, `D` 8, `M` 6, every one of them class (b). Those 26 plus the three `Date` lines are
exactly the 29 owed. The other 248 single-character lines (238 b + 10 a) are in the body, and
they are where the 96 surplus comes from.

**Attribution of the 125 `present` occurrences:**

| drawn run it came from | occurrences | in band |
|---|---|---|
| `DDMMYYYY` | 85 | 24 |
| `MIDDLENAME` | 15 | 0 |
| `LASTNAME` | 5 | 0 |
| `FIRSTNAME` | 4 | 0 |
| `MIDDLE` | 4 | 0 |
| `LAST NAME` | 1 | 0 |
| `STD` | 1 | 1 (page 0 bottom band) |
| `Date` / ` Date` (4-char lines) | 6 | 3 |
| singletons inside longer cut runs (`STD`, `District*:`, `Personalised Cheque…`, …) | 4 | 0 |
| **total** | **125** | **29** |

All 125 are faithful transcriptions: each is a real glyph the page drew, on the page and at the
column the `.txt` puts it. None is invented, duplicated or misplaced.

## 3. The exact asymmetry

`tools/p2w-bench/verify_txt.py`, `t09_page_furniture`, lines **1316-1353**:

```python
pages = _src_pages(src_pdf)                       # 1316
for pg in pages:                                  # 1319
    h = pg["height"] or 1.0
    for ln in pg["lines"]:
        if not (ln["y"] <= h * FURNITURE_BAND     # <-- owed: BAND ONLY
                or ln["y"] >= h * (1.0 - FURNITURE_BAND)):
            continue
        ...
        elements = {k: v for k, v in element_pages.items()      # 1334
                    if len(v) >= FURNITURE_MIN_PAGES and any(ch.isalpha() for ch in k)}
txt_furniture = Counter(_furniture_key(ln.strip()) for ln in lines)   # 1336  <-- present: WHOLE FILE
```

`owed` is filtered by `y` into the top/bottom 12 % band; `present` (line 1336) is a
`Counter` over **every line of the file**, with no y and no page. On a form whose body is full of
letter-spaced capitals this makes `present` a count of *the whole document's* `D`/`M`/`Y`
single-character lines against *the band's* 29.

## 4. What restricting the `present` side to the same band yields

**Ground truth** (each `.txt` line inherits the y of the drawn line it was written from; a line is
counted only if that y is inside the band):

| | `041122-Account_Opening_Form` | `..._Fillable_filled` |
|---|---|---|
| owed | 29 | 29 |
| present, whole file (today) | 125 | 125 |
| present, band-restricted | **29** | **29** |
| verdict under the fix | **PASS** | **PASS** |

Exact per `(page, key)`, both documents:

```
page 0: D 4, M 2, Y 4, Date 1     page 1: D 2, M 2, Y 4, Date 1     page 2: D 2, M 2, Y 4, Date 1
```

which is the owed set element for element. The writer reproduced all 29, on the right pages.

**Two implementable versions, measured, not assumed:**

1. **Align-then-band (recommended).** The instrument already holds both sequences — `_src_pages()`
   for the source and `_txt_lines()` for the `.txt` — and `t08_line_order` already aligns them.
   Give each `.txt` line the `y` of the drawn line it aligns to, then apply the existing band test.
   Measured: **29 vs 29, PASS, both documents.** This is the number in the table above.
2. **Ordinal window (rejected).** Take the first *n_top* and last *n_bot* non-blank lines of each
   `.txt` page, where *n_top*/*n_bot* are the source page's band line counts. Measured:
   **29 (PASS)** on `041122-Account_Opening_Form` but **22 (FAIL)** on
   `Account_Opening_Form_Fillable_filled` — the filled version draws 14 band lines on page 0
   against 13, and one extra line in the top band shifts every later window. A proxy that passes
   one of the two documents and fails the other is not a fix. (This is also why the earlier
   "first and last six lines" approximation returned 11 against 29: it is the same idea with a
   worse constant.)

Note that the `.txt` carries no y — it encodes x as leading spaces and y as blank lines only — so
a band restriction on the `present` side cannot be done from the `.txt` alone. It needs the
alignment, which is the same dependency `owed` already has on `_src_pages`.

## 5. The writer side: the code paths, and why they must not be "fixed"

The `.txt` is one line per model line, unconditionally:

* `TxtWriter.appendPara` — `app/src/main/java/com/kavopdf/app/engine/TxtWriter.java:516-552`:
  `for (int li = 0; li < para.lines.size(); li++) { … sb.append(trimmed).append('\n'); }` — one
  `.txt` line per `para.lines[i]`, no merging, no gap test.
* `TxtWriter.appendTable` — `TxtWriter.java:568+`: one cell per line, by design
  ("One cell per line, which is what a reader searching the text expects: every line the PDF drew
  stays a line of its own").

So `TxtWriter` is not where the split happens. The split is upstream, in the line assembly:

* `PdfToWord.toLines` — `PdfToWord.java:3801` `float outlier = Math.max(6f, median * 0.85f);`,
  `:3819` `gapPts = g.x - (prev.x + prev.width)`, `:3827` `boolean wideGap = gapPts > outlier;`
  — a glyph whose advance exceeds its own width by more than 6 pt starts a new segment, hence a
  new `Line`, hence a new `.txt` line. On these runs the advance is 12.96 pt for a ~4.3 pt glyph,
  so the gap reads ~8.7 pt against an outlier of 7.4 pt and the glyphs are cut. Where the gap
  dips under the threshold two or three glyphs survive joined — which is why the `.txt` shows
  `A T I` and `O N` between single characters of the same run. The 36 runs carry 1634 glyphs
  between them; 264 of those end up alone on a line and the rest are joined in groups of two or
  three.

**What the correct assembly would be, if this were to be changed at all:** the gap that separates
two fields is not the same quantity as the page's declared character spacing. A run drawn by one
show operation with `Tc = 1.45` is one word; subtracting the run's own `Tc` (or `Tw`) from
`gapPts` before comparing to `outlier` would keep a letter-spaced run whole while leaving every
real field gap (which has no `Tc` behind it) cut. That is a change in `toLines`, not in
`TxtWriter`, and it is **not implemented here** — see the next paragraph for why it must not be
made as a t09 fix.

**Merging the runs would make t09 worse, not better.** `owed` is computed from the per-glyph
`get_text("dict")` model. If the writer merged `DDMMYYYY` into one line, the `.txt` would carry
three `DDMMYYYY` lines and three `Date` lines in the band and nothing matching keys `D`, `M`, `Y`:
`present` would fall from 29 to **3** against an unchanged `owed` of **29**. The split is exactly
what the source side of the instrument asks for. Any change here has to move both sides of t09 at
once, which is the definition of an instrument question.

## 6. Measured vs inferred

**Measured this run:**
* both documents convert to 9 pages at HEAD and reproduce `t09 source=29 txt=125` exactly;
* 274 single-character `.txt` lines in each file, 264 class (b) / 10 class (a), by glyph-level
  attribution to `get_texttrace()` spans, with 0 unmatched model lines;
* the 125 `present` occurrences attributed one by one to the drawn run they came from, 29 in the
  band and 96 outside it;
* the content stream: `/Fm0 … 1.45 Tc … (DDMMYYYY)Tj`, one show operator, no single-char `Tj`, no
  `TJ` arrays; 17 form XObjects on page 0, one `Tj` each;
* `owed` 29 / `present` 125 / band-restricted `present` 29, with an exact per-`(page, key)` match
  on both documents;
* the ordinal-window proxy: 29 (PASS) on the first document, 22 (FAIL) on the second.

**Inferred, and flagged as such:**
* that the 12.96 pt advance against a ~4.3 pt glyph is what pushes `gapPts` past the 6 pt
  `outlier` on these runs. I did not instrument `toLines`; the glyph widths are read from the
  rendered boxes, and the code path and threshold are read from source. The *effect* (one `.txt`
  line per glyph) is measured; the exact arithmetic inside the running engine is inferred.
* that the writer would emit `present = 3` if the runs were merged. That is a counterfactual
  computed from the model, not a build.

**Not reproducible from the brief:** the brief's **247** single-character lines. At HEAD the
number is **274** on both documents, under the definition that produces t09's `present` (a
non-blank `.txt` line whose `strip()` is one character). I could not find a definition that gives
247 — not `len(line) == 1` (0), not paragraph-only (25), not excluding table cells (25), not
excluding the band (248), not excluding `col == 400` (181). The verdict does not depend on which
number is right: the census classifies every one of the 274, and the 29/96 split is computed from
the 125 occurrences rather than from the 274.

## 7. Repro

```bash
cd /scratch/work/CS
bash tools/p2w-bench/pod-prep.sh
cd tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/041122-Account_Opening_Form.pdf /scratch/work/p2w/t09out
java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/Account_Opening_Form_Fillable_filled.pdf /scratch/work/p2w/t09out
python3 ../p2w-bench/verify_txt.py /scratch/work/p2w/corpus/041122-Account_Opening_Form.pdf \
        /scratch/work/p2w/t09out/041122-Account_Opening_Form.txt
# the census and the recomputation, as run this slot:
javac -nowarn -cp "$CP" -d /scratch/work/dumpout DumpLines.java
java -cp "/scratch/work/dumpout:$CP" DumpLines <the.pdf> /scratch/work/dump-<base>.tsv
python3 census.py <the.pdf> <the.txt> /scratch/work/dump-<base>.tsv
python3 recompute.py
```

`census.py` and `recompute.py` are copied beside this file as `t09-census.py` and
`t09-recompute.py`. `tools/engine-verify/DumpLines.java` is left untracked in the working tree and
is not on the engine classpath.

## 8. What this does not settle

* `t06_encoding` (`source=47477 txt=127`) and `t12_word_invention` (`source=48845 txt=14`) also
  fail on both documents. They are outside this census and nothing here touches them.
* Whether a letter-spaced run *should* be one line in a `.txt` is a product question, not a t09
  question. This finding says only that it is not what makes t09 read 125, and that changing it
  without changing `owed` would break the check further.
