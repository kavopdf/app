# The slot dies at 45 minutes, the brief asks for hours, and the two reverts are the difference

## The contradiction, in two numbers

    round.py:204   CLAIM_STALE_MIN = {"fixer": 45, "baseline": 45, "classifier": 20}
    FIXER-BRIEF    "run until the work is done"; runs of 2h48m are described in its own pages

A run that legitimately works for ninety minutes has its slot declared dead at forty-five. The next cron
run - the fixer fires hourly at :50 - claims the slot, finds it free, and starts. Two runs are now editing
`app/src/main/java/.../engine/` at the same time.

The code says exactly what that costs, in its own comment on line 119:

    "a live run of up to forty-five minutes is never doubled - two runs editing the engine at once would
     each revert the other's fix."

So the pipeline knows the failure mode, guards against it for forty-five minutes, and then allows it. The
guard is not wrong; the window it guards is too short for the behaviour the brief asks for.

## What the ledger shows

    37 attempts recorded as `reverted`
    19 of 18_displacement's 20 attempts are `lead`, one `reverted`
    47_margins: 8 reverted of 16

A revert means the change was applied and did not hold. Some of those are genuine - the construct did not do
what was thought. But the brief's own instruction is to work until the time is used, and a run that obeys it
crosses forty-five minutes, and past that point a second run can revert it. The ledger cannot tell the two
apart, and neither can the run that comes next.

## Why this is a pipeline fault and not a discipline fault

The run is being asked to do two incompatible things: use its full time, and never outlive its claim. It
cannot do both while the claim lasts less than the work. Telling it to release the slot before measuring
(the brief's own rule for corpus measurement) covers one case - a measurement - and not the general one,
which is any long attempt.

## The options, with what each costs

1. RAISE THE LIMIT to cover a real run. 45 -> 150. A dead run then costs 150 minutes of an empty slot
   instead of 45. That is the trade: fewer doubled runs, slower recovery from a crash.

2. HEARTBEAT INSTEAD OF AGE. A run that is alive rewrites `started_ts` every few minutes; staleness is then
   "no heartbeat for 15 minutes", not "claimed 45 minutes ago". A dead run is detected in 15 minutes, a live
   one is never stolen, and the two requirements stop fighting. This is the one that fixes it properly.

3. RELEASE AND RE-CLAIM AROUND EVERY LONG STEP. The brief already does this for corpus measurement. Doing it
   around every engine build would work and would put the burden on the run to remember, which is what the
   ledger shows runs do not reliably do.

## Recommendation

Option 2. It is the only one where a live run is never mistaken for a dead one and a dead run is still found
in minutes, and it removes the need for the brief to teach a workaround.

Not changed here: the slot is what stops two runs corrupting the engine, and a wrong change to it is worse
than the fault. Recorded with the measurement so the change is made against the evidence.
