# P2W Fixer - Relay Run Report

**25 Nov 2026 · slot claimed 23:24 IST · released on takeover at 23:37 IST · 43 min of work**

> No engine change was kept this run. One measured finding was committed. The slot was taken over by
> the other fixer cron at 23:37 while this run's delegated measurement was running inline, so this
> report is filed as `LAST-MESSAGE-relay-1926.md` and does not touch the live `LAST-MESSAGE.md`.

## What this run did

| Step | Result |
|:--|:--|
| Claimed the slot | `a0666c44` / `afad8076`, pushed at 17:56 UTC |
| Gate on the committed tree | `regress.py --check` **PASS** at engine `981ff1fa35e2cf67` — both formats, google-safe included, no document worse than baseline |
| Measurement | 4 documents, 8 Google renders of the gap-carrier patch (delegated sub-agent, Drive upload → Google Doc → PDF export → `verify_google.py`) |
| Finding committed | `FINDINGS/18-displacement-GAP-CARRIER-25NOV-relay.md` + its 18 raw result JSONs, pushed as `3a88689b` |
| Attempt recorded | `18_displacement`, outcome **lead**, 0 moved (`attempt.py`, attempt 73) |
| Engine change | **none committed** — see below |

## The measurement: the gap-carrier rule, in Google, before and after

| document | base | gap-carrier v2 | `18` med / worst, base → v2 |
|:--|--:|--:|:--|
| `68_journal_wide_table_spanning` | 41/42 | 41/42 | −114.3 / 115.0 → −2.7 / 3.5 |
| `bank-statement-5-pages` | 42/47 | 46/47 | −55.2 / 355.5 → +9.1 / 36.0 |
| `mobile-bill` | 46/47 | 46/47 | −6.7 / 10.0 → +7.7 / 33.8 |
| `insurance-policy-schedule` | 46/47 | 46/47 | −7.7 / 47.8 → +7.2 / 29.4 |

## What the numbers say

1. **The page-top `w:before` drop is real.** Writing the gap as a 1×1 `w:trHeight hRule="exact"` row
   recovers four checks on `bank-statement-5-pages` (`25`, `27`, `44`, `59`) and cuts its worst
   displacement from 355.5 to 36.0 pt.
2. **The refused spacer is real.** `68_journal`'s 144 pt spacer charged to `w:before` instead of
   `w:line` exact moves its median from −114.3 to −2.7 pt.
3. **No document becomes CLEAN.** All four still fail `18_displacement`. Under the charter's own
   question — *if this works, which documents become CLEAN?* — the answer is none.
4. **The residual is an over-delivery, not a ramp.** Three of four documents land at +7.2, +7.7 and
   +9.1 pt after the patch: a near-constant ~8 pt added per carried gap. `topGapRow()` already writes
   `w:tblCellMar` and `w:tblBorders` as zero, so the surplus is Google's own minimum line box for a
   cell paragraph, not a margin the engine forgot. That is the next run's first measurement.
5. **`hRule="atLeast" → "exact"` on content rows is refuted a third time** — it moved three documents
   by 0.0 pt. It agrees with `18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`.

## Why nothing was committed

`regress.py --check` **passes** on the committed tree, so the gate is not what refuses the patch. The
charter is: `mobile-bill`'s `worst_dy` goes 10.0 → 33.8 under the patch — a Google regression on a
document that already passes 46 of 47 checks — and no document becomes clean to buy it with. The patch
is archived as `tools/p2w-bench/archive/DocxWriter-GAPCARRIER-25NOV.java` for the next run to finish.

## Corpus, as this run read it at 17:58 UTC

| | |
|:--|:--|
| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Documents clean | **42** |
| Classes with a kept attempt | **15** |
| Regressions | **none** |

## Corrections this run leaves behind

* The sub-agent's `DocxWriter.java` javadoc cites `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`.
  **No such file exists in this repo.** The citation is recorded as unsupported in the finding, so the
  next run does not inherit a reference to evidence nobody can read.
* A 23-minute inline sub-agent is a 23-minute silence: this run held the claim through it and lost the
  slot at 23:37. The lesson is in the finding's provenance note — beat before delegating, and delegate
  in the background.
