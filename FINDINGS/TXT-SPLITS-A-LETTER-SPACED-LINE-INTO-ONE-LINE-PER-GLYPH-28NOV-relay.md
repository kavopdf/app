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
