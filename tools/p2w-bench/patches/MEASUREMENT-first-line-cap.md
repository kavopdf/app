# The 2000-twip first-line cap: reach, origin, and a minimal fix

Engine HEAD measured: `29f89a6` (kavopdf/app, cloned to /scratch/work/f5).
Corpus: release `corpus-v1` (four assets, unzipped flat) = **211 PDFs, 545 pages**.
No commit, no push. `verify_google.py` / `verify_txt.py` untouched.

---

## Corrections first

1. **The corpus is 211 documents, not 208.** The three assets named in the brief
   (`p2w-all-groups` 53, `p2w-batch-1` 80, `p2w-round2-additions` 3) give **136** PDFs.
   The remaining 75 (`300_*`–`417_*`) come from a fourth asset in the same release,
   `pdf-to-word-test-corpus-v3.zip`. `tools/p2w-bench/BASELINE.md` holds **211** rows
   (`grep -c "^|" BASELINE.md` = 213 including 2 header lines). "208" is the older
   figure repeated in the repo's prose; every count below is over the real 211.
2. **The 29 pt / baseline-780 instance is not in this corpus.** No page in `corpus-v1`
   has a first line at baseline 780. The closest real instance is
   `411_nested_xobject_transforms`, first line at baseline **142.0**, needing a **132.8 pt**
   gap, losing **32.8 pt** — the same shape as the reported 130 pt → 29 pt case.
3. **`place()`'s copy of the cap is dead code.** `grep -n "\bplace(" DocxWriter.java` returns
   only the declaration (2855) and a comment (3010) — no callers. The live sites are the
   `flowFromBox` pair (2984, 3040) and the `flowRow` pair (2523, 2543).
4. **`315_gazette_notification` no longer fails `pageFits`.** The comment on
   `GAP_CAP_SPEND_TW` (DocxWriter.java:135-139) says the guard separates 315 (does not fit)
   from 344 (fits). Measured today with `-Dp2w.debugGaps=1`:
   `GAPS fits=true bands=true spend=true ph=841.8898`. The guard the comment relies on no
   longer discriminates that document, so the fix below cannot lean on it by name — only on
   what it measures.
5. My first census pass reported 0 pages over 100 pt. That was a bug in my script
   (PyMuPDF `rawdict` spans carry `chars`, not `text`), not a result. Corrected and rerun.

---

## 1. The cap, its comment, and what the records say

**Where it is.** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`

| line | site | live? |
|---|---|---|
| 2523 | `flowRow`, first row on a page | yes |
| 2543 | `flowRow`, row after a deliberate `breakPage` | yes |
| 2862 | `place()`, `ctx.newPage` | **no — no callers** |
| 2984 | `flowFromBox`, first line on a page | yes |
| 3040 | `flowFromBox`, line after a deliberate `breakPage` | yes |

All five read `Math.min(2000L, Math.round(topGap * TWIPS_PER_PT))` — 2000 twips = 100 pt
(`TWIPS_PER_PT = 20.0`, line 52).

**The comment at 2975-2981** (the branch the brief points at) says why the first line gets a
gap at all, and says nothing about the number:

```
2975| // The FIRST line on a page still has to land at its own y. The section carries zero
2976| // margins, so without this it starts at the very top of the sheet: on file 21 every
2977| // line measured 46 pt high against the PDF, a constant offset with the pitch already
2978| // correct. Measured, not guessed - dy was -46.2, -48.3, -45.0, -46.6 over the first
2979| // four lines of the page. The lift is the part of the box above its baseline, and
2980| // where the box is taller than the space the page leaves, the box is shortened to
2981| // fit rather than the line being placed below its own y.
```

There is **no comment stating why 100 pt**. The `2000` is bare in all five places.

**The only recorded trace of the number** is the commit that introduced it,
`3935e08` "3.51.4: the first line on a page now lands at its own y — file 21 goes from 0 % to
93 % within 5 pt" (Thu 5 Nov 2026 15:18 +0530):

> "Fix: on a new page, before = b.y - lineHeight, **clamped at 100 pt**."

That sentence is the whole record. The commit's own "RESULT" section reports the win
(file 21 dy −45.4 → −1.0, |dy|<5 pt 0 % → 93 %) and two regressions it chose to report
rather than hide (file 20, file 16). No measurement, no failure mode and no document is
attached to the 100 pt figure.

**Searches run, and what they returned:**

- `grep -rn "clamped at 100\|100 pt\b" --include=*.md .` → one hit, unrelated:
  `LESSONS.md:35` ("above 100 pt off on 70: the spacer could only ever reach the 16 near-misses").
- `git log --all --oneline --grep="100 pt"` → only `3935e08`.
- `HYPOTHESES.md`, `DEFECTS.md`, `REMAINING-DEFECTS.md`, `REMAINING-DEFECTS-ARCHIVE.md`,
  `BATCH-LOG.md`, `INCIDENTS.md`: **nothing records what the 100 pt clamp protected against.**
  What they do record is the *other*, later ceiling — `GAP_CAP_TW = 2400` (120 pt,
  DocxWriter.java:119, with a full rationale at 95-118) and `GAP_CAP_SPEND_TW = 20000`
  (1000 pt, 141, rationale at 121-140). `REMAINING-DEFECTS-ARCHIVE.md:724-725` and
  `BATCH-LOG.md:248` both describe spacing-before as "still capped at 120 pt" — i.e. the
  records document 120 pt as the general ceiling and never mention a separate 100 pt
  first-line ceiling.

**So: nothing records a reason.** What can be inferred from dates, and is inference only:
the clamp (5 Nov 15:18) predates every guard that could now do the same job —
`GAP_CAP_TW` (`1061a81`/`c79c81d`), `pageFits`/`spendGaps` (`4c8c2b7`, 7 Nov; `62c65ff`, 8 Nov),
and the page-budget guard `fitPage` (`ddbbb08`, 9 Nov, the commit that says the budget "shipped").
At the moment the clamp was written there was no ceiling on a page's total spend and no
`pageFits` test, so a hard 100 pt was the only thing standing between "spend the gap" and
"push the rest of the sheet off the paper" — the failure the `GAP_CAP_TW` comment later
describes for `373_leave_application_form`'s 422 pt footer. That is a plausible reason, not
a recorded one.

---

## 2. Reach: how many pages need more than 100 pt

Method — engine geometry, replicated: for every page, the topmost text span's baseline
(`span["origin"][1]`) and size; box `linePt = max(4, 1.15 * size)` (`LINE_FACTOR`,
DocxWriter.java:70); `topGap = baseline - 0.8 * linePt` (`LINE_BASE = 0.8`, line 93), which is
exactly the expression at 2982. Script: `/scratch/work/meas/gapcensus.py`.

```
{"docs": 211, "pages": 545, "pages_over_100pt": 5, "docs_with_over": 5, "max_gap_pt": 741.54}
docs with >100pt first-line gap: 5
  15_stamp_on_scanned_page.pdf                   pages 1  over 1  max 741.5
  410_form_xobject_reused.pdf                    pages 1  over 1  max 161.0
  414_transparency_softmask.pdf                  pages 1  over 1  max 271.9
  415_inline_images.pdf                          pages 1  over 1  max 251.9
  57_centred_title_page_left_body_pages.pdf      pages 2  over 1  max 226.2
```

**The reach is 5 pages, in 5 documents, out of 211 documents and 545 pages** (0.9 % of pages,
2.4 % of documents). The distribution has a hard cliff: the 6th-largest first-line gap in the
corpus is 91.9 pt, and 44 documents top out between 50 and 100 pt, so nothing else is close.

The census measures geometry, not the engine's actual clamp, so it was cross-checked against
what the engine wrote: `grep` for `w:before` exactly equal to the clamp (2000 twips) in all
211 produced docx (`/scratch/work/meas/capbound.py`):

```
paragraphs with w:before==2000 (cap bound): 5
  410_form_xobject_reused                  p1  base 172.0  need 161.0  loss 61.0   'Invoice line item - corrugat'
  411_nested_xobject_transforms            p1  base 142.0  need 132.8  loss 32.8   'NESTED FORM - scaled and rot'
  414_transparency_softmask                p1  base 282.0  need 271.9  loss 171.9  'The blue bar above is drawn '
  415_inline_images                        p1  base 262.0  need 251.9  loss 151.9  'The checkerboard above is an'
  57_centred_title_page_left_body_pages    p1  base 240.0  need 226.2  loss 126.2  'SRI VINAYAKA INSTITUTE OF TE'
```

Five clamped paragraphs, four of them in the census's five. The fifth
(`15_stamp_on_scanned_page`, 741.5 pt) does not clamp: its top text is a rotated stamp written
as a framed/anchored paragraph, and its first flow paragraph is written `before=0 line=1`.
The census missed `411` (132.8 pt) because `411`'s topmost *span* is not the first flow
paragraph. **Union of both methods: 5 pages in 5 documents.** Losses: 32.8, 61.0, 126.2,
151.9, 171.9 pt.

`-Dp2w.debugGaps=1` shows all five of these pages are `spend=true` (`fits=true`), so the
engine already believed it could afford the gap — the 100 pt clamp is what refused.

---

## 3. Measured baseline displacement (source PDF vs render)

Built with `tools/p2w-bench/build-engine.sh`, corpus converted with `ConvertAll`, both builds
rendered with LibreOffice and matched to the source PDF line by line on text
(`/scratch/work/meas/render_measure.py`). dy = render baseline − PDF baseline, in pt.

| document | page | PDF first-line baseline | render baseline, before | dy before | render baseline, after | dy after | worst |dy| on page, before → after |
|---|---|---|---|---|---|---|---|
| 411_nested_xobject_transforms | 1 | 142.0 | 109.2 | **−32.8** | 142.0 | **0.0** | 32.8 → **0.0** |
| 410_form_xobject_reused | 1 | 172.0 | 111.0 | **−61.0** | 172.0 | **0.0** | 341.0 → 280.0 |
| 57_centred_title_page_left_body_pages | 1 | 240.0 | 113.8 | **−126.2** | 240.0 | **0.0** | 126.2 → **0.2** |
| 415_inline_images | 1 | 262.0 | 110.1 | **−151.9** | 262.0 | **0.0** | 151.9 → **0.0** |
| 414_transparency_softmask | 1 | 282.0 | 110.1 | **−171.9** | 282.0 | **0.0** | 171.9 → **0.0** |

Every one of the five first lines lands exactly on its PDF baseline after the change, and the
whole page follows it (the loss is inherited by every line below, exactly as reported: on 414
and 415 *every* matched line moves from −171.9/−151.9 to 0.0).

`410` is the honest exception on the rest of the page: its first line is fixed (−61.0 → 0.0)
but other lines on that page stay 280 pt out — a separate, pre-existing defect on an
image/form page, not something this change touches or claims.

---

## 4. The minimal change, and what moves

**Change** (4 lines, one substitution each; `first-line-cap.patch`):

```diff
-                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
+                beforeTw = (int) Math.min(gapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));
```

at DocxWriter.java:2523, 2543, 2984, 3040. It does not invent a ceiling: it gives the first
line of a page the **same ceiling every other gap in the same method already obeys**
(2965, 3002, 3022 all call `gapCapTw(ctx)`): 2400 tw (120 pt) normally, 20000 tw (1000 pt)
when `pageFits` says the page's own content fits the sheet (`gapCapTw`, line 186). That
mechanism is not new — it is the one added for exactly this failure on 7-8 Nov
(`4c8c2b7`, `62c65ff`, "spend the page's white space when the page fits the sheet"), which is
already measured across the corpus and already guarded against the 315 regression by
`pageFits`.

**What moves — whole corpus, 211 documents, both builds converted and compared XML by XML
(`/scratch/work/meas/compare.py`):**

```
document.xml identical: 206   differing: 5
  ['410_form_xobject_reused', '411_nested_xobject_transforms', '414_transparency_softmask',
   '415_inline_images', '57_centred_title_page_left_body_pages']
files whose reconstructed page count changed: []
```

Per changed file, exactly one attribute, and no page-count change:

```
410_form_xobject_reused      diffs 1  pages 1->1   para 0  before 2000 -> 3219  (161.0 pt)
411_nested_xobject_transforms diffs 1 pages 1->1   para 0  before 2000 -> 2656  (132.8 pt)
414_transparency_softmask    diffs 1  pages 1->1   para 0  before 2000 -> 5438  (271.9 pt)
415_inline_images            diffs 1  pages 1->1   para 0  before 2000 -> 5038  (251.9 pt)
57_centred_title_page_left_body_pages diffs 1 pages 2->2  para 0 before 2000 -> 4524 (226.2 pt)
```

(The 5 "identical" exceptions are the 5 changed files; a byte-level `cmp` shows all 211 zip
files differ, which is container metadata only — `word/document.xml` for an unaffected
document is md5-identical, checked on `300_prescription_rx`.)

**Controls — nothing else re-opens.** Rendered before/after, same dy statistic:

| document | pages | matched lines | median dy | worst |dy| |
|---|---|---|---|---|---|
| 315_gazette_notification | 1 → 1 | 35 | 0.0 → 0.0 | 22.9 → 22.9 |
| 373_leave_application_form | 1 → 1 | 32 | −2.6 → −2.6 | 10.3 → 10.3 |
| 331_pid_diagram | 1 → 1 | 26 | −1.3 → −1.3 | 1.5 → 1.5 |
| 21_form_labels_x60_values_x300_txtpos | 1 → 1 | 48 | 0.0 → 0.0 | 1.9 → 1.9 |

`315_gazette_notification` is the document the records say rejected the last attempt to widen
this class of gap. It does not move, on one page, before or after.

**Engine's own suite, unchanged numbers** (`TestPdfToWord`, `TestRealDocs`, run with
`libs/aar/assets` on the classpath as `verify-engine.sh:22` does):

```
PDF2WORD TOTAL: 29 passed, 0 failed
  300_prescription_rx 96.8% ok   311_fir_police_form 97.0% ok   350_question_paper 81.7% ok
REALDOCS TOTAL: 3 passed, 0 failed
```

Identical to the figures recorded in `3935e08` (29 passed; 96.8 / 97.0 / 81.7).

**Residual risk, stated plainly.** When `spendGaps` is false the ceiling moves from 100 to
120 pt (`GAP_CAP_TW`). On this corpus that widening is inert — every page where the cap binds
has `spend=true` — so it is unmeasured here. If that 20 pt is not wanted, the strictly
conservative variant is `ctx.spendGaps ? GAP_CAP_SPEND_TW : 2000`, which by the same evidence
produces byte-identical output on all 211 documents while leaving the non-fitting-page
behaviour exactly as it is today. It is the variant I would ship if a reviewer wants zero
movement outside `pageFits` pages.

---

## 5. CONFIDENCE

- **The cap exists at those lines, and no record states its reason — HIGH.** Read directly;
  five grep/`git log -S` searches; the only mention is `3935e08`'s "clamped at 100 pt".
- **Reach = 5 pages / 5 documents — HIGH.** Two independent methods (PDF geometry; `w:before`
  exactly 2000 in the engine's own output) agree on the same five, and the cliff at 91.9 pt
  makes an off-by-a-few-points error irrelevant.
- **Measured displacement — HIGH for the five documents.** Rendered both builds, matched by
  text, all five first lines go to dy 0.0. Caveat: LibreOffice, not Google Docs, is the
  renderer here; Google's re-reading of `w:line` is a known separate class
  (`20_within_10pt`, closed unfixable) and was not re-measured through Drive.
- **"Nothing else moves" — HIGH on this corpus** (206/211 `document.xml` byte-identical,
  no page-count change, four controls frozen, suite unchanged). **MEDIUM beyond it**: the
  fix inherits whatever `pageFits` gets wrong on unseen documents, and the 100→120 widening
  for non-fitting pages is unexercised here.
- **The reason the cap existed — LOW / inference only.** Dates support "it predated the
  guards that now do the job", but no record says so, and I am not claiming it as fact.

---

## 6. EVIDENCE

```
$ gh release download corpus-v1 -R kavopdf/app -D corpus      # 4 assets, 136+75 = 211 PDFs
$ bash tools/p2w-bench/build-engine.sh                        # "engine built - ConvertAll ready"
$ java -cp "$CP" ConvertAll /scratch/work/corp /scratch/work/docx       # done: 211 files, 0 failed
$ python3 meas/gapcensus.py                                   # pages_over_100pt: 5
$ python3 meas/capbound.py                                    # 5 paragraphs with w:before==2000
$ python3 meas/compare.py                                     # 5 files changed, page counts unchanged
$ python3 meas/render_measure.py <5 docs> base fix            # first-line dy -> 0.0 on all five
$ java -Dp2w.debugGaps=1 ... ConvertOne <doc>                 # GAPS fits=true spend=true, all five
$ java -cp "$CP" TestPdfToWord                                # 29 passed, 0 failed
$ java -cp "$CP" TestRealDocs                                 # 3 passed (96.8 / 97.0 / 81.7)
```

Artifacts: `first-line-cap.patch` (the 4-line change, uncommitted, working tree only —
`git status` shows `M app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`).
Scripts kept at `/scratch/work/meas/` (`gapcensus.py`, `capbound.py`, `compare.py`,
`render_measure.py`), plus `census.json`, `capbound.json`, `compare.json`, `render5.json`,
`render_ctl.json`.
