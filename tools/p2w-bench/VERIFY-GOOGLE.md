# Verifying against Google Docs' own render

`verify_google.py` compares two PDFs and returns 31 checks. This file is the other
half: how the Google-rendered PDF is produced, in batches, without leaving anything
behind in the user's Drive.

## THE PATH THAT WORKS (measured 28 Nov 2026) - no s3key, no probe branch needed for the upload

Blocker #5 said "the upload call needs an s3key the s3 key does not belong to this project", and three
runs lost their `.docx` measurement to it. It is not a blocker. Two routes work, and the first needs
nothing but a local file:

    A. LOCAL FILE -> s3key -> Google Doc
       1. copy the .docx into /scratch/output (the platform `upload` tool refuses /scratch/work)
       2. upload(path=/scratch/output/x.docx, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
          -> {name, mimetype, s3key}
       3. GOOGLEDRIVE_CREATE_FILE(name=..., mimeType="application/vnd.google-apps.document",
              parents=["11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6"], file_to_upload={name,mimetype,s3key})
          -> {id}
       Measured: 313_power_of_attorney converted and exported clean this way.

    B. PUBLIC URL -> Google Doc  (the one to use for a BATCH: every call is an MCP tool, so a whole
       probe set runs inside ONE run_program with asyncio.gather)
       1. push the .docx to a probe branch - the corpus PDFs are already public release assets, so
          publishing a converted .docx publishes nothing new. Delete the branch after the measurement.
       2. GOOGLEDRIVE_UPLOAD_FROM_URL(source_url=<raw.githubusercontent.com URL>, name=...,
              mime_type="application/vnd.google-apps.document",
              parent_folder_id="11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6")
          -> {id}            (converts on upload; no s3key involved)
       3. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=id, mimeType="application/pdf")
          -> artifacts[0].workspace_path is the downloaded PDF, already on disk

    12 documents through route B took ONE program call and about 4 minutes, export included.
    The KavoPDF-Verify folder id is 11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6.

    ALWAYS pass --docx to verify_google.py. Without it 53_embedded_faces and 54_image_dpi pass
    unmeasured, and a face change then reads as "42 of 42" when the full instrument says 41/42. That
    exact hole is what made the font-map lead look landed on 27 Nov - see
    FINDINGS/FONT-MAP-REFUTED-53-FORBIDS-ANY-WIDTH-CHANGING-RENAME-28NOV-fixer.md.

## Why the Drive half is not in the script

The Drive calls are MCP operations, not shell commands. A plain Python script cannot
make them. So the pipeline is split:

    run_program  (Drive: upload, create, export, download)
        |
        v
    verify_google.py  (pure PDF comparison, no network)

Keeping the comparison separate means the 31 checks can be run against any pair of
PDFs - a LibreOffice render, a Word render, two versions of the engine - without
touching Drive at all.

## Setup, once

1. Create one folder, **`KavoPDF-Verify`**, at the root of My Drive.
   Record its id; every upload goes into it via `parents: [<id>]`.
   Nothing is ever created at the Drive root.

2. The user deletes their own unrelated documents. This pipeline never touches
   anything it did not create.

## Per document

    a. upload(path=<docx>, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
         -> {name, mimetype, s3key}

    b. GOOGLEDRIVE_CREATE_FILE(
           name      = <document name>,
           mimeType  = "application/vnd.google-apps.document",   # converts on upload
           parents   = [<KavoPDF-Verify folder id>],
           file_to_upload = {name, mimetype: <docx mime>, s3key})
         -> {id}      # the Google Doc

    c. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(
           fileId   = <id>,
           mimeType = "application/pdf")
         -> {file: {s3url}}      # Google's own render

    d. curl the s3url to <work>/gd-<name>.pdf

    e. python3 tools/p2w-bench/verify_google.py <source.pdf> gd-<name>.pdf --docx out1/<name>.docx --json out/<name>.json
       (--docx is REQUIRED. 54_image_dpi, 53_embedded_faces and 37_super_subscript measure nothing
       without it, and 54 scored 'asked and could not answer' as a PASS on twelve documents until
       6bb9111 made it fail loudly.)

    f. delete the Google Doc (see Cleanup)

## Batch size and rate limits

    Google Drive    ~1000 requests / 100 s per user; 3 calls per document
    so 20 documents per run is comfortable and leaves room for retries
    a run of 20 takes roughly 15-20 minutes including the downloads

    If a call returns 403 with "rate limit" or "userRateLimitExceeded",
    wait 60 s and retry that document once. If it fails again, record it as
    SKIPPED - never as PASS. A skipped document is a hole in the result.

## Cleanup

    After every document, delete the Google Doc:
        GOOGLEDRIVE_DELETE_FILE(fileId=<id>)

    Nothing is left in Drive. The folder stays, empty.

    If a run is interrupted, the next run should start by listing the folder and
    deleting anything in it - so an interrupted batch never accumulates.

## Reading the result

    verify_google.py exits 0 when all 31 checks pass, 1 when any fails, 2 when it
    could not run. Treat 2 as a failure, never as a pass.

    Each failure names the check, so defects group by class rather than by document:

        invisible_text      header band drawn in the band's own colour
        text_overlap        two runs on the same baseline box
        blank_where_ink     content the source had and the render lost
        worst_dy            a block placed by an ignored construct
        font_sizes          substitution changed the metrics
        page_count          a construct pushed content onto a second page

    Fix the class, not the document. A per-document patch is how the tool broke
    three times today.

## What this does not see

    It compares the exported PDF to the source PDF. Both are static documents.
    It cannot see:
      - how Google Docs behaves while editing (reflow on typing)
      - whether a text box is caret-editable on the phone
      - the Docs app's own rendering of a construct, as opposed to the export
        path, which is close but not identical

    So a phone check is still the last word. This pipeline is what makes that
    check necessary once per release instead of once per fix.

## Order of work

    1. Run all 208 through this pipeline, unmodified engine. That is the baseline.
    2. Group failures into classes.
    3. Fix the largest class.
    4. Re-run. Repeat until 206/208 pass.
    5. Record the last 2 with the reason they cannot pass.
