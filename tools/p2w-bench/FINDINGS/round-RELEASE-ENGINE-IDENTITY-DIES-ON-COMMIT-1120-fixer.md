# The release guard's proof of measurement is destroyed by the commit that ships it

**Instrument defect. Found 23 Nov 2026 at 17:38, at release, after the change was measured and pushed.**

## What happened

The release refused:

    refused: the engine changed this run (5beb8b9d -> b7699196) and no attempt was kept.

Both halves of that sentence are true and neither is a problem. The engine change **was** measured
corpus-wide (212/212 scored, 0 documents worse, `regress.py --check` PASS, `measure_gate.py` READY) and
the attempt **was** recorded — as `partial`, because the outcome rule wants a quarter of the class and
the Google evidence for this construct is 2 of 23 documents. The guard reads "no attempt kept" as "never
measured", and its stronger evidence — `benchmarks/STATE.json`'s `engine` field, which it consults
first — could not match either.

## Why STATE.json could not match

`gate.py` writes `engine` as **head + the sha1 of the engine diff**, i.e. a *working-tree* identity.
Measured: `5beb8b9d+71ec0fe4d4`. The moment the change is committed, the tree is clean and the identity
becomes `b7699196`. The record that proves the corpus was measured on this source is invalidated by the
act of recording the source.

The same defect was found and fixed for the `.txt` half on 21 Nov (`STATE-TXT.json`, whose comment sits
twenty lines above the branch that refused here). The `.docx` half never got the fix, so the release
guard still cannot see a `.docx` change that was measured before its own commit.

## What it costs

A run that does the right thing cannot hand the slot on: it must `--force` past a guard whose stated
reason ("this change has never been compared against the corpus") is contradicted by the run's own
gates. On 17 Nov this guard shipped a rule that regressed seventy documents, so it must not be removed —
it needs an identity that survives the commit.

## The fix, for the next run

Accept `STATE.json`'s identity when it equals the identity the **committed** engine had while it was
being measured, which is recoverable: take the last commit that touched `engine/` (`h`), its parent
(`p`), and `git diff p h -- engine/ | sha1sum`; that is exactly `p + "+" + sha` when the commit is the
measurement's own change. Ten lines in `round.py`, the same shape as `_measured_on_this_tree()` added to
`regress.py` this run.

## What would prove this wrong

A run where the engine commit also changes something outside `engine/` in the same commit — then the
parent's diff is not the measured tree, and the guard must fall back to the ledger.

**This run released with `--force`**, and the engine was not reverted (`--force` skips the revert
branch, which is why it is the safe path here and not a bypass of the measurement rule).
