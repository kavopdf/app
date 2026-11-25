# Two fingerprints for one engine

Found while checking the 23:58 fixer report's claim that measure_gate.py was NOT READY.

## The observation

    /scratch/work/p2w/.stamp                -> 981ff1fa35e2cf67
    measure_gate.py "engine docx"            -> 9e2b3e4d7869ea86
    measure_gate.py "tree"                   -> 9e2b3e4d7869ea86

All 213 verdicts in benchmarks/gverify/ carry 981ff1fa35e2cf67, and measure_gate calls the tree
9e2b3e4d7869ea86. measure_gate is READY because its own two values agree with each other - it never
compares against the stamp the verdicts carry, so it cannot see that the two disagree.

This is the same defect class as the one closed earlier today: report.py had a third derivation of
"which engine" and counted 0 scored on a corpus fully measured on it. report.py now reads .stamp. This
is the same question asked by a second tool with a second answer.

## Why it matters

A verdict stamped 981ff1fa35e2cf67 is a measurement of the build that wrote the .docx it describes.
If measure_gate believes the tree is 9e2b3e4d7869ea86, then either:

  - the two are the same build fingerprinted two ways (harmless but unverifiable), or
  - the tree moved after the verdicts were written and 213 verdicts describe an engine that is gone.

Nothing on disk distinguishes those two cases, which is the actual defect. measure_gate's READY is not
evidence that the verdicts are current, because it never looks at them.

## What the next run should do

Make one tool the authority for the engine identity and have the others read it, the way report.py now
reads .stamp. Until then, a green measure_gate and a fresh verdict store are two separate claims that
happen to be printed next to each other.

Verified this run and NOT changed: the verdicts do match .stamp (213 of 213), so nothing is stale by
that measure. measure_gate is READY by its own measure. Both statements are true and they are not about
the same number.
