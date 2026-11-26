Two stages read stopped, and neither is a mystery: classify is overdue on a table older than the measurement it groups, and fix is stopped on a silent claim that is still inside its own window.

## The picture

health.py --stalled exits non-zero and names classify and fix. measure-google is done, 213 of 213, 0.3 h. matrix is done, 213 of 213, 2.2 h. classify is stopped at 9.8 h against a 6 h threshold. fix is stopped, 2 attempt(s) in the last 3 h, 0.9 h. txt is moving, 204 clean and 9 failing, 4.6 h.

The first read of this pass said nothing was stopped, and that was true of the reading: classify read waiting while the Google measurement it depends on was incomplete, and fix had a live beacon. Both changed while I was writing, which is why this report carries a second read rather than the first.

## The trend

The row was appended, then amended, because the Google measurement completed mid-pass and the first row carried a partial reading of the clean count. It now reads docx open 59 to 59, no change. txt failing 9 to 9, no change. google 213 to 208, down 5. google clean 42 to 42, no change.

I read the tables rather than the report: RANKING.csv holds 59 documents above the share threshold, and the txt table holds 9 with a failed check. Both are current, and both are what the tools print.

## STEP 5 fires, and the answer is the gate

The earlier pass left itself a test: STEP 5 fires only if google clean is flat too, or if RANKING.csv is older than the engine it measures. google clean is 42 to 42, so the first condition now holds, on top of docx open reading 59 on six consecutive rows. Both flat columns carry 2 attempt(s) in the last 3 h and 0 kept beside them.

The decision is that the approach is wrong, not the class. The evidence is the 05:28 relay row in BLOCKERS.md: regress.py --check refuses on an unmeasured engine, a corpus re-score costs 4 slices and 11 min, and a revert costs the same again, so a change is measured, reverted and never lands inside a slot. That is why nothing is kept whichever class the fixer picks.

What replaces it: a scope keyed on the documents a change can actually move, so a patch whose .docx output is byte-identical on every probe does not pay a full corpus re-score before it can land. That is the repair the 05:25 row names. I did not implement it, because regress.py and the verifiers are on the do-not-touch list and the scope rule is the fixer's to change with a measurement.

What would overturn this: one engine change that lands and moves docx open, which would show the gate is passable and the class was the problem after all.

## The two stopped stages

classify: the class table is older than the Google results it must group, so it is overdue rather than misconfigured. The classifier cron owns it and fires hourly. I cannot read its runs or move it, because this pass has no cron tool.

fix: status.py reads SILENT, with no beacon and a claim that is still inside the fixer claim's stale window. round.py frees that claim on its own once the window runs out, and the next fixer slot takes the work. I did not force a release: a second run beside one that may still be alive is the thing the claim exists to prevent, and the window has not run out.

RUN.json also still carries an earlier unclosed run from this morning. That is a record, not a lock: ROUND.json held no claim while it sat there, so nothing was blocked by it.

## No cron tool in this pass

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation, and neither stopped stage can be checked or resumed by me. That is a missing tool, not a decision for a person. No cron was recreated, so there is no new id to record, and nothing here claims the platform was checked.

The calls I would have made and did not: cron with action list; cron with action runs and the classifier and fixer ids from HEALTH-BRIEF's table for the two stopped stages; then pause and resume in the same pass for a stale next\_fire\_at, never leaving one paused; then delete and create with the same name, schedule and prompt if a run were still running past an hour with ended\_at null.

Phase is fix. The committed rotation still has docx on 44\_header\_footer and txt on t12\_word\_invention, and 18\_displacement stays parked, because parking a class would be the wrong repair while the gate is what is failing.
