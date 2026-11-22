# 18_displacement — Google charges a table row's RULE on top of `w:trHeight`, and the spacer can now land

**22 Nov 2026 · fixer slot 10:51 → · engine `kavopdf/app` at HEAD, built in-sandbox · every Google
number below is a live round trip (upload → `GOOGLEDRIVE_CREATE_FILE` as a Google Doc in
`KavoPDF-Verify` → export PDF → `verify_google.py`). Every probe Doc created this run was left in
that folder for the next run to read; nothing outside it was touched.**

## What this slot set out to do, and the one thing it found instead

The 10:35 run left a build instruction: land the spacer as `w:before` **and** fix the row growth on
the two blocker documents, because the spacer alone takes 6 documents clean and pushes
`mobile-bill` and `insurance-policy-schedule` onto a second sheet. That run's explanation of the row
growth was **wrong on one fact and right on another**, and correcting it is what made the build work:

- **Wrong**: it said the 6-paragraph rows on `mobile-bill` are "two paragraphs per cell — a wrapped
  line". They are **six cells with one paragraph each** (`r5`-`r12`: `paras=[1,1,1,1,1,1]`, trHeight
  360, cell `w:before=190 w:line=10 exact`). The `cps.size() >= 2` multi-paragraph path is never
  entered on this document, so a diff against that path moves nothing here. Built and measured: it
  does not.
- **Right**: the row is laid out taller than the page's pitch, and the surplus accumulates.

## The measurement — a controlled probe in one document, rendered once

`probe-variants.docx` holds the whole body of `mobile-bill` three times, identical except that every
`w:trHeight` is set to 368 / 358 / 348 twips (18.4 / 17.9 / 17.4 pt). Rendered in Google and the row
rules read off the export with PyMuPDF:

| trHeight written | rows laid at | sum of 26 row gaps |
|--:|:--|--:|
| 368 tw = 18.40 pt | 19.0 / 20.0 alternating | **513.0 pt** |
| 358 tw = 17.90 pt | 18.0 / 19.0 alternating | **495.0 pt** |
| 348 tw = 17.40 pt | 18.0 uniform | **477.0 pt** |
| *the page itself* | 18.4 uniform | *483.6 pt* |

A dose-response with a slope of ~1.38 pt laid per 1.0 pt declared — **Google lays a row at the
declared height PLUS about one rule (0.9-1.3 pt here)**, so the rule is charged outside the
`w:trHeight` box, not inside it. That contradicts the engine's own comment at `DocxWriter.java:6153`
("content + rule <= pitch … the row is laid out at the page's pitch"), which is the premise the whole
`contentTwHere = rowTwHere - ruleTwHere` construction rests on.

## The second finding — `rowEdge` is snapped to whole points, and the average is exact

`mobile-bill` draws every row 18.40 pt apart (24 of 26 gaps exactly 18.4). The model's `rowEdge`
alternates **18.0 / 19.0**, so `rowTwHere = round(pitch * 20)` wrote `w:trHeight` 360 / 380 — a
+1.4 pt-per-row drift, 26 rows of it. `rowTw` (the table's own extent ÷ row count) is **368 twips,
exact**, on the same table. Where a row's own pitch agrees with that average to within a point, the
difference is the snapping and not the page.

## The build that works

`patches/18-spacer-before-rowpitch-rowrule.patch` (187 lines, three edits, applies to HEAD):

1. the table spacer's gap moves from `w:line` to `w:before`, line box cut to a hairline
   (`w:before=<gap> w:line="1" exact`) — the 10:05 construct, unchanged;
2. the spacer cap raised 2880 → 4320 twips (five documents draw a gap over 144 pt);
3. `rowTwHere` prefers `rowTw` when the row's own pitch is within 20 twips of it;
4. `w:trHeight` becomes `rowTwHere - 2*ruleTwHere`, **not floored by `rowLineTw`** — the floor is
   what kept the row at 19.04 pt. `w:trHeight` is `hRule="atLeast"`, so a row whose content needs
   more still grows to its content and nothing can be clipped.

## What it did, measured in Google, four documents

| document | HEAD | with the patch | outcome |
|:--|--:|--:|:--|
| `mobile-bill` | 41/42 (`18` alone) | **42/42** | **CLEAN** |
| `insurance-policy-schedule` | 41/42 (`18` alone) | **41/42** (`18` alone) | **not worse**, 1 page |
| `68_journal_wide_table_spanning` | 41/42 | **42/42** | **CLEAN** |
| `73_marksheet_subject_marks_grade` | 41/42 | **42/42** | **CLEAN** |

`insurance-policy-schedule` is the only one that does not close, and it is the only document in this
set whose 18_displacement is **not** the spacer and **not** the row rule: its residual is its own.
It is at its HEAD score with one page, which is the bar this slot had to clear.

## Why it is a `lead` and not a commit

`regress.py --check` refuses: **ENGINE CHANGED (docx): table measured on `6c6cf642e13b7ed2`, the tree
is `f2e6d49a9c7a3fa8` — an unmeasured change is not a pass. Re-measure, then --stamp.** The trHeight
edit reaches every ruled table in the corpus, so it needs the corpus-wide `gate.py` pass, and
`p2w.py --budget` is a *time* limit: 250 s measured 26 of 213 documents. Two 290 s calls did not get
through it and it does not carry its position across processes. There is no override, and a
half-measured table must not be published.

**The next run lands this in one pass, in this order:**

    git apply patches/18-spacer-before-rowpitch-rowrule.patch
    bash tools/p2w-bench/build-engine.sh
    python3 benchmarks/gate.py --budget 250        # repeat until STATE.json carries the tree
    python3 tools/p2w-bench/regress.py --check
    # then the Google ratchet: the 13 spacer-bearing documents that are clean today
    # (list in FINDINGS/18_displacement-table-spacer-CONFIRMED-…-1005-f1x.md) plus the 16 that
    # fail 18_displacement, before committing.

`insurance-policy-schedule` and `mobile-bill` are already proved with this exact patch, so the
Google ratchet does not need to re-measure them — only the 13 clean spacer-bearing documents and the
14 other 18_displacement documents.

## The instrument lesson, again

`screen.py` is soffice, and soffice charges `w:before + w:line`, so it is blind to edit 1 and sees
edit 4 as a pure shortening. **Do not judge this patch in soffice** — a soffice `share@5px` regression
here is the proxy disagreeing with the phone, which is the one thing non-negotiable 1 says to expect.
Every number in this file is a Drive round trip.

## Cost

14 Google renders, ~40 Drive calls, ~12 min of round trips, 4 engine builds. The engine is back at
HEAD; the change is carried as a patch.
