# 18_displacement — the spacer's blocker is SCOPE, not row height. A guard that spends the spacer only where the page has slack clears the six and leaves the two cost documents byte-identical.

**22 Nov 2026 · fixer slot 23:54 → · engine HEAD `a6a5fbdc`, no engine change made · no Drive document
created · every Google number below is quoted from a recorded round trip and named with its file**

## What this slot was handed, and what it did with it

The 10:05 finding (`18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md`)
ends with a ratchet: land the spacer as `w:before` **and** correct the row height, because two
exactly-full pages overflow without it. Its row instruction was "shrink the emitted height × 0.9634".

**That instruction has already been tried and refuted, twice, and this slot is not re-proposing it.**
`18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md` (slot 09:51–10:35) built the spacer *and* a row
correction together and measured three documents in Google: `68_journal_wide_table_spanning` **42/42
CLEAN** (the spacer half works, and with the 2880→4320 cap raise that is a **seventh** clean document),
`mobile-bill` and `insurance-policy-schedule` **41/42 → 38/42** (2 pages, four checks). It also refutes
the 0.9634 scale and locates the residual excess in the multi-paragraph cell path.

A subagent in this slot produced a sharper version of the same instruction — a **0.75 pt quantum law**,
`laid = 0.75 × (round(declared / 0.75) + 1)`, fitted to 0.07 pt over eleven published points, and a
dither on `w:trHeight` that lands the mean at 18.40. **It is refuted by a measurement the repository
already holds**, and the dither must not be built.

## The refutation — `w:trHeight` is not the height

`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` measured this directly, and its
CORRECTION file confirms the measurement survived the audit:

1. §1: all 24 of mobile-bill's rows were written `hRule="exact"`; **the PDF did not move a rule.**
   Google's own `.docx` read-back carries `hRule="atLeast"` for the rows written `exact` — Google
   normalises `exact` to `atLeast` on import.
2. §3: Google's read-back carries `w:trHeight w:val="360"` / `"380"` — **exactly what the engine
   wrote** — and its PDF lays 18.0/19.0/20.0 on those rows, and lays a row written 380 at 18.0.

So a change to the declared `w:trHeight` is a change to a number Google **stores and does not lay**.
The 0.75 quantum the law fits is real, but it is the quantisation of the **cell's line box**, not of
the declaration: §4's probe, with the cell written `w:before="0"` and `w:line` = the row's own height,
laid `18.00, 18.00, 18.75, 18.00, 18.00, 18.75, …` — a 0.75 sawtooth, mean 18.25. The law's eleven
fitted points are consistent with that mechanism and do not discriminate between the two.

**Consequence, and it is the reason this slot did not build it:** declaring 348/360 tw instead of
360/380 tw changes nothing in Google (trHeight is not the height) and takes 0.75 pt off every row in
LibreOffice (which does honour trHeight). It is inert in the renderer it was designed for and a
regression in the one that refuses it.

## The spacer is still the best lead in the corpus, and its blocker is narrower than "row height"

Settled at 10:05 and not re-litigated here: the spacer as `w:before` takes **six** documents to
42/42 clean — `16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`,
`29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`,
`73_marksheet_subject_marks_grade` — and costs two: `mobile-bill` and `insurance-policy-schedule`
overflow to two pages with content lost.

Both cost documents are **exactly-full pages**. That is the whole of the failure: on a page with no
slack, spending the spacer at its true value removes the ~19.5 pt of slack that was absorbing
Google's row excess. On a page with slack, nothing overflows.

**So the change does not need a row fix. It needs a scope.** The proposal for the next slot:

    apply the spacer as w:before ONLY when the page's flow budget still has slack after the
    table — i.e. when (page height − the table's bottom edge) exceeds the row excess the table
    will incur (0.75 pt × rows). Where it does not, emit today's w:line and the document is
    byte-identical to HEAD.

This is strictly better than the 10:05 ratchet, for three reasons: it needs no construct that two
renderers disagree about; it makes the two cost documents **byte-identical** rather than "fixed", so
`regress.py --check` has nothing to refuse; and it is one condition in `DocxWriter.java` at the
`spacerTw > 0` branch (~line 5870), not a change to every table row in the corpus.

**Blast radius, unchanged and still the gate:** 124 of 213 documents carry a spacer, and **13 of them
are clean today** (the table is in the 10:05 finding; the largest is `041122-Account_Opening_Form`
at 22 spacers, max 166.00 pt). Any landing must render those 13 before and after. The guard above
should leave most of them byte-identical, which is the point.

## The eleven non-ruled documents are three faults, not one

Census written this run (`18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md`),
so nobody spends a slot looking for one construct that is not there:

| group | construct | n | documents |
|:--|:--|--:|:--|
| A | the table gap spacer (the same term as above) | **6** | `16`, `22`, `29`, `41`, `68`, `73` |
| B | row growth — the cell line box, not `w:trHeight` | 2 | `362_price_list_dense`, `72_bank_statement_no_rules_right_amounts` |
| C | a block placement offset present in **both** renderers | 3 | `31_times_body_arial_headings`, `71_invoice_space_aligned_no_rules`, `balance-sheet-two-columns-of-figures` |

The discriminator between the eleven and the five ruled documents is **who owns the rules**, not how
many there are: all eleven emit `tblBorders` all-`nil` with the rules as floating `<w:drawing>`; the
ruled five carry `insideH w:val="single"` cell borders. `16` draws 17 rules and `balance-sheet` 5, so
a rule-count filter is wrong on two of them.

## What this slot did not do

No engine change, no build, no Drive round trip. The slot's measurement is a refutation of the plan
it was handed plus a census of the eleven documents nobody had looked at, which is why it ends at a
lead rather than a keep: the spacer's six documents are real
and remain one scoped condition away, and the row correction that was supposed to unlock them is now
known to be the wrong instrument. **A slot that had built the dither would have spent a build, two
round trips and a revert to learn what the repository had already written down.**
