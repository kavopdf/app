# The pending list, item by item: 6 closed, 6 still open, 3 refused, and two bugs in the list itself

**25 Nov 2026, fixer slot 09:13. Produced read-only by a subagent, acted on by the parent run the same
slot. Before/after measured with `pending.py` in one clone.**

## Before and after

| | before | after |
|:--|--:|--:|
| `pending.py` | **16** | **12** |
| `pending.py --decisions` | 2 | 4 |
| `classpick.py` | refused, 14 closeable | refused, 8 closeable |

The two rows that arrived between the two readings are not the parent run's: commit `fa5bd53b` (the 09:10
gverify pass) added them, and they are decisions-owed rows. 16 - 6 closed + 2 arrived = 12.

## The six closed, with the evidence each one rests on

| row | closed because |
|:--|:--|
| `stage.py` counts a result file as a measurement (2026-11-21 13:22) | fixed this run: `measured()` calls `gverify._done()`. `stage.py` 213 measured -> 82. See `FINDINGS/INSTRUMENTS-COUNTED-FILES-NOT-MEASUREMENTS-25NOV.md`. Also 7 cells -> 6, so `pending.py` could read the row at all. |
| the claim is advisory (2026-11-21 17:35) | (a) is already implemented: `round.py:501-503` returns 1 while live, `:543-566` makes the pushed claim the lock, `:420-431` decides from `origin/main`, `:441-461` ages from the newest beacon. `test_claim_remote.py` asserts both halves. |
| `--release-fixer` refused on a pending count (2026-11-22 10:09) | `round.py:975-993` honours `--force` and prints `FORCED past N pending item(s)`. Use it only when the pending count is the sole refusing guard. |
| `74_balance_sheet_indented_subitems` never committed (2026-11-24 09:10) | the verdict is committed and current: `benchmarks/gverify/74_balance_sheet_indented_subitems.json` 41/42, engine `85b8735f`, 03:14:41, failing `18_displacement` (med_dy 2.2, worst 4.2). `RANKING.csv:127` calls it `clean` - the proxy-vs-truth case. |
| a subagent has no repo (2026-11-22 12:07) | refuted by measurement: two subagents cloned the repo themselves this run and returned 40 KB each. What they lack is the corpus and Drive, not the repo. |
| the same wall, second row (2026-11-22 12:08) | same measurement. |

## Still open, and what each actually needs

- **`2026-11-20 23:19` ligature identity at Effra CIDs 0x123/0x124/0x126/0x127** - needs a reference face or an
  English word list; neither is in the repository. The four-checks half is already closed (3/12 -> 6/12).
- **`2026-11-23 07:37` the denominator** - needs a person to say whether `BASELINE.md` or the instrument is
  authoritative. `RANKING.csv` has no denominator column at all, `BASELINE.md` is retired, and `ratchet.py:36-52`
  takes the denominator only from `verify_google.py --list-checks`. Re-stamping it would change a number with no
  measurement before or after, which is non-negotiable 2.
- **`2026-11-22 09:16` watchdog forced a live slot** - part 1 is done and verified: `round.py:204` is
  `CLAIM_STALE_MIN = {"fixer": 45, ...}` and the comment at `:112-120` explains why `FIXER_STALE_MIN = 100` was
  removed. Part 2 needs a `cron` tool this run does not have. Left open on purpose: closing it would hide part 2.
- **`2026-11-23 23:05` x3** - the ratchet items (`05_chars_extra`, `32_stroke_lines`, `t08_line_order`); they wait
  on the denominator decision above.
- **`2026-11-25 06:05` x2, `2026-11-25 09:10` x2** - the cron platform. No `cron` operation in this run's tool
  list; nothing in the repository can close them.
- **`[measure] the docx table`** - work, not a decision: `gverify.py --plan 60`.

## Two bugs in the list itself, found and not fixed

1. **`pending.py:288` uses the MODAL engine, not the current one.** It reports "60 document(s) still carry a
   verdict from an older engine". Measured: 131 results carry `b7699196` (23 Nov), 60 carry `85b8735f` (25 Nov
   02:06) - so the 60 it calls stale are the freshest 60, and the 131 stale ones are invisible. `gverify.py --plan`
   still picks the right 60 because `plan()` uses `_done()`. This is the same defect as `stage.py`'s, one layer
   further in, and it is left for the next run: it changes a number in a tool that decides what a run works on.
2. **`pending.py:261` reads `RANKING-TXT.csv`'s mtime**, which a fresh clone stamps as "now" - so the `.txt`
   staleness `health.py` reports (23.9 h) can never surface in the pending list.
