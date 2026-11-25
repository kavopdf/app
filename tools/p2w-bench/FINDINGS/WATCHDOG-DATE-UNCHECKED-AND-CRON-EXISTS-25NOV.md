# Two watchdog claims that do not survive a check

Read from the watchdog pass whose PDF is dated 25 Nov and whose body is headed "Watchdog pass, 23 Nov".

## 1. "measure-google: done, 213 of 212" - already fixed, not repeated here

A stage cannot measure more documents than the corpus has. health.py `_corpus_total()` was counting
RANKING rows (212) while `done` counted gverify files (213). The fixer closed this on 25 Nov in
a323d424 ("two instruments counted files and called them measurements"), and health.py now prints
213 of 213 because `of` is taken from what gverify saw - scored plus page-count-refused.

Verified this run: `health.py --json` reports measure-google done 213 of 213.

## 2. The report's own date is wrong and nothing checks it

The PDF is a 25 Nov run. Its body says "Watchdog pass, 23 Nov". That is not a rounding difference: the
report is the only dated record of a pass, and a reader who trusts the heading has the pass a day and a
half early.

lastmessage.py checks every integer in a report against the tool output, and dates are deliberately
exempt (its own comment: "Numbers that legitimately come from elsewhere - a date, a commit sha, the
corpus size"). So the one field a reader uses to place the report in time is the one field the checker
does not verify. That is the same shape as every other defect in this directory: a value nobody
cross-checks.

## 3. "This watchdog has no cron tool" is not true of this platform

The report states plainly: "This watchdog has no cron tool, so a paused or zombie cron cannot be moved
by automation", and asks that the next pass overturn it. It is overturned: cron IS available here as a
platform tool, with list, create, delete, pause, resume and runs. So the blind spot the pass reports
does not exist, and STEP 3 and STEP 4 A/B of its own brief are runnable.

What that means for the next pass: a paused cron is not a permanent silence. The calls the pass said it
would have made - list, then pause and resume on the stalled id, then runs to look for a zombie - can
be made. Its own brief already forbids leaving a cron paused, so the guard against doing damage is
there.

## What was NOT touched

No instrument was edited to make a number look better. health.py is correct as it stands, and the two
remaining items above are a record for the next watchdog pass, not a change to what it measures.
