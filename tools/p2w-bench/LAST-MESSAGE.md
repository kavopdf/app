# Fixer report - 2026-11-23 22:51

```
# P2W Fixer - Run Report

<<<<<<< HEAD
**23 Nov 2026 · slot 20:54 → 22:43 IST · 1h 48m**
=======
**23 Nov 2026 · slot 22:51 → running IST · 41 min**
>>>>>>> 1d68dbea (fixer: 04_chars_missing lead - Google drops wps:txbx text; foot-band patch proved, Google render is the next measurement)

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **13** of the **63** re-measured on this engine - **127** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 127 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `04_chars_missing` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:31 | **lead** | 0/5 | txbxContent 4->0 on 4 of 5 (27,61,55,67; 66 stays 16), read from word/document.xml; LO share5 unchanged 27 1.62->1.62 55 0.00->0.00 because LibreOffice renders the anchored box and Google does not - t |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, both in the first ten minutes, both returned usable findings: one on the `04_chars_missing`
construct (nine documents, the missing strings quoted, a measured 14-document blast radius), one on
the `44_header_footer` lead (the `.txt` half clean — 0 header/footer lines lost or duplicated across 31
documents — and the .docx half confirmed with two corrections).

## The class I picked, and why

`classpick.py` suggested `44_header_footer` on an open lead. I took `04_chars_missing` instead, because
`classpick.py --leverage` puts it first at **13.5** clean documents and the two are the same construct —
the suggestion was naming the class, not the cause.

## The construct

**Google Docs does not read the text of a floating drawing.** A `wps:txbx` inside a
`<wp:anchor behindDoc="1">` comes back from Drive as pixels with no text layer, so every character in
it is missing from the export. LibreOffice renders the same box as a text frame and keeps all of them.

Two agents deployed in the first ten minutes reached this independently, from opposite ends:

- **`04_chars_missing`** — on 27, 55, 61, 67, 20, 13, 06, 09, 66 the missing-character multiset is
  **fully** explained by the text of the anchored boxes, zero unexplained characters. The missing runs
  share nothing typographic (8–44 pt, black, grey #595959 or red, unrotated, unclipped). Their only
  shared property is position: the bottom tenth of the sheet.
- **`44_header_footer`** — 20 of the 28 documents that carry a running foot write it as a floating
  anchor (`posOffset` 798.5 pt on an 842 pt page). The other 8 flow normally and **still fail 44**, so
  the class has a second mechanism this patch does not reach.

## The change, and why it was not kept

`DocxWriter.inFootBand(ctx, y)` = `y > 0.90 * ctx.pageHeightPt`, added as `&& !inFootBand(...)` to the
four `gapCapTw` anchor escapes. In the bottom tenth the measured gap is spent as `w:before` instead of
calling `anchorBox()`. The anchor rule is right about the position and wrong about the construct: its
justification — spending a wide gap pushes every line below it down — does not hold for the last line
on the sheet.

Saved as `tools/p2w-bench/patches/foot-band-spend-the-gap.patch` with its reasoning beside it. Keeping
it needs `regress.py --check`, which needs a 213-document pass of about forty minutes; the slot had
twelve. The tree is clean and the patch reverts nothing.

## The measurement that matters, and the one that cannot be made here

| document | `txbxContent` before | after | `share5` (LO) before | after |
|:--|--:|--:|--:|--:|
| 27_two_column_left_short_txtpos | 4 | **0** | 1.62 | 1.62 |
| 61_two_col_abstract_spanning | 4 | **0** | 2.01 | not scored |
| 55_sidebar_box_beside_body | 4 | **0** | 0.00 | 0.00 |
| 67_two_col_with_sidebar | 4 | **0** | 0.80 | not scored |
| 66_two_col_footnotes_bottom | 16 | 16 | 2.92 | not scored |

`txbxContent` is counted straight out of the produced `word/document.xml`, not from the tool that was
edited. The `share5` columns are the LibreOffice proxy and they **do not move** — and that is the
finding, not a disappointment: `55` is `clean` in RANKING.csv at `share5` 0.00 and still fails `04` and
`44` in Google. **The proxy is blind to this class in both directions.** A screen on LibreOffice will
report "nothing improved" whatever the patch does, and the next run must not read that as a verdict.

## Next run

1. `git apply tools/p2w-bench/patches/foot-band-spend-the-gap.patch`, build.
2. Measure the 14 documents the guard empties **through Google**, not LibreOffice: 27, 28, 46, 54, 55,
   61, 62, 67, 70, newsletter-3col-header-footer, one-page-rotated-180-degrees,
   report-2col-table-spanning-both-columns, table-inside-two-column-page, table-of-contents-dot-leaders.
3. Expect `04` and `44` to clear on 27 and 61 at minimum — they fail nothing else. `45` clears only
   where the missing share was over 3% (measured 3.8% on 55, 3.7% on 67, 3.1% on 61), so the floor is
   **2** documents, not 5. Do not claim 5 without the render.
4. The 40 documents that keep their boxes need a real `word/footer1.xml` — 1–2 files, six touch points —
   and `verify_google.py:3745-3750` already records that a header part moved every body line +10.9 pt
   on `bank-statement-5-pages`, so it is not free.

## Subagents

Two, both in the first ten minutes, both returned usable findings: one on the `04_chars_missing`
construct (nine documents, the missing strings quoted, a measured 14-document blast radius), one on
the `44_header_footer` lead (the `.txt` half clean — 0 header/footer lines lost or duplicated across 31
documents — and the .docx half confirmed with two corrections).

## The class I picked, and why

`classpick.py` suggested `44_header_footer` on an open lead. I took `04_chars_missing` instead, because
`classpick.py --leverage` puts it first at **13.5** clean documents and the two are the same construct —
the suggestion was naming the class, not the cause.

## The construct

**Google Docs does not read the text of a floating drawing.** A `wps:txbx` inside a
`<wp:anchor behindDoc="1">` comes back from Drive as pixels with no text layer, so every character in
it is missing from the export. LibreOffice renders the same box as a text frame and keeps all of them.

Two agents deployed in the first ten minutes reached this independently, from opposite ends:

- **`04_chars_missing`** — on 27, 55, 61, 67, 20, 13, 06, 09, 66 the missing-character multiset is
  **fully** explained by the text of the anchored boxes, zero unexplained characters. The missing runs
  share nothing typographic (8–44 pt, black, grey #595959 or red, unrotated, unclipped). Their only
  shared property is position: the bottom tenth of the sheet.
- **`44_header_footer`** — 20 of the 28 documents that carry a running foot write it as a floating
  anchor (`posOffset` 798.5 pt on an 842 pt page). The other 8 flow normally and **still fail 44**, so
  the class has a second mechanism this patch does not reach.

## The change, and why it was not kept

`DocxWriter.inFootBand(ctx, y)` = `y > 0.90 * ctx.pageHeightPt`, added as `&& !inFootBand(...)` to the
four `gapCapTw` anchor escapes. In the bottom tenth the measured gap is spent as `w:before` instead of
calling `anchorBox()`. The anchor rule is right about the position and wrong about the construct: its
justification — spending a wide gap pushes every line below it down — does not hold for the last line
on the sheet.

Saved as `tools/p2w-bench/patches/foot-band-spend-the-gap.patch` with its reasoning beside it. Keeping
it needs `regress.py --check`, which needs a 213-document pass of about forty minutes; the slot had
twelve. The tree is clean and the patch reverts nothing.

## The measurement that matters, and the one that cannot be made here

| document | `txbxContent` before | after | `share5` (LO) before | after |
|:--|--:|--:|--:|--:|
| 27_two_column_left_short_txtpos | 4 | **0** | 1.62 | 1.62 |
| 61_two_col_abstract_spanning | 4 | **0** | 2.01 | not scored |
| 55_sidebar_box_beside_body | 4 | **0** | 0.00 | 0.00 |
| 67_two_col_with_sidebar | 4 | **0** | 0.80 | not scored |
| 66_two_col_footnotes_bottom | 16 | 16 | 2.92 | not scored |

`txbxContent` is counted straight out of the produced `word/document.xml`, not from the tool that was
edited. The `share5` columns are the LibreOffice proxy and they **do not move** — and that is the
finding, not a disappointment: `55` is `clean` in RANKING.csv at `share5` 0.00 and still fails `04` and
`44` in Google. **The proxy is blind to this class in both directions.** A screen on LibreOffice will
report "nothing improved" whatever the patch does, and the next run must not read that as a verdict.

## Next run

1. `git apply tools/p2w-bench/patches/foot-band-spend-the-gap.patch`, build.
2. Measure the 14 documents the guard empties **through Google**, not LibreOffice: 27, 28, 46, 54, 55,
   61, 62, 67, 70, newsletter-3col-header-footer, one-page-rotated-180-degrees,
   report-2col-table-spanning-both-columns, table-inside-two-column-page, table-of-contents-dot-leaders.
3. Expect `04` and `44` to clear on 27 and 61 at minimum — they fail nothing else. `45` clears only
   where the missing share was over 3% (measured 3.8% on 55, 3.7% on 67, 3.1% on 61), so the floor is
   **2** documents, not 5. Do not claim 5 without the render.
4. The 40 documents that keep their boxes need a real `word/footer1.xml` — 1–2 files, six touch points —
   and `verify_google.py:3745-3750` already records that a header part moved every body line +10.9 pt
   on `bank-statement-5-pages`, so it is not free.

## Subagents

Two, both in the first ten minutes, both returned usable findings: one on the `04_chars_missing`
construct (nine documents, the missing strings quoted, a measured 14-document blast radius), one on
the `44_header_footer` lead (the `.txt` half clean — 0 header/footer lines lost or duplicated across 31
documents — and the .docx half confirmed with two corrections).

## The class I picked, and why

`classpick.py` suggested `44_header_footer` on an open lead. I took `04_chars_missing` instead, because
`classpick.py --leverage` puts it first at **13.5** clean documents and the two are the same construct —
the suggestion was naming the class, not the cause.

## The construct

**Google Docs does not read the text of a floating drawing.** A `wps:txbx` inside a
`<wp:anchor behindDoc="1">` comes back from Drive as pixels with no text layer, so every character in
it is missing from the export. LibreOffice renders the same box as a text frame and keeps all of them.

Two agents deployed in the first ten minutes reached this independently, from opposite ends:

- **`04_chars_missing`** — on 27, 55, 61, 67, 20, 13, 06, 09, 66 the missing-character multiset is
  **fully** explained by the text of the anchored boxes, zero unexplained characters. The missing runs
  share nothing typographic (8–44 pt, black, grey #595959 or red, unrotated, unclipped). Their only
  shared property is position: the bottom tenth of the sheet.
- **`44_header_footer`** — 20 of the 28 documents that carry a running foot write it as a floating
  anchor (`posOffset` 798.5 pt on an 842 pt page). The other 8 flow normally and **still fail 44**, so
  the class has a second mechanism this patch does not reach.

## The change, and why it was not kept

`DocxWriter.inFootBand(ctx, y)` = `y > 0.90 * ctx.pageHeightPt`, added as `&& !inFootBand(...)` to the
four `gapCapTw` anchor escapes. In the bottom tenth the measured gap is spent as `w:before` instead of
calling `anchorBox()`. The anchor rule is right about the position and wrong about the construct: its
justification — spending a wide gap pushes every line below it down — does not hold for the last line
on the sheet.

Saved as `tools/p2w-bench/patches/foot-band-spend-the-gap.patch` with its reasoning beside it. Keeping
it needs `regress.py --check`, which needs a 213-document pass of about forty minutes; the slot had
twelve. The tree is clean and the patch reverts nothing.

## The measurement that matters, and the one that cannot be made here

| document | `txbxContent` before | after | `share5` (LO) before | after |
|:--|--:|--:|--:|--:|
| 27_two_column_left_short_txtpos | 4 | **0** | 1.62 | 1.62 |
| 61_two_col_abstract_spanning | 4 | **0** | 2.01 | not scored |
| 55_sidebar_box_beside_body | 4 | **0** | 0.00 | 0.00 |
| 67_two_col_with_sidebar | 4 | **0** | 0.80 | not scored |
| 66_two_col_footnotes_bottom | 16 | 16 | 2.92 | not scored |

`txbxContent` is counted straight out of the produced `word/document.xml`, not from the tool that was
edited. The `share5` columns are the LibreOffice proxy and they **do not move** — and that is the
finding, not a disappointment: `55` is `clean` in RANKING.csv at `share5` 0.00 and still fails `04` and
`44` in Google. **The proxy is blind to this class in both directions.** A screen on LibreOffice will
report "nothing improved" whatever the patch does, and the next run must not read that as a verdict.

## Next run

1. `git apply tools/p2w-bench/patches/foot-band-spend-the-gap.patch`, build.
2. Measure the 14 documents the guard empties **through Google**, not LibreOffice: 27, 28, 46, 54, 55,
   61, 62, 67, 70, newsletter-3col-header-footer, one-page-rotated-180-degrees,
   report-2col-table-spanning-both-columns, table-inside-two-column-page, table-of-contents-dot-leaders.
3. Expect `04` and `44` to clear on 27 and 61 at minimum — they fail nothing else. `45` clears only
   where the missing share was over 3% (measured 3.8% on 55, 3.7% on 67, 3.1% on 61), so the floor is
   **2** documents, not 5. Do not claim 5 without the render.
4. The 40 documents that keep their boxes need a real `word/footer1.xml` — 1–2 files, six touch points —
   and `verify_google.py:3745-3750` already records that a header part moved every body line +10.9 pt
   on `bank-statement-5-pages`, so it is not free.

## Subagents

Two, both in the first ten minutes, both returned usable findings: one on the `04_chars_missing`
construct (nine documents, the missing strings quoted, a measured 14-document blast radius), one on
the `44_header_footer` lead (the `.txt` half clean — 0 header/footer lines lost or duplicated across 31
documents — and the .docx half confirmed with two corrections).

## The class I picked, and why

`classpick.py` suggested `44_header_footer` on an open lead. I took `04_chars_missing` instead, because
`classpick.py --leverage` puts it first at **13.5** clean documents and the two are the same construct —
the suggestion was naming the class, not the cause.

## The construct

**Google Docs does not read the text of a floating drawing.** A `wps:txbx` inside a
`<wp:anchor behindDoc="1">` comes back from Drive as pixels with no text layer, so every character in
it is missing from the export. LibreOffice renders the same box as a text frame and keeps all of them.

Two agents deployed in the first ten minutes reached this independently, from opposite ends:

- **`04_chars_missing`** — on 27, 55, 61, 67, 20, 13, 06, 09, 66 the missing-character multiset is
  **fully** explained by the text of the anchored boxes, zero unexplained characters. The missing runs
  share nothing typographic (8–44 pt, black, grey #595959 or red, unrotated, unclipped). Their only
  shared property is position: the bottom tenth of the sheet.
- **`44_header_footer`** — 20 of the 28 documents that carry a running foot write it as a floating
  anchor (`posOffset` 798.5 pt on an 842 pt page). The other 8 flow normally and **still fail 44**, so
  the class has a second mechanism this patch does not reach.

## The change, and why it was not kept

`DocxWriter.inFootBand(ctx, y)` = `y > 0.90 * ctx.pageHeightPt`, added as `&& !inFootBand(...)` to the
four `gapCapTw` anchor escapes. In the bottom tenth the measured gap is spent as `w:before` instead of
calling `anchorBox()`. The anchor rule is right about the position and wrong about the construct: its
justification — spending a wide gap pushes every line below it down — does not hold for the last line
on the sheet.

Saved as `tools/p2w-bench/patches/foot-band-spend-the-gap.patch` with its reasoning beside it. Keeping
it needs `regress.py --check`, which needs a 213-document pass of about forty minutes; the slot had
twelve. The tree is clean and the patch reverts nothing.

## The measurement that matters, and the one that cannot be made here

| document | `txbxContent` before | after | `share5` (LO) before | after |
|:--|--:|--:|--:|--:|
| 27_two_column_left_short_txtpos | 4 | **0** | 1.62 | 1.62 |
| 61_two_col_abstract_spanning | 4 | **0** | 2.01 | not scored |
| 55_sidebar_box_beside_body | 4 | **0** | 0.00 | 0.00 |
| 67_two_col_with_sidebar | 4 | **0** | 0.80 | not scored |
| 66_two_col_footnotes_bottom | 16 | 16 | 2.92 | not scored |

`txbxContent` is counted straight out of the produced `word/document.xml`, not from the tool that was
edited. The `share5` columns are the LibreOffice proxy and they **do not move** — and that is the
finding, not a disappointment: `55` is `clean` in RANKING.csv at `share5` 0.00 and still fails `04` and
`44` in Google. **The proxy is blind to this class in both directions.** A screen on LibreOffice will
report "nothing improved" whatever the patch does, and the next run must not read that as a verdict.

## Next run

1. `git apply tools/p2w-bench/patches/foot-band-spend-the-gap.patch`, build.
2. Measure the 14 documents the guard empties **through Google**, not LibreOffice: 27, 28, 46, 54, 55,
   61, 62, 67, 70, newsletter-3col-header-footer, one-page-rotated-180-degrees,
   report-2col-table-spanning-both-columns, table-inside-two-column-page, table-of-contents-dot-leaders.
3. Expect `04` and `44` to clear on 27 and 61 at minimum — they fail nothing else. `45` clears only
   where the missing share was over 3% (measured 3.8% on 55, 3.7% on 67, 3.1% on 61), so the floor is
   **2** documents, not 5. Do not claim 5 without the render.
4. The 40 documents that keep their boxes need a real `word/footer1.xml` — 1–2 files, six touch points —
   and `verify_google.py:3745-3750` already records that a header part moved every body line +10.9 pt
   on `bank-statement-5-pages`, so it is not free.

## Subagents

Two, both in the first ten minutes, both returned usable findings: one on the `04_chars_missing`
construct (nine documents, the missing strings quoted, a measured 14-document blast radius), one on
the `44_header_footer` lead (the `.txt` half clean — 0 header/footer lines lost or duplicated across 31
documents — and the .docx half confirmed with two corrections).

## Timing

| | |
|:--|:--|
<<<<<<< HEAD
| Slot window | 20:54 → 22:43 · 1h 48m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **72.2 min** — from 21:30:38, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 3 cleared · 2 parked, with the evidence to re-open them |
| Still a wall | **This watchdog has no `cron` tool**, so a paused or zombie cron cannot be moved by automation and STEP 3 cann |
=======
| Slot window | 22:51 → running · 41 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **23.3 min** — from 22:51:31, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |
>>>>>>> 1d68dbea (fixer: 04_chars_missing lead - Google drops wps:txbx text; foot-band patch proved, Google render is the next measurement)


### Where the time went

| Phase | Time | |
|:--|--:|:--|
<<<<<<< HEAD
| measure or build - a conversion, screen or compile writes no beacon | **25 min** | `#####` |
| record - attempt, handoff, class rows | **4 min** | `#` |
| report - the report and the chain | **1h 13m** | `###############` |
| other - not attributed to a tool | **5 min** | `#` |
=======
| fix - diagnose and change the engine | **16 min** | `#########` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `#############` |
| report - the report and the chain | **0 min** | `#` |
>>>>>>> 1d68dbea (fixer: 04_chars_missing lead - Google drops wps:txbx text; foot-band patch proved, Google render is the next measurement)
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: stop spending attempts on row pitch - measure the top of the block. The leading paragraph carries its vertical position in w:spacing w:before=1040 + w:line=13 exact, and the Google column of GVERIFY-BRIEF lists w:spacing as ignored. Build one variant that carries the same position WITHOUT w:spacing (exact-height empty paragraph, or w:ind/w:framePr), round trip table-with-no-header-row, and read the first line's dy: it is -10.16 now, and if it does not move the carrier is not the spacing. Then repeat on mobile-bill (-15.75).

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
