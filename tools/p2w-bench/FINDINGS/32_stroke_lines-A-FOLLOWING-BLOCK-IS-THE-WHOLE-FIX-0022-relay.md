# A rule carrier needs one block after it: 17 and 53 go 40/42 → 42/42 PASS in Google

**22 Nov 2026 · relay slot 00:15 → · every number below is a Google Docs export scored with the 42 checks**

## The finding in one sentence

Google Docs ignores `w:tblpY` on a floating `w:tblPr` table whose anchor paragraph has no body block
after it, and stacks that table under the carrier before it; put **one empty paragraph after each
carrier** and the same table renders at its own `tblpY`.

## What was measured

The carrier patch (`patches/rule-carrier-per-rule-2008.patch`) applied to HEAD `cef8de6`, the engine
built, and documents uploaded to Google Docs one at a time and exported. Baseline is the committed
`benchmarks/gverify/*.json`.

| document | committed | carrier alone | carrier + one empty `<w:p/>` after each |
|:--|--:|--:|--:|
| `17_three_column_widths_txtpos` | 40/42 | 41/42 (`32` lost 1 of 2) | **42/42 PASS** |
| `53_single_space_body_15_headings` | 40/42 | 41/42 (`32` lost 1 of 2) | **42/42 PASS** |

The rule geometry in the Google export, read with the check's own `_doc_rules` / `_rules_lost` at the
check's own constants (`RULE_THIN_REN` 4.25, `RULE_BAND_REN` 4.25, `RULE_TOL` 24, `RULE_OVERLAP` 0.80):

| document | source rules (y, pt) | render segments (y, pt) | lost |
|:--|:--|:--|--:|
| `17` carrier alone | 80.00, 793.89 | 80.5, 81.5 | **1** |
| `17` + following block | 80.00, 793.89 | 80.5, **794.5** | **0** |
| `53` carrier alone | 82.00, 793.89 | 81.5, 82.5 | **1** |
| `53` + following block | 82.00, 793.89 | 81.5, **794.5** | **0** |

Both documents keep one page. Nothing else changed: the same docx, the same carrier coordinates, the
same borders — one empty paragraph inserted after each carrier block and nothing else.

## The mechanism, isolated with a ladder probe

`17`'s carrier build was edited by hand so that six carriers sat at `tblpY` = 80.0, 700, 750, 775, 785
and 793.89 pt, each in its own paragraph, all six consecutive at the end of `<w:body>`. Uploaded to
Google once and exported. The render segments were:

    80.5   81.5   82.5   82.5   83.5   84.5      (page 0, h, length 483 pt, weight 1.0 pt)

The 80 pt carrier rendered at 80.5. **The other five rendered at 81.5–84.5, every one of them
ignoring its own `tblpY`.** The page's text runs to y = 811.6, so this is not clamping to the text
area and not a page overflow: the tables are laid out in flow, one under the other, directly beneath
the first floating table on the page.

That is the whole defect. `{source: 2, lost: 1}` on the sixteen documents that fail
`{05_chars_extra, 32_stroke_lines}` is not a lost shape and not a Google-dropped construct — it is the
second carrier being placed 712 pt from where the page drew its rule.

## Why `394` passes and these do not

`394_map_with_legend` carries six rules and scores 42/42 in Google with the carrier patch. Its six
carrier paragraphs are **interleaved with the page's content**, so each has a body block after it and
each is laid out at its own `tblpY`. `17`, `53` and `74` emit both carriers at the end of the body,
where the first is placed and the second stacks under it. This is the same property the last slot
observed on five documents and could not test.

## What this does to the two claims it touches

* **"A drawing-carried rule never passes" (last slot's headline, `76 of 76 fail`) is wrong as stated.**
  `373_leave_application_form` passes `32_stroke_lines` carrying its rule as a floating `<w:drawing>`
  and has **zero** `w:tcBorders` and **zero** floating tables. It passes because a real table's top
  border sits at y = 108.00 and the source rule is at 87.70 — inside the check's own 24 pt tolerance.
  The claim survives only in the weaker form "no document passes on a drawing *at the rule's own
  coordinates*", which is a claim about the check's tolerance, not about Google.
* **"The trailing-paragraph theory is dead" is also wrong as stated.** A corpus-wide cross-tab of
  carrier position against the committed verdicts found the property in 145 of 145 failures *and* in
  146 of 146 documents that carry a floating carrier — 100 % prevalence, so it has no discriminating
  power **on the HEAD build**. At HEAD every carrier is a drawing and the writer emits shapes after
  the page's paragraphs, so the cross-tab was measuring the writer's block ordering, not the cause.
  It cannot test the mechanism, and the mechanism is now measured directly in Google on two documents
  and a six-rung ladder.

## Why it is a lead and not landed

The change is `patches/rule-carrier-followed-by-block-2008.patch`: after the carrier's `</w:tbl>`,
emit one empty paragraph with `w:line="1" w:lineRule="exact"` so it costs no flow.

It is **not landed** because `regress.py --check` refuses an unstamped engine and the re-measurement
(`benchmarks/gate.py`, i.e. `p2w.py --budget`) needs about 25 minutes of corpus rendering — this slot
ran out before it finished (39 of 213 docx rendered, 0 of 212 measured when it stopped). Two
documents measured through Google is a proof of the mechanism, not a licence to change 146.

**The next slot's job, in this order:**

1. `python3 benchmarks/gate.py --budget 280` in a loop until `p2w.py` reports 213 of 213. It caches
   per-document results in `/scratch/work/p2w/dist2/`, so repeated calls make progress.
2. Apply the patch, rebuild, convert, `regress.py --check`, `regress.py --stamp`, commit.
3. Re-measure `17`, `18`, `19`, `24`, `26`, `32`, `34`, `37`, `45`, `47`, `49`, `53`, `74`, `315`,
   `334`, `product-catalogue-code-left-right` through Google. Predicted **42/42 on all sixteen**;
   `394` and `407` were already 41/42 on `32` alone and should reach 42/42 too.

## Reproduce

    bash tools/p2w-bench/build-engine.sh
    git apply tools/p2w-bench/patches/rule-carrier-per-rule-2008.patch
    git apply tools/p2w-bench/patches/rule-carrier-followed-by-block-2008.patch
    # convert, upload to Google, export the PDF, then:
    python3 tools/p2w-bench/verify_google.py <src>.pdf <google-export>.pdf --docx <out>.docx

The ladder probe is built by deep-copying the last carrier block in `word/document.xml` with lxml and
rewriting `w:tblpY`; a string-slicing version produces malformed XML and Google rejects the upload
with a bare 400.
