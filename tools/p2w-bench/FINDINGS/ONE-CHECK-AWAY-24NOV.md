# The cheapest route to CLEAN is not the biggest class: 24 documents fail exactly one check

**24 Nov 2026, fixer slot 15:03.** Computed from the committed Google verdicts,
`benchmarks/gverify/*.json` (213 files, `failed` list per document), against the 213 `.docx` this run
converted at HEAD.

## The answer to "if this works, which documents become CLEAN?"

The charter's headline defect — body text routed into an anchored DrawingML text box, 61 documents
carrying 1,037 boxes and 23,794 characters — **cleans zero documents on its own.**

| | |
|---|---:|
| documents failing `04_chars_missing` | 65 |
| ... of those, carrying text boxes | **54** |
| documents failing `45_char_accuracy` | 37 |
| ... of those, carrying text boxes | **35** |
| documents whose ONLY failures are `04` and/or `45` | **0** |

Every box-carrying document fails at least one other check. Emptying every box in the corpus would take
54 documents from "fails 04" to "fails something else". It is a real defect — a Docs user gets a picture of
a footer instead of a footer — but it is not a document-mover today, and a run that spends its slot
emptying boxes will report zero documents moved and be right.

## What is a document-mover

**24 documents fail exactly one check.** Thirteen of them fail only `18_displacement`.

| only failing check | documents |
|---|---:|
| `18_displacement` | **13** |
| `60_text_column_right_edge` | 5 |
| `32_stroke_lines` | 2 |
| `59_shape_anchor` | 2 |
| `17_matched_runs` | 1 |
| `47_margins` | 1 |
| **total** | **24** |

`classpick.py --leverage` agrees and says why: `18_displacement` is worth **39.1** clean documents,
`60_text_column_right_edge` 19.8, `04_chars_missing` 14.4, `45_char_accuracy` 6.9.

**So the order of work the evidence supports is: `18_displacement` first, and the box construct only
after it** — because `18_displacement`'s own findings say its two constructs (the `w:line` exact spacer
and the page-top `w:before`) must land together, and both are the *same* rewrite the box problem needs: a
line the flow cannot reach written as `w:before` at the page's own y rather than as an anchored box. One
rewrite, three classes.

## What this does not settle

- `04`/`45` are measured against Google's exported text layer. A document that fails only `18_displacement`
  today could fail `04` tomorrow if the box rewrite lands badly — the 13 are the cheapest target, not a
  guaranteed 13.
- The verdicts are per engine stamp; 186 of 190 are on the current engine and the rest are re-measured by
  the `:20 gverify` cron, so the one-check-away set can move by a document or two without the engine moving.
