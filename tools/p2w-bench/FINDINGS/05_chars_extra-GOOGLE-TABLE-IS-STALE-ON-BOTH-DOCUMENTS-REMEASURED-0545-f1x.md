# 05_chars_extra — the committed Google table is stale: on the current engine the check PASSES on both documents re-measured through Google Docs. 22 Nov 05:35–05:45.

**Why this matters.** `benchmarks/gverify/` is the Google truth the whole pipeline steers by, and its
`engine` field reads `462353f` — an engine that no longer exists. The tree at HEAD is
`6c6cf642e13b7ed2`. Every "6 clean of 192" number in the reports is measured against that old engine.

**What this run measured.** Two documents re-converted on the current engine and taken through a real
Google Docs round trip (create Doc in `KavoPDF-Verify` → export PDF → `verify_google.py` on source vs
export). Both were probe documents, both deleted afterwards; nothing is left in Drive.

| document | committed Google (engine `462353f`) | this run (engine at HEAD) | sha256 of export |
|:--|:--|:--|:--|
| `315_gazette_notification` | **40/42** — fails `05_chars_extra`, `32_stroke_lines` | **41/42** — fails `32_stroke_lines` only | `e486e42b…0ffb5` |
| `17_three_column_widths_txtpos` | **40/42** — fails `05_chars_extra`, `32_stroke_lines` | **41/42** — fails `32_stroke_lines` only | `fd8df7a5…8918b` |

`05_chars_extra` passes in Google on both, on the current engine, where the table says it fails. Two of
two — and the two were chosen only because they are in the `{05,32}` shape, not because they looked easy.

Corroboration from the local side: `05_chars_extra` fails 5 of 213 in LibreOffice and 141 of 213 in
Google, so the check is not something the proxy could have fixed by accident; the change had to reach
Google's renderer, and on these two it did.

## The round trip works, and it is cheap

The whole loop for one document — convert, upload, create Doc, export PDF, score — took about four
minutes, and `verify_google.py` writes the per-check map. That is the missing instrument: the two largest
Google classes (`32_stroke_lines` 145 of 213, `05_chars_extra` 141 of 213) are invisible to LibreOffice
(2 of 213 and 5 of 213), so no engine change for them can be judged without this loop.

## What the next run should do with it

1. **Re-measure before fixing.** The 192 Google rows are on `462353f`. A run that re-measures 20 of them
   on the current engine will find out how much of the 186-document gap is already closed — this run's
   two documents suggest `05_chars_extra` is. Do not build a fix for a class whose table is that stale.
2. **Record what a measurement leaves behind.** `verify_google.py --json` already writes the per-check
   map; `gverify.py --collect` should also write the export's sha256 and `regress.py`'s engine
   fingerprint, so a Google claim can be re-derived instead of transcribed. The sixteen files in
   `benchmarks/gverify-carrier-2008/` are the counter-example — see
   `32_stroke_lines-CARRIER-GOOGLE-EVIDENCE-IS-NOT-A-MEASUREMENT-0525-f1x.md`.
3. **Then** attack `32_stroke_lines`, which is the only check still failing on both documents here and is
   worth 36.5 clean documents. The carrier patch is not the way — it damages clean documents.

## Method, so it can be repeated

    java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
         ConvertOne /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/p2w/out
    # upload → GOOGLEDRIVE_CREATE_FILE(mimeType=application/vnd.google-apps.document,
    #          parents=[KavoPDF-Verify], file_to_upload=<s3key>)
    # GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId, mimeType=application/pdf)
    python3 tools/p2w-bench/verify_google.py <source.pdf> <export.pdf> --json <out.json>
    # GOOGLEDRIVE_DELETE_FILE(fileId) — the probe is deleted, never left behind

Note for the next run: `java` is not on PATH; the JDK the build fetches lives at
`/scratch/work/.p2w-jdk/jdk`, and the classpath must include `libs/aar/assets` or every Standard-14 font
dies.

## Third document, and the first CLEAN one — 06:06

`382_architecture_diagram` was the only document in the corpus whose committed Google row failed
`05_chars_extra` and nothing else: 41/42 on engine `462353f`. Taken through the same round trip on HEAD:

| document | committed Google | measured now | sha256 of export |
|:--|:--|:--|:--|
| `382_architecture_diagram` | 41/42 — fails `05_chars_extra` | **42/42 PASS** | `da518590…54a96c` |

**That is a document moving from failing to clean in Google Docs.** `benchmarks/gverify/382_architecture_diagram.json`
has been updated with the result and its provenance — `engine_fingerprint` from `regress.py`, the export's
sha256, the method, and a real timestamp — which is the shape every Google row should have. `regress.py
--check` passes; Google-clean goes **6 → 7** of 192 scored.

Three of three documents now pass `05_chars_extra` in Google on the current engine where the table says
they fail. The class is not 141 documents of work on HEAD; it is at least partly already done and
unmeasured.
