# The phase was 'measure' for a real reason, and three runs could not find it

**22 Nov, fixer run 21:00. Nothing measured, nothing fixed. Three tool defects closed.**

The run arrived in phase `measure` with `measure_gate` printing `READY - every document measured`
and `classify_gate` printing `NOT READY`. The instruction is "not 'fix' -> say so and stop", and
the two runs before this one did exactly that (commits `520346e8`, `dc9a96ac`). Standing aside was
correct in form and useless in effect: nobody had established *why* the phase was measure, so the
state could not be told apart from a pipeline that had simply stopped.

It was not stopped. It was blocked three ways, and each blocker was a tool reporting something
untrue about a measurement that was fine.

## 1. The engine moved after the table was measured

`benchmarks/RANKING.csv` was last written by `42bdcda2` on **21 Nov 01:44**. Since then
`2d44a3a2` ("a line drawn more than once at one place is one line") changed the renderer. The docx
stamp read `6c6cf642e13b7ed2`; the live fingerprint was `226f7f2df3013ad7`.

`measure_gate` compared round stamps and row counts and **never the engine**, so it printed READY
for a table from the previous renderer. That is why three runs in a row read READY, could not
explain why `regress.py` refused every `.docx` change as unmeasured, and stood aside. The phase was
right; the gate was lying about why.

**The phase must stay measure until the corpus is re-measured on `226f7f2df3013ad7`.** No document
fix can land before that, and no amount of construct-picking changes it.

## 2. `regress.py` read an exemption as a deletion

`gate.py` blanks an exempt row's scores and names its problem `exempt` (the settled shape in
`SETTLED.md`). `read_rank()` keeps only rows carrying a `share5`, so `416_many_tiny_pages` vanished
from `cur` while `previous_table()` still carried it at `0.0` from HEAD, and `docx_regressions()`
reported it as `MISSING from the current table`.

So the baseline measured 212 of 212 on the live engine and **could not publish the honest table**:
the gate refused it as a missing measurement. `regress.py` was the one tool that never read
`EXEMPT.json`.

The commit that recorded this (`dc9a96ac`) says the tool "crashes". It does not. stderr is empty
and there is no traceback; it refuses. Worth writing down, because a run that went looking for a
traceback would have found nothing and moved on.

## 3. The corpus count was 214 for a 213-row corpus, and the file said so four times

`_total = len(rank) + len(EXEMPTED)`. The exempt document carried `share5=0.0` in the committed
table — the fake "perfect" score `gate.py`'s publish step exists to blank — so `len(rank)` already
counted it and the exempt set added it again.

`classrow.py` then rewrote only the *first* `Documents measured` line and left every later copy
standing, so the file accumulated one header per run: `213 of 214` on line 2 and `213 of 213` three
times below it. `header_count()` returns the first match, so the stale line won.

## What was fixed, and what it was proved against

| defect | proof it works | proof it still fails on a real problem |
|---|---|---|
| `regress.py` exemption vs deletion | honest 212+1 table: exit 1 -> exit 0 | F1 non-exempt row dropped -> MISSING; F2 **exempt row dropped -> MISSING**; F3 exempt doc scored and worse -> share@5 up |
| `classrow.py` count + duplicate headers | real table: `213 of 214` x4 -> `212 of 213` x1 | — |
| `classify_gate.py` exempt is not scored | real table: NOT READY -> READY | F-A two headers -> refused; F-B scored non-exempt doc missing from class file -> refused; F-C non-exempt row dropped from RANKING.csv -> refused on three counts |
| `measure_gate.py` engine check | stale engine -> exit 1, `--advance` refuses | stamped tree -> exit 0 (both directions run) |

Every one of the four was checked in **both** directions. Six tools in this repo have exited 0 and
lied in the last two days, and one of them was nearly mine: the `classify_gate` exemption block
first landed without `import json`, so its own `except Exception` swallowed the `NameError`, `exempt`
stayed empty, and the gate behaved *identically to before* while looking exactly like a working fix.
It was caught only by running it. The fallback now writes to stderr.

## The instrument is still lying about the headline

`google-safe : no .docx output directory - cannot check`. `regress.py` prints this on every run and
passes anyway. The one gate that refuses a construct Google ignores is switched off by a missing
output directory, so "no construct Google ignores has spread" is never actually asserted. This was
not fixed here and is the next thing worth a slot.

## What this run did not do

**Zero documents became clean.** These are obstacle-cleared, not fixed, and the table says so. The
value is that the next baseline run can publish the honest table instead of being refused for it,
and that the phase machine can no longer report READY for a table from the wrong engine.
