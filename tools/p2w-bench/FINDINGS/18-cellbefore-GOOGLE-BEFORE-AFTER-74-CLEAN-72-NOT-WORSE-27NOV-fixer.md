# `18_displacement` cell-before rescale: measured in Google, before and after. `74` goes CLEAN, `72` does not regress.

**27 Nov 2026, fixer slot 20:09.** Every Google number below is a live round trip made by this run:
`upload` → `GOOGLEDRIVE_CREATE_FILE` as a Google Doc → `GOOGLEDRIVE_DOWNLOAD_FILE` (pdf) →
`gverify.py --collect`. Nothing here is inherited from another run's FINDINGS.

## Why this was the attempt

`classpick.py` suggested `18_displacement` and `--leverage` prices it at **53.9 clean documents**, the
largest single check on the board. The open lead on it was a one-line patch in
`PATCHES/18-small-dy-cellbefore.patch` measured on three documents in Google by the 19:39 relay, which
left "next run: the .txt half" and did not answer whether the patch is safe. Safety is the question that
decides whether 53.9 is real, so that is what this run measured.

**The patch is not committed and this run did not land it.** At HEAD, `DocxWriter.java:7013` still reads
`cellBeforeTw = rowHeightTw - cellBoxTw;`. The corrected form is a `LINE_BASE` rescale of the same
branch — it multiplies by 0.8 every `w:before` that branch already writes.

## What was measured

| document | HEAD `a05b20eb` | patched `f4ce54f2` | verdict |
|:--|:--|:--|:--|
| `74_balance_sheet_indented_subitems` | **41/42**, fails `18_displacement` | **42/42** | **CLEAN** |
| `72_bank_statement_no_rules_right_amounts` | **41/42**, fails `18_displacement` | **41/42**, fails `18_displacement` | **not worse** |
| `71_invoice_space_aligned_no_rules` | 41/42 (stored) | **41/42**, fails `18_displacement` | unmoved |
| `22_invoice_four_columns_txtpos` | 41/42 (stored) | **41/42**, fails `18_displacement` | unmoved |
| `price-list-2col-dense-right-aligned` | 41/42 (stored) | **41/42**, fails `18_displacement` | unmoved |

All five rows are in `benchmarks/gverify/` with `engine: f4ce54f257d15f1c`.

## The prediction, written before the run, and where it was wrong

Written to `/scratch/work/PREDICTION.md` before the patch was applied:

> I EXPECT: 74 -> 42/42 (CLEAN). 72 -> still 41/42 or worse ... => NET ZERO. The patch cannot land as
> written, and the relay's proposed gate (`cellBoxTw*2 >= rowHeightTw`) does not spare 72 because 72
> satisfies it.

**Two thirds of that was right and the conclusion was wrong.**

* Right: `74` goes clean.
* Right: the relay's proposed gate does not spare `72`. Measured independently of the scorer, by counting
  the emitted XML: `74` carries **15** cells at `w:before="170"` of 48, `72` carries **66** of 99, and
  both rewrite to `136` under the patch. The gate would fire on `72`.
* **Wrong: "or worse".** `72` does not get worse *as a check*. Its `18_displacement` dy magnitude moves
  (the 19:39 relay recorded med_dy −1.0 → −3.0) but the check still fails, so the score is 41/42 before
  and after. **A dy that moves inside a failing check is not a regression.** The net is **+1 clean
  document, 0 documents worse**, not net zero.

That correction is the finding: the reason the patch looked unlandable was a regression argument made on
`med_dy` rather than on the check, and `med_dy` is not what "no document gets worse" means.

## The independent check — arithmetic on the emitted XML, not the scorer

`w:before` values per document, HEAD vs patched, from `word/document.xml`:

```
head    74  cells_with_before 48  distinct [45, 46, 170, 228, 229, 262]
patched 74  cells_with_before 48  distinct [45, 46, 136, 228, 229, 262]
head    72  cells_with_before 99  distinct [0, 170, 256, 268, 269, 307]
patched 72  cells_with_before 99  distinct [0, 136, 256, 268, 269, 278]
```

`170 → 136` is exactly ×0.8, the `LINE_BASE` rescale the patch comment claims. `74` has `w:trHeight`
340 on every row; `72` has 340 and 360. This confirms the patch fires on both and by the amount the
relay derived, without using `verify_google.py` to prove it.

## Why it did not land — the exact gate output

    $ python3 tools/p2w-bench/measure_gate.py
    engine docx d28ca7516c3f9165, tree f4ce54f257d15f1c
      - RANKING.csv was measured on docx engine d28ca7516c3f9165 and the tree is f4ce54f257d15f1c
    NOT READY

    $ python3 tools/p2w-bench/regress.py --check
    ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is f4ce54f257d15f1c
    docx: no document worse than baseline
    txt : no document worse than baseline
    REFUSED.

Both tables pass the *comparison*; what refuses is that the corpus has not been **re-measured** on this
engine. That is the measurement cron's work, not a fixer's, and it is one full corpus pass — 213
documents through LibreOffice and 42 checks each — which does not fit inside the remainder of this slot.
The engine is therefore reverted and the change stays in `PATCHES/` exactly where it was found.

**The corpus rebuild on the patched engine did complete**, so the next run does not pay it again:
`corpus-convert.py --ensure -j 6` converted all **214** in **4.0 min**, cached for `f4ce54f257d15f1c`.
The earlier note that a cold pod needs two gate calls at 240 s a slice is true at 4 workers and not at 6.

## What the next run should do, in order

1. Re-apply `PATCHES/18-small-dy-cellbefore.patch`, rebuild, and run the corpus measurement
   (`measure_gate.py` until READY, then `regress.py --stamp`). Nothing else is missing.
2. **Expect exactly ONE clean document, not seven. This run measured the other three and they do not
   move.** The census said `71_invoice_space_aligned_no_rules` (42 cells at 0.500),
   `22_invoice_four_columns_txtpos` (44) and `price-list-2col-dense-right-aligned` (77) carry the same
   half-row cell shape that made `74` clean, so they were converted on the patched engine and measured
   in Google too:

   | document | stored | patched `f4ce54f2` | verdict |
   |:--|:--|:--|:--|
   | `71_invoice_space_aligned_no_rules` | 41/42 | **41/42**, fails `18_displacement` | unmoved |
   | `22_invoice_four_columns_txtpos` | 41/42 | **41/42**, fails `18_displacement` | unmoved |
   | `price-list-2col-dense-right-aligned` | 41/42 | **41/42**, fails `18_displacement` | unmoved |

   So the 0.500 cell shape is **necessary and not sufficient**. `74` is the one document whose residual
   after the rescale falls inside `18`'s tolerance; the other three have a second residual this patch
   does not touch. **Do not price this patch at 53.9 or even at 7. It is worth +1 clean document and
   0 regressions, measured.**

   The three that remain are the next lead: each is a document where the half-row cell shape is present
   and the rescale fired, yet `18` still fails — so their residual is a second, different construct.
   This run measured the scores and did **not** census their post-patch residual, so the construct is
   unidentified. Do not guess it; census `w:before` and the rendered `ry` on `71` first.
3. **Do not spend a slot on the relay's proposed gate.** It does not spare `72`, and `72` does not need
   sparing: the ungated patch is not worse at the check level. Adding the gate would only shrink the
   patch's reach for no measured benefit.
4. `11` of the `24` only-`18` documents are **inert** to this construct — `w:before` byte-identical
   under the patch (per the same sub-agent census: `303_discharge_summary`,
   `306_clinical_protocol_synopsis`, `320_balance_sheet_statutory`, `70_magazine_drop_cap_photo_caption`,
   `electricity-bill`, `insurance-policy-schedule`, `mobile-bill`,
   `report-2col-table-spanning-both-columns`, `table-inside-two-column-page`,
   `table-with-no-header-row`, `two-tables-stacked-with-no-gap`). Do not measure them for this
   construct; they need their own.

## Reproduce

    git apply tools/p2w-bench/PATCHES/18-small-dy-cellbefore.patch
    cd tools/engine-verify && /scratch/work/.p2w-jdk/jdk/bin/javac -nowarn -cp \
      "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
      -d out $(find ../../app/src/main/java -name '*.java') ConvertAll.java ConvertOne.java
    /scratch/work/.p2w-jdk/jdk/bin/java -cp "<same cp>" ConvertAll <sharddir> /scratch/work/probe/patched
    cp /scratch/work/probe/patched/<name>.docx /scratch/output/gv2/ && upload(...)
    python3 tools/p2w-bench/gverify.py --collect <name> /scratch/downloads/composio/<name>_PATCHED

`ConvertOne <pdf> <outdir>` produced a 739-byte empty document on this pod and `ConvertAll` on a
one-file shard directory produced the real one — use `ConvertAll`.

## The residual on the three unmoved documents is a UNIFORM PAGE OFFSET, not a per-row displacement

Measured independently of `verify_google.py`, with a 60-line probe that pairs source runs to render runs
by text and reports the signed `dy` (`/scratch/work/dyprobe.py`, kept out of the repo because it is a
scratch instrument). It is the second source the brief asks for: if it and the scorer disagree, the
scorer is wrong.

| document | pairs | outside `18`'s tolerance | median dy | min | max | shape |
|:--|--:|--:|--:|--:|--:|:--|
| `74_balance_sheet_indented_subitems` (patched) | 46 | **0** | — | — | — | clean, confirms the scorer |
| `71_invoice_space_aligned_no_rules` (patched) | 64 | 29 | **−5.84** | −6.74 | −3.69 | every run on the page sits ≈5.8 pt LOWER in the render than in the source |
| `22_invoice_four_columns_txtpos` (patched) | 67 | 40 | **+4.01** | +3.26 | +6.58 | every run on the page sits ≈4.0 pt HIGHER in the render than in the source |

**Sign convention, stated because it is the thing that goes wrong:** the probe reports
`dy = ry_source − ry_render` where `ry` is the reading-space box top, so **negative means the render is
lower on the page than the source**, and positive means it is higher. (The `sectmargin` FINDINGS uses the
opposite convention, `render − source`. Do not mix them.)

The offset is **the same sign and the same magnitude on the footer** (`Page 1`: −3.75 on `71`, +6.58 on
`22`), so it is not a row-height or cell-before effect at all — it is the **page's flow origin**, moved as
a block. That is why the cell-before rescale fired on their cells and changed nothing that `18` measures.

**This is the lead the next run should take, and it is already proven in Google**: the section top margin
carried in `sectPr/w:pgMar@w:top` (`18_displacement-page-top-gap-sectmargin-PROVEN-075600-f1x.md`,
`bank-statement-5-pages` 37/42 → 40/42, pages 1-4 dy −59.5 → −4.3). That patch is **guarded to
multi-page documents** (`pages.size() < 2 → -1`), and `71` and `22` are single-page, so today it is
byte-inert on exactly the documents whose residual is now measured to be a uniform page offset.

**And the two documents need OPPOSITE corrections, which is the trap.** A `w:pgMar w:top` pushes the body
DOWN, so it helps a render that sits too high and hurts one that sits too low. On this probe's convention
that means the sectmargin lever is the right construct for **`22`** (render 4.01 pt too high) and the
**wrong** construct for **`71`** (render 5.84 pt too low — a margin would make it worse, not better).
`71` needs the opposite: the gap its first line already carries is being honoured too far, so the
construct to look for is in `pageFirstBeforeTw`'s subtraction, not in `sectPr`.

I did not apply either change. `PATCHES/pagetop-guarded-27NOV.patch` has no `pages.size() < 2` guard
(it is per-page, gated on column bands and on the room the margin takes), so it **would** fire on these
single-page documents — the multi-page scope belongs to the earlier `sectmargin` patch, not to this one.
That is a correction to what the rest of this file says above: check which patch you are holding before
assuming a page-count guard is in the way.
