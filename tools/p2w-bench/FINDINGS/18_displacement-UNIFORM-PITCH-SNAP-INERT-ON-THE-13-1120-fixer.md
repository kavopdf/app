# The uniform-pitch snap rewrites the rows on 11 of the 13 sole-failure documents and clears `18_displacement` on none of them

**24 Nov 2026, fixer slot 16:00 IST.** Two Google measurements, plus a structural census of all 13.
The patch is `FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`. **Not landed, and the reason
is now a result rather than a cost: the construct is inert on the documents it was aimed at.**

## What was believed

`18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md` ranks `18_displacement` first because it is the sole
failing check in 13 documents, and `18_displacement-UNIFORM-PITCH-GUARD-GOOGLE-42of42-0450-fixer.md`
measured the guard at **42/42 on `362_price_list_dense`**. The standing instruction in `HANDOFF.md` was
therefore: apply the patch, run the 212-document pass, expect the 13.

## What is measured

The patch was applied and the engine built (`build-engine.sh`, 38-48 s). Each of the 13 sole-failure
documents was converted twice — once on the patched tree, once on the unpatched tree, one JVM per document
— and the two `word/document.xml` compared, together with every `w:trHeight/@w:val`.

| document | `w:trHeight` rows | rows whose value the guard rewrote | `document.xml` |
|:--|--:|--:|:--|
| `16_right_aligned_amounts_txtpos` | 13 | 12 | changed |
| `31_times_body_arial_headings` | 0 | 0 | **identical** (no table) |
| `36_embedded_subset_font` | 7 | 6 | changed |
| `68_journal_wide_table_spanning` | 7 | 6 | changed |
| `71_invoice_space_aligned_no_rules` | 14 | 3 | changed |
| `72_bank_statement_no_rules_right_amounts` | 18 | 17 | changed |
| `74_balance_sheet_indented_subitems` | 10 | 9 | changed |
| `balance-sheet-two-columns-of-figures` | 16 | 10 | changed |
| `bus-timetable-station-left-times-right` | 33 | 33 | changed |
| `insurance-policy-schedule` | 22 | 5 | changed |
| `mobile-bill` | 24 | 8 | changed |
| `table-with-no-header-row` | 26 | 11 | changed |
| `two-tables-stacked-with-no-gap` | 13 | 0 | **identical** |

So the guard admits the table on **11 of 13** — it is not being skipped. `31_times_body_arial_headings`
has no table at all, and `two-tables-stacked-with-no-gap` has a pitch the guard does not classify as
uniform.

## The two documents that were carried through Google

Each `.docx` was uploaded to the `KavoPDF-Verify` folder, converted to a Google Doc, exported as PDF and
scored with `gverify.py --collect`. Both Docs were deleted after scoring; the folder is empty.

| document | rows rewritten | before | after Google |
|:--|--:|:--|:--|
| `72_bank_statement_no_rules_right_amounts` | 17 of 18 | 41/42, fails `18_displacement` | **41/42, fails `18_displacement`** |
| `bus-timetable-station-left-times-right` | 33 of 33 | 41/42, fails `18_displacement` | **41/42, fails `18_displacement`** |

The most-favourable probe was chosen deliberately: `bus-timetable-station-left-times-right` has every one
of its 33 row heights rewritten, so if whole-pixel snapping were the mechanism behind this document's
displacement it would have to show. It does not move, and neither does the bank statement.

**Documents moved by this attempt: 0 of 13.**

## What this rules out, and what it does not

* It does **not** refute the 42/42 on `362_price_list_dense`. That document is a 29-row price list with one
  repeated fractional pitch; these are different tables with different row structures, and the guard can be
  right about one and useless for the other.
* It **does** refute the inference that `18_displacement` on the 13 sole-failure documents is the same
  construct as on `362`. Rewriting their row heights to whole pixels changes the row grid and leaves the
  check failing, so whatever `18_displacement` is measuring on these documents is **not** the row pitch.
* **Do not spend a corpus pass on the uniform-pitch patch for these 13.** A full `--force` pass is ~38 min
  of conversion plus ~15-20 min of measurement (measured: `18_displacement-FULL-PASS-DOES-NOT-FIT-A-SLOT-0650-fixer.md`,
  `pass-cost-1.05-CORES-AND-ONE-SHARED-DEADLINE-2400-fixer.md`), and this run has now measured, in the
  renderer that counts, that the pass would buy zero documents.

## The instrument fault that made this run expensive

`screen.py --docs <13>` was tried first, because it is the tool designed for exactly this question. It
converted all 7 documents and then **stopped inside `prerender 7 docx in soffice batches of 12`** on two
consecutive 280-second calls. This is the same pod-level soffice fault recorded in
`INSTRUMENT-soffice-bin-silently-converts-nothing-on-a-fresh-pod-1200-fixer.md`: the LibreOffice proxy is
not available on a fresh pod, so `screen.py` cannot return a verdict at all. The Google path was used
instead, and it cost about four minutes per document — affordable for two probes, not for thirteen.

**The consequence for the next run: `screen.py` cannot be trusted to answer a screening question on a
fresh pod until the soffice fault is fixed or the prerender is made optional.** The Google path is the only
one that returns a number.

## Reproduce

    bash tools/p2w-bench/corpus-fetch.sh                       # 213 PDFs, 16 s
    git apply tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch
    bash tools/p2w-bench/build-engine.sh
    # convert the 13 one JVM per document, then diff word/document.xml against the unpatched build
    # for the Google half: gverify.py --stage / upload / CREATE_FILE / EXPORT / --collect
