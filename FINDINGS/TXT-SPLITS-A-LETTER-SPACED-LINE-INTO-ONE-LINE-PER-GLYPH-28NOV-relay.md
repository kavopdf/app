# The `.txt` writes a letter-spaced line as one line per glyph — the `.docx` does not

**28 Nov 2026, relay slot 09:16.** Fixer run. Class: `t09_page_furniture`, then the txt's last three
documents. No engine change was landed: the construct below is real and measured, but a `TxtWriter` change
needs a full 213-document `.txt` re-conversion and re-stamp before the commit gate will take it, and that
did not fit the slot. **This is a named next step with a one-document measurement, not a hypothesis.**

---

## 1. The measurement

Three of the six failing `.txt` documents are the same defect, and it is a writer defect, not an
instrument one.

| document | txt lines | single-character lines | fails |
|:--|--:|--:|:--|
| `305_vaccination_certificate` | 85 | **47** | `t08_line_order` 32 of 33 |
| `041122-Account_Opening_Form` | 1193 | **274** | `t06_encoding`, `t09_page_furniture` 29 owed / **125** present, `t12_word_invention` |
| `Account_Opening_Form_Fillable_filled` | — | — | same three, same counts |

A line the page draws as **one** line — `NATIONAL IMMUNISATION REGISTRY`, letter-spaced — arrives in the
`.txt` as sixteen lines, one glyph each:

```
col 19 'N'   col 18 'A'   col 18 'T'   col 18 'I'   col 18 'O'   col 18 'N'
col 19 'A'   col 19 'L'   col 20 'I'   col 20 'M'   col 21 'M'   col 22 'U'
col 23 'N'   col 24 'I'   col 25 'S'   col 26 'A'   col 27 'T'   col 28 'I'  ...
```

The source draws it as one line at `y = 20.1`, `x = 28.0` (`_src_pages()` on the PDF, one entry). The
`.docx` for the same document carries it merged — `word/document.xml` contains the string
`NATIONAL IMMUNISATION REGISTRY` — so **`DocxWriter` merges the glyphs of one letter-spaced line and
`TxtWriter` does not.** Two writers, one model, opposite answers.

## 2. Why it costs three documents

* **`t08_line_order` on 305 (32 of 33).** The glyph lines are emitted at the END of the file, after the
  body, while the page draws them at the TOP (`y = 20.1` against a body that starts at `y = 82.4`). The
  `(text, column)` partner that is out of order is one of those glyphs. Fixing the merge puts them back
  where the page drew them.
* **`t09_page_furniture` on the two Account forms (29 owed / 125 present).** `_furniture_key` folds each
  one-character line to a one-character key; `M`, `Y`, `D`, `A`, `T`, `E` are counted as present against a
  running head the page drew 29 times in total. This is the "125 single-char present" the 26 Nov census
  found and could not attribute: the census called it instrument asymmetry because the *writer* was
  faithful — but a line broken into its glyphs is not faithful to a page that drew one line.
* **`t12_word_invention` / `t06_encoding` on the same two.** The 127 `U+FFFD` come from a ligature glyph
  the engine cannot name; the 09:08 slot refuted the glyph-name fallback and the geometric inference for
  those (`/ToUnicode` maps them to `<FFFD>` by the producer's hand, and 89 of 127 resolve nearest to the
  wrong ligature). **That part is unchanged by this finding** — the two Account forms will not go clean on
  the merge alone. `305` will.

## 3. What the next slot does, in order

1. `TxtWriter.appendPara` writes one line per `Para` in the model. Find the baseline-merge `DocxWriter`
   uses for letter-spaced runs and apply the same one before a `Para` is written as a line. The model is
   shared, so the merge must be writer-local — a change to `PdfToWord` would move the `.docx` too and
   drags the 54-minute docx re-measure with it.
2. Measure `305` alone first: `ConvertOne 305_vaccination_certificate.pdf`, then
   `verify_txt.py <pdf> <txt>`. Expected `t08 33 of 33` and `PASS`. **A merge that does not clear 305 is
   the wrong merge** — 305 is one page with one letter-spaced head and nothing else to confuse it.
3. Only then the full `213`-document `.txt` re-conversion and `restamp_txt.py`, diffed against
   `RANKING-TXT-BASELINE.csv`. The `t09` present count on the two Account forms must fall, not rise.
4. `t09`'s own counting formula was **not** touched this slot. Per-page (`B1`) and edge-window (`B2`)
   formulations were analysed by the 27 Nov relay and the census refuted the window family; the merge
   above is upstream of both and must be measured before either is judged again.

## 4. What this slot did verify, so the next run does not pay for it again

* `regress.py --check` **PASSES at HEAD**: `docx: no document got worse`, `84 document(s) still worse
  than the 15 Nov baseline — frozen, not forgiven`, `txt: no document worse than baseline`. The 84 are a
  frozen debt the table may pay down, not a refusal. `google-safe` is SKIPPED (no `.docx` output
  directory). **The gate is not what blocks an engine change; the re-measure is.**
* The corpus slice is warm on this pod: the first `regress.py --check` call spends its 280 s filling a
  slice, the second returns `PASS` in under a second. `install-gate.sh` calls `pod-prep.sh` and cannot
  finish inside one 300 s call on a cold pod — run `pod-prep.sh` on its own.
* `benchmarks/DISP-TABLE.csv` attributes the 103 `18_displacement` failures: **75 `table-row`** (median
  worst dy 13.0 pt, max 237.1), 16 `multipage/pagebreak` (median 104.5 pt), 6 `table-short`, 6 `other`.
  The table-row cluster is the largest single prize in the docx half and it is the `ROW_RUNG_UNDER_TW`
  trade the 28 Nov 02:24 slot measured (rung=0: 57 regressions against baseline, versus 84 at HEAD).
  **That table is not in the repo** — the `b648594972a7682b` stamp is referenced in
  `FINDINGS/ROW-RUNG-IS-A-PER-DOCUMENT-TRADE-NOT-ONE-CONSTANT-28NOV.md` and nowhere else, so landing the
  rung needs its own full re-measure.

---

# CORRECTION, same slot: the merge is not the fix — `t04` proves the `.txt` was faithful

Written after the change in §3 was actually built and measured on 305 (a sub-agent did the build; I ran
`verify_txt.py` on its output myself, so these are my numbers, not its report).

**The page really does draw 85 lines, and 47 of them are one character.** `_src_line_count()` — PyMuPDF's
own line granularity, the object `t04_structure` counts — returns **85**, of which **47 are
single-character**. The `.txt` carries **85** lines, **47** single-character: it is a *faithful
transcription*, line for line. The 26 Nov census was right and §1 of this file is wrong to call the writer
unfaithful.

| | non-empty lines | single-char lines | `t04_structure` | `t08_line_order` | verdict |
|:--|--:|--:|:--|:--|:--|
| `.txt` at HEAD | **85** | **47** | 85/85 pass | 33/32 **FAIL** | FAIL |
| merged `.txt` | **42** | 3 | 85/42 **FAIL** (drift 0.49, `MAX_LINE_DRIFT` 1.5) | 34/34 pass | **FAIL** |

The merge fixes `t08` and breaks `t04` by arithmetic: removing 43 lines from an 85-line file halves it,
and any merge of this family does. **305 does not go clean on the merge; it changes which check it fails.**

Two further facts from the build, both worth keeping:

* The merged line reads `NATIONALIMMUNISATIONREGISTRYGOVERNMENOFINDIA` — the inter-word spaces of the seal
  are drawn as their own one-character boxes and `rtrim` drops them, so the merge also loses the spaces.
  A merge that keeps them is a different, larger change.
* The seal paragraph is *appended last* in `page.blocks` (correct for the `.docx`'s anchored boxes) while
  its own `top` is y=271, so the glyph run sits after a footer at y=777. That misplacement is the `t08`
  inversion, and it is a `TxtWriter` **ordering** fact, not a line-splitting one — the same paragraph
  carries the `Issued: …` line at y=273 and that line lands in the right place.

**What this leaves as the next step, replacing §3.** The construct is a *granularity disagreement*, not a
writer defect: `t08`'s partner rule keys on `_src_pages` lines and the source's 47 one-character lines
cannot be ordered by `(text, column)`, while `t04` demands the `.txt` keep all 85. Both checks are
satisfiable at once only if the `.txt` keeps 85 lines **and** the one-character lines are placed in drawn
order — i.e. fix the *placement* of the appended paragraph (the ordering half), not the line count. That
is the measured, narrow target: move the run paragraph by its `top` without merging anything, then `t04`
stays 85/85 and `t08` should reach 33/33. **Not measured — the build stopped at the merge.**

**Do not land the merge.** It moves `305` from one failing check to another and it makes the `.txt`
unfaithful to a page that drew 85 lines.

---

# The placement fix works: 305 goes PASS. Here is the exact change, measured, not landed

A second build in the same slot, ordering only and merging nothing. **I re-ran `verify_txt.py` on its
output myself**: `7/12 applicable, 7 passed, 5 abstained  PASS` — `t04_structure` 85/85 (unchanged),
`t08_line_order` 33/33 (was 33/32), 85 non-blank lines, 47 single-character, 30 blank, 3384 bytes.

## Why it is right

The page's seal paragraph (`top = 270.89`, 48 lines, `lineY` **empty** — its glyphs sit on baselines that
are not horizontal) is block 10 of 11, i.e. **after** the footer at y = 781.9. `pageOrder()` emits blocks
in model order, so the seal's text lands after the footer. Hoisting it by the one number it has — `top` —
puts it between `This certificate is digitally signed…` (y = 264) and `Verify online` (y = 304), where the
page drew it. The inversion `t08` charged is in column 6: the page draws `Issued: 18-03-2022 14:22 IST |
Certificate ID: …` before `This is a computer generated certificate…`, and `Issued` is line 45 *inside*
the seal paragraph, so it travelled with the seal.

## The change, verbatim (TxtWriter.java, +82/−1, two hunks)

Hunk 1 renames the existing `pageOrder` body to `pageOrderByColumn` and wraps it:

```java
private static List<Object> pageOrder(PdfToWord.Page page) {
    return hoistLastPara(pageOrderByColumn(page));
}

/** A paragraph the model appended last, put back where its own top says the page drew it.
 *  MOVE UP ONLY; NEVER ACROSS A TABLE (the run of Paras immediately before it ends at a Table);
 *  NOTHING IS MERGED (line count must stay 85 for t04). */
private static List<Object> hoistLastPara(List<Object> blocks) {
    if (blocks == null || blocks.size() < 3) return blocks;
    int last = -1;
    for (int i = blocks.size() - 1; i >= 0; i--) {
        if (blocks.get(i) instanceof PdfToWord.Para || blocks.get(i) instanceof PdfToWord.Table) { last = i; break; }
    }
    if (last < 0 || !(blocks.get(last) instanceof PdfToWord.Para)) return blocks;
    PdfToWord.Para para = (PdfToWord.Para) blocks.get(last);
    float top = para.top;
    if (Float.isNaN(top) || top <= 0f) return blocks;
    int run = last;
    while (run > 0 && blocks.get(run - 1) instanceof PdfToWord.Para) run--;
    if (run >= last) return blocks;
    int at = -1;
    for (int i = run; i < last; i++) {
        float t = ((PdfToWord.Para) blocks.get(i)).top;
        if (Float.isNaN(t)) continue;
        if (t > top) { at = i; break; }
    }
    if (at < 0) return blocks;
    List<Object> out = new ArrayList<>(blocks);
    out.remove(last);
    out.add(at, para);
    return out;
}
```

Hunk 2, in `appendPara`, is one changed line and it is load-bearing:

```java
-            lastY = ly;
+            // A LINE WITH NO BASELINE DOES NOT SET THE FLOW'S Y. ly is 0 when the paragraph
+            // carries no lineY at all (the seal case), and letting that 0 become lastY tells
+            // the next paragraph the flow is at the top of the page: measured, hoisting the
+            // seal without this guard inserted ten blank lines before "Verify online" and took
+            // the file from 30 blanks to 37, where the page drew a three-line gap.
+            if (ly > 0f) lastY = ly;
```

## Blast radius, measured by the same build

* A probe over all 214 corpus PDFs: the hoist fires on **27 pages in 27 documents** (rotated stamps,
  seals, ornate borders, and 305).
* Full-corpus `.txt` byte-diff, base build against patched build: **27 of 214 differ, 187 byte-identical**
  — exactly the pages the probe named.
* `verify_txt.py` on all 27: `t04` and `t08` and the pass count are **identical on the other 26**;
  **305 is the only document that moves** (6 → 7 passed). No check regressed anywhere.
* The `.docx` is untouched: all 9 zip parts of `305_vaccination_certificate.docx` are byte-identical
  before and after.

## Why it is not in the tree

It was measured at 90+ minutes into the slot. Landing it needs the engine rebuilt on the pod, a full
213-document `.txt` re-conversion and a re-stamped `RANKING-TXT.csv`, and the commit gate refuses without
that stamp. **The next run should apply the two hunks above verbatim, re-convert, re-stamp, and expect
`305` to be the only mover.**
