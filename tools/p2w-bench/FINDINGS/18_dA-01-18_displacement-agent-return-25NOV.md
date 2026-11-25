# 18_dA-01 — the 18_displacement agent's own return: method, the patch, and what it could not measure

Agent `18_dA-01`, deployed 10:08 IST, landed 10:45 IST, on class `18_displacement`.
Its measured census is in `18_displacement-14-SOLO-IS-THREE-CONSTRUCTS-CENSUS-25NOV.md`.
This file carries the parts of its return that the census does not: how it measured, the patch
verbatim, and the honest list of what it could not determine.

## How it measured

Cloned the repo at HEAD `1b207aa`, fetched the 213-PDF corpus, fetched a JDK 17, built the engine
with `tools/p2w-bench/build-engine.sh`, converted the 14 solo-`18_displacement` documents with
`ConvertOne`, rendered them through LibreOffice, and scored every one with the project's own
`verify_google.py` (LibreOffice mode). Then instrumented the spacer guard (`p2w.dbgSpacer`) and
re-ran `ConvertOne` on all 14 to read `slack`, `rowExcessTw` and `spendable` per document.

It did **not** run Google (no Drive credential on the pod) and did **not** run a full corpus
conversion.

## The patch, verbatim, and why it was not landed

```java
// DocxWriter.java, in emitTable's row loop, immediately after
//     int rowHeightTw = Math.max(rowTwHere, rowLineTw);      // ~:6493
if (rowHeightTw > rowLineTw) {
    // Google lays a row at 0.75 * (round(declared / 0.75) + 1): the declaration is
    // snapped to a 0.75 pt ladder and one whole quantum is charged on top, so a
    // declaration equal to the page's pitch lays a rung too tall and the error is
    // one-signed and cumulative. Declare one quantum net of the nearest rung.
    rowHeightTw = Math.max(rowLineTw, 15 * Math.round(rowHeightTw / 15f) - 15);
}
```

It compiles, and all 14 documents still convert to one page each. It was **not** committed:

1. It must not ship alone. `18_displacement-ROW-GRID-AND-SPACER-1518-relay.md` §3 records that the
   row change alone made `mobile-bill` **worse**, -6.73 -> -12.73, because it cancels a -10.18 pt
   spacer step. The row change and the spacer spend have to land in one commit.
2. No Google measurement exists on this pod, so its pass/fail effect is predicted, not measured, in
   the only renderer the charter counts.

Prediction, stated so the next run can falsify it: removes the row-drift term corpus-wide and
unblocks the spacer spend on 6 of the 14 (`72_bank_statement`, `bus-timetable`,
`table-with-no-header-row`, `two-tables-stacked-with-no-gap`, `mobile-bill`,
`insurance-policy-schedule`). Cannot reach `31_times`, `71_invoice`, `68_journal`, or the five
spent-spacer documents.

## What it could not determine, and why

- **No Google measurement at all.** Every Google-side number it used is quoted from `FINDINGS/`;
  its own evidence is LibreOffice, the .docx XML, and the engine's guard print. The patched build
  was compiled and converted but never rendered and scored, so the patch's effect is predicted.
- The exact `dy` Google assigns to `31_times_body_arial_headings`, where a -2.87 pt constant that
  passes in LibreOffice fails in Google. Needs one `verify_google.py --json` with Drive.
- Whether the five spent-spacer documents fail on the residual ~0.1 pt overshoot or on something
  else. Their LibreOffice profiles are tight (`16` +0.82 constant, `74` +0.96, `303` +0.01), which
  points at a Google-only constant, unverified.

## Correction it found in the existing documentation

`DocxWriter.place()` at `:4149` is **dead code** — `grep -n "place("` returns the definition and
two comments, no call site. `DOCS-ROOT-CAUSES-24NOV.md` quotes it as the positioner. The live
positioner is the inlined block in `flowFromBox`/`flowRow` (`:3560–3715`, `:4453–4631`). A patch
inside `place()` changes nothing.
