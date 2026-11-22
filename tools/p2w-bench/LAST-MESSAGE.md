**22 Nov 2026 · fixer slot 17:00 → running IST**

> **The spacer change that converts 6 documents CLEAN in Google is not neutral in LibreOffice — the
> gate was right, and the finding that said LibreOffice could not see it was wrong.** The 08:56 run
> built the table spacer as `w:before` instead of `w:line`, measured **6 of the 16 solo
> `18_displacement` documents go to 42/42 in Google**, and wrote that "`screen.py` cannot see this
> construct" because both forms are the same twips. I built it and screened it: `mobile-bill` reads
> **1.55 → 1.74 (+0.19, worse)** and `16_right_aligned_amounts_txtpos` reads **0.00 → 0.00**.
> LibreOffice is not blind to it. Nothing was committed to the engine.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | **61** of the 212 compared |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| **Fixed - Google, all 42 checks** | **23**, and 192 of the 213 carry a Google score |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## The class, and why this one

`18_displacement`, on the arithmetic: `classpick.py --leverage` prices it at **38.7**, the largest step
in the table, and **16 documents fail it and nothing else** (read from `benchmarks/gverify/*.json`). It
is the only check where a single construct can turn 16 documents CLEAN at once.

Three slots have now been spent on this class without landing a fix, and the last one concluded the
blocker was an *instrument* question — Google-clean, proxy-regressed, ratchet refusing. **That framing
is what this slot corrects.** It was never an instrument question. The construct is genuinely not
neutral, and the instrument was telling the truth.

## What this slot measured

The 08:56 finding (`FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md`)
built the spacer gap as `w:before` with a hairline line box, raised the 2880-twip cap to 4320, and got
6 documents to 42/42 in Google. It then reverted, blocked on 2 Google regressions, and asserted that
LibreOffice could not see the construct at all:

> "`screen.py` measures in soffice, which honours `w:line` as a length and therefore cannot see either
> state of this construct."

That sentence was inferred, never measured. I built the same change (`build-engine.sh`, 37 s, engine
`462353f9` + the diff), converted with it, rendered with `soffice --headless`, and scored with
`benchmarks/p2w.py`'s own `measure_doc` — the instrument that writes `RANKING.csv`, so the "before"
column is `RANKING.csv` itself.

| document | `RANKING.csv` (HEAD) | spacer as `w:before` | delta |
|:--|--:|--:|--:|
| `mobile-bill` | 1.55 | **1.74** | **+0.19 — WORSE** |
| `16_right_aligned_amounts_txtpos` | 0.00 | 0.00 | 0 |

`mobile-bill`'s signature moves with it — share@5 1.74, median 1.44 pt, max 16.8 pt, invent5 0.29 —
so the document really moved, it did not just re-score.

**So the spacer change fails for two reasons, not one**: 2 Google regressions *and* at least 1
LibreOffice regression. `regress.py --check` refusing it was correct.

## Why it is a near miss and not a dead end

The residue is the hairline the change leaves behind. `w:before="G"` plus a `w:line="1"` line box is
`G` plus that line's own height; `w:line="G" lineRule="exact"` is exactly `G`. On `mobile-bill` — three
spacers — that is 0.19 pt of error. **The zero-line form (mark `w:sz="2"`, no `w:line` at all) is the
one variant no run has tried**, and it removes exactly that residue.

The order that follows from the measurement, and it is the opposite of the order the last three slots
used: **screen in LibreOffice first**, then spend Google round trips. The instrument can see this
construct; it should be asked before the expensive renderer.

## Also settled this slot

* The 16:36 finding's LibreOffice catastrophe belongs to the **row-pitch dither** half of
  `patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`, and is unchanged. The *spacer*
  half fails separately, for the reason above. Removing either half cannot rescue the other.
* **The charter's "6 clean" figure is still wrong and the data still says 23.** Recomputed from the 192
  `status: ok` JSONs in `benchmarks/gverify/`: 23 have an empty `failed[]`, 169 fail at least one
  check, 21 are `page_count_refused` and score nothing. Those 21 carry a numeric score in
  `RANKING.csv`, which is why 213 ranked and 192 scored are different populations.

## The next move

    # zero-line spacer: w:before="G", mark w:sz="2", no w:line
    bash tools/p2w-bench/build-engine.sh
    python3 tools/p2w-bench/screen.py --docs 16_right_aligned_amounts_txtpos,22_invoice_four_columns_txtpos,29_dot_leaders_txtpos,41_coloured_headings_white_bg,68_journal_wide_table_spanning,73_marksheet_subject_marks_grade,insurance-policy-schedule,mobile-bill

If LibreOffice is flat on all 8, take the 2 regressors through Google. If it is not flat, the spacer
construct is closed and the `w:trHeight hRule="atLeast"` row excess (+0.70 pt/row at an 18.40 pt
source pitch) is the remaining lever on this class — a different construct with its own finding.

Before spending a build on it: `python3 benchmarks/p2w.py --diagnose mobile-bill` — if HEAD really
scores 1.74 and not 1.55, `RANKING.csv` is stale for that document and this finding's before-number is
wrong.

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:15 | **lead** | 0/8 | spacer as w:before is LO-visible: mobile-bill 1.55 -> 1.74 (+0.19 WORSE), 16_right_aligned 0.00 -> 0.00; the 08:56 claim that soffice is blind to this construct is false |

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
| Slot window | 17:00 → running · 36 min |
| Tool beats | 10 |
| Longest silence | **25.6 min** — from 17:09:12, after `LO screen retry after soffice hiccup` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **25 min** | `###############` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **6 min** | `####` |
| record - attempt, handoff, class rows | **3 min** | `##` |

## Next run

1. **Do not re-screen the dither.** 14-of-16 in LibreOffice is measured twice, on two builds.
2. **Do not screen the spacer in Google first.** It is LO-visible; ask LibreOffice, it is far cheaper.
3. **Build the zero-line spacer.** It is the one form untried and it removes the exact 0.19 pt residue
   this slot measured.
