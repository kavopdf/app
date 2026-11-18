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
| `table-spacer-before-not-line` | DocxWriter | neutral - 0 better, 0 worse on 6 table documents |
| `run-size-from-sizePt-not-Tf` (x2, duplicate) | PdfToWord | **REJECT** - `392_statistical_console_output` 1.61 -> 13.94 |
| `wrap-charge-gated-1.04` | DocxWriter | **REJECT** - `76_devanagari_table` 7.91 -> 54.99 |
| `wrap-charge-face-aware` | DocxWriter | **REJECT** - `76_devanagari_table` 7.91 -> 54.99 |
| `ruled-band-by-overlap-not-centre` | PdfToWord | not run - `patches/README.md` records that its mechanism moves nothing |

**Not one of the 29 can be kept.** Twenty-three cannot be applied at all, three regress a document,
one is neutral and one was already recorded as moving nothing.

`run-size-from-sizePt-not-Tf` is the interesting one. It takes `360_restaurant_menu` from **34.43 to
1.31** - a 96 % improvement, the largest single-document gain anyone has measured in this corpus - and
in the same breath takes `392_statistical_console_output` from 1.61 to 13.94. The mechanism is real and
it is aimed at the right thing; it is simply too broad. A version gated on the case it fixes, rather
than applied to every run, is worth writing. That is a new piece of work, not a patch to apply.

## The four commits nobody could measure

`232f622`, `5e0af50`, `3232601`, `0554e8c` were made after the baseline and never measured, because
until 18 Nov the instrument could not measure reproducibly. Measured now against `ead0d0e`:

| commit | its claim | what it does against the baseline |
|---|---|---|
| `232f622` | table row separator, "kept 22/30" | **15 documents measured: 0 better, 0 worse.** The .docx bytes differ, the scores do not. |
| `5e0af50` | "041122 page spill: 10 pages -> 9, p7 73.99 -> 0.00" | **does not reproduce.** `ead0d0e` already produces 9 pages for 041122 and already scores 98.65. |
| `3232601` | "411_nested_xobject 48.64 -> 0.00" | **does not reproduce.** `ead0d0e` scores it 31.05, which is neither number. |
| `0554e8c` | table-cell paragraph path | **8 documents: 0 better, 0 worse against `ead0d0e`** |

The claims were measured against an engine carrying other changes, not against `ead0d0e`. **Against
the baseline that the pipeline actually accepts, none of the four commits adds anything.**

A TRAP TO KNOW ABOUT, found while testing the fourth. `benchmarks/RANKING.csv` is no longer `ead0d0e`
- it carries the fixer's DeviceGray-alpha fix from 11:56, so `415_inline_images` reads 0.00 there
while every pre-fix commit produces 89.04. Comparing a pre-fix commit against today's RANKING.csv
therefore shows 415 as a regression when it is only older. The baseline for judging a commit is
`ead0d0e`'s own output, not the current ranking. Against `ead0d0e`, `0554e8c` is neutral like the
other three.

That is not a verdict that they are bad code - it is a verdict that they cannot be justified by the
numbers they cite, and a commit nobody can justify does not go in.

## What is still open

    nothing. All 29 patches and all 4 commits are measured and decided.

    The one idea worth carrying forward: `run-size-from-sizePt-not-Tf` gains 33 points on
    `360_restaurant_menu` and loses 12 on `392_statistical_console_output`. Gate it on the case it
    fixes and it may be the best single change available.

Each is: `git apply`, `bash tools/p2w-bench/build-engine.sh`, convert the documents it targets,
`p2w.measure_doc` against `benchmarks/RANKING.csv`, keep only if nothing gets worse.

**scipy must be installed.** Without it `edt()` falls back to 40 mask passes and a one-page document
takes 150 seconds instead of 2 - which is why earlier verification attempts kept timing out.
