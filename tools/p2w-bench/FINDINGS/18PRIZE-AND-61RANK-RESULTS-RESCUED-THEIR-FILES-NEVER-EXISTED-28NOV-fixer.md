# `18prize-01` and `61rank-02`: their results, rescued — the findings files were never committed

**28 Nov 2026 · fixer · engine `a05b20eb05fe0fc8` · REPAIR, not a measurement**

The 04:00 run recorded two agents as **landed** in `RUN.json`, with these paths:

    FINDINGS/18prize-01-18-DISPLACEMENT-PRIZE-CENSUS-28NOV-agent.md
    FINDINGS/61rank-02-SIXTY-ONE-LOSSES-RANKED-BY-CHECK-28NOV-agent.md

**Neither file has ever existed in this repository.** `ls FINDINGS/ | grep 18prize` is empty and
`git log --all --diff-filter=A -- '*18prize*' '*61rank*'` finds no commit that added them. The self-check
caught it on the 04:58 run's report: *"subagents: 4 deployed vs no FINDINGS filename carries 18prize-01,
61rank-02."*

Their **`result` text is still in `RUN.json`**, and it is the most useful thing either run produced about
`18_displacement`. `RUN.json` is a state file that a reset can overwrite, so the text is copied here
verbatim. **This is the whole of what survived; nobody should treat it as more than a self-report.**

## `18prize-01` — which documents become CLEAN if `18_displacement` passes

> 108 documents fail 18_displacement; 18 are solo (would be clean if it passed); 28 are solo plus exactly
> one other (12 with 60_text_column_right_edge, 10 with 59_shape_anchor); leverage 46.56 reproduces
> classpick.py. All 18 solos are single-page bad_pages [0], which rules out the page-break w:before
> construct for them; 12 carry a rigid offset, 6 a per-run tail.

Two things follow, and both matter:

1. **46.6 is fractional, not 46.6 documents.** It is `sum(1/len(failed))` over the 108 and reproduces
   exactly. The real document count behind it is **18 solo + 28 solo-plus-one**. `classpick.py --leverage`
   is a **ranking, never a yield** — read `60`'s 23.63 the same way (its true count was 2).
2. **All 18 solo documents are single-page.** The page-break `w:before` construct cannot be the cause of a
   single one of them, which is what the −59.03 pt flat drop on pages 1–4 measured this run implies.

## `61rank-02` — which single check would clean the most of the 61 genuine losses

> 18_displacement fails 47 of the 61 and is the only failing check on 13 of them; no other check is worth
> more than 3. 60_text_column_right_edge 3, 26_text_overlap 1. Sub-construct B (the rung) is closed as a
> revert, so the 13 are A (LINE_BASE 0.8 vs Google 0.31 em) and C (afterTablePt/edgeGap) territory.

**`LINE_BASE` 0.8 em against Google's 0.31 em is a named, numeric lead and it is the best one on the
board.** A baseline constant is a number that can be measured in one probe; the line-box drift this run
measured (`dy = -8.44 - 0.027*y`) is a slope that has to be fitted. If the two are the same defect — a
baseline placed 0.49 em too low — the rigid-offset half of the 18 is explained by one constant.

## What a run should do with this file

Take the two numbers, **re-measure them** (`LINE_BASE` at `DocxWriter.java`, `grep -n LINE_BASE`), and do
not trust either as proof. What is proof here is only this: **the files were missing, and now the text
that was in `RUN.json` has a home in `FINDINGS/` that a reset cannot take away.**

**The rule this leaves:** an agent is not landed until its finding is a **file in `FINDINGS/`**, not a
`status: landed` row in a state file. A run that writes `landed` and no file has lost the work while
reporting that it kept it.
