# 18_displacement — the declared→laid row-pitch law, measured on a real-shaped ruled row in Google

**22 Nov 2026 · relay fixer slot 13:18 → · engine built from HEAD + two patches, in-sandbox · every
Google number is a live round trip (ConvertOne → Drive create-as-Google-Doc → export PDF →
`verify_google.py`) · all 6 probe Docs/files deleted after scoring, Drive root left empty**

Probe document: `two-tables-stacked-with-no-gap` (1 page, 13 ruled rows, source rule pitch **18.40 pt**
on every row, source rules at 86.52, 104.92, 123.32 …).

## Why this document

`benchmarks/gverify/*.json` census run this slot: 23 clean, 21 documents fail exactly ONE check, and
**16 of those 21 fail only `18_displacement`**. That single check is the largest clean-document step
available anywhere in the table — `classpick.py --leverage` prices it at 38.7 clean documents, nearly
double `32_stroke_lines` (23.3). The document above is one of the 16 and is one page, so a round trip
on it is cheap.

## The measurement

Same source PDF, same engine, three builds, three Google round trips. Rule positions read off the
exported PDF's drawings; the pitch column is the row-to-row difference.

| build | declared `w:trHeight` / `hRule` | rule pitch Google laid | `verify_google` |
|:--|:--|:--|:--|
| HEAD (no patch) | 360, 380 tw (18.0 / 19.0 pt), `atLeast` | **19, 19, 19, 19, 20, 18, 19, 20, 19, 21, 19, 19, 19** (mean 19.1) | **41/42**, `18_displacement` only |
| sub-point grid + declared = source pitch, `exact` | 368 tw (18.40 pt), `exact` | **20, 19, 20, 19, 20, 19, 20, 19, 21, 20, 19, 20, 19** (mean 19.5) | **40/42** — `18_displacement` **and `23_line_pitch` (source=18.4 render=19.5)** |
| sub-point grid + declared = source pitch **less the rule**, `exact` | 348 tw (17.40 pt), `exact` | **18, 18, 18, 18, 18, 18, 18, 18, 20, 19, 18, 18, 18** | **41/42**, `18_displacement` only |

Source, for the same rows: 18.4, 18.4, 18.4, 18.4, 18.4, 18.4, 18.4, 18.4, 18.4, 2.0, 18.4, 18.4, 18.4, 18.4.

## What the three points say

**1. `w:hRule="exact"` does not pin the row to its declaration, and declaring the source pitch makes
the document WORSE.** 368 tw declared with `exact` is laid at 19.5 pt — 1.1 pt taller than declared,
and 1.1 pt taller than the 19.1 the unpatched `atLeast` build laid. `23_line_pitch` goes from passing
to failing. This is the first measurement of the `exact` half of the construct and it is a refutation:
**do not build `hRule="exact"` at the page's pitch.**

**2. The map from declared to laid is not affine, so no declaration lands 18.40 pt.** Three points:

    17.40 declared -> 18.0 laid   (charge +0.60)
    18.00 declared -> 19.0 laid   (charge +1.00)
    18.40 declared -> 19.5 laid   (charge +1.10)

Laid pitches are always multiples of 0.5 and laid rule positions always sit on the half-point grid
(77.5, 95.5, 113.5 …). A source pitch of 18.40 pt is therefore **not reachable by any declaration** —
the achievable ladder is 18.0, 18.5, 19.0, 19.5. This supersedes the `+0.75 pt` constant every run has
been subtracting since 11:14: the charge is not a constant, it grows with the declaration, and it is
not slope 1.

**3. Declaring net of the rule is the closest reachable point and is not a regression.** Subtracting
the row's own rule (`2 * ruleTwHere`) takes the laid pitch from 19.1 to 18.0 against a source of 18.4
— cumulative error over 13 rows from −5.2 pt instead of +9.1 pt. It scores 41/42, the same as HEAD,
with the same single failure. **No document got worse, and no document got clean.** By the charter's
own test that is a lead, not a fix.

## Why 18.0 still fails `18_displacement`

18.0 is 0.4 pt short a row. `18_displacement` charges a page when a run is more than a tolerance away
from where the source puts it, and 13 rows at 0.4 pt is 5.2 pt of accumulated displacement at the foot
of the table. The next point on the ladder is 18.5 — 0.1 pt a row, 1.3 pt over the table — and it is
**reachable**: the three points above bracket it, so a declaration between 17.40 and 18.00 should land
it. That is the one experiment this slot did not have time for, and it is the cheapest open test in the
class: one build, one round trip, on a document that is one check from clean.

## What is in the tree

`tools/p2w-bench/patches/18-row-pitch-net-of-rule-and-subpoint-grid.patch` — both halves:

- **sub-point grid geometry** (`PdfToWord.meanX/meanY`): the grouping key stays whole-point so the same
  corners still group, but the coordinate handed to the writer is the *mean* of the edges that produced
  it, so a rule at 18.40 pt survives as 368 tw instead of being quantised to 360/380. Renderer-
  independent, a correctness fix, and the reason `23_line_pitch` could be measured at all.
- **declare net of the rule** (`DocxWriter`, `rowExact`): `w:hRule="exact"` only where the page itself
  decided the height (no type floor, no squeeze, no re-cut content extent, no cut at the paper edge),
  and the declaration is the page's pitch less the row's own stroke.

It is a patch and not a commit because it moves every ruled table in the corpus and a corpus ratchet
does not fit a slot — the same wall the 12:30 slot hit on the spacer.

## Two things a later run should know

1. `verify_google.py` on a fresh build of HEAD scores `two-tables-stacked-with-no-gap` **41/42**, the
   same as `benchmarks/gverify/`. The committed table is NOT stale for this document — a useful
   contrast with `FINDINGS/47_margins-STALE-TABLES-152500.md`, where it was.
2. `upload` needs `/scratch/output`, and `GOOGLEDRIVE_COPY_FILE_ADVANCED` with
   `mimeType=application/vnd.google-apps.document` is the conversion step; the export PDF lands at
   `/scratch/downloads/composio/<name>.pdf` and `verify_google.py` scores it directly. Three Drive
   calls per document, plus one delete.
