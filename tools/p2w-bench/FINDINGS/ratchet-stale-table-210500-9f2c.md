# The committed RANKING.csv does not reproduce from its own engine, and that blocks every fix

**Found 19 Nov 21:05 while trying to land an engine fix. No engine change needed to see it.**

**RESOLVED the same run, commit `c6d8cdf`:** the table this engine actually produces was measured
across all 213 documents and published (203 rows identical, 10 corrected upward), with no engine
change in that commit. `regress.py --check` then passed and the engine fix landed. The rule below
is still worth settling - the ten rows were invisible to every tool we have.

## What happened

The fixer measured the whole corpus in this pod with **origin/main's engine** - unmodified,
`4147d54` (11:55, "a justified line is written justified"). `p2w.py` syncs `/scratch/work/p2w/repo`
from `origin main` and builds it, so the measurement is of the committed engine and nothing else.

203 of 213 documents came back **identical to the committed `benchmarks/RANKING.csv` to six
decimal places**. Ten did not, and every one of the ten is worse in the fresh measurement:

| document | committed | fresh, same engine | delta |
|:--|--:|--:|--:|
| `table-of-contents-dot-leaders` | 8.52 | 10.72 | +2.20 |
| `magazine-2col-pullquote-spanning` | 1.45 | 2.58 | +1.13 |
| `report-2col-table-spanning-both-columns` | 15.22 | 16.10 | +0.88 |
| `journal-2col-with-footnotes` | 5.65 | 6.34 | +0.69 |
| `policy-2col-spanning-section-heading` | 1.76 | 2.36 | +0.60 |
| `37_font_not_embedded_substitution` | 0.04 | 0.58 | +0.54 |
| `table-inside-two-column-page` | 37.65 | 38.11 | +0.46 |
| `newspaper-2col-fullwidth-headline` | 0.01 | 0.42 | +0.41 |
| `landscape-page-inside-portrait-document` | 0.62 | 1.02 | +0.40 |
| `text-held-twice-shadow-text` | 30.20 | 30.29 | +0.09 |

Re-measured a second time in the same pod: 0.42 -> 0.42, 10.72 -> 10.72, 30.29 -> 30.29. The
measurement is reproducible; it is the table that is not.

## Why it matters

`regress.py --check` compares the current table against `git show HEAD:benchmarks/RANKING.csv`
as well as against the 15 Nov baseline. Those ten rows therefore read as ten regressions **for
any commit that re-measures the corpus, whatever the change is** - including no change at all.
An engine fix cannot land until this is repaired, and no fixer run can repair it, because the
commit that would repair it is the one the hook refuses.

The ten are exactly the documents the 11:55 justified-line commit touched (its message says
"7 documents newly clean, 0 worse"). The table kept the older numbers for them.

## What the next run should do - and it is a decision, not a measurement

The engine is right and the table is stale. One of these has to be written down as the rule:

1. **Re-measure and publish, then treat the correction as a table fix, not a regression.**
   `regress.py` already has the shape of it: the baseline is the floor, the previous table is
   the ratchet. A ratchet may only tighten, which is right - but the rule needs an honest door
   for "the previous table was not a measurement of this engine", which is exactly what its own
   stamp is supposed to prove and does not, because the stamp hashes the ENGINE FILES and the
   table was hand-edited after the fact.
2. Or stamp the TABLE with the fingerprint of the measurement that produced it (a column, not a
   sidecar), so a hand-edited row is visible as one.

Do not simply re-run `--stamp`: that asserts the table is this engine's measurement, and for
these ten rows it is not.

## Evidence

* fresh full-corpus table: `/scratch/output/RANKING.csv`, 213 rows, written 15:23 UTC
* committed table: `git show HEAD:benchmarks/RANKING.csv`
* 416_many_tiny_pages is EXEMPT and was measured by hand in eight 40-page windows and merged
  with `measure_doc_chunked`'s own rules (share@N = max, chars_missing = sum) - share5 0.00
