# The pending gate counts past events as work, so it can never open

## Verified

    classpick.py:560   "PENDING FIRST: %d item(s) you can close"
    pending.py         PENDING (19) - "Do not take a new class until it is empty."

Nineteen items. Every one is a `[blocker]` entry lifted from HANDOFF, dated 20 to 23 November.

## And some of them are not work

    [blocker] 2026-11-22 09:16
    "watchdog pass - the fix slot, and the platform - I forced a release on a slot...
     can I fix it: partly - the release is done and cannot be undone. No work was lost."

That item says in its own text that it cannot be undone, because it already happened. It is a record of a
past action. It is listed as pending work, and `classpick` refuses to name a class while it is there.

An item no run can close is not a gate, it is a wall. Every such entry makes the gate stricter without making
any work get done, and the ledger shows the result: the fixer spends its runs on bookkeeping it cannot finish.

## The distinction that is missing

There are three different things in that list and they need three different treatments:

1. A DEFECT THAT IS STILL OPEN - `t01_word_accuracy` counting one fault as four on the bank forms. Real work.
2. A DECISION ALREADY TAKEN - "the release is done and cannot be undone". A record, closed by definition.
3. A NARRATIVE OF A PAST RUN - "watchdog pass, I forced a release". Also a record.

Only the first is work. `pending.py` lifts all three out of HANDOFF and gives them the same weight, and
`classpick` blocks on the count of all three.

## What it costs, measured

19 items, and the fixer has been unable to take a new class. Meanwhile six checks can clean 40 documents
(verified: 18_displacement 25, 60_text_column_right_edge 6, 47_margins 3, 59_shape_anchor 3, 32_stroke_lines
2, 17_matched_runs 1) and none of them is being worked while the gate is shut.

## What to change

An item needs a way to be closed by evidence rather than by a run deciding it is done:

- If its text says it is done or cannot be undone, it is closed. That is a pattern, not a judgement.
- If it names a FINDINGS file that exists and is committed, it is closed - the finding landed.
- If it is older than a fixed age and its class has been attempted since, it is stale: report it, do not
  gate on it.

And the gate itself should count only items whose class is the class being chosen, so a blocker on
t01_word_accuracy does not stop work on 18_displacement.

## Verified, not assumed

Every number here was read from the tools today: 19 pending items from pending.py, the gate string from
classpick.py:560, the six cleanable checks and 40 documents from the gverify store on engine 981ff1fa35e2cf67.
