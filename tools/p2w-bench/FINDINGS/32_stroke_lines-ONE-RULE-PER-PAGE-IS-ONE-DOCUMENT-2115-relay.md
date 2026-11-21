# The single carrier is worth ONE document; the class is 31 documents that need rows

**21 Nov 2026 · relay slot 21:11 · measured on the full 213-document corpus, locally, in this sandbox**

## The answer, first

The floating-table carrier that two runs have now proved (`rule-carrier-tblppr-2008.patch`, measured
41/42 -> 42/42 on `394_map_with_legend`) is **worth at most one document** of the 192 Google scores,
and **landing it as it stands would put rules at the wrong y on 146 documents**.

Of the 32 documents that fail only `05_chars_extra`, `18_displacement`, `32_stroke_lines` — the whole
reachable ceiling of this class — **31 have two or more rules on at least one page**. One
(`334_patent_document`) has a single rule. The carrier places exactly one floating table per page; the
second and every later one stack under the first, which was measured on `73_marksheet` last slot
(`32_stroke_lines-FLOATING-CARRIER-DRAWS-BUT-STACKS-2050-f1x.md`).

So the one-table-per-page-with-rows construct is not an optimisation of the lead. It is the
precondition for the lead to be worth anything. Until it exists, the class is one document wide and
its own patch is a regression on the other 146.

## The census

Every one of the 213 corpus PDFs, every page, read with the instrument's own rule definition —
`verify_google._rules(page)`: thin face <= `RULE_THIN` 4.0 pt, long face >= `RULE_LONG` 10 pt, and
**isolated** (not touching another segment within `RULE_GAP` 3 pt). Not a re-implementation: the
module the 42 checks use, imported and called.

| | |
|:--|--:|
| Documents in the corpus | 213 |
| **No rule on any page** — the carrier cannot change one byte of these | **53** |
| Documents with at least one rule | 160 |
| … whose busiest page holds **at most one** rule | **14** |
| … whose busiest page holds **two or more** rules | **146** |
| Rules counted across the corpus | 1170 |

This is a lower bound on the documents the engine's carrier can touch, not an upper one: the engine's
predicate (`isRuleShape`, `RULE_MAX_PT` 4.0) does not require isolation, so it fires on the rules that
sit inside boxes as well as the isolated ones this census counts.

## Crossed with the committed Google results

`benchmarks/gverify/*.json`, 213 files, 192 scored, 6 clean.

| failing set | documents |
|:--|--:|
| exactly `05, 18, 32` | 15 |
| exactly `05, 32` | 15 |
| `05, 18, 32` + one more (`59_shape_anchor` / `60_text_column_right_edge` / `25_invisible_text`) | 15 |
| anything else | 141 |
| **failing only within `{05, 18, 32}`** — the class's ceiling | **35** |

Of those 35, three carry no rule at all (so `32` is failing for a reason this construct cannot reach)
and 32 carry rules:

| | |
|:--|--:|
| candidates with rules | **32** |
| … **one rule on their busiest page** — reachable by the 2008 patch | **1** (`334_patent_document`) |
| … **two or more** — need one table per page holding rows | **31** |

The busiest pages in that set: `407_id_card_front_back` 46 rules, `bus-timetable-station-left-times-right`
36, `16_right_aligned_amounts_txtpos` 17, `394_map_with_legend` 3.

`394_map_with_legend` is worth a note: the census reads **3** rules on its single page and the 2008
patch took it 41/42 -> 42/42 anyway. So the stack does not always cost a check — the two extra rules
there were not what `32` was asking about. That is why the ceiling is 32 and not 1: a document can be
made clean with one carrier only if the rules that stack are rules the check does not score. Nothing
in the census can tell those apart; only a Google measurement of each document can, and that is
32 documents of Drive round trips, not one slot.

## What this changes

1. **Do not land `rule-carrier-tblppr-2008.patch` on its own.** It is worth one document and it moves
   rules on 146. The gate cannot see that: `share@5` barely moves when a rule shifts 700 pt inside a
   page of text, and the Google half of the gate only compares documents whose result file changed.
2. **The build is the row carrier.** `w:tblpPr` once per page, `tblpY` at the first rule's y, one
   `w:tr` per rule with `w:trHeight` exact = the gap to the next, `w:tblCellMar` zeroed (5.4 pt
   otherwise, measured), `w:tblBorders` all `nil`. Rows inside one table do stack, so the placement
   problem does not recur — but **`w:hRule="exact"` on a floating table row is unmeasured in Google**,
   and if it is not honoured every rule after the first drifts by the empty cell's line box. That is
   the one probe to run before building: three rows, 40 pt gaps, read the three border y's.
3. **The 53 no-rule documents are free to prove.** Their output must be byte-identical before and
   after the patch. Any difference there is the dispatch leaking, and it costs no Google round trip
   to check.

## How it was measured, and what could be wrong with it

    python3 /scratch/work/rules_census.py     # 213 PDFs -> rules per page per document
    # then crossed with benchmarks/gverify/*.json by failing set

* The census is of the **source PDF**. It says what the page draws, not what the engine emits. A rule
  the engine already drops before it reaches `shape()` is counted here and cannot be fixed by a
  carrier — that inflates the 160 and leaves the 32 unchanged only if such rules are spread evenly,
  which is an assumption, not a measurement.
* `isolated=True` is the instrument's default for `_rules`, so a rule sharing a stroke with a table
  frame is not in these counts. The 32 are therefore the documents whose `32` failure involves at
  least one isolated rule, which is the right set for this construct.
* The failing sets are the **committed** Google results, and the last report recorded that 21 of the
  Google/LibreOffice pairs were measured on different engine stamps. The 32 is a count of what those
  files say, not a fresh measurement of the current engine.

## The corpus, which nobody had

Two runs could not land this work because the corpus was not in the sandbox and a docx engine change
cannot be stamped without measuring all 213. It is four release assets, and it took **6 minutes**:

    gh release download corpus-v1 --repo kavopdf/app -p '<zip>.zip'   # x4
    unzip -> /scratch/work/p2w/corpus ; + benchmarks/corpus-extra/*.pdf ; + benchmarks/realworld/*.pdf
    -> 213/213, 0 missing against benchmarks/RANKING.csv

`tools/p2w-bench/corpus-fetch.sh` does exactly that and prints the count. `build-engine.sh` then takes
38 s. `p2w.py --budget` is a **time** budget and manages ~26 documents per 250 s, so a full pass is
~33 minutes of wall clock and must be split across several commands — that is the real cost, and it is
now a known number instead of a guess.

---

# Second measurement, same slot: the patch's blast radius is not the class

Built the patched engine (`rule-carrier-tblppr-2008.patch`, 37 s), converted six documents, and
compared the bytes against the same six from HEAD. The patch was then reverted; the tree is at HEAD.

| document | rules, instrument's definition | `w:tblpPr` the patch emits |
|:--|--:|--:|
| `303_discharge_summary` | **0** | **15** |
| `305_vaccination_certificate` | **0** | **20** |
| `77_arabic_rtl_document` | **0** | **4** |
| `80_gstin_pan_cin_ifsc_table` | 0 (not in the 32) | 2 |
| `76_devanagari_table` | 0 | 0 |
| `15_stamp_on_scanned_page` | 0 | 0 |
| `73_marksheet_subject_marks_grade` | 2 | changed (known) |

**The predicate the engine uses is far wider than the rule the check scores.** A document with no
isolated rule on any page gets twenty floating tables. They are thin filled rects the instrument
excludes because they touch another stroke - table grid lines and frames drawn as fills - and
`isRuleShape` has no isolation test, so it takes them all.

**And the text moved.** On `303_discharge_summary` the same paragraph's `w:spacing w:before` went
**6740 -> 4291 twips** (337 pt -> 214.6 pt) with the carrier in place. The carrier is supposed to be
zero-flow; on this document it is not, and it moved a block up the page by 122 pt. `.txt` unchanged
on all three (SAME bytes), so the `.txt` checks would not see it and `share@5` would see it only as
a large displacement on a page with little ink.

Two things follow, and neither needs a Google round trip to be worth acting on:

1. **The blast radius must be narrowed before the construct is worth measuring.** `isRuleShape` needs
   the isolation test the instrument already has (`RULE_GAP` 3 pt), or every table border in the
   corpus becomes a carrier - and the carrier stacks, so on those documents the change can only
   make the render worse.
2. **The 53 "no rule" documents are not free.** Two of the four sampled there gained carriers. The
   claim in the section above that the patch "cannot change a byte" of them is **false as the patch
   stands** - it is true only of a carrier gated on the instrument's own definition.

What this does not establish: whether those 20 carriers draw anything visible in Google, and whether
the moved paragraph was moved by the carrier or by something else the patch touched. Both are one
document away, and both are worth the round trip before the row construct is built.
