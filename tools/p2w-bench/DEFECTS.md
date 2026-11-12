# Defects — the ledger

Every row here was checked against the code on 12 Nov, not copied from an earlier note.
Two rows in the previous version of this file were **wrong** and are corrected below: I had
written that `ATTEMPTS.json` had no writer and that `BASELINE-TXT.md` was a dangling
reference, and neither is true.

**How to read it**

| column | meaning |
|---|---|
| `fixed` | is the change in the code, on `main`, today |
| `verified` | was it tested in both directions — does it pass where it should and fail where it should |
| **benefit** | what fixing it buys. `blocks` = the pipeline cannot work. `quality` = the output is worse. `none` = nothing |

A finding is not done until it is fixed **and** verified. A row with `fixed = no` is owed
work, not forgotten work.

---

## 1. The instrument — `verify_google.py`

| # | defect | fixed | verified | benefit |
|---|---|---|---|---|
| 1.1 | `53_embedded_faces` compared exact font names, so every Google rename read as a loss | **yes** — 11 Nov, `ba695de` | yes | done — this is why check 53 can be trusted at all |
| 1.2 | `SAME_FACE` had no DejaVu entry, so DejaVu Sans → Verdana read as a vanished family | **yes** — 12 Nov, `8c21c0e` | yes | done — one whole class of false failures removed |

Both verified in the code today: `family()` is present, `SAME_FACE` carries
`dejavusans → verdana` and `dejavuserif → timesnewroman`, and the pair was unit-tested in
both directions — benign renames pass, a serif arriving as Arial fails.

**No work owed here.** The instrument is honest now.

---

## 2. The engine — `DocxWriter` · **the fixer's queue**

Measured on 12 Nov from Google's own export, one docx carrying every face:

| the docx says | Google renders | character kept |
|---|---|---|
| Liberation Serif | ArialMT | **no** — serif became sans |
| Liberation Sans | ArialMT | yes |
| Liberation Mono | ArialMT | **no** — monospace became proportional |
| DejaVu Sans | Verdana | yes |
| DejaVu Serif | ArialMT | **no** — serif became sans |
| Times New Roman | TimesNewRomanPSMT | yes |
| Arial | ArialMT | yes |

| # | defect | fixed | verified | benefit |
|---|---|---|---|---|
| 2.1 | Liberation Serif → ArialMT | **no** | no | **quality — 149 of 150 documents.** The largest single defect in the corpus |
| 2.2 | Liberation Mono → ArialMT | **no** | no | **quality** — column alignment goes |
| 2.3 | DejaVu Serif → ArialMT | **no** | no | **quality** — serif documents arrive sans |

Checked in the code today: `DocxWriter.BASE14` has exactly three entries — `times`,
`helvetica`, `courier`. There is no Liberation or DejaVu mapping anywhere in the engine.
The engine writes the PDF's raw face name into `w:rFonts` and lets Google substitute.

**The fix, already known:** extend the name map — Liberation Serif and DejaVu Serif →
`Times New Roman`, Liberation Sans → `Arial`, Liberation Mono → `Courier New`, DejaVu Sans →
`Verdana`. The instrument already passes those pairs, so all three turn green together.

**Is it worth doing?** Yes, and it is the best-value fix in the queue: one change in one
function, and it is the top class in the corpus at 99% of documents.

---

## 3. What round 1 has found so far — 150 documents, 41 classes

Re-run on 12 Nov 09:27, not carried over from the earlier count.

| class | documents | share |
|---|---|---|
| 53_embedded_faces | 149 | 99% |
| 18_median_dy (+3: 19_worst_dy, 22_reading_order, …) | 145 | 97% |
| 47_margins | 145 | 97% |
| 32_stroke_lines | 109 | 73% |
| 59_shape_anchor | 91 | 61% |
| 29_blank_where_ink_was | 85 | 57% |
| 02_text_run_count | 71 | 47% |
| 03_word_count (+1) | 70 | 47% |
| 23_line_pitch | 63 | 42% |
| 41_block_spacing | 60 | 40% |

The remaining 31 classes are in `DEFECT-CLASSES.md`. These are not pipeline defects — they
are the measurements the pipeline exists to produce. **The fixer reads that file, not this
table.**

---

## 4. Deliberately deferred — do not do these yet

| what | why not now | when |
|---|---|---|
| **Engine font mapping (2.1–2.3)** | round 1 must finish on one stable engine; changing it mid-round makes the baseline meaningless | after the measure gate is READY, as the fixer's first class |
| **Classifier and fixer crons** | paused. Nothing to classify until all 208 are scored in both halves | when `measure_gate.py` exits 0 |
| **Round 2 / 3 .txt backfill** | not needed: in those rounds both halves are measured in the same loop | never — by design |
| **APK** | ships once, when round 3 closes | after round 3 |

---

## 5. The repo sweep — corrected

Four things were written down on 12 Nov and then checked against the code. **Two were
wrong.** They are corrected here rather than deleted, because a record that quietly drops
its own mistakes is worth less than one that shows them.

### 5.1 — `ATTEMPTS.json` — **NOT A DEFECT. My earlier reading was wrong.**

I wrote that no production tool creates it. That is false. `classify.py` owns the ledger:

```
python3 tools/p2w-bench/classify.py --attempt <class> --moved <n> --total <n>
```

Tested: it creates `ATTEMPTS.json`, counts attempts, and parks a class after 12 without
progress (`attempts=13 status=PARKED`). What misled me is that `--attempt` with a bare
`--outcome kept` **refuses** — it demands numbers so the outcome is computed rather than
asserted. That refusal is deliberate and good.

| fixed | verified | benefit |
|---|---|---|
| **no defect** | yes — creates, counts, parks | none owed |

Residual note only: `FIXER-BRIEF.md` lists `ATTEMPTS.json` in its commit. The file exists by
then because every fixer run records an attempt. No action.

### 5.2 — `HYPOTHESES.md` — works, conditional by design

`hypothesis.py --add` creates it; tested, exit 0, file present. A bare `hypothesis.py` prints
usage and exits 2, which is why my first check saw nothing.

| fixed | verified | benefit |
|---|---|---|
| no defect | yes | none owed |

### 5.3 — `verify_toolbox.py` — **genuinely orphaned**

Nothing calls it. The only mentions in the repo are in this file. It tests what `TOOLBOX.md`
*claims* rather than which flags it names — the one thing that would catch a reference that
is flag-perfect and still lies.

| fixed | verified | benefit |
|---|---|---|
| **no** — not wired to anything | yes — zero callers | **small.** Nothing breaks without it. It would catch a wrong claim in the docs before a cron acts on it |

### 5.4 — stale docs — corrected

`BASELINE-TXT.md` is **not** a dangling reference: `TOOLBOX.md` and `ratchet.py` both say
"there is no BASELINE-TXT.md" on purpose. My grep counted the mention, not a reference.

The real staleness is `README.md`, last touched **7 Nov 11:45** — before the pipeline became
measure → classify → fix. It describes six gates (G1–G6) with `gate.py`, `reflow.py`,
`position.py`, `visual.py`, and names tools that no longer exist: `detect.py`, `score.py`,
`fidelity2.py`, `score_ids.py`, `score_tables.py`, `IDS.md`, `TABLES.md`, `WORK-MAP.md`,
`DETECTOR-PROOF.md`.

| fixed | verified | benefit |
|---|---|---|
| **no** | yes — 9 named tools absent | **none for the pipeline.** A reader is misled about how the folder works today. No cron reads it |

---

## 6. Where the baseline actually is, 12 Nov 09:27

| | |
|---|---|
| docx measured | 150 of 208 |
| txt measured | 41 of 208 |
| backfill gap | 109 |
| phase | measure, round 1 |
| engine | `2a68de6` |
| commits | one per document, flowing |

The gap is closing on both sides at once — 129 → 119 → 109 while the word half went 140 →
150 and the text half 21 → 41. The per-document commit, the heartbeat-first ordering and
the engine build fix are working together, which is what the eighteen silent runs lacked.

---

## 7. Summary of what is actually owed

| item | owed? | why |
|---|---|---|
| 2.1 / 2.2 / 2.3 — engine font map | **yes — highest value** | 149 of 150 documents; one function; the fix is already known |
| 5.3 — wire `verify_toolbox.py` | optional | small benefit, nothing breaks without it |
| 5.4 — rewrite `README.md` | optional | cosmetic, no runtime effect |
| everything else | **nothing** | fixed, or verified as not a defect |

---

## 8. The phase gates — two holes, found and closed 12 Nov

`round.py --advance` moved the phase on command. It validated nothing, so every rule about
"the classifier may not start until 208 + 208 are measured" lived in a brief, and a brief is
followed by an agent that can misread it.

| # | hole | what it allowed | fixed |
|---|---|---|---|
| 8.1 | `--advance` did no checking at all | the phase could move with 0 documents measured | **yes** — measure now runs `measure_gate.py` and classify runs `classify_gate.py`; a non-zero exit leaves the phase where it is |
| 8.2 | `--advance` from **fix** jumped straight to **done** | `--apk-status` returns 0 the moment the phase reads done, so one wrong `--advance` would have shipped the APK with rounds 2 and 3 never run and nothing archived | **yes** — refused. The only way out of fix is `--close-round` |

Also closed while in there:

- `measure_gate.py` never compared `BASELINE.md` with `RESULTS.jsonl`. A row scored in the
  table with no line in the store - a commit that half-succeeded - would have passed. Both
  must now agree.
- `measure_gate.py` reported a missing `txt_gap.py` as "backfill gap -1", which reads like a
  number. It now says the tool could not be read, and refuses either way.

**Verified by `gate_test.py`** — 17 cases, all passing: incomplete measure, txt gap, table
and store disagreeing, a stale class file, a short txt class file, a missing class file, the
fix refusal, that the APK still cannot ship from fix, that `--close-round` still works and
still archives, that `done` still allows a ship, and that a missing gate refuses instead of
crashing.

---

## 9. One document, one row — 12 Nov

A document must appear once in `BASELINE.md`, once in `RESULTS.jsonl` for a given round and
engine, and once in `RESULTS-TXT.jsonl`. Two rows for one document would double-count it and
the score would be meaningless.

What already held:

- `record.py` replaces any earlier line for the same **(round, engine, doc)**, so the stores
  cannot accumulate duplicates. Verified: three calls, one line.

What did not:

| # | hole | fixed |
|---|---|---|
| 9.1 | The gate compared **counts**, not sets. One document listed twice and another missing gives 208 rows against a store of 208 - the counts agree while the table no longer covers one of the documents. | **yes** — the sets must be equal, and duplicates are checked separately |
| 9.2 | A duplicate was reported as "table and store disagree", which names the wrong cause | **yes** — it now says which document is listed twice, which store row is duplicated, and which documents are on one side but not the other |

**Baseline only.** The check lives in `measure_gate.py`, which only the measure phase calls -
so the classifier and the fixer never see it, and a class or an attempt can never be blocked
by it.

Tested in `gate_test.py`: a document listed twice, a duplicate store row, a duplicate plus a
missing row whose counts still match, and a clean 208 that must still advance.

---

## 10. A round closes from fix, and only with nothing open — 12 Nov

`--close-round` had no guard either. Tested from every phase:

| called from | what happened |
|---|---|
| measure | round 1 archived, round 2 started in measure — the fix phase never ran |
| classify | round 2 started — no class was ever worked |
| fix, zero attempts | round 2 started — nothing fixed |

And the escalation: **three calls from measure** reach round 3, set the phase to `done`, and
`--apk-status` answers `may ship`. An app published with no measurement finished and nothing
fixed, from three calls that each looked like routine housekeeping.

The intended rule was in the brief: the fixer closes the round when its STEP 2 finds no class
still OPEN. Nothing enforced it.

| # | hole | fixed |
|---|---|---|
| 10.1 | `--close-round` worked from any phase | **yes** — refused unless the phase is `fix` |
| 10.2 | It did not check whether any class was still OPEN | **yes** — refuses and names them; a class that is PARKED or FIXED does not block, because parking is how the fixer moves on |

While writing the test for 10.2 I found a third thing: the guard matched `OPEN` only in the
**last** column. A column added to the class table would have turned it into a gate that
never fires. It now matches the cell wherever it sits, and the test fixture uses the real
eight-column shape so a format change shows up in the test rather than in a round that
closed with work still open.

---

## 11. Two classifier bugs — the checks it could not see, and the split it could not make — 12 Nov

Found by auditing the classifier on the user's instruction, before trusting a single
number it produces.

### 11.1 The pattern that hid two checks, one of them the second largest defect

`CHECK_RE` ended in `[a-z_]+`. Two real check ids carry digits in the suffix:
`20_within_10pt` and `43_within_10pt_x`. Both were dropped while parsing BASELINE.md,
silently. `20_within_10pt` fails on 182 of 200 documents — 91%, the second largest defect
in the corpus — and it never became a class, so the fixer was never pointed at it.

Measured: the classifier reported 50 checks firing. The stores hold 52. After the fix it
reports 52, and `20_within_10pt` appears at rank 3 with 182 documents.

The regression test reads `verify_google.all_check_ids()` and `verify_txt.all_check_ids()`
directly and asserts every emitted id matches the pattern. A check added tomorrow fails
that test unless the pattern accepts it, which is the failure that was missing.

### 11.2 The split that gave up without saying so

`split_oversized` re-clusters an oversized class at a stricter threshold until the parts
fit under `MAX_CLASS_CHECKS`. A threshold cannot separate checks that fail on exactly the
same documents — their Jaccard is 1.0 at any threshold — so the loop reached 0.95, left the
class oversized, and `out.extend(parts)` added it anyway. The invariant the function exists
to keep was broken in silence.

Tested: eight checks on the same 70 of 100 documents produced one class of eight against a
limit of six, with nothing printed.

The class stays whole, because identical document sets mean one cause with several symptoms
and cutting it at six would be arbitrary. What changed is that it is now said out loud:
"a class of 8 checks could not be split below 6 — its checks fail on exactly the same
documents... Treat it as one cause with 8 symptoms, not 8 causes."

### 11.3 What the audit found sound

| item | result |
|---|---|
| chaining in the real data | none — worst multi-check class has min Jaccard 0.81 |
| universal filter | correct — 2 checks at 90%+, each its own class |
| naming | after the check touching the most documents, as documented |
| ranking | by union size, largest first |
| ledger limits | PARKED at 24h or 12 attempts, as specified |
| class size distribution | 41 singletons, 4 pairs, 1 triple — the checks genuinely differ |

`classify_test.py` is new: 13 cases covering all of the above.

---

## 12. Baseline measurement audit — sound where it runs, three checks unproven

**DEFERRED TO ROUND 2 BY INSTRUCTION.** Nothing here is changed now. Recorded so it is
not lost: the measurement is not to be touched until round 2 begins.

### What was verified and holds

| test | result |
|---|---|
| denominator | `total = 59` on all 200 rows — one corpus, one set of checks |
| score arithmetic | `score == total - len(failed)` on all 200 — no drift |
| values completeness | every row carries exactly 59 values — nothing sampled out |
| control: a PDF against itself | **59/59** on five different documents — no check is over-strict |
| reverse: two different PDFs | **35/59** and **42/59** — the checks do fire |
| `test_checks.py` | 23/23 — every check tested on a pair that differs and a pair that does not |
| `test_txt_checks.py` | 7/7 |

So the arithmetic is real, the comparison is against the actual Google render, and the
verifier neither passes everything nor condemns everything.

### The gap: three checks the corpus never exercises

Seven checks never fired across 200 documents. Four of them are real evidence — those
documents do carry the feature and the check passed:

| check | documents that carry it | verdict |
|---|---|---|
| `08_image_count` | 14 | exercised, passes |
| `39_image_position` | 15 | exercised, passes |
| `48_image_area` | 5+ | exercised, passes |
| `49_page_size` | 200 (all have pages) | exercised, passes |

Three are not evidence at all — the source count is 0 on **all 200** documents, so the
check short-circuits to pass every time:

| check | source value | why it never fires |
|---|---|---|
| `50_annotations` | 0 on all 200 | no PDF in the corpus carries annotations |
| `51_form_fields` | 0 on all 200 | none carries an AcroForm |
| `52_outline` | 0 on all 200 | none carries a bookmark tree |

The corpus has documents named `form16-part-b`, `311_fir_police_form` and
`21_form_labels_x60_values_x300_txtpos`, but they are form **designs** — drawn boxes — not
interactive forms. Nothing in the 208 exercises those three checks, so a regression in how
the engine handles annotations, form fields or outlines would ship unseen.

### One discrepancy worth noting

`52_outline` reports source 0 and render 1–3 on several documents: the Google export adds
bookmarks the source never had. The check passes because `s_o == 0` short-circuits before
the comparison, so extra outlines in the render are invisible to it.

### What round 2 should do

1. Add to the corpus a PDF carrying real annotations, one with AcroForm fields, and one
   with a bookmark tree — then those three checks become evidence instead of decoration.
2. Decide whether `52_outline` should catch outlines the render *adds*, not only ones it
   loses. Today it can only fail in one direction.

---

## 13. The baseline, tightened — 8 checks now ask for 90%, and the ratchet can be reset

Done at the round boundary on the user's instruction: round 1 is measured and archived, so
rounds 2 and 3 measure with a stricter yardstick.

### What was loose, and what it hid

The checks were written with generous floors so they would not fail on substitution noise.
Measured against round 1's own values, three of those floors were hiding real losses:

| check | was | now | documents that newly fail |
|---|---|---|---|
| `50_annotations` | 50% | 90% | 0 — no corpus document carries annotations |
| `51_form_fields` | 50% | 90% | 0 — none carries an AcroForm |
| `52_outline` | 50% | 90% | 0 — none carries a bookmark tree |
| `56_rtl_runs` | 50% | 90% | 0 — all ten RTL documents already fail |
| `37_super_subscript` | 70% | 90% | 0 — all three already fail |
| `38_list_markers` | 70% | 90% | 0 — the two that fail already fail |
| `14_filled_shapes` | 50% | 80% | **12** |
| `44_header_footer` | 70% | 90% | **14** |

26 documents that lost between 10% and 30% of their filled shapes or their header and footer
text were passing. They now fail, and the fixer will be pointed at them.

A check at 50% says half of a document may vanish and the document still counts as correct.
That is not a measurement, and it cannot support a 99% claim.

### What was deliberately left loose

`32_stroke_lines` stays at 80%. Its counter walks `page.get_drawings()` and keeps only paths
with a stroke colour, so a table rule exported as a filled rectangle instead of a stroked
line is invisible to it. Tightening it would fail documents that look right — measured at
21 more failures, and every one of them is unverified. A false positive costs the fixer a
day; the loss is already caught by `06_table_columns` and `07_table_rows`.

`36_underline_rules` stays at 70% for the same reason: an underline may render as a border.

### The ratchet had to be resettable

Tightening a check lowers every score it touches. The ratchet keeps the best score a
document ever reached, permanently, so the fixer's first measurement in the fix phase would
have been below the old mark and refused — the pipeline would have stopped dead, and the
refusal would have looked like a regression that never happened.

`ratchet.py --reset --reason "..."` archives the store with a timestamp and empties it. A
reason is mandatory and a blank one is refused: a silent reset erases the only record that
the corpus ever scored higher. Both stores were reset today, and both archives are in the
repository:

    RATCHET-20261112-095333.json        208 marks, the old yardstick
    RATCHET-TXT-20261112-095333.json    208 marks, the old yardstick

### The gap this leaves, stated plainly

Round 1's fix phase now runs with an empty mark set, so only the twenty documents a run
measures carry a mark. A fix that hurt one of the other 188 would not be caught until round
2 re-measures it — and round 2's first measurement sets that document's mark, so the loss
would become the new standard rather than a regression.

Round 2 measures all 208 before its fix phase starts, so rounds 2 and 3 have full
protection. Round 1's fix phase does not, and that is the price of changing the yardstick
between rounds rather than at the very start.

### Verified

A PDF against itself still scores **59/59** on five documents, so no threshold became
over-strict. Two different PDFs still score 35/59. `test_checks.py` 23/23 and
`test_txt_checks.py` 7/7 still pass, which means every check still fires on a pair that
differs and still passes on a pair that does not.

### A trap in the reset, found by walking into it

`ratchet.py` without `--check` reads BASELINE.md and **raises** the marks. So resetting and
then running the tool to see whether it passes puts all 208 marks straight back — from
BASELINE.md, which still holds the old yardstick's scores. The reset looks done and is not,
and the fixer would have been refused on its first measurement for a reason nobody could see.

This was done once while verifying the reset. Checked afterwards: the store held 208 marks
and 402 KB, not zero and 2 bytes. Both stores were reset again and verified with
`--check`, which compares without raising.

Anyone resetting a store must verify with `--check` and look at the size, not at the
"PASS - the bar held" line, which an empty store and a full one both print.

---

## 14. The three checks that were decoration, and the documents that make them evidence

Section 12 found that 50_annotations, 51_form_fields and 52_outline each reported a source
count of 0 on **all 208** documents. Not one of them could fail. A check that cannot fail is
not a measurement, and a regression in how the engine handles annotations, form fields or
bookmarks would have shipped unseen through all three rounds.

Tightening their thresholds (section 13, 50% to 90%) fixed how much loss they tolerate. It
could not make them run.

### Three documents, added to the corpus

Ordinary Indian paperwork that happens to carry the feature - not fixtures built to trip a
check, and each one a document the tool should convert correctly anyway:

| document | carries | exercises |
|---|---|---|
| `600_reviewed_invoice_with_annotations` | a GST invoice marked up by a reviewer: highlight, underline, strikeout, a sticky note, a free-text comment, a stamp — **6 annotations** | `50_annotations` |
| `601_fillable_admission_form` | an admission form whose boxes are real fields: **11 AcroForm widgets** — text inputs, checkboxes, a combobox | `51_form_fields` |
| `602_bookmarked_annual_report` | a three-page annual report with a **6-entry bookmark tree** | `52_outline` |

They ship as a fourth corpus zip, `p2w-round2-additions.zip`, in the `corpus-v1` release.
The brief downloads it as `c4.zip` and now expects **211** PDFs rather than 208.

### Tested in both directions

Each document against itself scores **59/59**, so none of them is a document the verifier
would fail on its own account.

Then the feature was removed and the pair compared:

| pair | result | check |
|---|---|---|
| 600 with 6 annotations vs the same file stripped to 0 | **50/59 FAIL** | `50_annotations` fails |
| 601 with 11 fields vs the same file stripped to 0 | **53/59 FAIL** | `51_form_fields` fails |
| 602 with 6 bookmarks vs the same file with the tree cleared | **58/59 FAIL** | `52_outline` fails |

All three now fire. A check that fails when the thing it measures is removed, and passes when
the file is compared to itself, is the only kind worth having.

### What this changes for the rounds

Round 1 stays 208 - it is measured and archived. Round 2 will measure 211, so the three
documents enter the pipeline there and their checks become live evidence from that point on.
The classifier and the gates are data-driven and read the count from the stores, so nothing
else needed changing.

---

## 15. The fixer audit — four ways a fix could be recorded as working when it was not

The fixer is the only cron that changes code, so a bug here does not produce a bad report, it
produces a bad app. Each of these was tested before it was fixed, and each test is now in
`classify_test.py` so it cannot come back quietly.

### 15.1 A count larger than its own denominator was accepted

    --attempt "..." --moved 999 --total 20
    -> moved 999 of 20 (4995%) -> kept
    -> status FIXED

`kept` sets the class to FIXED, and a FIXED class is skipped by every later run. So one
invented number removes a defect from the pipeline permanently. A count of documents that
moved cannot exceed the documents that were measured; `moved > total` and `moved < 0` are now
refused.

### 15.2 The number was a claim, and nothing checked it

The comment above that code said "numbers cannot be talked into a better answer", which is
true only if the run does not supply the numbers. It did. `--moved 10 --total 20` marked a
class FIXED without a single document having moved, and the brief promised the opposite: "the
tool will refuse the claim and say what the numbers actually were".

`--attempt` now reads the store itself. For the class's own checks, it compares each
document's last two engine rows: a document moved if at least one of those checks was failing
before and none of them fails now. A claim that disagrees is refused with the true number.

    refused: you said 15 of 20 moved; the store says 8 of 20.

If the store holds only one engine, nothing was measured against a changed engine, so nothing
can have moved - refused too, with that reason.

### 15.3 The engine hash did not change until after the measurement

    ENGINE=$(git log -1 --format=%h -- .../engine/)

That reports the last **committed** change, and the brief commits at STEP 9 - after STEP 6 has
already measured. So a fix's rows carried the OLD hash, `record.py` replaced the rows they
should have sat beside, and the before-state was destroyed. That is what made 15.2
unverifiable, and it also labelled code that exists in no commit with the hash of one that
does.

The brief now appends `-dirty` when the engine folder differs from HEAD, so a fix's
measurements get their own engine id and the previous state survives.

### 15.4 The ledger was keyed by an unchecked string

    --attempt "koi bhi bakwas naam" --moved 5 --total 10
    -> koi bhi bakwas naam: attempts=1 status=FIXED

A typo in the class name wrote the attempt against nothing. The real class kept its attempt
count at zero, so it would run to twelve attempts that were never counted and then be parked
for not converging, while the ledger filled with names nothing could match. `--attempt` and
`hypothesis.py --add` now refuse a name that is not a class, and `--add` also refuses a
`--result` that is not `ruled-out`, `confirmed` or `untested` - an unknown one was filed in
capitals and read as a verdict nobody chose.

### What was checked and found sound

| item | result |
|---|---|
| `commit-gate.sh` | refuses unless the ratchet holds on BOTH halves, precommit passes, and BASELINE/RESULTS/RATCHET all changed with the engine |
| outcome thresholds | kept at 50%, improved at a third, reverted below - matches the brief |
| a claimed outcome that disagrees with the computed one | already refused |
| the slot | stale after a timeout, so two runs cannot work the same rows |
| `calibrate.py` | measures the renderer instead of assuming it - the lesson that recovered 36 documents |
| the control in STEP 7 | a document against itself must score full marks before the verifier is blamed |

---

## 16. The class file listed twenty of the forty-three classes it had just computed

`classify.py` builds the table from `classes[:top]` with `top = 20`, and the same cap applied
to the per-class document list below it. On this corpus it computes **43** classes and wrote
**20**.

Nothing noticed, because nothing compared the two numbers. `classify_gate` reads
"Documents measured: 208 of 208" and is satisfied; the file looks complete; the table is
sorted, so the twenty it showed were the twenty largest.

The failure arrives quietly and later: the fixer picks the largest OPEN class, works it, and
moves on. After twenty classes are FIXED or PARKED it looks in the file, finds nothing OPEN,
and closes the round — while twenty-three classes are still OPEN and were never written down.
A round that closes early is the one mistake this pipeline cannot recover from, because the
next round's numbers are built on it.

Both the table and the per-class list now carry every class. `--top` still limits the console
summary, which is what it was always for.

Verified: 43 computed, 43 in the file; the .txt half 4 and 4. The test builds a 30-class
fixture and asserts the file's row count equals the count the tool reported, so a cap
reintroduced anywhere fails immediately.

---

## 17. A fixer run that worked for seventeen minutes and left nothing at all

On 12 Nov the fixer's first real run started at 16:46 and ended at 17:03 — seventeen minutes,
status **succeeded** — and the repository showed no commit, no claim, no log line and no
attempt. There was no way, from outside, to tell it apart from a run that never started.

Every tool it would have used was tested afterwards and all of them work: `round.py --phase`
prints `fix`, `--claim-fixer` exits 0 and sets the slot, `build-engine.sh` builds the engine in
about five minutes, `classify.py` lists the 43 classes, `--subclusters` splits the top one, and
`hypothesis.py --show` answers. So the tools were not the cause, and the run's own output is
not retrievable — the cron reports `output_summary: null`.

What is certain is the shape of the hole: **the only early commit in the whole brief was an
instruction**, "commit ROUND.json immediately so the claim is visible to the next run". Every
other commit comes at STEP 9, at the very end. So a run that skipped that one sentence, or
tried it and failed, would leave nothing until the end — and a run that then stopped early
would leave nothing at all, while still reporting success.

### The fix: the tool writes the evidence

`round.py --claim-fixer` now appends its own line to RUN-LOG.md the moment the slot is taken:

    | 12 Nov 17:34 | fixer | slot claimed - fixer running |

A tool cannot forget to write it. The brief now asks for ROUND.json and RUN-LOG.md in one
commit straight after the claim, and says plainly that a run which has not made that commit
has not started, whatever else it is doing.

While adding it, the timestamp was written with `time.strftime`, which on this image is UTC —
five and a half hours behind every other row in the file. That is the same mistake the
RUN-LOG's own note exists to stop, so `round.py` now has an `ist()` helper and the claim line
goes through it. Verified: the line reads 17:34 when the sandbox clock says 12:04.

---

## 18. Tracking what a run actually did — a trace the tools write, not the run

A cron run is a black box from outside. It reports succeeded or failed, its output is not
retrievable (`output_summary` is null), and the only durable evidence is a commit. So when the
fixer worked for seventeen minutes on 12 Nov and left nothing, there was no way to tell whether
it had failed at the clone, the build, the class pick, the calibration or the measurement. Every
one of those tools works when called by hand, which means the failure was somewhere between
them — and nothing recorded the path.

An instruction to log is a promise. A tool that logs is a fact.

### `trace.py`

`TRACE.md`, one line per tool call, appended and trimmed to 400 lines:

    | 12 Nov 17:48 | fixer | claim        | fixer claimed the slot |
    | 12 Nov 17:48 | fixer | classify     | 43 classes from 208 documents |
    | 12 Nov 17:48 | fixer | ratchet      | held or rose |
    | 12 Nov 17:48 | fixer | ratchet --txt| held or rose |

The run name comes from the slots ROUND.json already keeps, so a line knows which cron wrote it
without being told. The timestamp goes through an `ist()` helper, because the sandbox is UTC and
every other row in this directory is IST.

Wired into: `round.py` (claim), `classify.py` (classes, attempts), `ratchet.py` (held or
regressed, both halves), `build-engine.sh` (started, built), `commit-gate.sh` (started),
`hypothesis.py` (theory recorded), `record.py`.

Every entry point is wrapped in `try/except`. A trace that raises would turn a working run into
a failed one, which is worse than no trace at all.

### How it becomes visible

The brief now asks for ROUND.json, RUN-LOG.md and TRACE.md in one commit straight after the
claim, and for TRACE.md alone to be committed again after each step — build, class picked,
calibration, measurement, outcome. Six small commits that show the path beat one at the end,
because a run that dies between two steps then leaves the steps it did finish.

TRACE.md is explicitly not code, so it is committed without the commit gate: the gate exists to
guard the engine, and the trace touches nothing. That matters — the fixer is told never to
commit outside the gate, and this is the one safe exception.

### What it does not fix

It cannot make a run commit. If a run never commits, the trace dies with its sandbox. What it
does is make the commit cheap and automatic in content: the agent does not have to remember what
to write, only to send one file it did not author.

---

## 19. The fixer worked about a fifth of the day, and the schedule was why

The first real attempt took **twelve minutes**: claim, build, classify, calibrate, eighteen
documents through Drive, ratchet, revert, commit, release. The slot was then free for the next
**108 minutes** until the next scheduled run. Twelve runs a day at two-hour gaps, against twelve
minutes of actual work each, is roughly 2.4 hours of work in a 24-hour day.

The two-hour gap was not arbitrary. It was the number that made `MAX_ATTEMPTS = 12` span one
full day: 12 runs × 2 hours = 24 hours. The day was the limit the user asked for, and the attempt
count was chosen to fit inside it. So the gaps could not be closed without moving both.

### What changed

| | was | now | why |
|---|---|---|---|
| schedule | `40 */2 * * *` — 12/day | `40 * * * *` — **24/day** | hourly, still offset from the baseline at :00 and the classifier at :20 |
| `MAX_ATTEMPTS` | 12 | **24** | one per slot, so the day is still the limit: 24 × 1 h = 24 h |
| slot stale | 100 min | **45 min** | above the longest run, below the one-hour gap |

Half-hourly was the first choice and the platform refused it: the minimum interval is 3600
seconds. Hourly is therefore the fastest this cron can fire, and 24 tries a day is the most a
day can hold.

The stale limit matters more than it looks. A run that finishes releases its own slot, so the
number only governs a run that died — but if it is shorter than a live run, the next slot starts
while the first is still working, both edit the engine, and each reverts the other's fix. 45
minutes is above the twenty-five a real attempt needs and below the sixty between two slots, so
a crash costs one slot and a live run is never doubled.

### What this costs

A class that will not converge now burns 24 attempts instead of 12 before it is parked — the same
24 hours, twice the tries. That is the intent: the machine was idle and the tries are free.
Drive traffic roughly doubles to about 140 calls an hour, the rate the baseline already ran at
without trouble.

The brief's own text said "one attempt takes about two hours" and "the claim expires after 100
minutes". Both were wrong — the attempt takes twelve to twenty-five minutes — and are corrected
in the same commit, because a brief that misstates its own timings teaches the next run to
misjudge its budget.

---

## 20. Twelve minutes is enough — what the first real attempt actually did

The question was whether a twelve-minute run can touch a class of 203 documents. The trace and
the hypothesis ledger say it can, and they say why: the run does not have to solve the class, it
has to rule out one approach and leave the next one named.

The whole of the first attempt, from the trace:

    18:41  claim
    18:42  build-engine started
    18:43  classify - 43 classes from 208 documents
    18:46  build-engine started   (after the code change)
    18:47  build-engine started   (after reverting it)
    18:52  ratchet held, ratchet --txt held
    18:52  hypothesis -> confirmed
    18:52  hypothesis -> ruled-out
    18:52  hypothesis -> untested
    18:52  attempt -> reverted (OPEN)
    18:52  commit-gate started

What it produced in eleven minutes:

1. **A renderer fact, measured rather than assumed.** Three probes through Drive established
   that Google renders `w:line` as a multiple of the substitute face's line height — 12 pt asked
   gives 11.5 pt, and the advance is `w:before + 0.069 em`, face-independent.
2. **A real code change** — converting the page-body flow to a hairline box plus absolute
   `w:before` — built and measured on twenty documents.
3. **An honest result**: one of the ten failing documents moved. Reverted, and the outcome
   recorded as `reverted`, not `improved`.
4. **The next hypothesis, named**: the same hairline-plus-before model in the *table-cell* path
   (`rowLineTw`), because `electricity-bill` and `362_price_list_dense` are table documents and
   both moved less than the body-only model predicts.

That is the shape the process was built for. Twenty-four of those a day is four hours of measured
experiments on one class, and each one starts where the last finished instead of at the beginning.

### The cost that matters

Of the eleven minutes, about five went to building and about five to measuring twenty documents
through Drive. Roughly two minutes were the actual thinking and editing. That ratio is fine while
the ledger carries the reasoning forward — it is the ledger, not the run, that has to remember —
but it does mean the build and the measurement are the budget, and shortening either is worth
more than any prompt change.

### One bug found while reading the result

`hypothesis.py` stamped entries with `time.strftime`, which on this image is UTC: the first
attempt recorded "13:22" for work done at 18:52, five and a half hours before it happened. Every
other timestamp in this directory is IST. Fixed, and the entry now reads 19:14 when the sandbox
clock says 13:44.

---

## 21. What a run reads, and what grows until it cannot work

The fixer's fixed cost is measured, and so is the part that grows.

### Read on every run, whether or not it is needed

    FIXER-BRIEF.md          23,115 bytes
    TOOLBOX, six sections    9,280 bytes
    LESSONS.md               2,750 bytes
                            ----------
                            35,145 bytes  ~ 8,800 tokens

That is the floor. Nothing below it can be cut without cutting a rule.

### Grows over time

| file | now | grows by | read by the fixer? |
|---|---|---|---|
| **RESULTS.jsonl** | 913 KB | **+2 MB a day** | no — through `record.py --show` |
| REMAINING-DEFECTS.md | 328 KB | per park | no — it only appends |
| BASELINE.md | 66 KB | stable | no — through `classify.py` |
| DEFECTS.md | 39 KB | per finding | no — it is the ledger for a person |
| RUN-LOG.md | 15 KB | +14 KB a day | no — it only appends |
| **HYPOTHESES.md** | 1.8 KB | **+29 KB a day** | yes — its own class only |
| DEFECT-CLASSES.md | 10 KB | with classes | no — `classify.py` prints the top ten |
| TRACE.md | 1.4 KB | capped at 400 lines | no |

Two of those mattered enough to change.

### RESULTS.jsonl — four kilobytes a row, and every attempt adds twenty

A row carries `values`: all 59 checks with their source and rendered number. That is 4 KB.
The fixer measures twenty documents under a new engine id on every attempt, twenty-four
attempts a day, so the file grew by about **2 MB a day** — 14 MB in a week, and one `cat`
of it would have ended a run before it started, looking exactly like nothing happened.

Nothing reads `values` except a person looking at one document. The classifier groups on
`failed`, the ratchet compares `failed` and the score, the gates count documents.
`record.py` now keeps `values` for the **last two engines** — enough for a before and an
after — and every older row keeps its score and its failed list, which is everything the
pipeline uses. The file stops growing with history and starts tracking only the recent one.

### HYPOTHESES.md — the fixer reads this one, so its growth was the expensive kind

Three entries per attempt, twenty-four attempts a day, about 29 KB a day — and the fixer
reads its class section on every attempt. By the end of a day it would be reading a class's
entire history to find the one entry that shapes the next try.

`hypothesis.py` now keeps the last **eight entries** of each class in full and collapses
everything before them into a single line: "2 earlier entries collapsed on 2026-11-12 — the
last 8 are below". Tested at twelve entries: nine lines, 991 bytes, and the newest eight
intact.

### The warning that costs nothing

Four files are large enough to end a run by being read, and each has a tool that prints the
slice that was actually wanted. The brief now opens with them, by name and by size, and says
what to use instead — `record.py --show`, `classify.py`, `hypothesis.py --show`,
`trace.py --show`, or `wc -l` and `head -3` for a file's shape.

### Left alone, deliberately

`LESSONS.md` is 50 lines against its own "capped at fifteen" rule, but it is 2.75 KB — 0.7%
of the fixed read — and all nine lessons are load-bearing. Trimming it would cost quality to
save 1.8 KB. `REMAINING-DEFECTS.md` at 328 KB is history the fixer never reads; archiving it
would risk the parking step that writes to it, so it gets the warning instead.
