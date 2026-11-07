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
| moved: | 31 | 4 | 0 | the workhorse: 374 -329.3 pt, 375 -172.4, 381 240.8, 393 132.7, 401 -484.1 all held. 8 Nov v3 batch 2 added 8 verified. Re-checked after the gap-clamp fix, 3 of those 8 came back REFUTED (318 7.8 pt, 320 8.9, 325 9.4 stayed VERIFIED on the residual; 326 2.4, 333 0.6, 340 0.1 were refuted by the fix, which is the outcome a fix should produce). The one earlier refutation was mine - "Employee name" was 2.6 pt out, inside the 3.0 pt tolerance, and I had read the cell grid wrong |
| count: | 0 | 0 | 0 | |
| breaks: | 1 | 0 | 0 | |
| wraps: | 0 | 1 | 0 | one refutation, 303's WARNING SIGNS: the eye saw one line on the PDF and two in the render, and the verifier counted 2 on both sides. The eye misread a line the page had already wrapped at the right margin - the claim was right in form and wrong in fact, which is what the verifier is for |
| missing: | 0 | 0 | 0 | |
| extra: | 0 | 0 | 0 | |
| pagecount | 4 | 0 | 0 | 8 Nov: 330 and 332 both 1 page in, 2 out, verified twice (once from the eye's FAIL, once from the computed question). Both are drawing pages whose dimension lines and tables overflow |
| overlap | 1 | 1 | 0 | 401 held (3 pairs against the PDF's 0). 393 was refuted by a check that only compares LINE boxes: the peak table and the caption are drawn over the CHART, and a table over a picture is not a line overlap. The eye was right and the check is blind |
| shapes | 0 | 2 | 1 | 400 lost one speech bubble's outline and the claim came back UNVERIFIABLE - there is no visual check for a shape count at all, only the "charts" measure question, which answers "yes" on 5 paths against 4. 316 came back REFUTED: the question said "1 in the PDF, 0 in the docx" and verify.py counted 1 on both sides, so the charts question is what is wrong |
| emphasis (not a type yet) | 0 | 0 | 1 | 380's Escalation line is bold in the render and regular in the PDF. q8 only asks whether a line the PDF emphasised KEPT its size; a line the render emphasised on its own is invisible to it |
| columns (not a type yet) | 0 | 0 | 1 | 383's RESPONSE FIELDS table has a fourth empty column and row rules the PDF does not draw. No claim type describes a table's shape |
| order (measure) | 24 | 0 | 0 | 373 91.9 %, 400 42.1 %, 401 50.0 % - all three agreed with what the eye saw. 7 Nov batch: 301 78.7 %, 303 88.5 %, 305 47.1 %, 311 90.2 %, 312 60.9 %, 315 29.1 % all held against the PDF, but only five of the six agreed with the eye: 312 was passed on sight, so that row is a measurement bug, not a document defect. 8 Nov batch 2 added 9 verified, and 2 of them disagreed with the eye (331 93.3 %, 334 89.7 %, both passed on sight): reading order on a page of a drawing or a figure is the same measurement bug |

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

## What the batch of 7 Nov added

15 documents from v3 batch 1 went through the whole chain: 15 pages looked at, 15 findings
emitted, 15 verified - **13 VERIFIED, 2 REFUTED, 0 UNVERIFIABLE**. That is the first run
where every finding was checkable; the UNVERIFIABLE column did not move at all.

The two refutations are both worth keeping:

    wraps: 303's WARNING SIGNS. The eye read the PDF's own right-margin wrap as one line.
    shapes 316's SCHEDULE C. visual.py's charts question said "1 in the PDF, 0 in the
           docx"; verify.py counted 1 on both sides. The document is fine and the
           question's shape count is not comparable between the two sides.

And one finding came back VERIFIED while the eye had passed the page:

    312's order at 60.9 %. looked.py --combine named it correctly - "eye (numbers wrong,
    repair the tool)" - and the document stays PASS. The reading-order question is
    pairing rows that the page draws as a form, so the tool is what needs the work.

## Run 8 Nov 2026 - v3 batch 1 re-processed (300-317)

15 findings, 14 verified, 1 refuted, 0 unverifiable. Added above: moved +7, breaks +1,
order +6, shapes +1 refuted.

Two claims had to be REWORDED before the verifier could check them, and both times the eye was
the thing that was wrong, not the check:

    moved:Dr. A. Bhat, MD, DNB (Radiology)   UNVERIFIABLE - the page says "(Radiodiagnosis)".
                                             I read the word off a 150 DPI image. The offset
                                             was real: 231.5 pt.
    count:This is a computer generated ...   REFUTED - 1 on both sides, not 2. I thought I saw
                                             the line twice in the render; the copy at the foot
                                             of the page is the PDF's own and the render's one
                                             copy is 351.8 pt too high. The right claim was
                                             moved:, and it verified.

The rule that held: a claim whose TEXT is wrong comes back UNVERIFIABLE or REFUTED and costs
one round trip, while a fix applied on the same reading would have edited a page that was
already right.

## Run 8 Nov, v3 batch 3 (341-370)

19 findings, 18 verified, 1 refuted, 0 unverifiable. moved +1, missing +1, wraps +2, rules +1,
order +10, pagecount +2, shapes +1 refuted.

`rules` is new this run. 351_omr_answer_sheet's extra table rules were real and no claim type
could say so: `extra:1` came back REFUTED because "1" matches sixteen lines, and the page was
about to be recorded PASS behind a false alarm. It now reads 11 rules in the PDF against 32 in
the render and VERIFIED. This is the case PIPELINE.md calls "the claim vocabulary is missing
something", and it is the same gap that left 380 and 383 unverified on 7 Nov.

Two needles were too short to be claims and both were refuted on a substring: `wraps:12` matched
"ACC-447112". The defect behind it was real - the row count said 17 against 15 - so the finding
was kept on the measured claim and the visual one dropped. A two-character needle is not a claim.
