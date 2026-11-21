# 32_stroke_lines — the "13 of 16 clean in Google" carrier result is not a measurement record, and the patch damages clean documents. Measured 22 Nov 05:00–05:20.

**What two runs believed.** `benchmarks/gverify-carrier-2008/` holds sixteen Google results for
`rule-carrier-horizontal-only-2008.patch`: 13 documents at 42/42, 3 at 41/42, 0 regressions. The 04:18
report called this the largest lead in the corpus (32_stroke_lines worth 36.5 clean documents) and asked
the next run to apply the patch, run the corpus pass and land it.

**What this run measured.** The sixteen files are hand-authored summaries, not output of any measurement
tool in this repo, and the patch they describe moves clean documents the wrong way when measured. Two
independent tests, below. Nothing was applied to the engine in this run.

## Test 1 — no writer in the repository produces these files

| writer | keys it emits | files |
|:--|:--|--:|
| `gverify.py:_write()` | `name, status, rc, passed, total, failed` (6) | 192 in `benchmarks/gverify/` |
| `verify_google.py` | `source, render, passed, total, failed, engine, ok, checks` | — |
| **`gverify-carrier-2008/*.json`** | **10 keys — the six above plus `engine_patch`, `engine_note`, `measured`** | **16** |

    $ grep -rn "engine_patch\|engine_note" --include=*.py .
    (no matches)

Those three fields are written by no script anywhere in the repo. The files also carry **no per-check
map** — only `passed: 42` and a `failed: []` — so `42/42` cannot be re-derived from them by any checker.

The `measured` field is the clearest evidence:

    "measured": "2026-11-22T02:2xZ fixer slot 01:53"

`2x` is an unexpanded placeholder digit; no program emits that. The files were committed at
`2026-11-21 20:40Z`, six hours *before* the instant the string claims.

`engine: "462353f9"` does not identify a build either: it is the last commit touching the engine
directory, and `git apply` creates no commit, so the patched and unpatched trees return the same string.
The repo's real attestation is `regress.py engine_fingerprint()` — `78ab519d6e92a2ee` patched against
`226f7f2df3013ad7` at HEAD — and none of the sixteen records it.

**What this does not prove.** That no Google Doc was ever created for these documents. The numbers may
be a faithful transcription of a real round trip. What is established is that the repo holds no record
that can be re-checked, and that three runs have now built on the transcription as though it were one.

## Test 2 — measured in a clean clone, patch applied and rebuilt

Own clone, `git apply` of the patch (193 lines to `DocxWriter.java`), rebuild 34 s, 26 documents:
the 16 of the `{05_chars_extra, 32_stroke_lines}` shape plus 10 controls that pass everything at HEAD
and carry drawn rules.

| document | set | checks HEAD → patched | share@5 | carriers |
|:--|:--|:--|--:|:--|
| `product-catalogue-code-left-price-right` | target | 42/42 → **37/42** | 0.47 → **85.32** | 0 → 21 |
| `16_right_aligned_amounts_txtpos` | control | 42/42 → **36/42** | 0.00 → **13.98** | 0 → 17 |
| `315_gazette_notification` | target | 42/42 → **41/42** | 1.91 → **15.87** | 0 → 2 |
| `373_leave_application_form` | control | 47/47 → 47/47 | 0.00 → **3.98** | 0 → 1 |
| `351_omr_answer_sheet` | control | 42/42 → 42/42 | 0.00 → **1.78** | 0 → 2 |
| `352_certificate_ornate_border` | control | 42/42 → 42/42 | 3.00 → **4.18** | 0 → 4 |
| the other 20 measured | — | unchanged | unchanged | 0 → 1–3 |

**4 of 10 clean controls got worse.** Two of them lose checks outright — `16_right_aligned_amounts`
loses six (`01_page_count`, `04_chars_missing`, `27_text_off_page`, `32_stroke_lines`,
`44_header_footer`, `55_orientation_mix`) and grows a second page. Damage tracks carrier count: 21
carriers → 1 to 3 pages, 17 carriers → 1 to 2 pages, 1 to 4 carriers → unchanged or drifting slightly.
This is the same page-overflow mechanism already recorded in
`32_stroke_lines-CARRIER-REGRESSION-IS-PAGE-OVERFLOW` and `-CARRIER-54-REGRESSIONS`, reproduced here on
documents that were clean.

`regress.py --check` with the patch applied: **exit 1, REFUSED** (unmeasured engine, and the
re-measurement above would refuse it on the regression clause too).

## Test 3 — the local instrument is blind to the class the patch is for

Corpus-wide, same engine, both renderers, from the committed tables:

| check | fails in Google (`benchmarks/gverify/`) | fails in LibreOffice (`benchmarks/gverify-lo/`) |
|:--|--:|--:|
| `32_stroke_lines` | **145 of 213** | **2 of 213** |
| `05_chars_extra` | **141 of 213** | **5 of 213** |

On all 16 target documents LibreOffice reports `32_stroke_lines: ok` and `05_chars_extra: ok` **before
and after** the patch — a local pass there is a pass the document already had. `compare_strokes.py`
reports 30/30 rules matched both before and after. So no local instrument can confirm or refute this
patch, which is why the hand-authored Google file was the only evidence — and why a Google result that
writes machine-checkable artifacts is worth more than any engine change this run could have made.

## Verdict

`32_stroke_lines` is **not one build from landing**. The patch is falsified twice (corpus pass 03:14:
54 documents worse, gate refused; this run: 4 of 10 clean controls worse) and its Google evidence cannot
be re-derived. Do not apply `rule-carrier-horizontal-only-2008.patch`.

## What would re-open it

1. A Google round trip that writes what a measurement leaves behind: per-check map, the exported PDF's
   sha256, the engine fingerprint from `regress.py`, and a real timestamp. `gverify.py --collect` already
   scores the 42 checks; the gap is that nothing records the bytes it scored.
2. A carrier emitter that is inert on documents with 1–4 rules — every regression above appears at 17+
   carriers and no document below 5 moves.
3. Re-measure the 16 through that path before any further claim about 13 of them.
