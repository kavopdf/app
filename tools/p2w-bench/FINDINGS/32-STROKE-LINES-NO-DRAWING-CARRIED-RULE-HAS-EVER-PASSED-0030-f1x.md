# 32_stroke_lines — no rule carried as a floating drawing has ever passed in Google

**Measured 22 Nov 2026, 00:20–00:30 IST, fixer slot. Engine HEAD `6c6cf642e13b7ed6`, corpus
fetched (213 PDFs), all 213 converted with `ConvertAll`, cross-tabulated against the 192
committed Google verdicts in `benchmarks/gverify/`.**

## The claim

A rule that the `.docx` carries **only as a floating `<w:drawing>`** has never been observed to
pass `32_stroke_lines` in Google Docs. Across the 192 scored documents there is **no
counter-example**. The only two documents that carry a source rule *and* pass the check carry
that rule as a **table-cell border** (`w:top|bottom|left|right w:val="single"` inside a `w:tbl`).

## The numbers

For every scored document: count the rules the source PDF draws (`verify_google._doc_rules`),
count the border declarations in the emitted `word/document.xml`, and read the committed Google
verdict.

| source rules | `.docx` has a border | fails `32` | documents |
|:--|:--|--:|--:|
| yes | yes | fail | 69 |
| yes | **no** | fail | **76** |
| yes | yes | **pass** | **2** — `373_leave_application_form`, `64_newspaper_uneven_columns_ad_boxes` |
| yes | **no** | **pass** | **0** |
| no | no | pass | 24 |
| no | yes | pass | 21 |

The two directions that matter:

* **pass with rules and no border: 0.** Not one document in the corpus.
* **fail with no source rules: 0.** The check never fires on a document that has no rule, so it is
  not simply "fails when the page has lines".

The 69 documents that fail *with* borders are not a counter-example: their borders are the grid of a
real table the source drew, at the table's own coordinates, not a carrier placed at the rule's
coordinates. A border only satisfies the check when it is **at the rule's geometry**.

## The four probe documents, side by side

| document | source rules | `<w:drawing>` | tables | single borders | Google `32` |
|:--|--:|--:|--:|--:|:--|
| `373_leave_application_form` | 1 | 20 | 2 | **8** | **pass** |
| `64_newspaper_uneven_columns_ad_boxes` | 4 | 3 | 1 | **4** | **pass** |
| `17_three_column_widths_txtpos` | 2 | 2 | **0** | **0** | fail (`{source:2, render:1}`) |
| `45_coloured_callout_box` | 2 | 5 | **0** | **0** | fail at HEAD (`{source:2, render:1}`) |

`45` is the document that reached **42/42** under last slot's carrier patch
(`patches/rule-carrier-per-rule-2008.patch`), which replaces the floating drawing with a 1×1
floating table carrying `w:tcBorders`. That is the same construct `373` and `64` already carry, and
it is the second independent confirmation of this law.

## Why the check cannot see the drawing

`verify_google._rule_segments()` (line 1096) walks `page.get_drawings()` only. Google's PDF export
rasterises every anchored shape, so a rule that Google *did* draw arrives as an image XObject and
contributes zero segments. This was recorded as a lead at 23:13 on 21 Nov
("CHECK BLIND TO PICTURES"). **This finding does not depend on it**: whether Google drops the
drawing or rasterises it, the result for the check is the same, and the fix is the same — do not
carry a rule as a drawing.

## What this settles, and what it does not

**Settled.** The pBdr carrier is refuted (HANDOFF), the floating-drawing carrier is refuted here,
and the table-cell border carrier is confirmed on 2 corpus documents plus 2 patched ones. The next
`32_stroke_lines` build is not a guess: emit every rule as a table-cell border.

**Not settled, and this is the whole remaining risk.** The carrier patch still loses **one of two**
carriers on `17`, `18`, `19`, `24`, `26`, `53`, `74`, `315`, `32`, `334`, `34`, `37`, `47`, `49`,
`74`, `product-catalogue-code-left-price-right` — 16 documents that fail **only** `{05, 32}` and
would be **clean** if both carriers placed. A subagent read the XML of `17`, `45`, `53`, `74`, `394`
and found the carriers byte-identical between a document that places both (`45`) and one that does
not (`17`): same `tblpX/tblpY`, same `trHeight 1 exact`, same `tcBorders`. The only property that
separates them is **position in the block sequence**: in `17`/`53`/`74` the two carriers are the
**last two blocks of `<w:body>`**, with nothing after them; every placed carrier in `394` and `45`
has a paragraph after it or between it and the next carrier.

**The falsification is one build and one Google round trip**: append one empty `<w:p/>` after each
carrier. If the trailing pair is the cause, `17`/`53`/`74` read `{2, 2}` and 16 documents go clean.
If they still read `{2, 1}`, the cause is elsewhere and the 69-borders-failing population needs the
same treatment.

## Reproduce

```
bash tools/p2w-bench/corpus-fetch.sh
bash tools/p2w-bench/build-engine.sh
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
    ConvertAll /scratch/work/p2w/corpus /scratch/work/out3
python3 - <<'PY'   # the table above
import zipfile,re,json,glob,sys; sys.path.insert(0,'tools/p2w-bench')
import fitz, verify_google as V
...
PY
```
