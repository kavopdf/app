# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | - |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> The 232f622 fix is in the engine and measured on 30 class documents. It has never been ratcheted. Two nine-page bank forms cannot be converted by soffice inside the 290 s call limit, which is why the class measurement stalls - that is a tooling problem, not an engine one.

## What the next run should do first

> Run the full 213-document ratchet on commit 232f622 (per-row tcBorders). Measured on 30 class documents + 12 controls: 22/30 moved, 0/12 controls worse, mobile-bill 18.48 -> 1.55. Never measured at corpus scale, so 180 documents are unproven. Until that ratchet passes, the pipeline has a fix it cannot vouch for. This is ahead of any new class.

## What happened, most recent last

- `13:08` seeded by the agent: the 232f622 ratchet is the open item carried into this run

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
