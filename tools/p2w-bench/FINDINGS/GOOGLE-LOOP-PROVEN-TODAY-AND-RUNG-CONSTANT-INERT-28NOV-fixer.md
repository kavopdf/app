# The Google loop, proven end to end today; and the row-rung constant is inert on the document it was meant for

**Run:** fixer slot claimed 15:08 IST, 28 Nov 2026. Engine in the tree: `a05b20eb05fe0fc8`.
Two measurements, both below. No engine change kept.

---

## 1. A locally built `.docx` DOES reach Google today — the 12:15 blocker is answered

`BLOCKERS.md` carries, at 2026-11-28 12:15, "cannot reach drive for a NEW engine output: the upload call
needs an s3key" and concludes that the only path that works is pushing a probe to a public branch. **That
conclusion is wrong as of today, and the cost of believing it is that no engine change can be measured in
Google in the slot it is built.**

The s3key is minted by the **platform `upload` tool**, which is not importable and is not in
`GOOGLEDRIVE_*` — which is why a run that looks only at the Drive tools concludes no such path exists.
It mints one for a file that is **already saved**, and the only saved locations are `/scratch/output`,
`/scratch/input`, `/scratch/saved`, `/scratch/downloads`. A file under `/scratch/work` is refused **before**
any Drive call, and the refusal surfaces as the Drive tool's 403 *"file key does not belong to this project
or session"* — the same message three earlier runs read as a permission problem.

The three calls, exactly as run today:

```
# 1. stage locally, copy into a SAVED location, then mint the s3key (platform tool, not importable)
cp /scratch/work/p2w/gverify/stage/<name>.docx /scratch/output/gv/
s3 = upload(path="/scratch/output/gv/<name>.docx",
            tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
# -> {"name": ..., "mimetype": ..., "s3key": "project_scope/.../files/xxxx.docx"}

# 2. the middle call that makes the Doc (a blob upload cannot be exported)
doc = await GOOGLEDRIVE_CREATE_FILE(
        name="p2w-verify-<name>", mimeType="application/vnd.google-apps.document",
        file_to_upload={"name": "<name>.docx",
                        "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "s3key": s3["s3key"]},
        parent_folder_id="1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij")
# -> doc["id"]

# 3. export the render, then collect it locally
pdf = await GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=doc["id"], mimeType="application/pdf")
# -> artifacts[0].workspace_path = /scratch/downloads/composio/p2w-verify-<name>.pdf
python3 tools/p2w-bench/gverify.py --collect <name> <that path>
```

**Proof it is the same document and the same metric, not a new one.** `bank-statement-5-pages` was put
through the three calls today and `gverify.py --collect` scored it **42/47**, failing exactly
`18_displacement, 25_invisible_text, 27_text_off_page, 44_header_footer, 59_shape_anchor` — identical to the
row already stored in `benchmarks/gverify/bank-statement-5-pages.json` (engine `a05b20eb05fe0fc8`,
`med_dy -54.1`, 585 runs matched). The path reproduces the stored number, so it measures the same thing.

**Two limits, measured, so the next run does not rediscover them.** `GOOGLEDRIVE_UPLOAD_FILE` stores the
.docx as a blob and a blob cannot be exported ("Export only supports Docs Editors files", HTTP 400) — the
`CREATE_FILE` step is what makes the Doc. And the upload has a 5 MB ceiling per file.

The probe Google Doc was deleted after collection (`GOOGLEDRIVE_DELETE_FILE`, ok), and the staged copies
under `/scratch/output/gv/` were removed. Nothing was written to the Drive root; the verify folder
`1OoSHtsv-...` is the one `GVERIFY-BRIEF.md` names.

## 2. `ROW_RUNG_UNDER_TW` is inert on `320_balance_sheet_statutory` — the 16.2 pt drift is not reachable from it

`320_balance_sheet_statutory` fails **only** `18_displacement` (46/47): `med_dy 7.2`, `worst_dy 16.2`,
`bad_pages [0]`, 73 runs matched. 21 `w:trHeight` rows, and 21 x 0.75 pt = 15.75 pt is close enough to
`worst_dy 16.2` that construct (3) of `DOCS-ROOT-CAUSES-24NOV.md` — Google re-quantising a declared row
height onto the 0.75 pt ladder — looked like the whole of it.

**Hypothesis.** The engine already declares each pitch-bound row `ROW_RUNG_UNDER_TW = 10` twips (0.5 pt)
under its own pitch to knock the rung down one; 10 twips is short of the 0.75 pt quantum, so the residual
accumulates. Declaring 25 twips (1.25 pt) under should remove it.

**Test, and the result that refutes it.** The constant was moved 10 -> 25, the engine recompiled
(`12 engine sources`, new fingerprint `cd07e3e783801800`), and the corpus reconverted. The emitted row
heights on `320_balance_sheet_statutory` are **identical at both settings**:

| `ROW_RUNG_UNDER_TW` | first 21 `w:trHeight w:val` |
|---|---|
| 10 (HEAD) | `280 280 280 280 280 280 280 280 280 280 280 280 280 280 280 280 260 260 260 260 260` |
| 25 | `280 280 280 280 ...` (same values) |

So the subtraction never runs on any row of this document. It is guarded by
`if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW)` (`DocxWriter.java:6601`), and one of those
two predicates is false for every row of a dense balance sheet. **The declared height is the raw pitch, and
the 0.75 pt per row is being charged on top of a declaration that was never compensated.**

**What this means for the next run, stated as a measurement and not as a plan.** The lever for construct (3)
on this document is **`footRoom`**, not the constant: `footRoom` asks whether the row's own text leaves
`FOOT_ROOM_MIN_TW` (5 pt) of room below it, which a dense table never does, so the compensation that exists
to stop the drift is switched off exactly where the drift accumulates. Changing the constant cannot reach it.
The change was reverted and the engine left byte-identical to HEAD; `regress.py --check` passes.

**Not established by this run:** whether dropping the `footRoom` guard (or lowering its threshold) improves
`320` without clipping the rows it protects. That is the experiment the next run should run first — the
Google loop above makes it a one-document measurement, and 19 documents currently fail `18_displacement`
**alone**, so a construct that lands turns 19 documents CLEAN rather than moving them.

---

## 3. `footRoom` is the lever, and it is worth 11 pt of drift on `320` — measured in Google, both ways

The run above said the lever was `footRoom` but had not tested it. It has now been tested, end to end, in
Google, on `320_balance_sheet_statutory`.

**Which predicate is false, per row, instrumented (not read off the code).** `pitchBinds` is **true on all
21 rows**; `footRoom` is **false on all 21**. The row loop reports, for each row:

| table | rows | text need | clearance below the lowest baseline | `footRoom` wants | verdict |
|---|--:|--:|--:|--:|---|
| T1 | 16 | 195 tw (9.75 pt) | 4.25 pt | 5.0 pt | **false** |
| T2 | 5 | 185 tw (9.25 pt) | 3.75 pt | 5.0 pt | **false** |

The guard misses by **0.75 pt on T1 and 1.25 pt on T2** — it is refusing rows that have 4.25 pt and 3.75 pt
of room under their own text, because its threshold is 5.0 pt. A threshold of 75 twips (3.75 pt) flips both
tables; 85 twips would flip T1 only.

**The change:** `FOOT_ROOM_MIN_TW = 100 -> 75`. All 21 rows then emit `w:trHeight` **270** (T1) and **250**
(T2) instead of `280`/`260`, and the rung subtraction finally runs.

**Measured in Google, same document, same day, same three-call loop, both engines:**

| | passed | `med_dy` | `worst_dy` | engine |
|---|:--|--:|--:|---|
| HEAD (`FOOT_ROOM_MIN_TW = 100`) | 46/47 | **7.2** | **16.2** | `a05b20eb05fe0fc8` |
| `FOOT_ROOM_MIN_TW = 75` | 46/47 | **0.4** | **5.2** | `31324da9a1c1672e` |

**`worst_dy` 16.2 -> 5.2 pt and `med_dy` 7.2 -> 0.4 pt.** The class did not close — `18_displacement` still
fails, so the document is not CLEAN and this is a **lead, not a kept change** — but the drift construct (3)
describes is now spent, and the residual is the one the agent predicted: T2's five rows are **ladder-inert**,
because 260 and 250 both land on 13.50 pt on Google's `0.75 * (round(d/0.75) + 1)` ladder. Those rows need a
**240-twip** declaration (12.75 pt) to move at all.

**Why it is not committed.** `regress.py --check` refuses an unmeasured engine: the table is stamped on
`a05b20eb` and the changed tree is `31324da9`. Landing it needs a corpus-wide Google re-measure and
`--stamp`, which is 206 documents x 3 Drive calls and does not fit in one slot. The change was reverted, the
corpus reconverted for HEAD, the gate re-run and passing, and the stored `320` row re-measured at HEAD so the
table still describes the engine in the tree (46/47, `med_dy 7.2`, `worst_dy 16.2`, engine `a05b20eb`).

**What the next run should do, in this order.** (1) Re-apply `FOOT_ROOM_MIN_TW = 75` **and** take T2's rows to
240 twips in the same change, so the ladder moves on both tables. (2) Measure `320` in Google first — one
document, ~3 minutes with the loop in section 1 — and expect `18_displacement` to pass if `worst_dy` goes
under the check's tolerance. (3) Only then pay the corpus-wide re-measure and `--stamp`. 19 documents fail
`18_displacement` alone; this is the construct most likely to turn them CLEAN.
