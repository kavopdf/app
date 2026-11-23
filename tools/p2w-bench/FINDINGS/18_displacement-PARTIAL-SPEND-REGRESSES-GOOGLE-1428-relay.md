# 18_displacement — PARTIAL SPEND OF THE TABLE-GAP SPACER REGRESSES GOOGLE

**23 Nov 2026 · relay/fixer · 14:28 IST · measured in Google Docs, with a control**

## The idea under test

`DocxWriter.java:6050-6075` emits the gap between the last prose line and a table's top rule as an
empty paragraph carrying the whole height in `w:line="…" w:lineRule="exact"` with `w:before="0"`.

Google does not honour `w:line="exact"` on that paragraph — it advances by a multiple of the
substitute face's line height, so a declared 144 pt gap arrives as roughly 30 pt and the table, and
everything under it, ride up by the rest. `w:before` *is* honoured. The existing guard was
all-or-nothing: it spent the whole gap in `w:before` only when the page had room for all of it, and
spent nothing otherwise, so every spacer on a full page stayed in the dropped form.

The change tested here made the spend **partial**: `before = min(want, slack − rowExcess − already
spent)`, remainder in `w:line`, the two always summing to `spacerTw`.

## Why it looked safe

Before and after `.docx` sets over all 213 documents were compared paragraph by paragraph:

| check | documents |
|:--|--:|
| paragraph count changed | **0** |
| `sum(w:before + w:line)` changed | **0** |
| same sum, different split | **51** |
| byte-identical | 162 |

Because Word and LibreOffice advance an exact-line paragraph by `before + line`, the flow is
invariant to the twip — so the proxy **cannot** move. 51 documents carry the construct. That is the
whole argument for the change, and it is also why a LibreOffice measurement could not have refuted
it.

## The measurement — Google Docs, 68_journal_wide_table_spanning

The document with the largest gap in the corpus (144 pt). Exported from Google as PDF and scored by
`verify_google.py` (the 42 checks), **both sides through the same renderer, same session**:

| build | Google score | failing checks |
|:--|:--|:--|
| **control** — engine reverted to HEAD | **41 / 42** | `18_displacement` |
| **after** — partial spend | **40 / 42** | `18_displacement`, **`59_shape_anchor`** |

`18_displacement` reads `source=0 render=1` in **both** builds. The partial spend did not move the
displacement at all, and it **added** `59_shape_anchor` (42 anchored runs whose enclosing box is now
a different rectangle from the source's).

**This is a Google regression. The gate would have refused it, correctly.**

## What this refutes

1. **"Spending more of the gap in `w:before` reduces displacement."** On the largest gap in the
   corpus it reduces it by nothing. The 144 pt gap still lands short.
2. **"The spacer's `w:before` is honoured at the value declared."** If it were, 144 pt of `w:before`
   would have closed a 144 pt gap. It did not. The guard's premise — that `w:before` is the
   honoured channel — is not supported by this document.
3. **"A flow-invariant change is a Google-safe change."** It is not. Preserving `before + line`
   preserves LibreOffice and Word exactly, and Google re-derived its own box geometry from the new
   split and failed `59_shape_anchor` where the old split passed.

## What is still open

- The other 5 documents this construct reaches (`insurance-policy-schedule`, `mobile-bill`,
  `72_bank_statement_no_rules_right_amounts`, `two-tables-stacked-with-no-gap`,
  `bus-timetable-station-left-times-right`) were **not** measured in Google. Each fails exactly
  `18_displacement` and nothing else, so any one of them is a clean probe. They were not run because
  the slot ran out, not because the result was in doubt for 68_journal.
- Why `w:before` is not honoured at its declared value. That is the real question, and this run did
  not answer it. Until it is answered, moving mass between `w:before` and `w:line` is a guess with a
  measured regression attached.
- The patch is kept at
  `FINDINGS/18_displacement-PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.patch` as evidence, **not
  applied**. Do not re-apply it without a Google measurement of at least one of the five above.

## Method note — what made this cheap

`gverify.py`'s `--collect` was bypassed: the export artifact lands at a local path, so
`verify_google.py <source.pdf> <export.pdf> --docx <docx> --json <out>` runs directly. Four Drive
calls per document (upload, create, export, delete), no curl round trip. Two documents — the probe
and its control — took under 15 minutes end to end, and the control is what makes the number mean
anything.
