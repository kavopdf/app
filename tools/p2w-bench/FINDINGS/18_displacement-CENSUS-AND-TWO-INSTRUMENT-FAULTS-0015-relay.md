# 18_displacement — the population the spacer split can reach, and two instrument faults that were starving every run

**23 Nov 2026 · relay slot 02:13 → running IST**

## 1. The construct is already on main, and this slot's patch was a duplicate

Main (ef99cb2c) already spends the spacer gap as `w:before` with a one-twip `w:line` hairline,
guarded by "the page has room" — the source's lowest ink must leave the gap plus the row excess the
table will incur. This slot independently built the same split from the 01:14 slot's handover patch
(`...SPACER-BEFORE-GUARDED-NO-DITHER.patch`) and measured it across all 213 documents before
discovering the collision at the rebase. **The patch was dropped, not merged.** Main's guard is the
better one: it reasons about the page's remaining room, which is the failure I could only see
empirically, and its hairline law (0.2156 pt delivered at L=20) is measured.

What the duplicate measurement still established, and main does not record:

| document | committed | nil-border guard only | + measured-only gap | + no shape on the page |
|:--|--:|--:|--:|--:|
| 363_warranty_card | 10.58 | 11.13 | 11.13 | **10.58** |
| price-list-right-aligned-amounts | 1.79 | 1.90 | 1.90 | **1.79** |
| gst-invoice-3line-items | 0.54 | 0.56 | 0.56 | **0.54** |
| 03_stamp_vertical_90deg | 16.98 | 17.50 | 17.50 | **16.98** |
| 29_dot_leaders_txtpos | 0.00 | 0.00 | 0.00 | 0.00 |
| 41_coloured_headings_white_bg | 0.00 | 0.00 | 0.00 | 0.00 |
| 73_marksheet_subject_marks_grade | 0.00 | 0.00 | 0.00 | 0.00 |
| 22_invoice_four_columns_txtpos | 0.00 | 0.00 | 0.00 | 0.00 |
| 16_right_aligned_amounts_txtpos | 0.00 | 0.00 | 0.00 | 0.00 |
| 72_bank_statement_no_rules_right_amounts | 0.00 | 0.00 | 0.00 | 0.00 |

Three of the four costs disappear when the gap is spent only where it was **measured** from the
page's own flow position (the D-26 absolute branch) rather than estimated from the substitute face's
baseline arithmetic. The fourth, 03_stamp_vertical_90deg, survives that and dies under "no floating
shape on the page": its two spacers dump as `measured=true, gap=165/194 twips, bandClear=true` with
**23 shapes on the page**, none on the gap band. A page that carries floating ink anywhere can anchor
that ink to the flow position the spacer moves. All six documents the split fixes carry no shape on
their page. **If main's room-guard ever needs a second clause, this is the one that is measured.**

## 2. The split is invisible to LibreOffice, so the proxy can neither justify nor refute it

Same documents, same corpus, unpatched engine vs patched:

| document | unpatched | patched |
|:--|--:|--:|
| insurance-policy-schedule | 0.53 | 0.53 |
| 29_dot_leaders_txtpos | 0.00 | 0.00 |

`RANKING.csv` does not move. The 01:14 slot's Google measurement (5 of 8 documents to 42/42, none
worse) is the only evidence this class has ever produced, and it is the evidence that counts. A
construct whose effect is invisible to the proxy has to be landed on a Google measurement plus a
proxy that shows no cost — never on a proxy improvement that is not there.

## 3. `_soffice_warm()` never built the profile, and that is why runs measured nothing

`gate.py` reported `measured 0 of 212` and `pre/` stayed empty while 213 .docx existed. The warm-up
runs `soffice.bin --version`, which short-circuits **before** the profile is initialised. On a fresh
pod the first *document* launch then exits 81 with no PDF and no diagnostic at all.

Three experiments, each from a clean `HOME`, through the real `soffice_pdf()` path on a 12-docx chunk:

| clean HOME | setup | profile after warm-up | first convert |
|:--|:--|:--|:--|
| /scratch/work/h1 | none | **absent** (only an empty `.config`) | rc=81, no PDF |
| /scratch/work/h2 | `mkdir -p $HOME/.config/libreoffice/4` | created by hand | rc=81, no PDF |
| /scratch/work/h3 | `--version` twice | **absent** | rc=81, no PDF |
| — | `--headless --norestore --terminate_after_init` | **fully populated, 0.6 s** | **rc=0, PDF** |

`mkdir` alone fixes nothing. **Fixed this slot** in `benchmarks/p2w.py`: the warm-up now runs
`--headless --norestore --terminate_after_init`. This is the gate, not a construct: four runs that
stood aside reading "measured 0" were not blocked by policy, they were blocked by this.

## 4. The engine stamp describes the wrong tree, and wipes the corpus it just built

`_engine_stamp()` hashes `ENGINE_SRC`, but `_invalidate_if_engine_changed()` is called on a path where
`ENGINE_SRC` resolved to `/scratch/work/p2w/repo` while the measurement was of `P2W_ENGINE_SRC`. The
stamp written therefore describes a different tree, the next call reads the real one, sees a different
hash and `rm -rf`s `DOCX`, `DIST` and `PRE`. It cost this slot two full reconversions — 40 minutes of
213-document conversion — and it is the mechanical reason a local tree's patch could not be measured
twice in a row. **Not fixed**: what the stamp should describe (the tree measured, or the commit
measured) is a decision, not a typo. Worked around by writing the stamp by hand before each
measurement pass.

## 5. The population, so the next run does not have to recount it

Census over all 213 documents, instrumenting the writer at the exact statement the gate reads
(harness: `SpacerCensus.java` + `instrument.py`, delivered with the slot's evidence):

    reachable (nil-border table, gap <= 20 pt)      50
    of those, failing Google                        46
    of those, exactly one check short, and it is    9
      18_displacement
    of those, already 42/42 (must not break)         1   (74_balance_sheet_indented_subitems)
    not Google-scored (page_count_refused)           3

The nine one-check-away documents, with the qualifying gap each carries:

    16_right_aligned_amounts_txtpos      4.65 pt     73_marksheet_subject_marks_grade     16.70
    22_invoice_four_columns_txtpos       6.65        72_bank_statement_no_rules_right     18.30
    29_dot_leaders_txtpos               15.85        362_price_list_dense                 15.20
    41_coloured_headings_white_bg        3.45        balance-sheet-two-columns-of-figures 12.60
                                                       bus-timetable-station-left-right      6.35

Six of those nine are already at 42/42 in Google under the split-only build the 01:14 slot measured
(29_dot_leaders, 41_coloured, 73_marksheet, 22_invoice, 16_right and — at 41/42, unchanged —
72_bank). The other three were never measured in Google. **That is the open lead: three documents,
one Google round trip each, on a construct that is now committed.**
