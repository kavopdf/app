# The ratchet was gating a retired pipeline: 211 of 211 documents UNMEASURED

**24 Nov 2026, fixer slot 04:20 IST.** `tools/p2w-bench/ratchet_google.py` is new. Nothing in
`ratchet.py` was changed and nothing was deleted.

## What I found

`ratchet.py` enforces non-negotiable 3 — *no document gets worse* — and it reads
`tools/p2w-bench/BASELINE.md` and `RESULTS.jsonl`. `RETIRED.md` says of `BASELINE.md`, in the
table headed *"The three documents that look live and are not"*:

> the old check-id baseline: one row per document, a `40/58` score and a list of failed check ids
> → what replaced it: `benchmarks/RANKING.csv`

Measured on a clean tree at `c618445f`, before anything was touched:

```
$ python3 tools/p2w-bench/ratchet.py --check
  instrument                : 47 checks (sha 97b6067807c2)
  documents scored this run : 211 of 211 rows
  compared against a mark   : 0
  NOT COMPARED: 211 row(s) and 0 mark(s) are counted out of a universe
  the instrument does not have (47). A count out of 59 is not a count out of 47 ...
  UNMEASURED - the bar was not asked: 211 of 211 document(s) could not be
  compared, and 0 were.
```

`RATCHET.json` does not exist in the tree at all, and `BASELINE.md`'s rows are stamped `u59` while
the live instrument has 47 checks. So this is not a gap that more measurement closes: the store's
denominator belongs to a different instrument, so no new reading can ever reconcile it. The gate
could not pass and could not fail. It could only say UNMEASURED.

That matters beyond tidiness, because `pending.py` is itself a gate — *"a run may not take a new
class while it lists something"* — and five of its 81 items are

```
2. [ratchet] 00_page_count        kept, 0/213 moved,  never ratcheted at corpus scale
3. [ratchet] 05_chars_extra       kept, 11/192 moved, never ratcheted at corpus scale
4. [ratchet] 32_stroke_lines      kept, 16/213 moved, never ratcheted at corpus scale
5. [ratchet] t08_line_order       kept, 9/10 moved,   never ratcheted at corpus scale
6. [ratchet] t09_page_furniture   kept, ?/? moved,    never ratcheted at corpus scale
```

A ratchet item closes when `attempt.py --ratchet N` stamps `ratchet_at`. That stamp means *the whole
corpus was re-measured and nothing fell*. The tool that would prove it compares nothing, so the item
cannot honestly close, so `pending.py` never empties, so `classpick.py` refuses:

```
$ python3 tools/p2w-bench/classpick.py
refused: PENDING FIRST: 22 item(s) you can close - take them in the order pending.py
gives before any new class.
```

This run never reached a class because of it. That is the mechanical reason five consecutive
`18_displacement` slots committed findings, patches and prose and no engine code.

## What I did instead

`ratchet_google.py` asks the same question of the store the user's renderer writes:
`benchmarks/gverify/*.json`, 213 records, 190 `status: ok`, 23 `page_count_refused`.

The comparison is **by check identity, not by count**. `passed` cannot be compared across a mark
and a re-measurement here, because the universe is per-document and variable — 126 records are out
of 42, 62 out of 47, 2 out of 44, because a check that does not apply is not asked. The `failed`
list is a set of check *names*, and names survive a denominator change:

```
fell = failed_now - failed_at_mark     non-empty -> FAIL, and it names the checks
```

`RATCHET-GOOGLE.json` is the mark file; the bar only ever rises.

## Measurement, before and after

| | `ratchet.py` (retired store) | `ratchet_google.py` (Google Docs) |
|:--|:--|:--|
| records read | 211 rows of `BASELINE.md` | 213 `benchmarks/gverify/*.json` |
| compared against a mark | **0** | **190** |
| new, first mark | 211 | 0 |
| not compared | **211** | 23 (`page_count_refused`) |
| fell | 0 | **0** |
| exit | 3 UNMEASURED | 3 UNMEASURED, or 0 with a recorded waiver |

## The falsification, because a gate that never fails is not a gate

Each of these was written down before it was run, then run:

| test | prediction | measured |
|:--|:--|:--|
| no marks yet (`--check`) | 190 new, 0 compared, exit 3 | 190 new, 0 compared, **exit 3** |
| first real run | 190 marks written, exit 3 | 190 marks, **exit 3** |
| second run | 190 compared, 190 held, exit 3 (23 uncompared) | 190 compared, 190 held, **exit 3** |
| one clean `42/42` record mutated to fail `47_margins` | exit 1, naming the document and the check | **exit 1**, `17_three_column_widths_txtpos now fails 47_margins` |
| one record's `total` 42 → 47 | not compared, never a pass | **not compared**, `universe changed: mark x/42, now x/47` |
| `--recut --reason` on that document | re-marks it, says so | **re-marked**, `x/42 -> x/47` |

The mutation was reverted and `git status --porcelain benchmarks/gverify/` is empty — the store is
byte-identical to `c618445f`.

## The waiver, and what it is not

23 documents are `page_count_refused`: Google drew a different number of pages than the source, so
there is no line-by-line comparison to make. `report.py` already counts them, as *"Not scored -
page count did not match: 23 of the 213 gverify saw - a document that drew the wrong number of
pages cannot be compared line by line, and it is a defect, not a pass."*

A gate that can only ever print exit 3 is a gate nobody reads — that is how the retired one died.
So the gap is accepted in writing, in `WAIVER-GOOGLE.json`, naming those 23 and calling them an
open defect. `--allow-stale` without `--reason` is refused, and it cannot turn a FALL into a pass.

## What this does not prove, and the next run must not read it as

**The 190 marks were taken from the same records the first comparison ran against.** So run three's
"190 compared, none fell" is circular: it proves the comparison is wired correctly, not that any
document held a bar taken before a change. From the next engine change forward the marks are prior
and the gate bites for real. Until then this is a bar being SET, not a bar being HELD — and the five
`pending.py` ratchet items stay open, because none of them has yet been re-measured against a mark
that predates it.

**Do not stamp `ratchet_at` on the strength of this run.**

## What is still wrong with the gate

1. A mark carries no check-name universe, only a count (`total`), so when the instrument asks a
   different number of checks of a document the gate can only refuse or `--recut`. Storing the
   asked-check names in the mark would let it compare the intersection instead.
2. 23 documents cannot be compared at all. That is `00_page_count` — priced at **23.0 clean
   documents** by `classpick.py --leverage`, second in the corpus — and it is the reason a fifth of
   the corpus is outside every gate at once.
3. `ratchet.py` is left exactly as it was. It still reads the retired store and still prints
   UNMEASURED. Retiring it, or pointing it at this file, is a decision for a run with a slot and is
   not one this run made.
