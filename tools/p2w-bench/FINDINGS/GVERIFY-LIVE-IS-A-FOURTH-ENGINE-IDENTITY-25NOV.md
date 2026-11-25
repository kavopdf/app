# gverify --plan's "live" is a fourth answer to which engine

The 10:56 run fixed the comparison that made the Google scoreboard blind, across three instruments -
report.py:460, gverify.py:194 and classify_google.py:34. Verified after it landed:

    report.py              google_fixed -> (42, 213, 42, 213, 0)
    classify_google --print  "Every result above was measured on engine 981ff1fa35e2cf67, the engine in
                              the tree."
    engine on disk           11 .java files -> sha256(name+bytes)[:16] = 981ff1fa35e2cf67
    .stamp                   981ff1fa35e2cf67

All four agree. What does not is the plan:

    gverify.py --plan 60
    live  : 36b7913c98da (12 checks)
    Not compared, not carried forward, and not replaced: the marks were left as they were. Re-measure
    the corpus, or reset with a reason if the universe really moved.

36b7913c98da is not this tree's engine. The tree hashes to 981ff1fa35e2cf67 over 11 files; "12 checks"
is not a file count and not a check count for any document in the store. So `live` is computed from
something else again - a fourth derivation of the same question, after the three that were just
reconciled.

## Why it matters

The plan is what tells the hourly cron what to re-measure. A `live` that matches nothing means the cron
is told the universe moved, which is the same perpetual re-measure the run just closed on the other
three instruments - moved one layer down rather than removed.

## The rule

One question, one derivation. report.py now reads .stamp and is right. classify_google.py now reads the
same thing and is right. gverify.py's plan should read it too, and its `live` line should print the
value it actually compared, not a second hash computed beside it.

## Verified, not changed

The engine was not touched and the store is correct: 213 verdicts on 981ff1fa35e2cf67, 42 clean. Only the
plan's own `live` label disagrees, and it is the label the cron steers on.
