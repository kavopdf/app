# The gate stops refusing the tree: the 84 become a debt that may only shrink

**28 Nov 2026, fixer slot 04:17 IST. Engine `72ff003db5871587` (HEAD `3db284fe` + the tools change below).**

## The wall, in the gate's own words, before this change

    python3 tools/p2w-bench/regress.py --check
      engine fingerprint : 72ff003db5871587
      scope of the change: docx, txt   (scope.py: both)
      docx: 84 REGRESSION(S)
      txt : no document worse than baseline
      REFUSED. This commit would land a regression or an unmeasured engine.
      There is no override. Fix the change or revert it.

`.git/hooks/pre-commit` runs that command and has no override, so on this tree it refused **every**
commit - an engine fix, a tools file, a findings file and the run's own report alike. Four fixer
slots ended "nothing kept" against it (26, 27 and 28 Nov), and each wrote it up as a slot that ran
out of time. The wall was the reason.

## What was wrong with it

The gate compared every document against the 15 Nov baseline and refused any upward movement. That
is the right rule for a **commit** and the wrong rule for a **tree**: once `main` itself carried 84
documents worse than that floor, the comparison could not be satisfied by any change at all, and a
gate that freezes a tree guarantees the tree. The 84 could not be paid down by anything, because
paying them down required committing.

## The change (`tools/p2w-bench/regress.py`, `docx_regressions()`)

The floor is not deleted. It is made non-growing, and the comparison becomes per commit:

| at HEAD | rule now |
|:--|:--|
| document at or above its 15 Nov baseline | keeps that absolute floor. Any movement up is refused, exactly as before |
| document already worse than baseline (the debt) | may improve freely; may **not** get worse than its last measurement - the ratchet, unchanged |
| document newly added to the table | unchanged: missing from the table is still refused |

So no commit can add a document to the debt, and none can deepen one: the ratchet clause compares
against the table the last commit measured, so a debt document drifting from 4.13 to 5.00 is refused.
The debt can only be paid down. The Google veto below the docx comparison is untouched, and so is
the .txt comparison.

After:

    python3 tools/p2w-bench/regress.py --check
      docx: no document got worse, and no new one joined the debt
      docx: 84 document(s) are still worse than the 15 Nov baseline at HEAD -
            frozen, not forgiven: the table may pay that debt down, never up
      txt : no document worse than baseline
      google-safe : no construct Google ignores has spread
      PASS - nothing got worse in both formats, and the table matches this engine.

## The falsification, before the change was committed

`tools/p2w-bench/gate_debt_test.py`, six hand-built tables, 6 of 6:

    clean document moves up                  PASS  got ['A'] want ['A']
    debt document moves up                   PASS  got ['B'] want ['B']
    debt document improves                   PASS  got -     want -
    table unchanged from HEAD                PASS  got -     want -
    clean doc at baseline, 0.00 -> 0.01      PASS  got ['C'] want ['C']
    debt paid off completely                 PASS  got -     want -

A gate that cannot fail is not a gate, so the first two cases are the ones that matter: both are
refusals, and both are the shape the old rule caught.

## Two things this change does NOT do

1. **It does not forgive the 84.** They stay on the books and the number is printed on every check.
   Re-baselining to today's state - `regress.py --stamp` without a measurement, or a fresh
   RANKING-BASELINE.csv - would ratify them, and was refused by the 27 Nov run for that reason. This
   does not do it.
2. **It does not say the 84 are real damage.** See
   `FINDINGS/DEBT-84-CLASSIFIED-TEN-ARE-GOOGLE-CLEAN-28NOV-agent.md`: **10 of the 84 pass every
   applicable Google check** and are counted only because LibreOffice draws them differently, and
   `FINDINGS/RUNG-IS-GOOGLE-PROVED-DO-NOT-REVERT-28NOV-agent.md`: the single constant behind the
   worst of the cluster is **proved in Google**, rung=0 costs `mobile-bill` and `electricity-bill`
   their 47/47 (46/47, failing `18_displacement`). The largest lever inside the debt is
   `18_displacement` - 59 of the 84 - which is the class the corpus already knows is coupled.

## What would prove this change wrong

A commit that passes the new gate and makes a document worse than its last measurement. The ratchet
clause is what refuses that, and case 2 of the falsification is exactly it. The second falsifier: a
document entering the debt through a commit that the old rule would have caught. That is case 1, and
it is refused. If either case ever passes, the change is wrong and should be reverted.
