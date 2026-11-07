# PDF to Word — how this folder is laid out

## The pipeline

Six gates. They are the whole measurement. Nothing else in this folder decides whether
a change is good.

| Gate | Script | Question |
|------|--------|----------|
| G1 build | `javac` + `TestPdfToWord` + `TestRealDocs` | does it compile and do the engine tests pass |
| G2 regression | `gate.py` | did any document get worse than its own baseline |
| G3 structure | `reflow.py` | is this a Word document, or a PDF wearing one |
| G4 txt isolation | `txt-guard.py` | did a txt change reach the .docx |
| G5 position | `position.py` | is the text where the PDF put it |
| G6 visual | `visual.py` | the eight questions, answered per page |

## The records

| File | What it holds |
|------|---------------|
| `base208.json` | the regression floor: one entry per document, 208 of them |
| `base208-position.json` | the position floor, same shape |
| `base208-history.md` | one row per move of the ratchet |
| `REMAINING-DEFECTS.md` | model defects, with the measurement that proves each |
| `TXT-DEFECTS.md` | txt defects; every fix carries the G4 proof |
| `TXT-SCORE.md` | the txt position score and its history |
| `VISUAL-SCORE.md` | the visual score and its history |
| `BATCH-LOG.md`, `V3-BATCH-LOG.md` | what each batch covered |

## Removed

`score.py`, `score_tables.py`, `score_ids.py`, `detect.py` and `fidelity2.py` were the
older bench. Nothing in the pipeline ran them, so their numbers were never compared
against anything and never recorded. They are gone rather than left to be run by
mistake; `visual.py` now answers the table, chart, image and emphasis questions and
`position.py` answers the font and colour ones.

The .md files that described them are gone too: `WORK-MAP.md`, `TABLES.md`, `IDS.md`
and `DETECTOR-PROOF.md`.
