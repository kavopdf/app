# Verifying against Google Docs' own render

`verify_google.py` compares two PDFs and returns 31 checks. This file is the other
half: how the Google-rendered PDF is produced, in batches, without leaving anything
behind in the user's Drive.

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

    e. python3 tools/p2w-bench/verify_google.py <source.pdf> gd-<name>.pdf --json out/<name>.json

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
