# The relay's ready patch regresses LibreOffice by 21.5 points - measured, and it is the DITHER, not the spacer

**22 Nov 2026, fixer slot 19:00.** `report.py`'s "Next run" tells the next run to *"APPLY
patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch and ratchet it corpus-wide"*,
because the 15:18 relay measured it **42/42 PASS in Google** on `two-tables-stacked-with-no-gap`.

**It was never measured in LibreOffice.** I applied it (`patches/18-spacer-before-rowpitch-rowrule.patch`,
110 insertions), added the LO-neutral spacer split on top (see
`FINDINGS/18_displacement-SPACER-SPLIT-1900-f1x.md`), built `462353f9+…`, and measured with
`benchmarks/p2w.py measure_doc` - the instrument that writes `RANKING.csv`.

| document | `RANKING.csv` (HEAD) | relay patch + split | delta |
|:--|--:|--:|--:|
| `two-tables-stacked-with-no-gap` | share1 **21.85** / share5 0.77 | share1 **43.33** / share5 **30.01** | **+21.48 worse** |

So the patch that makes this document Google-clean makes it **twice as wrong** in the proxy. That is
not a proxy artefact to waive away: `regress.py` has a Google-clean / proxy-worse waiver, but a waiver
is a decision that the proxy is wrong for that document, and nothing here establishes that. The dither
rewrites `w:trHeight` on every ruled row of every table, and LibreOffice lays `w:trHeight` as a real
height - so the construct that repairs Google's 0.75 pt row grid necessarily moves LibreOffice's rows.

## What this changes for the next run

1. **Do not apply the relay patch and ratchet it.** It is LO-regressive by 21.5 points on the one
   document it was measured on, and it touches every ruled table in the corpus.
2. The **spacer half is safe** and separable: split the gap (`w:before = G-20`, `w:line = 20`) instead
   of moving it, and LibreOffice is bit-identical (`mobile-bill` 43.87 / 1.55 before and after) while
   Google's table-top step falls 11.3 -> 2.6 pt. That half is a lead with both renderers measured.
3. The **row-pitch half needs a construct LibreOffice agrees with**, or a per-document waiver with an
   argument. `w:trHeight` is not it.

## The falsification that was not run, and should be

`mobile-bill` under the same patch. The relay measured it 41/42 with n_out 100 -> 39, i.e. Google got
*better*, and its residual is "+2 to +5 pt low". My LO run of `mobile-bill` hit the 280 s command
limit before printing, so it is unmeasured here and is the first thing the next run should take.
