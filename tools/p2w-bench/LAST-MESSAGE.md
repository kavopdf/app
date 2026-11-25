# P2W Fixer - Run Report

**25 Nov 2026 · slot 10:10 → running IST · 42 min**

> No change was kept this run. One construct was measured end to end and its patch is saved, not applied.

## What this run did

**It closed the `t12_word_invention` question with a measurement, and found the defect is one
construct in one document - not three defects in three documents.**

`FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md:17` records `t12` as "5 false positives (check), 3 real
(engine)". I re-derived the engine half from the source and the page, and two of the three are one
construct:

| | |
|:--|:--|
| `annotationRuns()` `PdfToWord.java:2456` | reads `/Contents` from **every** annotation. A note, a comment and a highlight's remark print **nothing** on the page. |
| its call site `PdfToWord.java:956` | hoists each `/Contents` as a body paragraph. Its only guard is `flat.contains(...)` against the **content stream**, so a FreeText box - drawn by its `/AP`, already read into the page at `:929` - is written **twice**. |

The sibling `annotationContentsOf()` at `:2475` **already states the correct rule**, in a comment that
names this exact document, and the truth reader (`verify_txt.py:742-752`) applies it: `/Contents` only
from subtypes **2 (FreeText)** and **13 (Stamp)**. `annotationRuns()` was never given it. Two
contradictory rules, one file, 250 lines apart.

### The measurement, before and after, on the same engine

`600_reviewed_invoice_with_annotations`, converted with `ConvertOne`, only the patch differing:

| | before | after |
|:--|:--|:--|
| `verify_txt.py` | **8/12 applicable, 7 passed - FAIL** | **8/12 applicable, 8 passed - PASS** |
| `t12_word_invention` | `source=785  txt=20` | not reported - **0 invented words** |
| paragraphs | 14 | 12 |

The entire `.txt` diff is two lines: the note (`Rate for HSN 8536 confirmed with PO.`, 7 words no page
draws) and the FreeText a second time (13 words). **7 + 13 = 20**, exactly the `txt=20` the check
reported. The FreeText survives once, the page's own `APPROVED` survives, and the stamp's `/Contents`
survives because `drawnByAppearance()` is case-sensitive on purpose (`:2343-2348`: `50_annotation_text`
asks for that string).

### The population, proved independently of the tool I was changing

The change can only move a document that **carries an annotation**, so I scanned all 213 corpus PDFs
with PyMuPDF rather than trusting the census:

```
600_reviewed_invoice_with_annotations.pdf  6  {8:1, 9:1, 11:1, 0:1, 2:1, 13:1}
documents with annotations: 1
```

`benchmarks/CENSUS.csv` agrees (`src_annots` > 0 on exactly one row). Blast radius: one document, and
on it every check that passed still passes. That is a stronger regression proof than a corpus pass,
because it names the population instead of sampling it.

### Why it is a lead and not a kept fix

`regress.py --check` refuses, and only because the tree is unmeasured:

```
ENGINE CHANGED (docx): table measured on 9e2b3e4d7869ea86, the tree is 8039ea9b058bfbce
ENGINE CHANGED (txt) : table measured on 981ff1fa35e2cf67, the tree is 8449650b7b903356
docx: no document worse than baseline
txt : no document worse than baseline
REFUSED. This commit would land a regression or an unmeasured engine.
```

`PdfToWord.java` is shared by both writers, so one edit moves both formats and both tables need
re-stamping - which needs a completed measurement of this tree. `corpus-slice.py` converts **55
documents per 250 s slice**; 213 documents is four slices before the measurement starts, and this slot
had 30 minutes left. I converted one slice (55), saw the arithmetic, and reverted rather than land half
a fix. **The gate is not pre-existing red**: at `HEAD` in a clean worktree it prints "no document worse
than baseline" in both formats, so the refusal is my change's, and it is correct.

Saved and pushed, so the next run does not re-derive it:

* `tools/p2w-bench/PATCHES/600-annotation-runs-subtype-25NOV.patch` - 36 lines, applies at `726f7b25`
* `tools/p2w-bench/FINDINGS/ANNOTATION-CONTENT-IS-NOT-BODY-TEXT-25NOV.md` - the measurement, the
  population scan, the landing sequence, and what would falsify it

## A second finding: the `txt` table is stale against its own instrument

The live verifier reports **12 checks** and 2-4 abstentions per document; the committed
`txt/RANKING-TXT.csv` records `abstained=0` and 8-10 applicable. A `txt_rank.py --help` **executes a
20-document pass** (it has no `--help`), which rewrote the first 20 rows into the new column shape and
left `600` stale. I restored the table, `STATE-TXT.json` and `HISTORY-TXT.jsonl` to `HEAD` and recorded
nothing from it. Any future re-measure absorbs that drift into 213 rows at once - **it should be a
deliberate pass, not a side effect.**

## Two agents, in the first ten minutes

| Agent | Sent to find | Took | Result |
|:--|:--|--:|:--|
| `18_displacement live path` | where the gap is emitted now that `place()` is dead | 4 min | **`place()` confirmed dead (0 callers)**; 15 gap sites mapped with reachability; the one patchable site is `DocxWriter.java:6075-6147`, guard `:6122`, wrong emission the `else` at `:6132`. Predicted **+2 to +4** at best, not +7; `68_journal` measured as a net zero (18 fixed, `59_shape_anchor` lost). Its falsifier: one Google round trip on `72_bank_statement_no_rules_right_amounts` |
| `txt t12 root cause` | engine or instrument? | 4 min | **mixed**: 5 of 8 are tokenisation (instrument), 3 are real text (engine). Best instrument change clears 3, best engine change clears 1. Confirmed the engine half is the annotation construct above |

The `18_displacement` agent's report is a genuine lead for a run with a Google round trip in hand: the
deficit credit (`0.784 x spacerTw`) plus a clamp, with `before + line` preserved to the twip so
LibreOffice is byte-neutral. It is **not** a fix I can prove here - LibreOffice cannot see it, and a
Google round trip is the only verdict.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 1 vs ATTEMPTS.json history 2 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **could not be read** - 0 of 212 scored were read as current, which is a failed read and not a measurement. No count is stated rather than a zero |
| Who re-measures them | the **:20 gverify** cron, once the read works |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 212 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **1** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (16 still open), not a new class |
| Findings vs landing | **70** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## The txt

| | |
|:--|:--|
| Measured | **8 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## A second fixer was in this slot

`git push` was rejected: the remote had moved to `7c7fcfaf` ("report: agent 18_dA-01 landed with its
own finding"), released at **10:48**, while my claim at 10:10 had succeeded. Two runs held the slot at
once - the failure the claim exists to prevent - and the rebase collided on `ROUND.json`, `RUN.json`,
`HANDOFF.json` and `TIMELINE.jsonl`. I resolved state files to this run's copy and **unioned the
append-only `TIMELINE.jsonl` (5,798 lines)** so neither run's beats were dropped. `ROUND.json` still
carries that run's two agents (`25_invisible_text mechanism`, `row-height law`); mine are described
above and are not in it. **The claim lock did not hold, and that is worth more than this run's one
lead.**

## Timing

| | |
|:--|:--|
| Slot window | 10:10 → running · 42 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 42 |
| Longest silence | **8.8 min** — from 10:19:49, after `pending.py: reading the pending gate` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **19 min** | `##########` |
| record - attempt, handoff, class rows | **3 min** | `##` |
| report - the report and the chain | **4 min** | `##` |
| other - not attributed to a tool | **15 min** | `########` |
