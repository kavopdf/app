# P2W Fixer - Run Report

**22 Nov 2026 · slot 05:56 → running IST · 20 min**

> The largest Google class was not a document defect. `32_stroke_lines` read only vector
> paths, and Google Docs exports every anchored rule as a small raster image at the rule's
> own coordinates — so a rule Google rendered perfectly was counted as lost. Thirty-five
> documents through a live Google round trip: **16 went 41/42 → 42/42**, none got worse,
> **Google-clean 6 → 23**, and the class that actually blocks documents is now
> `18_displacement`, which is the only failure left on 16 of them.

## Progress

| | |
|:--|:--|
| Documents improved this run | **19** — 3 attempt(s), 2 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `18_displacement` |

The 19 is the ledger's count across three attempts; the distinct documents that went clean
are 16, because the first attempt's three are also in the twenty-document batch.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 06:10 | **kept** | 3/213 | `verify_google.py:_rule_segments()` reads `page.get_drawings()` — vector paths only. `_stroke_pictures()` sits in the same file, is already called by `_strokes()`, and was never called here. Google Docs exports an anchored shape as a small raster image at the shape's own geometry, so a rule it drew perfectly read as zero segments and was counted LOST. Made the check read image bands, at `RULE_BAND_REN` so a 3 pt rule counts whether Google drew it as a vector band or an image band. |
| 06:13 | **kept** | 16/213 | The change measured on 20 Google exports from a live round trip: 16 documents 41/42 → 42/42, 0 worse. 13 of 14 documents failing `{05_chars_extra, 32_stroke_lines}` came back 42/42 — `05_chars_extra` passes on HEAD too, so the table's 05 column is stale as well. |
| 06:17 | **lead** | — | The 15 documents that failed `{05, 18, 32}` re-measured through Google on HEAD: every one is 41/42 failing `18_displacement` ALONE (4 are 46/47 failing it alone). `05` and `32` pass on all 15, so `32_stroke_lines` is cleared on 34 of the 35 documents re-measured this run. |

## What this run measured

**1. The check could not see what Google rendered.** From the exports of this run, printed
straight out of `page.get_image_info()`:

    394_map_with_legend  rule y=691.89 t=1.6  ->  image 21.00 x 2.25 at (394.9, 690.7)
                         rule y=707.89 t=3.0  ->  image 21.00 x 3.75 at (394.9, 706.0)
    315_gazette          5 source rules, 5 image bands, each at its own coordinates
    17_three_column      2 source rules, 2 image bands, each at its own coordinates

Every rule the check called LOST was present in the document the user opens. The band limit
matters: `_stroke_pictures()` was hardcoded at 1.5 pt and two of `394`'s three rules are
2.25 pt and 3.75 pt — at 1.5 pt the fix recovers 1 of 3 and the document still fails.

**2. Thirty-five documents through the round trip, before and after.** `ConvertOne` at HEAD,
`GOOGLEDRIVE_CREATE_FILE` as a Google Doc in `KavoPDF-Verify`, `GOOGLEDRIVE_DOWNLOAD_FILE`
as PDF, `verify_google.py --json`, probe deleted. Before and after are the same command on
the same export, and the before column was re-taken with the pre-change file:

| document | before | after |
|:--|:--|:--|
| `394_map_with_legend` | 41/42 | **42/42 PASS** |
| `17_three_column_widths_txtpos` | 41/42 | **42/42 PASS** |
| `315_gazette_notification` | 41/42 | **42/42 PASS** |
| 13 of 14 `{05,32}` documents | 40/42 | **42/42 PASS** |
| 15 `{05,18,32}` documents | 39/42 | 41/42 — `18_displacement` alone |
| `49_coloured_background_block_paragraph` | 40/42 | 41/42 — still fails 32 |
| `407_id_card_front_back` | 41/42 | 41/42 — 46 lost rules → 8 |
| `311_fir_police_form` | 42/47 | 43/47 — 32 passes, 4 Google checks fail |
| `382_architecture_diagram` | 42/42 | **42/42 PASS** — clean control held |

**3. Why no document can get worse.** The change only ADDS render segments, and
`_rules_lost()` matches 1:1, so it can only turn FAIL into PASS. `regress.py --check` passes
and `google-gate.sh` passes; neither is relied on for the argument.

**4. `407_id_card_front_back` is a real loss, not an instrument one.** 46 source rules, 18
image bands, and its card borders (a 228 pt horizontal at y=220, x 46..274) are in none of
them. That is the engine construct — a rule emitted as a floating `<w:drawing>` that Google
drops — and it needs `w:tcBorders` on a 1×1 floating table carrier.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 05:56 → running · 20 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 21 |
| Longest silence | **8.8 min** — from 05:56:39, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **12 min** | `#############` |
| record - attempt, handoff, class rows | **3 min** | `###` |
| other - not attributed to a tool | **2 min** | `##` |

The 8.8-minute silence is the engine build, the corpus fetch and two agent delegations
before the first `--heartbeat`. It is the reason the slot reads as short.

## Next run

**`18_displacement` is the class, and it is now a measured one.** It is the only failure
left on 16 documents — 15 of them established this run, all uniform at 41/42 — and it is
the largest column in the table at 124 documents. Implement it; do not re-measure it. A fix
that lands takes those 16 straight to 42/42, and the class is worth 28.7 clean documents
corpus-wide.

**The remaining `32_stroke_lines` rows are still unmeasured.** 113 documents still carry the
vector-only result; 34 of the 35 re-measured this run were wrong. A round trip on
`{05, 32}` documents takes about a minute a document, so sixty fits in one run.

Two things a round trip needs that this run had and a sub-agent's did not: the platform
`upload` tool, which mints the `s3key` — `GOOGLEDRIVE_CREATE_FILE` refuses a sandbox path
with *"The file key does not belong to this project or session"* — and the file under
`/scratch/output`. Do not route around it by publishing a probe to a public host.

**Then the engine, for `407`.** It is the proof that a floating `<w:drawing>` rule is
genuinely dropped by Google while a `w:tcBorders` rule is not:
`64_newspaper_uneven_columns_ad_boxes` passes with its rules as table borders. Route an
isolated hairline rule to a 1×1 floating table carrier — `<w:tblpPr>` +
`<w:trHeight w:hRule="exact" w:val="1"/>` + `<w:tcBorders><w:bottom>` — based on
`patches/rule-carrier-per-rule-2008.patch`, never
`rule-carrier-horizontal-only-2008.patch`, which is falsified twice: 54 documents worse on
the corpus pass and 4 of 10 clean controls worse on the 05:14 controls.

Details: `tools/p2w-bench/FINDINGS/32_stroke_lines-CHECK-BLIND-TO-RASTERISED-RULES-MEASURED-0610-f1x.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
