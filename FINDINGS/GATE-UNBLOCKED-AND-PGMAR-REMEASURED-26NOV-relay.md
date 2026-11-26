# The docx table now exists on the current engine — and it says the page-top change cost one document 86 points

**26 Nov 2026, relay/fixer slot 22:20-23:50 IST.** Engine tree `aa496ebe` (clean), fingerprint
`025fe9deda5ac7b1`, docx hash `7e0de1abdeb221ae`. Nothing in `app/` was changed this run. No file,
row or asset was deleted.

## 1. Why every commit has been refused since 10:46 UTC

`tools/p2w-bench/txt/ENGINE-STAMP.json` was last written by engine commit `9f0a820`; one engine
commit landed after it, `aa496eb` (26 Nov 10:46:45 UTC, the `w:pgMar w:top` patch, +135/-6 in
`DocxWriter.java`). `DocxWriter.java` is inside the docx file set, so:

| hash | value | computed by |
|---|---|---|
| stamped docx | `a4de7df896875a39` | `engine_fingerprint("docx")` at `9f0a820` |
| live docx | `7e0de1abdeb221ae` | same function at `aa496ebe` |
| stamped txt | `a4d8fca469bba636` | `engine_fingerprint()` at `9f0a820` |
| live full-engine | `025fe9deda5ac7b1` | printed only, never stored |

`regress.py` line 506 compares the first two. The tree is clean because the change is **committed**,
so "the tree is X" is HEAD's engine and the stamp is stale by exactly one engine commit. This is the
same refusal recorded as blockers 19:02 and 20:15 on 26 Nov; both were correctly diagnosed as "the
baseline must re-measure", and neither run could, because the docx corpus had no output directory
(`google-safe : SKIPPED - no .docx output directory`).

## 2. What this run did about it

| step | command | result |
|---|---|---|
| corpus built | `corpus-slice.py` x3 | 213 of 213 converted, 0 failed, stamp for `025fe9deda5ac7b1` |
| corpus measured | `P2W_ENGINE_SRC=$PWD p2w.py --budget 250` x8 | **212 of 212 scored** (213 PDFs less `416_many_tiny_pages`, EXEMPT) |
| STATE written | `P2W_ENGINE_SRC=$PWD gate.py --budget 250` | `measurement: ok, 212 of 212, complete: true`, `engine: aa496ebe` |

`P2W_ENGINE_SRC` is mandatory: without it `p2w.py` builds the engine from `origin/main` instead of
the tree. `gate.py` runs `p2w.py --validate` first with a 240 s budget, so on a pod with work left a
`gate.py --budget 250` call spends its window on validation and measures nothing — that is why five
`gate.py` calls in a row left `docs_with_result` at 61 while `p2w.py --budget 250` called directly
moved it 61 → 109 → 143 → 191 → 203 → 211 → 212.

## 3. The measurement: `aa496eb` against the last committed table

`benchmarks/RANKING.csv` at HEAD was measured on `a4de7df896875a39`, the engine **before** the
page-top change. The new table is the same 212 documents on `aa496ebe`. Four documents moved by more
than 0.05 share@5:

| document | share@5 | max_pt | signature |
|---|---|---|---|
| `newsletter-3col-header-footer` | **0.20 → 86.30** | 5.28 → **172.80** | clean → content-loss |
| `600_reviewed_invoice_with_annotations` | 54.30 → 62.46 | 37.44 → 62.88 | mixed → content-loss |
| `itr-computation-with-slab-table` | 42.33 → **9.10** | 15.36 → 53.28 | mixed → content-loss |
| `39_small_caps_letter_spacing` | 0.70 → 0.80 | 4.80 → 4.80 | clean → clean |

**`newsletter-3col-header-footer` is a one-page document and it lost 172.8 pt.** That is the single
most important number in this file: a document with no page break, whose page count did not change
(1 → 1), moved by more than a page's worth of points. The page-top patch was predicted to reach only
multi-page documents with a non-zero smallest page-first gap (finding
`18-displacement-PAGE-SCALE-IS-THE-DROPPED-PAGE-TOP-26NOV-explore.md` §5, "9 of 17 reached, 1 clean").
A one-page document moving 172.8 pt is outside that prediction and needs its own explanation before
the patch is kept.

Two readings are open and this run did not have the slot to separate them:

1. **The patch double-counts on a single-page document.** `w:pgMar w:top` pushes the body down in a
   renderer that honours it, and the flow model already placed the first line at the gap, so the body
   moves by `pageTopTw` twice. The finding's `secTopTw` guard only zeroes the section for a body that
   opens with a `w:tbl`; it does not exclude a one-page body.
2. **The instrument, not the engine.** `p2w.py` logs `corpus : could not be prepared (2) - the pass
   below converts from scratch` on the run that finished the last document, so at least part of this
   table may have been measured against a `.docx` rebuilt in the same pass rather than the cached
   corpus. `corpus-slice.py` did write a stamp for `025fe9deda5ac7b1` and `p2w.py --status` reports
   `docx 213/213`, so the bytes should be the current engine's — but that warning is unexplained and
   the next run should confirm `newsletter-3col-header-footer`'s `.docx` carries `w:pgMar w:top` and
   how many points.

Reading (1) is the more likely one, because the direction and size fit: 172.8 pt of extra downward
movement on a document whose page-first gap is the section top.

## 4. What is now true that was not true at 22:20

- The docx table exists on the current engine for the first time since 10:46 UTC, and `STATE.json`
  records it (`engine: aa496ebe`, `complete: true`). `regress.py --stamp` can now legitimately stamp
  `docx` — the evidence `_measured_on_this_tree()` asks for is present.
- **The stamp must not be taken yet.** `regress.py --check` refuses on the ratchet, not on the stamp:
  `newsletter-3col-header-footer 0.20 → 86.30 share@5 up vs the last commit`, and
  `600_reviewed_invoice 54.30 → 62.46`. Non-negotiable 3 holds. The table is not committed.
- The two blockers (19:02, 20:15) are no longer "cannot measure". They are now "measured, and the
  engine change it measured regresses two documents".

## 5. Next run, in order

1. Convert `newsletter-3col-header-footer` alone at `aa496ebe`, unzip it, and read `w:pgMar w:top` and
   the page-first `w:before`. If `pgMar + before` exceeds the source's page-top gap, reading (1) is
   confirmed and the guard in `sectionTopTw()` must exclude one-page bodies.
2. If confirmed, the choice is to fix the guard or revert `aa496eb`. Reverting is measured-cheap: the
   pre-`aa496eb` table is in `git show 9f0a820:benchmarks/RANKING.csv`.
3. Only then `regress.py --stamp` and commit `RANKING.csv` + `STATE.json` + `ENGINE-STAMP.json`.

## 6. Candidates this run ruled out for the next one

Both spacer patches in `tools/p2w-bench/patches/` were audited and neither should be measured again:

- `table-spacer-before-not-line.patch` — does not apply to HEAD (preimage `4a621bd`, HEAD `6d14865`),
  and its unconditional form is already measured in Google on 26 Nov (7 documents, one clean at the
  cost of three 30 pt tails) and refused by non-negotiable 3. `SETTLED.md` records it as neutral.
- `gap-para-before-not-line.patch` — does not apply, and has no measurement anywhere in the repo.

Neither touches the room test the single-page finding names (`slackTw` at `DocxWriter.java:6281`,
`roomTw` :6284, `spendTw` :6286), which measures spare room from the source ink bottom and so
double-counts the gap it is asked to afford. That room-test change is not in `patches/` and is still
the unspent lever for the 8 single-page `18_displacement` documents.
