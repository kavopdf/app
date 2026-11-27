## The pipeline is moving. One stage was stopped, and it was the slot, not the engine.

At the start of this pass `health.py` read fix stopped: a run had claimed the fixer slot and stopped
speaking. That was the only stop. Everything else was moving, done, or correctly waiting.

| stage | state | progress | age |
|---|---|---|---|
| measure-google | moving | 72 of 213 | 0.4 h |
| matrix | done | 213 of 213 | 1.9 h |
| classify | waiting | - | 6.8 h |
| fix | moving | 3 attempt(s) in 3 h | 1.1 h |
| txt | moving | 205 clean, 8 failing | 0.6 h |

## What I did about it

The fixer claimed the slot at 08:34 and its last beat was 08:40:38, in the middle of a corpus slice, and
after that nothing - no beacon, no attempt, no commit. By 09:08 the claim was older than round.py's own
stale window, so the relay cron firing at 09:10 would have found the slot held and stood down, and the
next fixer run at 09:50 would have been the first able to take it.

I ran `round.py --release-fixer --force` and it released. The relay is the next run that can claim the
slot, and after the release `health.py` reads fix moving again. The reason, the evidence and what would
overturn it are in BLOCKERS.md.

I did not delete or recreate either fixer cron. The fixer and relay pair shares one slot on purpose, and
deleting one of them puts the silent-dead failure back.

**This watchdog has no `cron` tool.** So a paused cron, or one enabled and not firing, cannot be seen or
moved by this run - and neither can a zombie run. The calls I would have made are written out in
BLOCKERS.md with the ids from the health brief's table. That is a missing tool, not a decision waiting
for a person.

## The trend

`progress.py` already had a row for today and appended nothing. Today against yesterday:

docx open 60 to 59, txt failing 8 to 8, google 205 to 205, google clean 47 to 47.

One column moved. txt failing has read 8 on two consecutive rows and google clean 47 on two, with the
fixer's 3 attempts in 3 h beside them - the fixer is working and the corpus is not moving. The upload
bridge blocker recorded earlier today is why the Google column cannot advance.

Phase is fix, round 1, so there is nothing to reopen.
