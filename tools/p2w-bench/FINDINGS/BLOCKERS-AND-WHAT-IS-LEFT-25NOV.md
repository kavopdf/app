# What is blocked, what is left, and what NOT to do

Written at the end of the 24-25 Nov session, so the next run does not rediscover it.

## THE ONE BLOCKER UNDER EVERYTHING

`preflight.py` reports it and it has not moved:

    verdicts  FAIL  0 of 191 verdicts are from this engine; 191 are on b7699196

The Google verdicts describe an engine that is not the one on disk. Consequence: a fixer patch changes
the engine, the corpus rebuilds, the verdicts are NOT re-measured, so the clean count cannot move and the
attempt reads as `moved=0` whether it helped or not. **This is the most likely mechanical reason 218
attempts produced 0 kept changes.**

To fix it, a .docx must reach Google Docs. That needs one of:
  - platform staging of a local file into the `s3key` that GOOGLEDRIVE_CREATE_FILE / UPLOAD_FILE require
  - GOOGLEDRIVE_UPLOAD_FROM_URL, which needs the .docx at a public URL (a data-exposure decision)
Neither is available from a sandbox. **Reading** Drive works - all 213 renders were exported - but
exporting an old render cannot produce a verdict on a new engine.

## FIVE THINGS THAT ARE CLOSED, AND SHOULD NOT BE REOPENED

1. **"Google charges the w:line="1" carrier a full line."** Withdrawn. `w:line="14.4" lineRule="auto"` is
   240ths of a line, ~0.78 pt, not 14.4 pt. The repo's own `18_displacement-CORRECTION-1045-relay.md`
   caught this and withdrew it; the session repeated it anyway. The sign does NOT flip.
2. **"A rule carried only as a floating w:drawing has never passed 32_stroke_lines."** False. 163 of 191
   scored documents carry w:drawing and PASS; only 9 fail. The class is 9 documents, not 192.
3. **"The two positioners disagree by 105.7 pt."** Not reproducible. The real figures are 101.85 / 110.48
   / 112.28 depending on build, and the recorded 51/27/21 census matches no build in the repo.
4. **"210 documents carry w:before-page-top."** That pattern matched every `w:before` in the file,
   table cells included. Real counts: 18 documents after a page break, 206 on page one. And it is not a
   cause at all - 185 of 191 carry it, including 87 that pass. Do not map it in a CAUSE table.
5. **"Fixing the page-top gap would make 13 documents clean."** An artefact of the over-broad pattern.
   With the correct key the number is 0.

## WHAT IS MEASURED AND SOLID

- The docx's vertical geometry is correct: median dy 0.02 pt, IQR 0.11 pt, slope 0.0004 pt per pt of
  page, over 18,327 lines in 213 documents.
- The engine carries pages in anchored boxes because a two-column band cannot be a flow: 18 of 54 lines
  need a negative gap, worst -85.05 pt. With boxes removed, up to 138.78 pt of drift.
- Google rasterises anchored boxes, which is why the pixel score is not 99%.
- Pixel score, 112 documents: median SSIM 88.59%, max 99.24%, **3 documents at or above 99%**; ink
  overlap median 38.98%, **none at or above 99%**.
- `18_displacement` is table-row height: Google 1.11 pt/row, worst 10.2 pt, against LibreOffice
  0.13 pt/row. 51 of 51 single-page table failures imply a Google row height above the declared one.
  The engine's declarations are correct (declared/source pitch = 1.00 in both fail and pass sets).
- Route (c) works for two-column bands: `policy-2col` 62 boxes -> 2, one page stays one page, max dy
  0.08 -> 0.02 pt. Patch is in `PATCHES/route-c-col-rows.patch`, NOT landed (never regression-checked).

## WHAT IS LEFT

| work | who | why it is not done |
|---|---|---|
| Verdict restamp on the current engine | fixer, with platform help | the upload 403 |
| Land route (c) | fixer | needs the restamp to regression-check |
| `18_displacement` table-row fix | fixer | cause known, no fix built; 3 routes sketched |
| 6 unclassified `18_displacement` docs | fixer | `31_times_body_arial`, `601_fillable_admission_form`, `70_magazine_drop_cap`, `78_mixed_english_devanagari`, `bank-statement-horizontal-rules-only`, `gst-invoice-horizontal-rules-only` |
| 43 overlay documents | nobody yet | they need a NEGATIVE before-gap (96-446 pt); a flow cannot express it. Route (c) is not the answer for them |
| Pixel score, remaining 101 docs | agent | the scorer hangs on the remaining documents; 112 is a large sample but alphabetically biased (01_ to 413_) |
| 19 pending queue items | fixer | blockers, ratchets, measures |

## WHAT NOT TO DO

- **Do not loosen `18_displacement`'s tolerance.** `verify_google.py:5800-5877` fails a page when
  max(|dy|/tol) > 2.0, so one run 3-9 pt out fails a document; passes reach 4.2 pt, failures start at
  3.3 pt. Widening it would move the number without moving the document. Decided against, deliberately.
- **Do not land route (c) without a full-corpus regression check**, however good the three documents
  look. It is a patch for that reason.
- **Do not price `32_stroke_lines` at 192 documents.** It is 9.
- **Do not treat `w:before-any` as a cause.** It fires on 210 of 213.
- **Do not trust a .docx file hash to detect change.** A .docx is not deterministic as a file - zip
  local-header timestamps differ between builds of the same document. `corpus-changed.py` hashes
  `word/document.xml` for that reason.
