# Defects — the ledger

A finding is not done until it is **fixed in code** and **verified in both directions**. A row
with `fixed = no` is work that is owed, not work that was forgotten about.

This file exists because of a specific failure. On 11 Nov the font substitution was measured
and the conclusion written down — *140 of 208 documents use Liberation Serif, so the docx
should say Times New Roman* — and then nothing happened. On 12 Nov an audit found the same
defect still open, and the only reason it was found is that somebody asked. A conclusion in a
commit message is not a queue. This is the queue.

---

## The measured font map

Taken from Google's own export on 12 Nov: one docx carrying every face, converted by Drive,
exported back to PDF, and each marker word read with its rendered font.

| the docx says | Google renders | character kept? |
|---|---|---|
| Liberation Serif | ArialMT | **no** — serif became sans |
| Liberation Sans | ArialMT | yes — sans to sans |
| Liberation Mono | ArialMT | **no** — monospace became proportional |
| DejaVu Sans | Verdana | yes — sans to sans |
| DejaVu Serif | ArialMT | **no** — serif became sans |
| Times New Roman | TimesNewRomanPSMT | yes — serif stayed serif |
| Arial | ArialMT | yes |

The rule that follows: **a serif or a monospace face must be written as a face Google keeps
serif or monospace.** Times New Roman survives; everything else collapses to Arial.

---

## 1. The instrument — `verify_google.py`

| # | defect | scope | identified | fixed | verified |
|---|---|---|---|---|---|
| 1.1 | `53_embedded_faces` compared exact font names, so every Google rename read as a loss | all documents | 11 Nov | **11 Nov** (`ba695de`) | yes |
| 1.2 | `SAME_FACE` had no DejaVu entry, so DejaVu Sans → Verdana — a benign rename — read as a loss | every DejaVu document | 12 Nov | **12 Nov** | yes — unit test both directions, and `300_prescription_rx` now 41/59 instead of failing 53 |

The instrument is now correct in both directions: it passes where Google renamed a face
without losing its character, and it fails where a serif or a monospace face arrived as Arial.

---

## 2. The engine — `DocxWriter` · **the fixer's queue**

The engine writes the PDF's raw font name into `w:rFonts` and maps nothing except the
base-14 PostScript names (`times`, `helvetica`, `courier`). Verified by opening real output:
`01_stamp_rotated_15deg_upright.docx` says `w:ascii="Liberation Serif"` 41 times.

| # | defect | documents | identified | fixed | verified |
|---|---|---|---|---|---|
| 2.1 | Liberation Serif → ArialMT: a serif document arrives as sans | ~140 of 208 | 11 Nov | **no** | no |
| 2.2 | Liberation Mono → ArialMT: monospace arrives proportional, column alignment goes | unknown | 12 Nov | **no** | no |
| 2.3 | DejaVu Serif → ArialMT: serif arrives sans | unknown | 12 Nov | **no** | no |

**The fix, already known:** extend the name mapping in `DocxWriter.faceName` —
Liberation Serif and DejaVu Serif → `Times New Roman`, Liberation Sans → `Arial`,
Liberation Mono → `Courier New`, DejaVu Sans → `Verdana`. Then re-measure: the instrument
already passes those pairs, so 2.1–2.3 turn green without touching the check again.

---

## 3. Everything else round 1 has found

From `DEFECT-CLASSES.md`, 140 documents, 42 data-driven classes. The top of the list, and
every one of these is `fixed = no` until the fixer says otherwise:

| class | documents | share |
|---|---|---|
| 53_embedded_faces | 139 | 99% |
| 18_median_dy (+2: 19_worst_dy, 22_reading_order) | 135 | 96% |
| 47_margins | 135 | 96% |
| 32_stroke_lines | 101 | 72% |
| 59_shape_anchor | 88 | 63% |
| 30_ink_where_blank_was | 86 | 61% |
| 29_blank_where_ink_was | 75 | 54% |
| 02_text_run_count | 64 | 46% |
| 03_word_count (+1: 04_words_missing) | 61 | 44% |
| 23_line_pitch | 59 | 42% |

The other 32 classes are in `DEFECT-CLASSES.md`; the fixer reads that file, not this table.

---

## 4. Deliberately deferred — do not do these yet

| what | why not now | when |
|---|---|---|
| **Engine font mapping (2.1–2.3)** | round 1 must finish on one stable engine; changing it mid-round makes the baseline meaningless | after the measure gate is READY, as the fixer's first class |
| **Classifier and fixer crons** | paused. Nothing to classify until all 208 are scored in both halves | when `measure_gate.py` exits 0 |
| **Round 2 / 3 .txt backfill** | they are not needed: in those rounds both halves are measured in the same loop. The round gap is printed, not gating | never — by design |
| **APK** | ships once, when round 3 closes | after round 3 |
| **DejaVu Serif's own row in the map** | it is mapped to `timesnewroman` on the assumption the engine will write Times New Roman. If the engine instead picks another serif, re-measure | when 2.3 is fixed |

---

## 5. Found by the repo sweep, 12 Nov — recorded, not fixed

A pass over the whole repo and the commit history, looking for work that was started and
then dropped. These are all `fixed = no`. Nothing here is being acted on today.

| # | what | why it matters | fixed |
|---|---|---|---|
| 5.1 | **`ATTEMPTS.json` has no writer.** `round.py` reads, archives and deletes it; `verify_toolbox.py` writes it only as a test fixture; no production tool ever creates it. `TOOLBOX.md` says it "appears only when the first class is opened" and nothing opens a class. | `FIXER-BRIEF.md` opens STEP 2 by reading it, and closes by committing it. On the fixer's first run the read finds nothing and the commit names a file that does not exist — which is the exact failure that stopped the baseline committing for eighteen runs. | **no** |
| 5.2 | **`HYPOTHESES.md` only exists if the fixer follows the brief exactly.** `hypothesis.py` creates it on `--add`, and `FIXER-BRIEF.md` does instruct `--add`. A bare `hypothesis.py` prints usage and exits 2. | Conditional, not broken — but the commit list names it, so a fixer that skips the `--add` step fails to commit. | **no** |
| 5.3 | **`verify_toolbox.py` is orphaned.** Nothing calls it: not a brief, not `precommit.sh`, not CI, not `smoke.py`. | It is the only thing that tests what `TOOLBOX.md` *claims* rather than which flags it names. A reference can be flag-perfect and still lie, and nothing checks. | **no** |
| 5.4 | **`README.md` and `TOOLBOX.md` name ten files that do not exist:** `detect.py`, `score.py`, `fidelity2.py`, `score_ids.py`, `score_tables.py`, `IDS.md`, `TABLES.md`, `WORK-MAP.md`, `DETECTOR-PROOF.md`, `BASELINE-TXT.md`. | Stale documentation from the benchmark era. `TOOLBOX.md` listing `BASELINE-TXT.md` contradicts `ratchet.py`'s own comment, which says there is no such file. A reader believes both. | **no** |

Clean: there is no `TODO`, `FIXME`, `XXX` or `HACK` anywhere in `tools/` source.

---

## 6. Where the baseline actually is, 12 Nov 09:16

| | |
|---|---|
| docx measured | 145 of 208 |
| txt measured | 26 of 208 |
| backfill gap | 119 |
| phase | measure, round 1 |
| commits | one per document, flowing |
| last batch | 15 closed — documents 66 to 75 |

Healthy. The per-document commit, the heartbeat-first ordering and the engine build fix are
all working together, which is what the eighteen silent runs were missing.
