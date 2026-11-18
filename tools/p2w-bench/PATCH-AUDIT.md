# Patch audit - 18 Nov, run by the agent, not the fixer

29 patches were sitting in `patches/` and `tools/p2w-bench/patches/`, described as "proved and
measured but not shipped". This is what they actually are, measured against the 15 Nov baseline
(`ead0d0e`), which is the only engine the pipeline accepts.

## They cannot be applied

    6 of 29 apply cleanly to ead0d0e
    23 of 29 conflict

The 23 were written against an engine state that no longer exists. Their class labels are check ids -
`20_within_10pt`, `47_margins`, `59_shape_anchor`, `29_blank_where_ink_was`, `23_line_pitch` - and the
live classification has none of them. Applying them needs them rewritten against the current engine,
not `git apply`.

## The six that do apply

| patch | touches | result |
|---|---|---|
| `table-spacer-before-not-line` | DocxWriter | **tested: 0 better, 0 worse on 6 table documents** |
| `ruled-band-by-overlap-not-centre` | PdfToWord | not tested - `patches/README.md` says its mechanism moves nothing |
| `run-size-from-sizePt-not-Tf` (x2, duplicate) | PdfToWord | not tested |
| `wrap-charge-face-aware` | DocxWriter | not tested |
| `wrap-charge-gated-1.04` | DocxWriter | not tested |

## The four commits nobody could measure

`232f622`, `5e0af50`, `3232601`, `0554e8c` were made after the baseline and never measured, because
until 18 Nov the instrument could not measure reproducibly. Measured now against `ead0d0e`:

| commit | its claim | what it does against the baseline |
|---|---|---|
| `232f622` | table row separator, "kept 22/30" | **15 documents measured: 0 better, 0 worse.** The .docx bytes differ, the scores do not. |
| `5e0af50` | "041122 page spill: 10 pages -> 9, p7 73.99 -> 0.00" | **does not reproduce.** `ead0d0e` already produces 9 pages for 041122 and already scores 98.65. |
| `3232601` | "411_nested_xobject 48.64 -> 0.00" | **does not reproduce.** `ead0d0e` scores it 31.05, which is neither number. |
| `0554e8c` | table-cell paragraph path | not tested |

The claims were measured against an engine carrying other changes, not against `ead0d0e`. **Against
the baseline that the pipeline actually accepts, none of the three tested commits adds anything.**

That is not a verdict that they are bad code - it is a verdict that they cannot be justified by the
numbers they cite, and a commit nobody can justify does not go in.

## What is still open

    wrap-charge-face-aware        build, measure, decide
    wrap-charge-gated-1.04        build, measure, decide
    run-size-from-sizePt-not-Tf   build, measure, decide
    0554e8c                       build, measure, decide

Each is: `git apply`, `bash tools/p2w-bench/build-engine.sh`, convert the documents it targets,
`p2w.measure_doc` against `benchmarks/RANKING.csv`, keep only if nothing gets worse.

**scipy must be installed.** Without it `edt()` falls back to 40 mask passes and a one-page document
takes 150 seconds instead of 2 - which is why earlier verification attempts kept timing out.
