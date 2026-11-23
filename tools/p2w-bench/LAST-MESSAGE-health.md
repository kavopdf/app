Watchdog pass, 23 Nov. The pipeline is moving. Two stages are stopped and this run could not move either
of them.

health.py --stalled exits 1.

- measure-google: done, 213 of 212, age 4.2 h
- matrix: done, 213 of 213, age 4.2 h
- classify: stopped, age 7.5 h
- fix: moving, 2 attempt(s) in 3 h, age 0.6 h
- txt: stopped, 199 clean and 14 failing, age 12.7 h

Trend, today's row against the last: docx open 59 -> 59, txt failing 16 -> 14, google 192 -> 190,
google clean 23 -> 30. Today's row already existed, so nothing was appended and PROGRESS.md had nothing
to commit.

Round: phase fix, round 1 of 3. The phase is not done, so round.py --reopen does not apply; the class
count round.py prints was not carried into this report because this checker will not verify it.

Fixer slot: not dead. ROUND.json records the claim twelve minutes before this pass, so --release-fixer
--force was not run - releasing a slot a run took twelve minutes ago would put a second run into the
engine. The fixer landed a commit while this pass was running.

Both stopped stages belong to crons:

- classify: the class table is older than the newest Google results it describes. Owner is the
  classifier cron.
- txt: the .txt table predates restamp_txt.py, one of the three inputs that can change a score; health
  reports those inputs 6.8 h old. Owner is the baseline cron, which has made no recorded claim for over
  a day.

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. I could not
read next_fire_at, paused status or the run list for either cron. The exact calls I would have made are
written into BLOCKERS.md: list, then pause and resume on the stalled id in the same run, then runs to
look for a zombie.

What would overturn this: a watchdog run whose tool list contains cron. Until then every pass reports
the same blind spot, and a paused cron stays silent with nothing in the repository able to notice it.

BLOCKERS.md is updated and pushed.
