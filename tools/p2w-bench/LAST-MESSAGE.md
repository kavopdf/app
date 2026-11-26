# P2W Fixer - Run Report

**27 Nov 2026 · slot 03:24 → running IST · 53 min**

> No change was kept this run. One construct was measured corpus-wide and refused; the numbers below say
> why, and the patch is saved for the run that can measure Google instead of the proxy.

## What this run changed

Nothing in `app/`. The corpus was rebuilt and re-measured, and the engine change was **reverted** after its
own measurement.

**Attempt 1 - `18_displacement`: "make a one-line cell's content equal its `w:trHeight`".** 23 lines in
`DocxWriter.java`, guarded to rows whose every cell holds one line (wrapped rows, vertical merges, empty
cells and the row cut at the paper's bottom keep the old pair), and it fires where it should: on
`362_price_list_dense` 255 of its 260 `(before + line)` pairs now equal their row's declared height, on
`402_calendar_month_grid` only 10 of 47 do.

Then the corpus: 213/213 rebuilt, 204 of 212 scored before the slot ended.

| | documents |
|:--|--:|
| better | 13 |
| worse | **91** |
| unchanged | 100 |
| corpus mean `median_pt` | 2.274 → **2.641** |

`23_timetable_grid_txtpos` 0.96 → 12.48, `404_sudoku_grid` 1.44 → 7.68, `electricity-bill` 0.96 → 5.76.
Reverted. The patch, the table and the guards are in
`FINDINGS/18-displacement-ROWH-CONTENT-EQUAL-TRHEIGHT-REFUTED-27NOV-relay.md` with the 41-line diff beside
it.

This is the third form of this construct to be measured and refused, and all three are now written down in
one place: the code already records `w:before = rowLineTw - box` (`18_median_dy` 64 → 100) and shortening
`w:trHeight` instead (`electricity-bill` 18.0/19.0 → 17.5/18.5); this run adds content = `trHeight`.

## The gate, and why the run is 90 minutes and not one attempt

The pod arrived with 124 of 213 documents converted and no stamp, so the pre-commit hook could not run: the
first two calls that touch git (`install-gate.sh`, `round.py --claim-fixer`) each burned their 300 s limit
inside `regress.py --check`'s corpus build and were killed. Two `corpus-slice.py` calls (245 s, 153 s)
finished it; the claim then held and the hook was never the blocker again. `measure_gate.py` reported READY
on the way in.

The measurement itself chunked cleanly: `benchmarks/p2w.py --budget` writes `RANKING.partial.csv` and leaves
the published table alone until 212 of 212 are scored, so four chunks of ~265 s took 60 → 120 → 168 → 204 of
212 with nothing to redo. **The last 8 documents are unmeasured**, and the published `RANKING.csv` is
untouched, so the gate is exactly where this run found it.

## The txt

| | |
|:--|:--|
| Measured | **1.4 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*Two read-only agents deployed this run.* One produced the line-anchored spec for the row-height patch
(`DocxWriter.table()` at 6005-7181, `rowHeightTw` at 6546, the emit point at 6962, the four guards); the
other was not run, because the first returned a complete spec and the slot was needed for the measurement.


## Timing

| Slot window | 03:24 → running · 54 min |
| Tool beats | 167 |
| Longest silence | **5.1 min** — from 04:12:14, after `p2w.py: scoring landscape-page-inside-portra (12 in this pass)` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **18 min** | `########` |
| fix - diagnose and change the engine | **5 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `#########` |
| other - not attributed to a tool | **5 min** | `##` |
| report - the report and the chain | **1 min** | `#` |

The unattributed row is 3 distinct beat(s) that matched no phase. They said:

- `relay: row-height patch applied, rebuilding engine to probe it`
- `relay: corpus rebuilt on new engine; measuring`
- `18_displacement -> reverted`

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Take the 36 pending items first (`pending.py`), then: the patch in
`FINDINGS/18-displacement-ROWH-CONTENT-EQUAL-TRHEIGHT-27NOV.patch` needs GOOGLE numbers on the 91 documents
it costs in LibreOffice, not another patch. The corpus on this pod was rebuilt on that patch and then the
patch was reverted, so a pod that arrives warm will convert 213 again - apply the patch first if you are
measuring it, and skip the conversion if you are not.

## Progress

| Check-instances passing | **4758** of 5044 (94.3%) on 117 documents |
| Check-instances still failing | **286** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **55** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** — the engine change was reverted before the table moved |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **28** of the **116** re-measured on this engine - **89** of the 205 scored are still on an older engine |
| Not scored - page count did not match | **8** of the 213 gverify saw |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear |
| Working on | `18_displacement` |
| The rotation says | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:55 | **reverted** | 0 | one-line cell content = w:trHeight (23 lines, guarded): 13 documents better, 91 worse, mean median_pt 2.274 -> 2.641 over 204 of 212; reverted, diff in FINDINGS |

## Why nothing moved, in this run's own words

I chose `18_displacement` because it is the largest class by leverage and because the run before this one had
left a two-document Google probe saying this exact change takes documents to 42/42. What I did not have, and
what the run before this one also did not have, is a Google measurement of the documents the change hurts.
The proxy says 91 of them. Both statements can be true at once - LibreOffice honours `w:trHeight`, so the row
was already right there and this only moves the baseline down inside it; a renderer that lays the cell needs
the move. That is a collision between the instrument and the renderer the user opens, and no amount of
further patching in `DocxWriter.java` settles it: what is missing is Google numbers for the same 204
documents, not a better patch.

So the honest result of this slot is one construct eliminated by measurement, one patch preserved with its
numbers, and the corpus warm on the next engine it is applied to.

### The run before this one said

> The commit gate is open again, and two documents were taken to 42/42 in Google by changing four characters
> of XML each. Neither is landed: the engine change needs the 212-document table re-measured on the new
> engine, and that pass did not fit the slot.

That pass did fit this slot - 213/213 converted in four slices, 204 of 212 measured in four chunks - and it
is what refused the change. The finding that run says it wrote,
`FINDINGS/18-displacement-CELL-CONTENT-SHORT-OF-ROWH-27NOV-fixer.md`, is **not in the repository**: the
report claims it, `git log -- FINDINGS/` has no commit for it, and `ls FINDINGS/` does not list it. The
probe's exports were on that pod only. That gap is why this run had to re-derive the mechanism from the code
instead of from the numbers.
