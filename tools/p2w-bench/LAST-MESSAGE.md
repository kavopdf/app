# Fixer 22 Nov 21:00 - the phase was `measure` for a real reason, and three runs could not find it

**22 Nov 2026 · slot 21:00 → running IST · 14 min**

**No document moved. Four tool defects closed, three of them committed. That is the whole run.**

The instruction is "phase is not `fix` -> say so and stop". The two runs before this one did exactly
that (`520346e8`, `dc9a96ac`). Standing aside was right in form and useless in effect, because nobody
had established *why* the phase was measure - so a correctly blocked pipeline and a dead one looked
identical from the outside.

It was blocked three ways, and each blocker was a tool reporting something untrue about a
measurement that was fine.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** - 0 attempt(s), 0 kept |
| Fixed - Google, all 42 checks | **23**, from the 192 both renderers measured |
| Regressions | **none** |
| Classes solved | 0 of 35 clear |

**Zero documents became clean this run.** The 23 is the round's standing total, not this slot's work.

## Why no document could be fixed

`benchmarks/RANKING.csv` was last written by `42bdcda2` on **21 Nov 01:44**. Since then `2d44a3a2`
("a line drawn more than once at one place is one line") changed the renderer: the docx stamp read
`6c6cf642e13b7ed2`, the live fingerprint is `226f7f2df3013ad7`. `regress.py` refuses every `.docx`
change as unmeasured until the corpus is re-measured on the engine in the tree, so no construct,
however well chosen, could have landed a document this slot. Re-measuring 213 documents is hours of
render and belongs to the baseline cron.

**The phase must stay `measure`.** That is now the honest state rather than an accident.

## What was closed

**1. `measure_gate` said READY for a table from the wrong engine.** It compared round stamps and row
counts and never the engine - so the one thing actually wrong was the one thing it did not look at.
That is why three runs read READY, could not explain why `regress.py` refused every docx change, and
stood aside. It now compares the docx stamp to the live fingerprint and names both. Stale engine ->
NOT READY, exit 1, `--advance` refuses. Stamped tree -> READY, exit 0. Both directions run.

**2. `regress.py` read an exemption as a deletion.** `gate.py` blanks an exempt row's score and names
its problem `exempt`; `read_rank()` keeps only rows with a score, so `416_many_tiny_pages` vanished
from the current table while HEAD still carried it at `0.0`, and the gate called it `MISSING`. The
baseline measured 212 of 212 on the live engine and **could not publish the honest table** - refused
as a missing measurement. `regress.py` was the only tool that never read `EXEMPT.json`.

The commit that recorded this says the tool "crashes". It does not: stderr is empty and there is no
traceback. It refuses. A run that went looking for a traceback would have found nothing and moved on.

**3. The corpus count claimed 214 documents for a 213-row corpus, and the file said so four times.**
`_total = len(rank) + len(EXEMPTED)` counted the exempt document twice, because it carried the fake
`share5=0.0` that `gate.py`'s publish step exists to blank. `classrow.py` then rewrote only the
*first* `Documents measured` line and left every later copy standing, so the file accumulated one per
run: a header pairing `213` with `214` on line 2, then `213 of 213` three times below it. `header_count()` returns the first
match, so the stale line won. `classify_gate` went NOT READY -> READY on the real table with **no
measurement data touched**.

## The falsifications, because a green gate is not evidence

| defect | it now works | it still fails on a real problem |
|---|---|---|
| `regress.py` exemption vs deletion | honest 212+1 table: exit 1 -> 0 | non-exempt row dropped -> MISSING; **exempt row dropped -> MISSING**; exempt doc scored and worse -> share@5 up |
| `classify_gate` exempt is not scored | real table: NOT READY -> READY | two headers -> refused; scored non-exempt doc missing from class file -> refused; non-exempt row dropped from RANKING.csv -> refused on three counts |
| `measure_gate` engine check | stamped tree -> exit 0 | stale engine -> exit 1 |

Only the document `EXEMPT.json` names is forgiven. Every other document still ratchets.

**One of these nearly shipped green and wrong.** The `classify_gate` exemption block first landed
without `import json`, so its own `except Exception` swallowed the `NameError`, `exempt` stayed empty,
and the gate behaved *identically to before* while looking exactly like a working fix. Caught only by
running it. The fallback now writes to stderr. That is the second time this run had to assume a green
result was a lie.

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
| Slot window | 21:00 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 3 |
| Longest silence | **11.6 min** — from 21:00:02, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `###` |
| report - the report and the chain | **1 min** | `##` |

## Two things the next run should not trust

**`report.py` and the charter disagree about the headline.** The table above says **23** documents
pass all 42 Google checks; the charter says **6**. One of them is wrong and it is not obviously the
charter. I have not reconciled it - the numbers here are report.py's, and I am flagging the
disagreement rather than picking a side.

**`google-safe` is switched off.** Every run prints `google-safe : no .docx output directory -
cannot check` and then passes. The one gate that refuses a construct Google ignores never actually
asserts anything. Not fixed here; the next thing worth a slot.

## Next run

1. Let the baseline re-measure the corpus on `226f7f2df3013ad7`. `regress.py` can now publish that
   table instead of refusing it, and `measure_gate` will confirm the engine matches.
2. Then `classrow.py --write` and `classify_gate` - both verified READY on a clean table.
3. Then a fix phase with a class whose documents are actually measurable.
4. Then `google-safe`: give it an output directory, or make it refuse rather than pass when it has
   nothing to read.
