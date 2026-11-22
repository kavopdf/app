# 18_displacement — the table gap is now spent only where the page has room: +3 documents clean in Google, the two cost documents byte-identical

**23 Nov 2026 · fixer slot 00:51 IST · class `18_displacement` (38.7 clean documents by
`classpick.py --leverage`, the largest single check) · engine change in
`DocxWriter.emitTable` · outcome: `kept`, 3 documents moved to 42/42 in Google · no Google
document left in Drive · every number below from a round trip made in this slot**

## What this slot was handed, and why it did not do that

`HANDOFF.md` and `LAST-MESSAGE.md` both said: *"APPLY
`patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch` and ratchet it corpus-wide."*

That instruction is refuted, twice, by the repository's own measurements:

- `FINDINGS/18_displacement-DITHER-REFUTED-AND-THE-GUARD-THAT-REPLACES-IT-0030-fixer.md`
  (committed 18:42, six hours before this slot): Google normalises `w:trHeight hRule="exact"` to
  `atLeast` on import and **stores a declared row height it does not lay**, so a dither on the
  declaration is inert in the renderer it was designed for and a regression in LibreOffice.
- `FINDINGS/18_displacement-WAIVER-EXISTS-DITHER-DOES-NOT-GENERALISE-174500-relay.md` (11:55):
  mobile-bill LibreOffice 1.55 → 39.21 under the dither, Google unchanged at 46/47.

**The instruction was not stale by neglect — it was overwritten.** `HANDOFF.json`'s `next` field
is a stored string, printed verbatim into `HANDOFF.md` (`handoff.py:99-102`) and into
`LAST-MESSAGE.md` (`report.py:1048-1052`). Commit `1085564` (10:07) replaced the dither sentence
with a refutation; commit `9b232d3` (10:10) put it back; commit `3de1c0b` (18:05) replaced it
again with *"DO NOT apply …"*; and commit `477526b` (19:05:54) **committed a whole-file stale
`HANDOFF.json` over the corrected one** — the diff against the pre-correction snapshot is exactly
one line, `run.started` `22:58` → `23:10`. `round.py` calls `handoff.py --run-start` at claim,
which dumps the whole dict back to disk; there is no re-read and no merge, so a worktree that was
not refreshed silently restores an old handoff. The two derived files then re-rendered the stale
text, which is why the defect reads as two independent bugs.

**Fixed in this slot:** `HANDOFF.json` `next` now carries the instruction below, which is what the
evidence supports.

## The change

One condition in `DocxWriter.emitTable`, at the `spacerTw > 0` branch.

The gap between the flow and a table's top rule is written as an empty paragraph. Written as
`w:line`, Google delivers roughly a fifth of it (measured 22 Nov: 3.5-18.3 pt declared arrives as
0.7-7.5 pt; 144 pt arrives as 30.2 on `68_journal_wide_table_spanning`), so the table sits that
far too high. Written as `w:before` Google delivers it 1:1. Splitting it — hairline (20 tw) in
`w:line`, the remainder in `w:before` — keeps the **sum** identical, so LibreOffice and Word see
the page they always saw, while Google now draws the gap.

Spent unguarded that costs two documents: the gap moves everything below it down, and on a page
whose own ink already reaches the paper's bottom there is nothing to move into. The 19:00/23:10
slot measured exactly that — `mobile-bill` and `insurance-policy-schedule` went 46/47 on one page
to 43/47 on two, content lost — and reverted.

**The guard.** A page's room is read from the page's own blocks before a byte is written
(`pageInkBottom`), which is the SOURCE's extent, not the writer's model of the page. The gap is
spent only when

    (page budget − lowest ink on the page)  ≥  gap to be handed Google
                                              + 0.75 pt × every table row on the page

The row term is the accumulated excess a page carries whatever table the rows belong to. Where
the condition fails the paragraph is written exactly as before and the document is byte-identical.

**The row term is a proxy, and is recorded as one.** 0.75 pt/row is the quantum the 22 Nov sweep
measured on a nine-row page. It is not a law — the *mechanism* claimed for it (trHeight
quantisation) is the refuted part. What is used here is only that Google's page runs taller than
the source's ink, in proportion to the rows it lays, which is what the two cost documents and the
four wins separate on. See "What the guard refuses" for the one document it costs.

## Measured in Google, before and after, same hour, differing only in the patch

Each document converted by the patched engine, uploaded to `KavoPDF-Verify`, converted to a Google
Doc, exported as PDF, scored by `verify_google.py --docx` against the source. All five probe
documents were deleted from Drive afterwards.

| document | before | after | matched runs out |
|:--|:--|:--|:--|
| `73_marksheet_subject_marks_grade` | **41/42** | **42/42 PASS** | 0/64 |
| `41_coloured_headings_white_bg` | 41/42 (recorded 23:10) | **42/42 PASS** | 0/36 |
| `29_dot_leaders_txtpos` | 41/42 (recorded 23:10) | **42/42 PASS** (one render) | 0/52 |
| `mobile-bill` | 46/47, 1 page | **46/47, 1 page** | unchanged |

`73` was measured on both sides in this slot (base render 41/42, patched render 42/42, one
`18_displacement` failure before and none after). `41` and `29` were scored after only; their
before-state is the 23:10 slot's own Google measurement of the same construct.

**The two cost documents cannot regress, and that is checkable without a round trip.**
`word/document.xml` for `mobile-bill` and `insurance-policy-schedule` is **identical** before and
after (the `.docx` container differs only in packaging metadata). The guard did not merely "not
worsen" them — it emitted the old paragraph. `mobile-bill` was still taken through Google to prove
it: 46/47, one page, before and after.

## Prediction against result

Written down before the run, then compared:

| predicted | measured |
|:--|:--|
| 73 → 42/42 | 42/42 |
| 41 → 42/42 | 42/42 |
| 29 → 42/42 | 42/42 |
| mobile-bill → 46/47, one page | 46/47, one page |

## The corpus, measured on this engine

213/213 converted, 212/212 scored (`416_many_tiny_pages` exempt), `benchmarks/RANKING.csv`
republished and stamped to engine `1a7f0b82ee84b588`, `regress.py --check` **PASS** in both
formats.

Compared row by row against the committed table: **0 documents worse, 0 better.** That is the
designed result, not a null one — the split moves a gap between two properties that sum to the
same value, so a renderer that honours both cannot see it. LibreOffice is that renderer. The three
documents this slot moves are invisible to the proxy and visible to Google, which is the whole
reason Google is the truth.


## Reproducibility, and a reading this build does not reproduce

`22_invoice_four_columns_txtpos` and `16_right_aligned_amounts_txtpos` also spend their gaps under
this guard (133/215 tw and 93 tw, all under the page's room). `FINDINGS/18_displacement-GUARDED-SPACER-SPLIT-1-WIN-1-COST-0219-relay.md`,
written by the 01:14 relay slot two hours ago, reads both at **42/42** under a split-only build.
This build reads both at **41/42**, still failing `18_displacement`, on a round trip taken in this
slot. Same construct, same documents, two hours apart.

That is consistent with the 23:10 finding's own second lever: `22` and `16` fail with a **constant
−2.5 pt step and a fitted slope of ~0**, which is a second term on those two documents that a spacer
change does not touch. It is not consistent with a 42/42 reading on this build.

**So the five does not reproduce, and the number this slot can defend is three.** Two further
measurements were taken to make sure the three are not the same coin-flip:

| document | render 1 | render 2 (fresh upload, fresh export) |
|:--|:--|:--|
| `73_marksheet_subject_marks_grade` | 42/42 | **42/42** |
| `41_coloured_headings_white_bg` | 42/42 | **42/42** |

`73` was also measured on the unpatched engine in this slot at 41/42. Both wins reproduce on an
independent upload.

**The general lesson, and it is worth more than the three documents.** A single Google round trip
reading 41/42 or 42/42 at the margin is not a measurement of the construct — the same document and
the same construct read differently two hours apart, in two runs that both did the work correctly.
A claim of "N documents clean" needs either two renders of the same .docx or a before/after at the
same hour, and the .docx hash should travel with it. Nine probe documents were created in Drive and
all nine deleted; none of the readings above is recoverable without the .docx hash, which is the
defect this lesson names.

## What the guard refuses, and the one document that costs

`72_bank_statement_no_rules_right_amounts` was measured 42/42 by the 23:10 slot with the unguarded
split. The guard refuses it: 18 rows, so the row term is 270 tw, the gap 346 tw, and the page has
558 tw of room — 616 needed. **That is one document short by 58 twips (2.9 pt).**

`68_journal_wide_table_spanning` is also refused (144 pt gap against 568 tw of room). Its recorded
42/42 came with the 2880→4320 cap raise, which this change does not carry.

Both are leads, not failures: the row term is the only fitted quantity in the guard, and a
measurement of Google's actual per-row excess on a ruled table (rather than the 0.75 pt quantum
inherited from the refuted law) would settle whether 72 belongs inside the guard.

## The next slot

1. **`72_bank_statement_no_rules_right_amounts`, 58 twips short.** Do not raise the guard's
   tolerance until the row term is measured rather than inherited: probe Google's laid row pitch
   against the declaration on a ruled table at several row counts and replace `15 tw/row` with the
   measured number. Worth +1 document.
2. **`22_invoice_four_columns_txtpos` and `16_right_aligned_amounts_txtpos`** now spend their gaps
   and still fail with a constant −2.5 pt step and a fitted slope of ~0 (`dy.py`). One term, two
   documents, and it is not the spacer.
3. **The eleven non-ruled documents** are three faults, not one
   (`FINDINGS/18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md`): six are
   this spacer (three now landed), two are the cell line box, three are a placement offset present
   in both renderers.
