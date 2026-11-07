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
| moved: | 9 | 1 | 0 | the workhorse: 374 -329.3 pt, 375 -172.4, 381 240.8, 393 132.7, 401 -484.1 all held. The one refutation was mine - "Employee name" was 2.6 pt out, inside the 3.0 pt tolerance, and I had read the cell grid wrong |
| count: | 0 | 0 | 0 | |
| breaks: | 0 | 0 | 0 | |
| wraps: | 0 | 0 | 0 | |
| missing: | 0 | 0 | 0 | |
| extra: | 0 | 0 | 0 | |
| pagecount | 0 | 0 | 0 | |
| overlap | 1 | 1 | 0 | 401 held (3 pairs against the PDF's 0). 393 was refuted by a check that only compares LINE boxes: the peak table and the caption are drawn over the CHART, and a table over a picture is not a line overlap. The eye was right and the check is blind |
| shapes | 0 | 0 | 1 | 400 lost one speech bubble's outline and the claim came back UNVERIFIABLE - there is no visual check for a shape count at all, only the "charts" measure question, which answers "yes" on 5 paths against 4 |
| emphasis (not a type yet) | 0 | 0 | 1 | 380's Escalation line is bold in the render and regular in the PDF. q8 only asks whether a line the PDF emphasised KEPT its size; a line the render emphasised on its own is invisible to it |
| columns (not a type yet) | 0 | 0 | 1 | 383's RESPONSE FIELDS table has a fourth empty column and row rules the PDF does not draw. No claim type describes a table's shape |
| order (measure) | 3 | 0 | 0 | 373 91.9 %, 400 42.1 %, 401 50.0 % - all three agreed with what the eye saw |

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
