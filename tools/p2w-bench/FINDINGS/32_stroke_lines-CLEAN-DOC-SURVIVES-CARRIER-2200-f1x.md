# The carrier does not damage the clean document, and it clears a second one - measured in Google

**22 Nov 2026, fixer slot 03:53 IST. Two documents, both scored through Google Docs itself.**

## What this settles

The 02:50 run stopped the carrier patch with one sentence: *"a document that is already right,
rewritten by a patch that is supposed to fix documents that are wrong, is the definition of the trade
the gate forbids."* That sentence is about a **change**, not about a **score**. Non-negotiable 3 is
*no document gets worse*. Nobody had measured whether `51_two_cm_margins` stays right.

It does.

| document | committed Google (HEAD) | this run, patched engine | what changed |
|:--|:--|:--|:--|
| `51_two_cm_margins` | **42/42** | **42/42** | rewritten: 2 drawings -> 1 drawing + 1 carrier table. **Score unchanged.** |
| `17_three_column_widths_txtpos` | 40/42 (fails `05_chars_extra`, `32_stroke_lines`) | **42/42** | 0 drawings, 2 carrier tables. **Both failures gone.** |

Both renders are Google's own PDF export of a Google Doc created from the patched `.docx`, scored by
`verify_google.py` against the source PDF. Drive folder `KavoPDF-Test-Outputs`, nothing in the Drive root.

## Why the last run's blocker was not a blocker

The 02:50 finding prescribed narrowing the predicate *"so it cannot fire where the rule already
renders"*, and named the five documents that pass `32_stroke_lines` while changing as the set it had to
be right about. A subagent took that question first and **refuted the premise**:

* There is **no structural difference** in `word/document.xml` between `51`'s drawings and the drawings
  Google drops. `51` and `17_three_column_widths_txtpos` differ in four numbers only (`cx`, `cy`,
  `posH`, `posV`); every attribute - `wp:anchor`, `behindDoc`, `wrapNone`, `prstGeom rect`,
  `a:ln/noFill`, `relativeHeight` - is identical, from the one fixed template in `DocxWriter.shape()`.
  `315_gazette_notification`'s first drawing is a numeric near-twin of `51`'s and *fails* `32`.
* `51` passes `32_stroke_lines` **vacuously**. Its 0.8 pt rule touches the page frame at both ends, so
  the check's 3 pt isolation filter discards it and the source set is empty
  (`"32_stroke_lines": {"source": 0, "render": 0, "ok": true}` in the committed JSON).
* Corpus-wide the split is exact: **45 scored documents have zero isolated source rules and all 45 pass
  `32`; 147 have at least one and 145 fail.** `51` is in the first class. A predicate over the `Shape`
  fields cannot separate the two classes, because the property that separates them is on the **source**
  side, which is what the check measures - not something the engine can see.

So the five "risk" documents were not evidence of a rendering difference. They were evidence that the
check has nothing to check on them. **There is no narrowing to build. The question was whether the
substitution is harmless, and it is.**

## What the second subagent said to watch

A check-by-check reading of `verify_google.py` found exactly one check that a *correctly placed* border
can newly fail - `46_text_crossing_rule` (`g_c == 0`, and a rule that lands 1.5 pt inside a span's box
counts as crossing) - and six conditional ones (`18_displacement`, `59_shape_anchor`,
`60_text_column_right_edge`, `61_blank_not_filled`, `62/63` for a text-carrying cell, `47_margins`).
None fired on either document here. `51` is the sharper test of the two, because it passes `46` today
with source = 0 and it is the document the carrier rewrites.

## What is still not proven, and what it costs

* **`17`'s 40/42 is a possibly-stale record.** `05_chars_extra` was re-instrumented on 21 Nov 23:37
  (one U+200B per `w:tab`); `ATTEMPTS.json` records that fix, and the committed JSONs predate it. `17`
  has 23 tabs. The defensible reading is that HEAD is **41/42** (failing `32` alone) and the carrier
  takes it to 42/42. The before-number was **not** re-measured on HEAD in this slot - that is the one
  hole in this table, and it is cheap to close (one conversion, one Drive round trip).
* **`407_id_card_front_back` is not reachable by this patch.** It is 41/42 failing `32` alone, and the
  patched engine leaves it at **41 drawings, 0 carriers** - `isRuleShape()` declines all 41. The blast
  radius already said 52 documents do not change; this is what one of them looks like. The carrier is
  worth what it reaches, and 41 drawings of rules it does not reach is a separate question.
* **The carrier still cannot land, for a reason that is not this one.** The 04:00 run converted all
  213 and the gate refused: **54 documents worse on the proxy, 58 regressions counted**, with regressed
  documents carrying a median of **9 carriers** against 1 for unchanged ones. A floating table nested
  inside a table cell displaces the cell's flow. The blocker is *placement*, not *substitution* - which
  is why neither the clean-document objection above nor the narrowing the 02:50 run prescribed was ever
  going to find it. See `FINDINGS/32_stroke_lines-CARRIER-54-REGRESSIONS-0400-f1x.md`.

## The build the next slot should run

Not a narrowed predicate: the predicate already declines what it cannot reach, and there is no property
in the `.docx` to narrow on. What is missing is a guard on **where the carrier goes** - a rule whose
anchor paragraph sits inside a `w:tc` must keep its drawing, because the carrier's own floating table
then nests in a cell and displaces it.

1. Add that guard, then convert the 54 regressed documents and count carriers per document. The number
   to beat is a median of **1**; regressed documents currently carry **9**.
2. If the 54 come back clean, `gate.py --budget 250` + `regress.py --stamp` on all 213.
3. `gverify.py` the 16 documents that fail exactly `{05_chars_extra, 32_stroke_lines}` - `17` says they
   go to 42/42, and that is **16 documents clean from 6**, if the other 15 behave like `17`.

## Files

    tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch   unchanged, applies clean to HEAD
    FINDINGS/32_stroke_lines-CLEAN-DOC-SURVIVES-CARRIER-2200-f1x.md   this file

The engine is reverted to HEAD; the tree is clean; nothing in this finding is a commit of the patch.

## A contradiction with the 00:15 relay finding, recorded rather than smoothed

`FINDINGS/32_stroke_lines-A-FOLLOWING-BLOCK-IS-THE-WHOLE-FIX-0022-relay.md` measured
`17_three_column_widths_txtpos` at **41/42 under the carrier alone** (one of two rules lost, the second
carrier stacked under the first) and **42/42 only with one empty `<w:p/>` after each carrier**. This run
measured **42/42 under the carrier alone**, with no extra paragraph added.

The two are not the same patch. The relay used `patches/rule-carrier-per-rule-2008.patch` on HEAD
`cef8de6`; this run used `patches/rule-carrier-horizontal-only-2008.patch` on HEAD `c55e1916`, and the
emitted `.docx` differs - `17` carries **2 carrier tables and 0 drawings** here. Either the horizontal-only
patch already interleaves its carriers, or `17`'s two rules happen to land interleaved in it. **This was
not isolated and the next run should not assume either patch is the other.** What both measurements agree
on is the thing that matters: `17` is reachable at 42/42, and the target set is not blocked by a lost
shape.

