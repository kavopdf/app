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
