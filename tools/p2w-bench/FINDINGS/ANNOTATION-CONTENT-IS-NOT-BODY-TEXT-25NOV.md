# The annotation /Contents rule: one document, measured, patch saved and NOT applied

**25 Nov 2026 · fixer slot 10:10 · engine `981ff1fa35e2cf67` (patch measured on a working tree, reverted)**

## What I believed

`FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md:17` splits `t12_word_invention` 8 documents into
"5 false positives (check) · 3 real (engine)". This run re-measured the engine half from the
source and the page, and found that one of the three is a single construct with two halves, and
that its population in the corpus is **exactly one document** - so the construct is provable,
landable and cheap, and it was never the check that was wrong on it.

## What I measured

### The two halves of the defect, in `PdfToWord.java`

| # | where | what it does | what the page does |
|--:|:--|:--|:--|
| 1 | `annotationRuns()` at `PdfToWord.java:2456-2473` | takes `getContents()` from **every** annotation that is not a widget | a note / comment / highlight remark prints **nothing** on the page |
| 2 | the `annotationRuns()` call site at `PdfToWord.java:956-965` | hoists each `/Contents` as a body paragraph; its only guard is `flat.contains(...)` against the **content stream** | a FreeText box is drawn by its **/AP appearance**, which `readAnnotationAppearances()` (`:929`) has already put into the page as glyphs - so the box is written twice |

The sibling method `annotationContentsOf()` at `:2475-2506` **already carries the correct rule**, and its
comment names this very document:

> ONLY A FREE-TEXT BOX PRINTS ITS /Contents. ... Reading them here put them in the document as body
> text - 600_reviewed_invoice_with_annotations gained "Rate for HSN 8536 confirmed with PO." (the note)
> and "Approved" (the stamp's caption, which then also REPLACED the page's own upper-case "APPROVED"),
> 34 characters that no page shows.

`annotationRuns()` was never given the same rule. Two contradictory rules, one file, 250 lines apart.

The truth reader agrees with `annotationContentsOf()`, not with `annotationRuns()`:
`verify_txt.py:742-752` and `:901-916` take `/Contents` only from subtypes **2 (FreeText)** and
**13 (Stamp)**, and only when the text is not already in the walked content stream.

### The document, before and after

`600_reviewed_invoice_with_annotations` - 1 page, 6 annotations: subtype 8 Highlight, 9 Underline,
11 StrikeOut, 0 Text (the note), 2 FreeText, 13 Stamp. Converted with `ConvertOne` on the same
engine, only the patch differing:

| | before | after |
|:--|:--|:--|
| `verify_txt.py` | **8/12 applicable, 7 passed - FAIL** | **8/12 applicable, 8 passed - PASS** |
| `t12_word_invention` | `source=785  txt=20` | not reported - 0 invented words |
| paragraphs | 14 | 12 |

The whole `.txt` diff is two lines and nothing else:

```
1,2d0
< Rate for HSN 8536 confirmed with PO.                       <- the note: 7 words no page draws
< Checked against PO 4471. Quantity on line 3 raised from 20 to 25.   <- the FreeText, a 2nd time: 13 words
```

7 + 13 = 20, which is exactly the `txt=20` the check reported. The FreeText survives once (line 71),
the page's own `APPROVED` survives (line 73), and the stamp's `/Contents` "Approved" survives (line 1)
because `drawnByAppearance()` is case-sensitive on purpose - see its comment at `:2343-2348`:
`50_annotation_text` asks for the `/Contents` string, so a case-insensitive match would delete it.

### The population - proved independently, not through the tool being changed

The change can only move a document that **carries an annotation**. I did not ask the census; I scanned
all 213 corpus PDFs with PyMuPDF and counted annotations by subtype:

```
600_reviewed_invoice_with_annotations.pdf  6  {8:1, 9:1, 11:1, 0:1, 2:1, 13:1}
documents with annotations: 1
```

`benchmarks/CENSUS.csv` agrees (`src_annots` > 0 on exactly one row). So the blast radius is one
document, and on that document every check that was passing still passes and `t12` flips to pass.
That is a complete regression proof for the construct - it is stronger than a corpus pass, because it
names the population rather than sampling it.

## The patch, saved and NOT applied

`tools/p2w-bench/PATCHES/600-annotation-runs-subtype-25NOV.patch` (36 lines, applies to
`PdfToWord.java` at `726f7b25`). Two changes, both a rule and neither a document name:

1. in `annotationRuns()`, skip any annotation whose subtype is not `FreeText` or `Stamp` - the same
   rule `annotationContentsOf()` and the truth reader already apply;
2. at the `:956` call site, skip a run `drawnByAppearance(apDrawn, ar.text)` already reports as drawn -
   the same guard the form-value loop nine lines above (`:947`) has carried all along.

## Why it is not committed

**The gate, and only the gate.** `regress.py --check` refuses:

```
ENGINE CHANGED (docx): table measured on 9e2b3e4d7869ea86, the tree is 8039ea9b058bfbce
ENGINE CHANGED (txt) : table measured on 981ff1fa35e2cf67, the tree is 8449650b7b903356
docx: no document worse than baseline
txt : no document worse than baseline
REFUSED. This commit would land a regression or an unmeasured engine.
```

Nothing got worse - the refusal is purely "this tree was not measured". `PdfToWord.java` is shared by
both writers (`txt_gate.py:11-20`), so one edit moves both formats and both tables must be re-stamped.
Re-stamping needs a completed measurement of this tree, which needs the corpus converted:
`corpus-slice.py` converts **55 documents per 250 s slice**, so 213 documents is four slices (~17 min)
before the measurement even starts, and this slot had 30 minutes left when the conversion was tried
(55 converted, then abandoned rather than half-landed).

I verified the gate is not pre-existing red: at `HEAD` in a clean worktree, `regress.py --check`
prints "docx: no document worse than baseline / txt: no document worse than baseline" and refuses only
for the missing compiled engine. So this refusal is caused by my change, and it is correct.

## The next run's first hour, in order

```
bash tools/p2w-bench/pod-prep.sh                    # warm: corpus, jdk, libs, engine
git apply tools/p2w-bench/PATCHES/600-annotation-runs-subtype-25NOV.patch
bash tools/p2w-bench/build-engine.sh
python3 tools/p2w-bench/corpus-slice.py --budget 250 -j 6   # x4, until --status says 0 to go
python3 tools/p2w-bench/gate.py --corpus /scratch/work/p2w/corpus \
        --out <the dir corpus-slice fills> --baseline benchmarks/RANKING.csv
python3 tools/p2w-bench/regress.py --stamp          # now allowed: STATE.json carries this tree
python3 tools/p2w-bench/restamp_txt.py --run --budget 260   # x N, then --report, then --apply
git add -A && git commit && git push
```

The two table rows to expect to move: `600` in `benchmarks/RANKING.csv` (its `.docx` loses two
paragraphs of text the page never drew) and `600` in `txt/RANKING-TXT.csv` (`8,7,1,0,t12` ->
`8,8,0,0,`). No other row can move, by the population scan above.

## What is now true that was not

* The "3 real engine" half of `t12` is **one construct in one document**, not three defects.
* `annotationRuns()` and `annotationContentsOf()` have been contradicting each other since the note was
  written into the latter's comment; the fix is to give the first the rule the second already states.
* The `txt` table is **stale against its own instrument**: the live verifier reports 12 checks and 2-4
  abstentions per document, the committed table records `abstained=0` and 8-10 applicable. A 20-document
  pass run by accident this slot (a `--help` on `txt_rank.py` executes a pass) rewrote the first 20 rows
  with the new column shape; I restored the table to `HEAD` and recorded nothing from it. **Any future
  re-measure will absorb that drift into 213 rows at once - it should be a deliberate pass, not a
  side effect of a fixer landing an engine change.**

## What would prove this wrong

* A corpus document with an annotation whose `/Contents` the page *does* print but whose subtype is
  neither 2 nor 13 - then change 1 would delete drawn text. The 213-PDF scan found none.
* A document where the FreeText text appears **only** in `/Contents` and not in its `/AP` - then
  change 2 would delete the only copy. On 600 the appearance draws it (line 71 of the after-`.txt`),
  which is why the copy survives.
