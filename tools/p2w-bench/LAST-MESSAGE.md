**21 Nov 2026 · slot 23:19 → running IST · 20 min**

> The largest class in the corpus was not a rendering defect at all. `05_chars_extra` failed 141 of
> the 192 scored documents, and every one of them was failing on a character Google's exporter
> writes to mark a **tab advance** — one `U+200B` per `<w:tab/>` in the `.docx`. The separation on
> the corpus is total: 141 fail, all with tabs; 51 pass, none with tabs. I proved it causally by
> deleting 23 tabs from one document's own `.docx` and watching 23 characters disappear. The check
> now ignores zero-width characters, symmetrically, and 11 of 11 measured documents cleared `05`.

## Progress

| | |
|:--|:--|
| Documents improved this run | **11** — 1 attempt(s), 1 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `05_chars_extra` |

The **6** is the committed corpus record and it is now stale by construction: this slot changed the
verifier, and 141 stored `05` verdicts are false until the next Google pass re-scores them. Two
documents reached **42/42** on this slot's own fresh Google measurement and are not in that 6 —
`394_map_with_legend` (41 → 42) and `45_coloured_callout_box` (40 → 42).

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:13 | **lead** | 0/192 | CHECK BLIND TO PICTURES, measured both ways. _rule_segments() walks get_drawings() only; Google exports every anchored shape as a raster image, so a rule it drew reads as zero |
| 23:38 | **lead** | 0/192 | THE RULE CARRIER IS WORTH TWO DOCUMENTS, NOT 32. Applied, built, 11 documents through Google: `394` 41→42, `45` 40→42 with the `05` correction, clean control `51` stayed 42/42, seven others gained the `05` check only. Not landed: it changes 146 rule-carrying documents and 9 were measured |
| 23:52 | **kept** | 11/192 | `05_chars_extra` WAS COUNTING GOOGLE'S TABS. 141 fail / 141 with tabs, 51 pass / 51 without, no exception. Causal on `17`: its own `.docx` minus 23 tabs exports with 0 extras. `norm_text()` now strips `U+200B`/`U+FEFF` on both sides |

## The class I chose, and why

`classpick.py` suggested staying on `32_stroke_lines` because it holds an open lead. I took the
instrument question inside that lead instead, and the arithmetic is why: `05_chars_extra` is worth
**35.0 clean documents** by `classpick.py --leverage`, and it sits on 141 documents — three quarters
of the scored corpus. A check that fails 141 documents for a reason no engine can fix is not a lead,
it is a false floor under every other class, and two consecutive runs spent their slots chasing the
"anchor becomes a stray U+200B" story that this measurement replaces.

The `32` lead was not abandoned. It was measured first, and it is now a lead with a number instead of
an assumption: the carrier patch is worth two documents, not the 32 the census promised.

## Why the carrier is a lead and not a fix

`patches/rule-carrier-per-rule-2008.patch` applies cleanly and works. Eleven documents through Google:

| document | committed | carrier | carrier + `05` |
|:--|--:|--:|--:|
| `394_map_with_legend` | 41/42 | **42/42** | 42/42 |
| `45_coloured_callout_box` | 40/42 | 41/42 | **42/42** |
| `51_two_cm_margins` (clean control) | 42/42 | 42/42 | 42/42 |
| `17`, `18`, `19`, `24`, `26`, `53`, `74` | 40/42 | 40/42 | 41/42 |
| `73_marksheet_subject_marks_grade` | 39/42 | 39/42 | 40/42 |

Nothing got worse — and that is the whole of what I can say. It changes the construct on **146**
documents that carry a rule; I measured **9** of them. "No document gets worse" cannot be asserted
for the other 137 inside one slot, so it stays measured and unlanded rather than landed and unproven.

## The one thing that stops the class, and it is one number

`32_stroke_lines` on `17`/`53`/`74` reads `{"source": 2, "render": 1}`: two rules on the page, two
carriers emitted, **one placed**. `45` has the identical two rules at the identical positions and
loses none. `394` places five on one page. So the construct is not wrong and the count is not the
limit — something about where the second anchor sits in those three documents is. That is the next
probe, and it is one Google round trip, not a build.

## Falsification

The claim was that a tab becomes a character. Two ways to break it, and both were run:

| test | expected if the claim is right | measured |
|:--|:--|:--|
| all 192 documents: does every `05` failure carry a tab, and does every pass carry none? | total separation | **141/141 and 51/51 — no exception** |
| `17`'s own `.docx` with only its 23 `<w:tab/>` deleted | 23 fewer extras, nothing else | **`{'U+200B': 23}` → `{}`** |
| the 5 documents already clean in Google | 0 tabs | **0 tabs in all 5** |
| `test_checks.py` after the change | 44/44 unchanged | **44/44** |

The change strips from **both** multisets, so it can only remove a disagreement: it cannot hide
missing text (`04_chars_missing` reads the other side) and it cannot mask a duplicated line, because
a duplicate adds real characters. `U+200C`/`U+200D` are deliberately left in — they are ZWNJ/ZWJ and
they shape Indic text.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

One agent, deployed 23:22, returned in 5 minutes: `rule-emission-census`. It converted seven of the
class's documents with the engine and compared every rule the source page draws with every rule the
`.docx` emits — **107 rules matched at Δ 0.000 pt and one dropped**, and the dropped one is 127 pt
below the bottom of the paper, where `attachShapes` discards it by design. So the engine is not
losing rules before the writer and the carrier is not writing into a hole.

**One agent, not two.** The second was the `05` question and it became the slot's own build once the
census came back in five minutes; sending it twice would have duplicated the measurement I was about
to make by hand.

## Timing

| | |
|:--|:--|
| Slot window | 23:19 → running · 20 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **6.2 min** — from 23:20:20, after `relay: reading lead evidence` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **7 min** | `########` |
## Next run

Two measurements, both cheap, both already specified:

1. **One Google round trip** on `17_three_column_widths_txtpos` with its two carriers re-anchored —
   one in the body, one inside the table — and read `32`'s `render` count. If the inside-the-table
   anchor is the one Google drops, the fix is "never anchor a carrier inside a `w:tbl`", and it is
   worth the 7 documents in the table above.
2. **Re-score the corpus.** `benchmarks/gverify/*.json` still carries the pre-fix `05` verdicts on
   141 documents. Until a Google pass replaces them, every count in this pipeline understates the
   corpus by up to 141 documents on that one check.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
