# CORRECTED: the slot does not die at 45 minutes while a run is alive

This file claimed that `CLAIM_STALE_MIN["fixer"] = 45` kills a live run's slot after forty-five minutes and
that long runs therefore revert each other. That was wrong, and it was wrong because I read the constant and
not the code that uses it.

## What the code actually does

    round.py:456   newest = s.get(key) or 0
    round.py:457   for other in ("%s_last_beat" % name, "%s_doing_since" % name):
    round.py:458       newest = max(newest, s.get(other) or 0)

The age is taken from the NEWEST of the claim stamp, the heartbeat and the doing-since stamp - not from the
claim alone. `round.py:452` says so in its own words: "The age that matters is time since the run last did
anything, not time since it started."

And the heartbeat is real and live. `origin/main:tools/p2w-bench/ROUND.json` right now holds:

    fixer_started    0
    fixer_last_beat  1795609860.7376003

`attempt.py` writes it, `status.py:61` reads it, `round.py` consults it. The forty-five minute limit governs
only a run that has stopped beating - which is exactly the run that should lose the slot.

The mechanism even carries the incident I was trying to explain: the 17 Nov case where one slot's whole-file
commit reverted another's 218-line engine fix is written into the code as the reason the reader was fixed.

## Why the mistake is worth recording

The constant `CLAIM_STALE_MIN["fixer"] = 45` reads like a hard cap on run length. It is not: it is the
patience for silence. A run that works for three hours and beats is never touched; a run that dies is replaced
in minutes.

Sixth wrong finding today, and the same shape as the other five: a number read in isolation, and the code that
consumes it not read. The real defects this session were all found the other way round - read the consumer,
then measure.

## What this leaves

The 37 reverted attempts are still unexplained by this file. They are not a slot fault. Something else
reverted them, and that is now an open question rather than a conclusion.
