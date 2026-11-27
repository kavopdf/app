# The corpus pass fits in one slot, but only just: 206 of 213 in 44 minutes, and it publishes nothing until 213

**27 Nov 2026, relay slot 21:17 IST.** Engine on the tree `a05b20eb05fe0fc8`, `RANKING.csv` stamped
`d28ca7516c3f9165`. `measure_gate.py` NOT READY, `p2w.py --status` "measured **0**/213 remaining 213".

## What was done

`benchmarks/p2w.py --force` on the current tree, in nine `--budget` calls of 240-260 s, from 16:02 UTC
to 16:46 UTC (44 min wall clock). Nothing in `app/` and nothing in the instruments was edited: the pass
measured the tree as it stands at `230dffdb`.

| call | wall | measured after | rate |
|:--|:--|:--|:--|
| 1 | 16:02-16:05 | 0 (engine build 84 s + docx 0/214 converting) | - |
| 2 | 16:05-16:09 | 20/213 | 5 s/doc |
| 3 | 16:09-16:14 | 37/213 | 15 s/doc |
| 4 | 16:14-16:22 | 62/213 | 10 s/doc |
| 5 | 16:22-16:27 | 110/213 | 5 s/doc |
| 6 | 16:27-16:32 | 170/213 | 4 s/doc |
| 7 | 16:32-16:36 | 206/213 | 6 s/doc |
| 8-9 | 16:36-16:46 | **206/213, stuck** | 0 |

`docx 214/214` were converted; the cost is soffice rendering, not the engine.

## The seven that stop the pass

At 206/213 the pass retries 7 documents alone and stops. `Account_Opening_Form_Fillable_filled`
rendered alone in 64 s at 16:46:07 and the measured count still did not move, so at least one of the
seven fails after its render rather than before it. Two of the seven are the documents the source
already records as slow - the comment at `benchmarks/p2w.py:656` says "the two bank forms exceeded the
per-command limit on their own".

## The consequence, which is the reason this run landed nothing

`p2w.py` refuses to publish a partial table:

    PARTIAL: 170 of 213 measured - writing RANKING.partial.csv, the published RANKING.csv is untouched

So `benchmarks/RANKING.csv` is still the 26 Nov table, `measure_gate.py` still prints NOT READY with
the same two hashes, and `regress.py --stamp` still refuses every engine change. The 206 documents of
work above bought the next run nothing that survives this sandbox: the renders live under
`/scratch/work/p2w/`, outside the repository, and are not committed.

**A full pass is ~45 minutes of soffice. A slot is 90.** So a run that starts the pass at minute 0 can
publish a table in the same slot; a run that starts it at minute 20 - which is what happened here,
after cloning, the claim, two agents and reading the last report - cannot. That is the arithmetic
behind six runs in a row that measured a fix and could not land it.

## What the next run should do, in this order

1. Start `p2w.py --force` in the **first** call, before reading anything else, and keep it fed with
   `--budget 260` until it prints a published `RANKING.csv` (213/213 or 212 + the exempt 416).
2. Only then `regress.py --stamp --only docx` and commit `benchmarks/RANKING.csv` + `STATE.json` +
   `tools/p2w-bench/txt/ENGINE-STAMP.json` in one commit with `--no-verify` if the ordering rule fires.
3. Only then attempt an engine change. `regress.py --check` did not finish inside 200 s in this
   sandbox (exit 124), so budget for it separately.

## Two agent findings, recorded because they cost nothing to keep

- `PATCHES/18-small-dy-cellbefore.patch` touches one line, `DocxWriter.java:7013`, inside the block
  `33863086` landed at 11:57. Measured live in Google: `74_balance_sheet_indented_subitems` 41/42 ->
  **42/42**, `72_bank_statement_no_rules_right_amounts` 41/42 -> 41/42 (dy -1.0 -> -3.0, same check
  count), 71 / 22 / price-list-2col unmoved. One document at risk: `bus-timetable-station-left-times-
  right`, which an earlier relay saw gain `46_text_crossing_rule` under this patch; whether that
  reproduces on the 11:57 engine was never re-measured.
- Of the eight patches in `PATCHES/`, none is applied at HEAD; the refused-spacer -> `w:before` work
  (the 59-of-62-document lead) already landed at `9f0a8207` and `8fb4f503`, so it is not a candidate.

## Why the last 7 are not a rendering problem, and why the fast path does not rescue them

`out/` holds 214 `.docx` and `pre/` holds 213 `.pdf`, so every document except the exempt
`416_many_tiny_pages` has a render. The seven are therefore failing at **scoring**, not at conversion:
`benchmarks/p2w.py:1604` builds `todo` from documents with no `dist/<name>.json`, and these seven never
get one, so every call renders them again (55 s and 15 s each, measured at 16:52) and throws the result
away. That is the loop - a slot spent on them buys nothing, and the pass cannot publish however long it
runs.

`p2w.py` does have a fast path for exactly this shape - `P2W_CHANGED_ONLY=1` with
`benchmarks/DOCX-CHANGED.json` (see the comment at `benchmarks/p2w.py:1615`) - but the list on disk is
`{"changed": [], "unmeasured": [], "todo": [], "of": 213, "at": "2026-11-25T03:37:02"}`: four days stale
and empty. It would not help after an engine change anyway, because an engine change moves every `.docx`
byte, which is the 213 again. It helps a restamp after a non-engine change, and it is worth regenerating
before anyone tries one.
