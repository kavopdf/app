# CORRECTION to 18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md

**Written by the same run, 22 Nov, after an independent audit of that file against the repository.
Three of its five claims do not survive. Read this before you read the finding, and read the finding
as narrowed here — it is not deleted, because how it went wrong is the useful part.**

---

## What is still true

- **16 documents fail `18_displacement` and nothing else** in `benchmarks/gverify/*.json`, and
  `classpick.clean_leverage()` returns **38.72** for the check. Recomputed by the audit, not trusted.
  Two caveats it added: 7 more fail it in the LibreOffice table, and **21 documents are
  `page_count_refused`** — unmeasured, not clean.
- **`mobile-bill` 46/47 and `insurance-policy-schedule` 46/47 fail only `18_displacement` in Google;
  `68_journal` 41/42 fails only `18_displacement` too, and its second failure `59_shape_anchor` is
  LibreOffice-only.** So the finding's sentence "all three fail only this check" is true in Google
  and false in LibreOffice.
- **The measurement loop** (four Drive calls, ninety seconds, and the two traps: `upload` refuses a
  path under `/scratch/work`, and `KavoPDF-Verify` is folder id `11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`)
  is right and reproducible, and it reproduced the committed mobile-bill result before judging
  anything.
- **On mobile-bill's own rows, three builds produced byte-identical Google geometry.** That is a fact
  about those 24 rows. It is not a law about `hRule` and not a law about `w:before`.

## Correction 1 — "`google_safe.py` lists only `w:position`" is FALSE

`tools/p2w-bench/google_safe.py:35-64` carries **seven** `IGNORED` entries — `w:framePr`,
`w:drawing`, `wp:anchor`, `w:w`, `w:spacing-letter`, `w:position`, `w:before-page-top`, plus
`embedded-font`. The narrower point the finding was reaching for is still worth something: **no entry
matches `w:line` or `lineRule`.** But the gate's regex at `:58` already matches the `<w:spacing …>`
element the hairline rides in, and `GOOGLE-SAFE-MARK.json` records it on **213 of 213 documents,
33,930 instances** — so it is counted, and only one attribute inside an already-counted element is
untracked. That is a smaller claim than the one written.

## Correction 2 — "`w:hRule="exact"` is inert" is OVERSTATED, and the repository already knew

Two committed findings falsify the general form:

- `FINDINGS/32_stroke_lines-CELL-BORDER-HONOURED-1830-f1x.md:119,124-127` — a **1440-twip `exact`
  row measured 72.00 pt** in the Google export. 1440/20 = 72.0. Honoured exactly.
- `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md:25,36-37` — a **1103-twip `exact`
  row** came back at y = 55.83 against 55.15 asked.

And the engine's other row emitter already writes `exact` unconditionally —
`DocxWriter.java:2161`, in `columnPage()`, with `annual-review-2col-uneven-columns` measured 39/42 in
Google with `18_displacement` **passing**. (There `rowTw` equals the content height, `:2143`, so the
two rules coincide and that document does not settle it either way.)

**What is actually true, and is what the next run should carry:** `exact` was inert on
mobile-bill's 360/380-twip rows. It is not inert in general. The difference is row height, and the
likely reading is the one the 09:51 run had and this run failed to disprove: **Google lays a table
row at `max(trHeight, its own content height)`, and at 18 pt the content wins.** Above roughly 72 pt
the floor wins again, which is what the two findings above show.

Also: "Google re-emits `atLeast` on export" (measured, true — it is in Google's `.docx` export of
mobile-bill) and "Google ignores `exact`" are different claims. The repo separates them; this finding
ran them together.

## Correction 3 — "`w:before` does not enter the row's height" is OVERSTATED, and the probe cannot see it

The probe swept `before` from 100 to 340 twips — **5.0 to 17.0 pt** — against rows that laid
**19.0 pt**. Every value tested fits underneath the laid height. So "the row did not move" is what you
observe whether `before` is charged or not: **the probe is not sensitive to the question it was used
to answer.** The same is true of the corpus build, which cut `before` from 190-210 to 163-188 twips
(8.2-9.4 pt) against an 18 pt floor.

Worse, **Correction 3 contradicts the finding's own Correction 2 story.** If Google really replaced
the hairline with a 14.4 pt box, then `before` = 17.0 pt would have laid 31 pt, not 19. Both cannot be
true on one probe. The read-back value `w:line="14.399999999999999" w:lineRule="auto"` is almost
certainly **not 14.4 pt** — under `lineRule="auto"` that attribute is in 240ths of a line, so the
export is writing a number this run read as points and should not have.

**So the mechanism this finding proposed — "Google substitutes a ~14.4 pt box for the hairline" — is
withdrawn.** What survives from that read-back is only the plain observation that the value and the
`lineRule` come back changed.

## What the probe did establish, stated narrowly

Cell written `w:before="0"` and `w:line` = the row's own height, floors 360/360/380, eleven rows:
laid **18.00, 18.00, 18.75** — the sawtooth reproduced. That is a real measurement and it is the only
one this run has that points anywhere. It is one document, one font size, one column width, and it
was not repeated on a second probe, so treat it as a lead and not a law.

Its price is unchanged and still blocks it: a box the height of the row puts the baseline at
`LINE_BASE` = 0.8 of the row, mobile-bill draws at 0.5, and `before + 0.8·box = 184` with
`before + box = 360` has no solution. Built with `w:vAlign="center"` to lift the line and it cost
LibreOffice 47/47 → 45/47 on mobile-bill and 47/47 → 46/47 on insurance-policy-schedule. Reverted
**unmeasured in Google**, so whether the pair fixes the class in Google is unknown.

`w:tcMar` is still the cheapest untried candidate and still untried — the audit confirms
`DocxWriter.java` emits **no** `w:tcMar` anywhere and `w:vAlign` only as `top` (at `:2164` and
`:6629`), so there is no shipped construct that sets a row's height without also setting its baseline.

## One thing the audit could not check, and it should worry the next run

Every Google table in `benchmarks/gverify/*.json` is stamped `"engine": "462353f9"`, written by
`verify_google.py:4563-4573`. **That commit does not resolve in the published repository**
(`git cat-file` says it is not a valid object name). The tables cannot be tied to this HEAD by their
own provenance field, so "the engine is back at HEAD" is not checkable from the repo alone. It changes
none of the counts above, and it is a question for whoever owns the engine history, not for a fixer.

---

*The audit is `audit-18_displacement-1045.md` in the same run's output. Every correction above cites
the file and line that decides it. Nothing in the repository, the corpus or the Drive was changed to
write this.*
