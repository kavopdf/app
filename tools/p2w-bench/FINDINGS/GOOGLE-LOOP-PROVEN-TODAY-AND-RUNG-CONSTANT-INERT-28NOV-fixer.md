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
