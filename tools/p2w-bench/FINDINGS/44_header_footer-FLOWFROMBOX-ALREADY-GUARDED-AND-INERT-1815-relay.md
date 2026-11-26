# `flowFromBox` is already guarded and the guard is inert: the "second anchor site" does not exist at HEAD

**Recorded:** 2026-11-26 ~18:10 IST, relay slot 17:12, from a sub-agent census. Engine HEAD `d8026f0`.
**Class:** `44_header_footer`. **Outcome: refutation of a recorded hypothesis, nothing changed.**

## The hypothesis being tested

`FINDINGS/RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md` (written at engine `b7699196`)
ends with:

> `55_sidebar_box_beside_body` and `61_two_col_abstract_spanning` still carry 4 text boxes each: their
> footer rows reach `flowRow` through a different branch (or are single-box paragraphs through
> `flowFromBox`, which anchors the same oversized gap). **The same defect therefore has a second site —
> `flowFromBox` — which this change does not touch.** That is the next attempt, and it is worth more
> documents than this one.

## What is true at HEAD

`flowFromBox` (DocxWriter.java:4566) has **two** oversized-gap anchor sites — the `afterTablePt` edge
gap (4625–4642) and the pitch gap (4657–4678) — and **both already carry `!inFootBand(ctx, b.y)`**,
via the helper `inFootBand(ctx, y) { return y > FOOT_BAND_FRACTION * ctx.pageHeightPt; }` with
`FOOT_BAND_FRACTION = 0.90f` (DocxWriter.java:420–425). It landed in **`85b8735f`** ("fixer: foot-band
four-site patch", 25 Nov), which is an ancestor of HEAD. The finding that calls it untouched predates
that commit; `FOOTBAND-FOUR-SITES-61-IS-CLEAN-24NOV.md` still says "not landed", which is also stale.

## The ablation

Two builds, both converted with `ConvertOne`, compared at `word/document.xml` (the `.docx` bytes are not
deterministic; two runs of the same engine differ in bytes on 12/12 documents — see
`foot-band-spend-ab-01-MEASURED-NEUTRAL-25NOV.md`).

| build | 27 | 55 | 61 | 67 |
|:--|:--|:--|:--|:--|
| HEAD (all four sites guarded) | txbx **0**, anchor 0 | **0**, 0 | **0**, 0 | **0**, 0 |
| only the two `flowFromBox` guards removed | **0**, 0 | **0**, 0 | **0**, 0 | **0**, 0 |
| whole foot-band patch reverted | **4**, 2 | **4**, 2 | **4**, 2 | **4**, 2 |

Row 2 is byte-identical to row 1 on these four **and** on a 12-document box-carrying sample
(`331_pid_diagram` 50/59/25, `66_two_col_footnotes_bottom` 16/12/8, `401_trifold_brochure` 10/26/0,
`374_org_chart`, `382_architecture_diagram`, `46_chart_coloured_labels_body_text`,
`63_three_column_brochure`, `62_two_col_newsletter_pull_quote`, `45_coloured_callout_box`, `67`,
`70_magazine_drop_cap_photo_caption`, `54_…_header_footer`) plus `brochure-3col-with-sidebar-box`
(identical 60 812-byte `document.xml`, `anchor=0` in both builds). Rows 2 and 3 differ only in the two
`flowRow` guards, and that difference alone accounts for all 2 anchors and all 4 `w:txbxContent` per
document.

**Conclusion: the boxes come from `flowRow`, not `flowFromBox`, and `flowRow` is already guarded. The
"second site" is not a site.** `55` and `61` carry 0 text boxes at HEAD, so the "4 text boxes each"
figure belongs to the pre-`85b8735f` writer, which also emitted two `w:txbxContent` per shape.

## Why the guard would not be the right fix even if it were missing

The predicate is positional, not semantic — "bottom tenth of the paper", not "page furniture". The
section has zero margins, so on A4 the band (757.8–842 pt) contains the bottom ~12 pt of the live text
area, and a packed last body line is classified as furniture. At the `flowFromBox` pitch site the anchor
is what holds a *label* at its own y: `331_pid_diagram` takes 25 anchors through that branch, and
suppressing one because it sits low hands the y back to the flow, charging the page the whole 130–340 pt
gap. `66_two_col_footnotes_bottom` is a footnote block that is content and also sits inside the bottom
tenth. A correct guard there needs a "no baseline below this one on the sheet" flag or the page's
declared bottom margin; `Ctx` has neither.

## What was not measured, and what would prove this wrong

No Google render was taken this run; every number above is `word/document.xml` and the converter's own
counts. The corpus-wide ablation was not run. It would prove this wrong if any document's
`document.xml` differs between "all four guarded" and "`flowRow` guarded, `flowFromBox` unguarded" —
that document would reach the anchor through `flowFromBox`. The 17 documents measured say none does.
