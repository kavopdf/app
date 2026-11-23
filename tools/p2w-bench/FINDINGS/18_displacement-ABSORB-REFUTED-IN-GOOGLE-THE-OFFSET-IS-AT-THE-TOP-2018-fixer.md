# 18_displacement — the trHeight-absorb construct is REFUTED in Google. What check 18 charges is the TOP of the block, not the row pitch.

**Run:** fixer 19:57 slot, 23 Nov 2026. **Engine:** HEAD `e9dd3716` + `patches/18-trheight-rule-absorb.patch`
(agent B's construct) for the "after" render; HEAD alone for the "before" render. Both built with
`bash tools/p2w-bench/build-engine.sh` on this pod. Converted with `ConvertOne` from
`tools/engine-verify` (cwd matters — from the repo root the same command writes a 3984-byte .docx with
0 paragraphs and an empty .txt; from `tools/engine-verify` it writes 7455 bytes and 5 paragraphs).

## What was believed

Agent B (`FINDINGS/18_displacement-TRHEIGHT-CROSS-RENDERER-1506-agentB.md`) measured in LibreOffice
that `w:trHeight = pitch − 20 tw` plus a cell bottom margin `w:tcMar` lays **18.40 pt on all 26 rows**
of `table-with-no-header-row` (HEAD: 18.0/19.0, 26 of 26 off) and predicted Google would then lay
`348 + 20 = 368 tw = 18.40` and pass `18_displacement` for the first time. The falsifier it named was
Google's per-row charge on a 0.5 pt `insideH` rule.

## What was measured

Two live Google round trips on `table-with-no-header-row` (source 1 page, export 1 page both times),
plus two on `mobile-bill`. Route: upload .docx -> `GOOGLEDRIVE_CREATE_FILE` converting to
`application/vnd.google-apps.document` in `KavoPDF-Verify` -> `GOOGLEDRIVE_DOWNLOAD_FILE` as PDF ->
`gverify.py --collect`.

| document | engine | Google | failed |
|:--|:--|--:|:--|
| table-with-no-header-row | HEAD (baseline record) | 46/47 | `18_displacement` |
| table-with-no-header-row | HEAD + absorb patch | **46/47** | `18_displacement` |
| mobile-bill | HEAD (baseline record) | 46/47 | `18_displacement` |
| mobile-bill | HEAD + absorb patch | **46/47** | `18_displacement` |

**Nothing moved in Google.** The construct did reach the output — the emitted `.docx` carries
`<w:trHeight w:val="348" w:hRule="atLeast"/>` on all 26 rows and `w:tcMar bottom=154` — so this is
"the construct reached the output and Google did not do what the prediction said", not a code-path miss.

## Independent geometry, both renders (PyMuPDF, not the repo's scorer)

Text lines paired by exact string (61 unambiguous pairs on the page), `dy = ours − source`, negative =
drawn higher. Rule positions from `page.get_drawings()`.

| render | dy min | p10 | median | p90 | max | ramp (max−min) | rule pitches | table span |
|:--|--:|--:|--:|--:|--:|--:|:--|--:|
| source PDF | — | — | — | — | — | — | 18.40 uniform | 478 pt (26 × 18.4) |
| Google, HEAD | −10.16 | −8.66 | −1.66 | +5.38 | +6.09 | **16.25 pt** | 18.0 / 19.0 / 20.0 | 495 pt |
| Google, HEAD + absorb | −10.16 | −9.41 | −8.08 | −6.75 | −1.78 | **8.38 pt** | 18.0 / 19.0 | 482 pt |

Three things follow, and only the first was expected:

1. **The patch halves the drift in Google** — the ramp across the table falls from 16.25 pt to 8.38 pt
   and the table span from 495 pt to 482 pt against a source 478 pt. The row pitch really did get
   closer. Google still quantises each row to whole points (18.0/19.0), so a 18.4 pt pitch is not
   reachable by any single `w:trHeight`; the patch narrows the sawtooth, it does not remove it.
2. **The first line of the block is at −10.16 pt in BOTH renders, to the hundredth.** The residual
   `18_displacement` failure is therefore not the row pitch at all: it is a **constant offset at the
   top of the block** that the row construct cannot touch. Check 18 charges a run for its absolute
   distance from the source position, so a block that starts 10 pt high fails however flat its rows are.
3. The offset is not one number corpus-wide — `mobile-bill` starts at −15.75 pt under the same patch —
   so it is a property of each document's leading content, not a page margin.

## The gate's side

LibreOffice, agent A (`18_displacement-LO-PROXY-VERDICT-2013-agentA.md`) and agent B agree and my run
did not re-measure it: the patch costs LibreOffice 30–36 share@5 on four documents (mobile-bill
1.55 -> 36.90 patched standalone, 5.82 in the engine build). So the change is: **no gain in Google, a
real cost in LibreOffice, nothing moves to clean.** Not landable, and reverted.

## What is now true that was not

* A row-pitch construct cannot make a document pass `18_displacement` while the block it sits in starts
  10–16 pt off. **Measure the top of the block before spending another attempt on row pitch.**
* The `w:trHeight` half of the spacer/row-pitch patch family is now measured twice in Google (2
  documents, 4 round trips) and has never turned a document clean. Treat further row-pitch shaves as
  closed unless the top offset is fixed first.

## The next lead, with its falsifier

The top of the block is carried by the paragraph immediately before the table. On this document it is
emitted as `w:spacing w:before="1040" w:line="13" w:lineRule="exact"` — position carried by
`w:spacing`, which the Google column of `GVERIFY-BRIEF.md` lists as **ignored**, with a 0.65 pt exact
line box. Hypothesis: Google drops the `w:before` and the exact line box, so the block starts at the
page's default position and the error is the difference between them.

Falsifier: build a variant that carries the same vertical position **without `w:spacing`** — e.g. an
empty paragraph with an explicit exact line height, or `w:ind`/`w:framePr` — and round trip it. If the
first line's dy does not move from −10.16, the carrier is not the spacing and this lead is dead. If it
moves, the same change should be measured on `mobile-bill` (−15.75 pt) before anything is committed,
because a per-document offset is not a construct.

## Instrument defect, found at release time

`round.py --release-fixer` refuses with **"this run has recorded no attempt at all"** while
`_attempts_this_run()` counted 1 (`TRACE.md` has the claim at 19:57 and the attempt at 20:44). The
branch is `if done < 3 and not force:` — the threshold is three, the message says zero, and a run
that has done its one attempt is told it did nothing. A run that believes the message goes looking
for a missing ledger entry that is not missing. Either the threshold drops to 1 (which is what the
surrounding comment says it is) or the message says three.
