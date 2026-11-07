# Claim ledger — which claim types the verifier believes, and which it does not

Every finding the eye records goes through verify.py. The verifier answers VERIFIED,
REFUTED or UNVERIFIABLE. A REFUTED finding is not a document defect and is never fixed -
but it is still information, and until now nothing kept it.

That mattered because a claim type that is refuted again and again is telling you
something about the TOOL, not about the documents:

    the eye misreads the image            -> the eye's instruction is wrong
    the verifier's check is wrong         -> the tool has a bug
    the claim is too loosely worded       -> the claim vocabulary is missing something

All three are fixable, and none of them shows up if refuted findings are silently dropped.
This table is the diagnostic. One row per claim type, updated at the end of every run.

## The table

| Claim type | Verified | Refuted | Unverifiable | What it means |
|---|---|---|---|---|
| moved: | 0 | 0 | 0 | |
| count: | 0 | 0 | 0 | |
| breaks: | 0 | 0 | 0 | |
| wraps: | 0 | 0 | 0 | |
| missing: | 0 | 0 | 0 | |
| extra: | 0 | 0 | 0 | |
| pagecount | 0 | 0 | 0 | |
| overlap | 0 | 0 | 0 | |
| shapes | 0 | 0 | 0 | |

## The rule

At the end of a run, take the verify.py output for that run and add its counts to the
table. Then read the table:

  a claim type with more REFUTED than VERIFIED is not working. Stop fixing documents on
  it. Work out which of the three causes it is, fix that, and say so in the run's report.
  A document must not be left FAIL on a claim type that the verifier itself refutes.

  a claim type with UNVERIFIABLE counts is not checkable. Either the claim is worded too
  loosely - "looks wrong" instead of "moved:Resident Medical Officer" - or the verifier
  has no check for it. Both are fixable, and neither is a document defect.

  a claim type that is never used is either not needed or not understood. If the eye never
  reaches for it, drop it from the brief rather than carrying a claim nobody makes.

## What this is not

It is not a defect list. Documents go in VISUAL-SCORE.md, engine and writer problems go in
REMAINING-DEFECTS.md. This file is only about whether the eye and the verifier are telling
each other the truth.

## Starting state

Empty. The counts above are placeholders for the first run that fills them. Before this
file existed, a refuted finding left no trace at all - which is exactly how a claim type
can be wrong for weeks without anyone noticing.
