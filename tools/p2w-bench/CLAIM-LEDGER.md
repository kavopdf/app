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
| moved: | 68 | 4 | 1 | the workhorse: 374 -329.3 pt, 375 -172.4, 381 240.8, 393 132.7, 401 -484.1 all held. 8 Nov v3 batch 2 added 8 verified. Re-checked after the gap-clamp fix, 3 of those 8 came back REFUTED (318 7.8 pt, 320 8.9, 325 9.4 stayed VERIFIED on the residual; 326 2.4, 333 0.6, 340 0.1 were refuted by the fix, which is the outcome a fix should produce). The one earlier refutation was mine - "Employee name" was 2.6 pt out, inside the 3.0 pt tolerance, and I had read the cell grid wrong |
| count: | 7 | 2 | 0 | 8 Nov v3 batch 2: five `count:` claims on 323's spend-by-category labels (Travel, Shopping, Fuel, Groceries, Health) all verified - the page draws six labels against six amounts and the render keeps only the amounts. This is the type to use when a word occurs more than once on the page, because `missing:` refutes on the first hit anywhere. One refutation the same run: 326's `count:Taxable amount` - the header cell spans two grid columns and python-docx reports it twice, so 1 on both sides. Earlier: 38's subtitle is drawn twice on the page to fake bold and once on both sides of a line in the render; the count held |
| breaks: | 5 | 0 | 0 | 8 Nov v3 batch 2: 318's TAKE NOTICE line held - the PDF's line ends at "your", the render carries "absence." onto it and no render line ends there. Earlier: 8 Nov re-run of v3 batch 1: 303's WARNING SIGNS held as a `breaks` claim - the PDF's line ends at "needed" and no render line does, because the PDF's own line overruns the paper by 1.4 pt and its tail never reaches the page |
| wraps: | 1 | 5 | 0 | one refutation, 303's WARNING SIGNS: the eye saw one line on the PDF and two in the render, and the verifier counted 2 on both sides. The eye misread a line the page had already wrapped at the right margin - the claim was right in form and wrong in fact, which is what the verifier is for |
| missing: | 4 | 0 | 2 | 39's NOTICE TO MEMBERS is UNVERIFIABLE - the page writes the heading with letter spacing, so its text layer reads collapsed too and the needle is not there on either side |
| extra: | 1 | 0 | 0 | 8 Nov re-run of v3 batch 1: 312's `extra:NOTARY` held - the circular seal's arc text is drawn twice in the render and once on the page. First use of this type |
| pagecount | 5 | 0 | 0 | 8 Nov: 330 and 332 both 1 page in, 2 out, verified twice (once from the eye's FAIL, once from the computed question). Both are drawing pages whose dimension lines and tables overflow |
| overlap | 1 | 1 | 0 | 401 held (3 pairs against the PDF's 0). 393 was refuted by a check that only compares LINE boxes: the peak table and the caption are drawn over the CHART, and a table over a picture is not a line overlap. The eye was right and the check is blind |
| shapes | 2 | 5 | 2 | 400 lost one speech bubble's outline and the claim came back UNVERIFIABLE - there is no visual check for a shape count at all, only the "charts" measure question, which answers "yes" on 5 paths against 4. 316 came back REFUTED: the question said "1 in the PDF, 0 in the docx" and verify.py counted 1 on both sides, so the charts question is what is wrong |
| rotated: | 9 | 0 | 0 | NEW 9 Nov, b80 batch 1. The type that was missing: nine stamp documents whose only defect is an ANGLE could not be claimed by any of the other nine. Every check reported on the wrong property - `moved:` found the words 3.9 pt across on 02 and called them in tolerance, `missing:` found them in the render's text layer, `count:` matched 1 against 1 - so all nine came back UNVERIFIABLE and the document's FAIL stood on nothing. It compares the PDF line's writing direction with the render's: 01 15.0->0.0, 02 15.0->0.0, 03 90.0->0.0, 04 180.0->0.0, 06 8.0->0.0, 07 12.0->0.0, 08 9.0->0.0, 09 11.0->0.0. Written modulo 180 at first and it refuted 04, because a line's dir is its writing direction and 180 degrees is upside down, not level; the full-turn comparison is what shipped |
| emphasis (not a type yet) | 0 | 0 | 2 | 380's Escalation line is bold in the render and regular in the PDF. q8 only asks whether a line the PDF emphasised KEPT its size; a line the render emphasised on its own is invisible to it |
| rules | 2 | 0 | 0 | 9 Nov v3 batch 4 added one: 373_leave_application_form, 11 rules in the PDF against 28 in the render, because every label/value cell is written as two table rows. First use was 8 Nov: 351_omr_answer_sheet, 13 rules in the PDF against 32 in the render - a ruled grid drawn round rows 16-45 of a bubble sheet the page leaves unruled. Both directions count, because a check that can only see "too many" turns every missing rule into a false pass |
| columns (not a type yet) | 0 | 0 | 1 | 383's RESPONSE FIELDS table has a fourth empty column and row rules the PDF does not draw. No claim type describes a table's shape |
| order (measure) | 64 | 0 | 0 | 9 Nov v3 batch 4 added 2: 400 at 80.0 % of 15 rows, 401 at 72.2 % of 18. Earlier: 373 91.9 %, 400 42.1 %, 401 50.0 % - all three agreed with what the eye saw. 7 Nov batch: 301 78.7 %, 303 88.5 %, 305 47.1 %, 311 90.2 %, 312 60.9 %, 315 29.1 % all held against the PDF, but only five of the six agreed with the eye: 312 was passed on sight, so that row is a measurement bug, not a document defect. 8 Nov batch 2 added 9 verified, and 2 of them disagreed with the eye (331 93.3 %, 334 89.7 %, both passed on sight): reading order on a page of a drawing or a figure is the same measurement bug. 8 Nov second pass of v3 batch 1 added 6 verified; 1 of the 6 disagreed with the eye (305 47.1 %, passed on sight - the PDF draws every table cell as its own line and the render joins a row's cells with tabs, so 27 rows against 24 can never match) |

### 8 Nov 21:03, v3 batch 1 final sweep - what this run added

16 findings from 15 documents: moved 6 verified, breaks 1, missing 1, order 6, wraps 1 refuted
(314, 2 lines on both sides), moved 1 unverifiable (305's seal legend, drawn per glyph on both
sides so no `moved:` check can match it). `order` disagreed with the eye once more - 312 at
67.6 % of 34 rows, passed on sight - which is the tab-joined-row blind spot, now recorded four
times. No claim type is refuted more often than it is believed.

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

## Run 8 Nov, v3 batch 5 (402-417)

17 findings, 14 verified, 2 refuted, 1 unverifiable. moved +3, count +1, missing +1, rules +2
(both refuted after the fix), order +4, pagecount +2, shapes +1 (refuted by the tool fix), wraps
+1 unverifiable.

Both `rules` findings were real and both were the same cause, which is the useful part: the
writer bordered every table whatever pass found it, so two whitespace tables arrived with a box
the page never drew. A claim type that verifies on two documents for one reason is worth more
than the two documents.

The refuted pair matters too. `rules` on 403 and 406 came back 0 against 0 after the fix, which
is how the ledger proves the fix landed rather than the finding going quiet.

One UNVERIFIABLE: `wraps:Board meeting`. The wraps check needs to follow the needle's words
through the render, and the render splits the cell it is looking for - which is the defect. A
claim that describes a split cannot be followed across the split. The page is not left on this
claim: `pagecount` and `order` both verify on it.

## Run 8 Nov, b80 batch 1 (01-20)

32 findings, 22 verified, 1 refuted, 9 unverifiable. moved +9 (8 verified, 1 refuted), wraps +1
(refuted), missing +1 (unverifiable), extra +1 (unverifiable), shapes +1 (unverifiable), order
+15 (all verified), pagecount +1 (verified), overlap 0.

The nine unverifiable claims are one pattern, and it is the claim that is wrong, not the page:
every rotated stamp is written by the writer as several lines ("AUTHORISED SIGNATORY" and
"SUNRISE FASTENERS" are two lines of one stamp), so a claim that quotes the whole stamp as one
string matches neither side. `moved:SANCTIONED`, one line of the stamp, verifies. The rule for
the next run: a stamp claim quotes ONE line of the stamp, never the whole block.

The one refuted claim is mine, not the document's: `wraps:Branch Manager, Kunigal Branch` on
11_stamp_with_signature_image - both sides carry that line twice, so there was nothing to fix.
This is the second time in two runs that a wraps claim read off a side-by-side has been refuted
with "2 line(s) on both sides"; the eye is judging the stamp's position and blaming the wrap.

`order` verified on 15 of 15 documents where it was claimed, including every document the eye
passed. On 05 the eye passed and order read 62.5 %; that is the seal's per-character text, the
measurement blind spot already recorded, and it is the only eye/numbers disagreement in the
batch.

## Run 8 Nov, b80 batch 2 (21-40)

10 findings, 9 verified, 0 refuted, 1 unverifiable. moved +2 (both verified), count +1
(verified), missing +1 (unverifiable), order +6 (all verified).

Six of the ten findings are the `order` question, and two of those six disagree with the eye:
28 (79.1 %) and 40 (92.7 %). Both are the same shape as the 331/334 disagreement in batch 2 of
v3 - reading order pairs rows by text, and on a page whose cells deliberately overrun, or whose
script is reshaped, a row has no counterpart to pair with. `looked.py --combine` named both
"eye (numbers wrong - repair the tool)" and both documents stay PASS. That is now three
documents on this one blind spot; it is a tool repair, not a page repair.

The UNVERIFIABLE is the useful one this run. `missing:NOTICE TO MEMBERS` on 39 is a real
defect - the render joins every word of a letter-spaced heading - but the page's own text
layer is written the same spaced way, so the needle is absent on both sides and the check
cannot fire. The finding survives on `order` alone. A claim whose needle does not exist on
the PDF is the fourth form of the vocabulary gap: not too loose, not missing a check, but
pointing at text the page never spells the way a reader sees it.

## b80 batch 3 (41-60), 8 Nov — what this run added

20 findings, 16 verified, 1 refuted, 0 unverifiable. moved: +5 verified, pagecount: +2,
missing: +1, order: +7. The two refutations both name a tool fault, and both are written up
in REMAINING-DEFECTS.md:

    rules   2 refuted, and both were FALSE ALARMS caused by the check, not the page. The
            one-way `b > a` test was replaced with a two-way comparison, and the classifier's
            `height <= 1.2` was excluding a 1.2000000476 pt band - the widest rule on
            58_header_rule_footer_rule. With RULE_MAX_PT = 1.5 the page is 3 and 3, and 58
            passes. A claim type that refutes on a hairline is the tool talking.
    wraps   1 refuted on 56_table_indented_from_margin, where a value really is broken. The
            check follows words, the PDF holds `640.00` and the render `640.0` + `0`, so the
            follow stops and the block reads as two lines on both sides. `missing:640.00`
            verified the same defect. wraps must match on characters, not words.

## b80 batch 4 (61-80), 8 Nov — what this run added

45 findings, 45 verified, 0 refuted, 0 unverifiable. That is the first clean sweep in the
ledger, and it is worth saying why: every claim this batch was written AFTER the page was
measured, not guessed from the image. `moved:` +15, `pagecount:` +13, `order:` +11,
`shapes:` +4, `wraps:` +1.

    moved      15 verified. The batch's claim of choice, because the defect it describes
               is positional: a column stacked below another column puts text somewhere
               else on the paper and leaves its x alone. moved: compares y, so it fires.
    pagecount  13 verified. Nine of them are the same document's sheets counted once each.
    order      11 verified, and 4 of the 11 are the tool talking. `rows()` bands lines by
               y across the whole page, so on a two-column page each visual row is counted
               twice - 61 reports 29 PDF rows against 39 render rows for a page whose 39
               lines are all within 0.2 pt. The four eye-passed / numbers-failed documents
               in this batch (61, 66, 71, 80) are all that, and all four are recorded PASS.

### The refutation that did not happen

Nothing was refuted this run, and that is the opposite of 7 Nov, where two of nine were
false alarms. The difference is not that the verifier got better; it is that three FAILs
written from the 130 dpi image (72, 73, 74) were checked at 220 dpi before they were
recorded, found clean, and never entered the findings file. A finding that is not written
cannot be refuted, and that is the right place for it to die.

## g53 corpus, batch 1 - the run of 8 Nov

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| pagecount | 16 | 0 | 0 |
| order | 11 | 0 | 0 |
| shapes | 3 | 0 | 0 |
| wraps | 1 | 0 | 0 |
| breaks | 1 | 0 | 0 |
| moved | 0 | 0 | 1 |
| overlap | 0 | 1 | 0 |
| **total** | **32** | **1** | **1** |

`pagecount` is 16 of 32 verified findings, and every one of them is the same defect: a
multi-column page written as one flow. That is the claim type to work next, not the document.

`moved:1,994` came back UNVERIFIABLE because the value is not a line of its own on both sides -
the claim was written against a sidebar whose label and value are separate fields, and neither
side sets them as one line. A `moved:` claim needs text that is a line on both sides; the
brochure's real evidence is `shapes` and `pagecount`, both of which verified.

## v3 batch 1 (300-317), re-run 8 Nov 09:06 - after the gap fix

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| order | 6 | 0 | 0 |
| moved | 1 | 0 | 0 |
| count | 1 | 0 | 0 |
| breaks | 1 | 0 | 0 |
| **total** | **9** | **0** | **0** |

Every finding verified and none refuted, which is the first run where that is true. The
first pass of the same batch, before the fix, was 9 verified / 1 refuted / 2 unverifiable:
the refuted one was `wraps:WARNING SIGNS`, where the eye read a wrap and the page holds two
lines on both sides - the claim should have been `breaks:`, and as `breaks:` it verified.
The two unverifiable ones were wording: `moved:Copy forwarded to Superintendent of Police`
omitted the colon the PDF draws ("Copy forwarded to:"), so `startswith` never matched, and
`extra:560067Mobile` is not a line on either side - the welded label is better claimed as
`count:Mobile`.

Six `order` findings verified and all six were decided for the document by the eye. That is
the row-banding blind spot (D-03) showing up as a claim type, not as a defect.

## g53 batch 2 (B 14-20, C 21-26), 8 Nov - the statements class

26 findings: 25 verified, 0 refuted, 1 unverifiable.

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| pagecount | 7 | 0 | 0 |
| order | 15 | 0 | 0 |
| moved | 2 | 0 | 0 |
| wraps | 1 | 0 | 0 |
| extra | 0 | 0 | 1 |
| **total** | **25** | **0** | **1** |

Fifteen of the twenty-five are `order`, and thirteen of those fifteen were decided for the
document by the eye - the row-banding blind spot (D-03) again, now the single largest claim
type in the ledger. The five documents it passed are the five the eye passed.

The unverifiable one is `moved:Directors' report` on the table of contents: the entry is two
lines in the render and one line in the PDF, so the needle is not a line on both sides. The
claim vocabulary has no form for a phrase that is a whole line on one side and a fragment on
the other, and this is the third run to want one.

`extra:DUE 10 September` was recorded by the eye on the invoice and **refuted** - 0 lines on
either side. It is not in this table's verified column because it was re-recorded as PASS once
the verifier had checked it. The refutation belongs here as a note: a red difference panel is
a rendering artefact, and reading one as a defect is the eye's failure mode on dense tables.

## g53 batch 3 (C 27-39), 8 Nov

23 findings: 22 verified, 0 refuted, 1 unverifiable.

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| order | 11 | 0 | 0 |
| pagecount | 4 | 0 | 0 |
| moved | 3 | 0 | 0 |
| wraps | 2 | 0 | 1 |
| overlap | 1 | 0 | 0 |
| shapes | 1 | 0 | 0 |
| **total** | **22** | **0** | **1** |

Eleven of the twenty-two are `order` again, and ten of those eleven are on pages the eye
passed - the row-banding blind spot, still the largest claim type in the ledger.

The unverifiable one is `wraps:Rate` on gst-invoice-with-qr-code: the header is one word in a
column too narrow for it, so the render sets it as "Rat" over "e" and the verifier cannot
follow a word that is not whole on the render side. The defect is real and visible, and the
document is FAIL anyway on a verified `order` finding, so nothing is left on that claim. This
is the second run to want a claim form for "a word the render breaks", which `wraps` almost
is: it needs the word to survive as a word before it can count the lines it takes.

## g53 batch 4 (the four C-group documents), 8 Nov 12:04

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| moved | 1 | 0 | 0 |
| order | 2 | 0 | 0 |
| **total** | **3** | **0** | **0** |

Three findings, three verified. `moved:M. Sathe` is the signature block 36.9 pt above the
rule the page drew it under. The two `order` findings are the row-banding blind spot again,
both on pages the eye passed - salary-slip-corporate's page is faithful and its order is
93.8 %, which is the D-03 class and not a defect.

## The D group (10 documents), 8 Nov

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| moved | 4 | 1 | 2 |
| wraps | 1 | 1 | 0 |
| pagecount | 2 | 0 | 0 |
| order | 4 | 0 | 0 |
| **total** | **11** | **2** | **2** |

`moved:Table 1. Metric weights and results (per cent)` was REFUTED at y=108.9 in the PDF
against y=108.6 in the render: the table itself did not move, only the prose around it. The
eye had listed it as part of the two-column complaint and the verifier was right to split it.
`wraps:Revision of trade prices for fasteners and fittings` was REFUTED - the PDF's own text
layer holds the line twice, so both sides count two lines. The document still fails on
`pagecount` and `order`, both verified, so nothing is left on that claim.

Two UNVERIFIABLE, both the same shape: the string is not on both sides as one string.
`SAHAYDRI ELECTRICALS PVT. LTD.` and `and a false boundary splits a paragraph that should
have continued` are each broken across lines on one side. That is the second run to want a
claim form for a phrase the render splits, and the second run where the measured `order`
finding on the same page carried the defect instead.


## v3 batch 2 (318-340, 15 documents), 8 Nov 09:36 run

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| moved | 1 | 0 | 0 |
| pagecount | 2 | 0 | 0 |
| shapes | 1 | 0 | 0 |
| order | 8 | 0 | 0 |
| **total** | **12** | **0** | **0** |

The first pass verified all twelve findings and nothing was refuted. Two of them were real
document defects and were fixed (see REMAINING-DEFECTS.md, batch 2). The other ten were the
`order` question on eight pages plus `shapes` on 332, and every one of them was a MEASUREMENT
bug: the eye passed all eight pages and was right. After the fix the second pass emitted seven
findings, all `order`, all verified, all measurement. That is nine `order` verifications in one
run with zero document defects behind them - the strongest signal yet that the order question
needs repair, not the pages.

The `shapes` finding on 332 (`15 shapes in the PDF, 0 in the render`) was true of the first
pass and gone after the fix, because the drawing's own shapes had been pushed onto a second
sheet by the flow overrun.


## v3 batch 4 (371-400, 15 documents), 8 Nov 12:36 run

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| order | 2 | 0 | 0 |
| moved | 4 | 0 | 0 |
| overlap | 1 | 0 | 0 |
| shapes | 0 | 1 | 0 |
| **total** | **7** | **1** | **0** |

The first pass emitted 14 findings from the eye's notes; five of them were the prose half of a
note, which is not a claim, and came back UNVERIFIABLE - my own wording error, not the tool's.
They were dropped and the notes reduced to claims only.

Two things this run found about the instruments:

    shapes    371_experience_certificate. The eye saw the seal's two circles gone and said
              `shapes`. Emitted as a visual claim it came back UNVERIFIABLE - check_visual has
              no shapes check - so the document's FAIL was left backed by nothing. verify.py
              has implemented `shapes` under check_measure all along; only the vocabulary was
              missing. looked.py now routes `shapes` and `order` to the measure checks, which
              is the "the claim vocabulary is missing something" cause in PIPELINE.md.

    shapes    371 again, and this one is a real disagreement between two tools. visual.py's
              charts question says "the PDF draws 2 shapes here and the docx draws none"
              because it drops rules and white rects before counting. verify.py's `shapes`
              check counts every drawing of 1.5 pt or more and answers "2 shapes in the PDF,
              2 in the render" - REFUTED. One word, two definitions. Until they agree, a
              shapes finding can be both true and refuted, and the document still fails on
              `order`, so nothing was fixed on it. Recorded in REMAINING-DEFECTS.md.

The `order` question failed on 2 of 15 pages. On 371 it is the seal's per-glyph arc text and on
400 it is the panels' text; both pages the eye also failed. That is the first batch where the
order question and the eye agreed on every page it fired on.

## 8 Nov 19:40 - one document re-checked, and the `moved:` check repaired

303_discharge_summary, one page, every step in order. Four findings: 2 verified, 1 refuted,
1 unverifiable.

The run found a hole in the verifier rather than in the page. `moved:<text>` compared the y of
the two lines and nothing else, so a line drawn 11.4 pt to the LEFT of where the page put it -
seven times the 1.5 pt x tolerance, and the very defect the eye had reported - came back REFUTED
with the note "2.8 pt apart". The check now compares both axes against the tolerances every gate
uses, x 1.5 and y 3.0, and reports both numbers. `moved:WARNING SIGNS` came back VERIFIED on the
re-run with x=28.0/16.6 and y=398.3/401.1, which is what the page actually shows.

    moved      verified 1   refuted 1   unverifiable 0     (the refuted one was the same claim
                                                            before the check was repaired)
    count      verified 0   refuted 1   unverifiable 0
    wraps      verified 0   refuted 0   unverifiable 1     "wraps:4 times a day" - the PDF has no
                                                            line STARTING there, only one containing it
    order      verified 1   refuted 0   unverifiable 0

`count:DISCHARGE SUMMARY` was refuted and correctly so: the words are present once on both sides.
What the eye saw in the title is the letter spacing, not missing text - the same reading the D
group recorded for 391's welded header. The claim type cannot express it, so it is not a defect
and nothing was fixed on it.

## 9 Nov - v3 batch 3, and what the refutations were telling us

20 verified, 1 refuted, 0 unverifiable over 21 findings. Two of the three refutations this run
were the same fault in the tool, and the third was the eye.

**`shapes` was a count, and a count cannot see a shape change size.** 352_certificate_ornate_border
draws two page-sized border rectangles and twelve corner curls; the render draws twelve curls and
no border. 12 against 12, so the check answered REFUTED while the frame was gone. 371's seal is two
rings of 84 x 84 and 74 x 74 pt; the render has two 16 x 9 pt blobs. 2 against 2, refuted again. The
check now classifies each shape by size as well - a shape covering more than a tenth of a per cent
of the page is a frame, a ring or a panel edge, not an ornament - and both findings came back
VERIFIED with the numbers that show it: 352 "8 large against 4 large", 371 "2 large against 0
large". This is the row the ledger has been asking for since 400 and 316: the check was wrong, not
the pages.

**`wraps:` refuted twice on 343, and the eye was wrong both times.** The eye read "1,144.00" as one
line on the page and two in the render. The page draws that cell as two spans that sit on one
baseline and look like one line; the render breaks it one character earlier. The claim cannot
express "one character", so it refutes. Recorded as an eye-instruction problem: a cell whose value
is split across spans looks whole to the eye.

**`count:Butter Naan` refuted, and the claim kind was wrong.** The word is on both sides; what the
eye actually saw was the whole BREADS & RICE block 149 pt above where the page puts it, because the
four menu groups are written as tables with a tighter row pitch. Re-recorded as `moved:Butter Naan`
and verified at 149.1 pt. `count:` answers "is it there", not "is it where it was".

**`moved:CONTACT US` came back UNVERIFIABLE on 401, and the claim was the wrong shape.** The eye saw
the rotated block 79 pt right of the page's x, but the render has lost the string: it is drawn past
the sheet edge and its text layer reads "CON", "Merid", "Surve", "leasin". A `moved:` claim needs the
needle on both sides, so it answered "not on both sides" - which is a `missing:` finding, and
`missing:CONTACT US` verified immediately (1 line in the PDF, 0 in the render). The lesson is the
one this file already carries: when the render has lost the text, the claim is `missing:`, not
`moved:`.

**373's lost bold is the emphasis gap this ledger already names, now measured.** 15 of 17 emphasised
lines on the page lost their weight. `visual.py` answers the question; no claim type can carry it, so
the document's FAIL rests on `rules`, which is the same cause seen a different way. Until `emphasis`
is a type, a page whose only defect is weight cannot be recorded as a defect at all.

### 9 Nov 02:05, b80 batch 1 (20 documents) - what this run added

34 findings: `rotated:` 9 verified (new type), `moved:` 9 verified and 1 unverifiable (05's seal, drawn
per glyph on both sides so no line exists to measure), `order` 14 verified, `shapes` 1 refuted (12 page 2:
2 shapes on both sides, 2 large on both sides - the question, not the page).

**The unverifiable one is a vocabulary gap, named rather than dropped.** 05_round_company_seal_curved_text
draws its arc one glyph per position, so the PDF's own text layer has no line for the verifier to compare.
`rotated:` cannot fire either, for the same reason. The eye sees the arc land across the body 600 pt above
the seal and there is no claim that can carry it; the document's FAIL rests on the eye alone and is recorded
as such. The fix would be a check that compares glyph positions, not lines.

**`order` disagreed with the eye twice more, the same way as before.** 11 (88.4 % of 21 rows) and 12
(97.9 % of 23, 82.4 % of 16) both pass on sight; both pages draw each table cell as its own line and the
render joins a row's cells, so the row counts cannot match. Fourth and fifth occurrences of the same
blind spot.

**A page count the eye got wrong.** 20 was recorded FAIL on `pagecount` - the side-by-side sheet appeared
to show two footers - and the verifier answered REFUTED, "both have 1 pages". PyMuPDF agrees: one page,
one footer at y=831. The eye was reading the second panel's label as a second page. The FAIL stands on
`moved:2.` (12.4 pt) instead, which is the real defect.


## 9 Nov, 03:07 IST - b80 batch 2 (21-40)

11 findings: 9 verified, 2 refuted, 0 unverifiable.

| claim type | verified | refuted | unverifiable |
|---|---|---|---|
| `moved:` | 2 | 0 | 0 |
| `wraps:` | 1 | 0 | 0 |
| `count:` | 1 | 0 | 0 |
| `missing:` | 0 | 1 | 0 |
| `overlap` | 0 | 1 | 0 |
| `order` (measure) | 5 | 0 | 0 |

The two refuted are both 28_value_overflows_cell_txtpos, and both were the eye reading a
description that overruns its cell as a lost value. `missing:Nos` answered "2 line(s) in the
PDF, 2 in the render" and `overlap` answered "4 overlapping pairs in the PDF, 0 in the render"
- the page overlaps and the render does not. Neither was fixed, and the document's FAIL rests
on the verified `order` instead. That is the ledger doing its job: an eye finding that the PDF
contradicts is not a defect.

`count:` earned its place on 38. `wraps:` and `breaks:` both came back REFUTED there because
the PDF holds the line twice (faux bold) and the line-count comparison saw 2 on both sides;
`count:` names the real difference, 2 against 1.

## 9 Nov 05:03 IST — b80 batch 3 (41-60)

19 findings emitted, 15 verified, 1 refuted, 3 unverifiable. Added to the table by claim type:
moved: +7 verified, +2 unverifiable; shapes: +1 verified, +1 refuted; missing: +1 unverifiable;
order: +7 verified.

The two unverifiable `moved:` claims are the same blind spot twice: 57.3 on 46 is a value label
the render drops or merges, so the string is on one side only, and Compacted sludge bed on 59
is a table cell whose words the render joins with the cell beside it. Both are the cell-versus-
line difference already recorded four times, and neither is a document defect.

The unverifiable `missing:` is the seal's arc text on 60 - one glyph per position on the page,
so no line spells KENGERI CAMPUS on either side. That is the vocabulary's gap, not the page's:
an arc-text claim would need to compare glyph positions, which is what `rotated:` does for a
single slanted line and does not do for a ring.

## 9 Nov 06:05 IST — v3 batch 1 (300-317), third pass

15 findings emitted, 13 verified, 2 refuted, 0 unverifiable. By claim type: `moved:` +5
verified, +2 refuted; `breaks:` +1 verified; `missing:` +1 verified; `order:` +6 verified.

Both refuted claims are the same mistake on the eye's side: the claim named a string that the
page holds twice. `moved:NATIONAL IMMUNISATION` on 305 was answered against the title line
NATIONAL IMMUNISATION REGISTRY at y=33.1, where the render is 0.5 pt off - the eye meant the
seal's arc text, which no line spells. `moved:REFERRED BY` on 301 was a re-measure of an 8.0 pt
finding from 8 Nov and came back 0.5 pt apart on both axes: that finding was a false alarm on
the previous pass and is now refuted, which is the ledger earning its keep.

The `order` finding on 312 is verified (63.8 % of 34 rows) while the eye passed the page. That is
the tab-joined-rows measurement bug recorded on 8 Nov, not a document defect: the eye decides and
the document is PASS, and the row here is the repair ticket for the tool.


## 9 Nov 07:20 IST — v3 318-340, first pass

21 findings emitted, 21 verified, 0 refuted, 0 unverifiable. By claim type: `moved:` +10
verified (nine of them the same table offset), `count:` +4 verified, `order:` +6 verified.

One claim was refuted and then reworded, and the reword is the lesson. `missing:INDIA` on 318
came back REFUTED - "1 line in the PDF, 1 in the render" - because the seal's words are all
there; the verifier was right and the eye had named the wrong fault. The arc glyphs are drawn
on the page at x=90 to x=140, y=490 to y=528 where the PDF puts them at x=446 to x=496, y=300
to y=335: nothing is missing, everything is 160 pt away. `moved:B` says that and verified at
160.5 pt. A ring of per-glyph text still has no claim that describes it, and `moved:<first
glyph>` is a poor stand-in - it is the fourth time the arc-text vocabulary gap has cost a
finding.

The three `order` findings on 325, 326 and 330 are verified while the eye passed the page.
All three are the tab-joined-rows measurement bug: a row of table cells reads as one string in
the render and as separate strings in the PDF, so the sequence never matches. The eye decides,
the documents are PASS, and these rows are the repair ticket for the tool.


## 9 Nov 08:08 IST — v3 341-370, re-run from the start

16 pages, 16 findings emitted, 14 verified, 1 refuted, 0 unverifiable after the record was
corrected mid-run. By claim type: `order:` +8 verified, `rules:` +2 verified, `pagecount:` +2
verified (the same document, both pages), `moved:` +1 verified, `wraps:` +1 verified, `shapes:`
+1 REFUTED.

The `shapes` refutation is the eye's mistake and it is worth writing down. 352's ornate border
was claimed gone on the strength of the 120 dpi side-by-side panel; the verifier answered
"12 shapes in the PDF, 12 in the render, 8 large on both sides" and a 300 dpi crop of the
top-left corner shows the outer rule, the inner rule and the corner curl identical on both
sides. The panel is a third of a page wide - a 2.5 pt rule and a 6 pt curl cannot be judged in
it. That is the second time this run's eye has been wrong about a fine detail (the first was
350's page count, where the eye believed the PDF's own footer text "PDF page 1 of 2" instead of
counting the pages). Both were caught because the claim was structured and the verifier went to
the page.

`rules` is now the highest-value claim type in the batch: it is the only one that can say "the
render draws a line the page does not", and it caught 351 and 360, two documents whose text is
perfect. Both are `nil`-side regressions - the writer borders a table the page leaves open - and
the frame guard that was supposed to prevent exactly this is documented as excluding 351 and 360
by name while doing no such thing today.

The three `order` findings on 353, 364 and 370 are verified while the eye passed the page, and
`--combine` decided all three on the eye. They are the band-join measurement: a render row that
holds two of the page's lines in one band, or a rotated edge text joining the row it sits beside.
Repair ticket for the tool, not a defect in the documents.
