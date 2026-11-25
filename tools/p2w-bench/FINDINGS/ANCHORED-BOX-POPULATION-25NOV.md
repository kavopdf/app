# The anchored-box population at engine 981ff1f: replication, drift, and the brief that was never corrected

**25 Nov 2026 · slot 08:14 · engine 981ff1fa35e2cf67 · 213 documents**

## What this is, and what it is not

This is **not a new discovery.** `FINDINGS/gapcap-latch-census-01-GAPCAP-LATCH-CENSUS-25NOV.md`
(Agent A, 25 Nov 06:07, engine `b97d8172ce642eb0`) measured the same population with the same reader
and reached the same conclusion: the anchored box is worth about **8 documents, not 166**.

This run re-measured it three hours later on a **different engine**, because the charter's headline
claim was still standing in `FIXER-BRIEF.md` and every run since 06:07 has been pointed at it. The
replication is the finding: the population moved, and the brief did not.

## The measurement, two independent instruments

1. **The engine's own census** — `-Dp2w.census=<file>`, one line per page, counting which writer
   wrote the page's lines. This counts *writer calls*.
2. **`anchors.py`, new this run** — reads `word/document.xml` and counts characters actually inside
   a `<w:txbxContent>`. This counts *output*, and no counter can mislead it.

```
anchors.py, engine 981ff1f        anchors.py, engine b97d8172 (the 06:07 run)
  documents              213        documents              213
  characters         463,228        body characters    433,453
  boxed characters    27,501 (5.94%) boxed characters    28,432
  documents with boxed text  47     box carriers              61
```

Same five top carriers to within engine drift (`041122-Account_Opening_Form` 6,840 vs 6,789;
`policy-2col-spanning-section-heading` 3,046 vs 3,041; `academic-paper-ieee-2col-abstract` 2,942 both;
`magazine-2col-pullquote-spanning` 2,182 both). **The population shrank from 61 documents to 47
between the two engines.** Fourteen documents stopped carrying boxed text.

The engine census puts the mechanism's split beyond doubt:

```
anchor boxes   690   of which anchorPos 652 (94.5 %) - PAGE_POSITION_ON_ANCHOR propagation
                          anchorRule  13 ( 1.9 %) - the gap threshold the brief blames
documents with >=1 anchor box   20
```

**The gap threshold writes 13 boxes in the entire corpus.** It cannot be the mechanism of anything
large. This agrees with the 06:07 run's decomposition (latch 70 %, cap 16 %) and with its most
important correction: *the latch alone zeroes no document; only the pair does.*

## The A/B this run added: the propagation flag on its own

`-Dp2w.pagepos=0` alone, all 213 converted both ways, `word/document.xml` diffed:

```
document.xml changed : 8 of 213
boxed characters     : 27,501 -> 22,476  (-5,025, -18 %)
total characters     : 463,228 -> 463,265 (+37)
```

Consistent with the 06:07 dose table (`pagepos=0 + anchorkeep=0` = 8,572 chars, 0 documents zeroed).
**Not landed:** 5,025 characters is not worth the overlap risk the flag's own comment records
(two positioners per page, 21 overlaps and median |dy| 105.7 pt on
`policy-2col-spanning-section-heading`), and this run had no Google verification path. A lead with a
number on it, not a fix.

## New, and not in the 06:07 finding: the `!ctx.inColumn` asymmetry is empty

`flowFromBox` guards the wide-gap branch with `!ctx.inColumn` (`:4474`); `flowRow` does not (`:3591`),
so a row inside a column cell could anchor to the page and land outside its cell. Patched, rebuilt,
all 213 converted, `word/document.xml` diffed:

```
document.xml changed: 0 of 213
```

Real in code, unreachable on this corpus. **Reverted** — an unmeasurable change is a finding, not a
commit. It stays a latent fault for a document the corpus does not contain.

## What is actually wrong here, and it is not the engine

The 06:07 run measured 61 carriers and wrote it down. This run measured 47 and wrote it down. The
`FIXER-BRIEF.md` **still says**:

> That single threshold is ~166 document-failures across `04_chars_missing`, `45_char_accuracy`,
> `13_text_colours`, `44_header_footer` and `17_matched_runs`. **It is the largest engine defect
> anyone has found.**

Two runs have now disproved that sentence and neither corrected the file. A finding in `FINDINGS/`
does not reach a run that opens `FIXER-BRIEF.md` first — which is every run, by instruction. This run
corrected the sentence in place, keeping the original numbers visible so the correction is auditable.

## Method notes a later run should not have to rediscover

- **Compare `word/document.xml`, never the `.docx` bytes.** Measured: 213 of 213 differ at the byte
  level and **0 of 213** differ in `document.xml`, between two runs of the *same* engine (zip
  timestamps). A byte diff is a false positive on every document.
- **`corpus-convert.py` needs `--ensure` or `--force`.** With no flag it prints its docstring and
  returns 2 — it looks like a successful no-op and converts nothing.
- **The census file is opened in append mode**; remove it between passes or two engines' pages sum.
- `corpus-fetch.sh` + `build-engine.sh` + a full 213-document conversion is **about 5 minutes** on a
  2-core pod at `-j 4`. With the corpus on disk the commit gate's `google-safe` line stops saying
  "no .docx output directory - cannot check" and starts actually checking. It passed.
