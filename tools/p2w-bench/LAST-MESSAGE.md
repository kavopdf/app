# P2W Fixer - Run Report

**22 Nov 2026 · slot 05:14 → running IST · 5 min**

> Three Google round trips, no engine change, and one document that is CLEAN in Google where the table
> said it was not. The lead the last report left — land the carrier patch — is
> falsified: its Google evidence is a hand-typed summary and the patch damages clean documents. What
> replaces it is a real Google round trip, run twice, and it says the table the pipeline steers by is
> measured on an engine that no longer exists.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What this run measured

**1. The carrier's "13 of 16 clean in Google" is not a measurement record.** The sixteen files in
`benchmarks/gverify-carrier-2008/` carry three fields (`engine_patch`, `engine_note`, `measured`) that
no script in the repo writes — `grep -rn "engine_patch\|engine_note" --include=*.py .` returns nothing —
no per-check map, and a `measured` value of `2026-11-22T02:2xZ` with a placeholder digit and a timestamp
six hours before the files were committed. `engine: 462353f9` cannot identify a build either: `git apply`
creates no commit, so patched and unpatched trees return the same string.

**2. The patch damages clean documents.** Own clone, patch applied, rebuilt: of the 16 target documents
plus 10 controls that pass everything at HEAD, **4 of 10 controls got worse**. `16_right_aligned_amounts`
loses six checks and grows a second page; `product-catalogue-code-left-price-right` goes 42/42 → 37/42
with 21 carriers and 1 → 3 pages. Damage tracks carrier count; documents with 1–4 carriers do not move.
`regress.py --check` refuses the patch.

**3. The local renderer cannot see the class the patch is for.** `32_stroke_lines` fails 145 of 213 in
Google and 2 of 213 in LibreOffice; `05_chars_extra` 141 and 5. Every local pass on the 16 was a pass
they already had.

**4. So this run did the Google round trip itself, twice.** Two documents converted on the current
engine, uploaded, exported from Google Docs, scored, probes deleted:

| document | committed Google (engine `462353f`) | measured now (engine at HEAD) |
|:--|:--|:--|
| `315_gazette_notification` | 40/42 — fails `05_chars_extra`, `32_stroke_lines` | **41/42** — fails `32_stroke_lines` only |
| `17_three_column_widths_txtpos` | 40/42 — fails `05_chars_extra`, `32_stroke_lines` | **41/42** — fails `32_stroke_lines` only |

`05_chars_extra` passes in Google on both, on the current engine, where the table says it fails.

**5. And one document is now clean.** `382_architecture_diagram` was the only document in the corpus whose
committed Google row failed `05_chars_extra` and nothing else — 41/42. Re-measured on HEAD: **42/42 PASS**.
Its `benchmarks/gverify/382_architecture_diagram.json` now carries the result with its provenance (docx
engine fingerprint, export sha256, method, real timestamp), `regress.py --check` passes, and Google-clean
goes **6 → 7** of the 192 scored. The
table's `engine` field reads `462353f`; the tree is `6c6cf642e13b7ed2`. **The 192 Google rows are stale,
and part of the 186-document gap is already closed.** The loop costs about four minutes a document and
`verify_google.py --json` writes the per-check map — that is the instrument the two largest Google
classes never had.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 05:14 → running · 5 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **3.1 min** — from 05:14:57, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **1 min** | `#####` |
| report - the report and the chain | **4 min** | `#################` |

## Next run

**Do not apply `rule-carrier-horizontal-only-2008.patch`.** It is falsified twice: the 03:14 corpus pass
(54 documents worse, gate refused) and this run's controls (4 of 10 clean documents worse).

Instead, spend the slot re-measuring. Take the documents that fail `{05_chars_extra, 32_stroke_lines}`
and have a Google row stamped `462353f`, and run twenty of them through the round trip in this order:
`ConvertOne` → `GOOGLEDRIVE_CREATE_FILE` into `KavoPDF-Verify` → `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`
→ `verify_google.py --json` → `GOOGLEDRIVE_DELETE_FILE`. Write the export's sha256 and `regress.py`'s
engine fingerprint beside the result. Two of two came back one check better than the table says, so the
first twenty will tell you how much of the gap is already closed before any engine work is done — and
`32_stroke_lines`, the one check still failing on both, is worth 36.5 clean documents.

Details and the exact commands: `FINDINGS/05_chars_extra-GOOGLE-TABLE-IS-STALE-ON-BOTH-DOCUMENTS-REMEASURED-0545-f1x.md`
and `FINDINGS/32_stroke_lines-CARRIER-GOOGLE-EVIDENCE-IS-NOT-A-MEASUREMENT-0525-f1x.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
