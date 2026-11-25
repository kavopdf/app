# The platform upload's s3key expires in minutes - upload and convert must stay together

Measured 26 Nov 2026, the gverify run at 03:28 IST.

## What happened

The run uploaded fifty `.docx` files through the platform `upload` tool (one call per document, not
batchable), collected the fifty `s3key` values, and then ran one `run_program` that called
`GOOGLEDRIVE_CREATE_FILE` for each. All fifty failed with

    GOOGLEDRIVE_CREATE_FILE: The connected-service operation returned an error:
    IO error occurred while retrieving or processing file content

The keys were between ten and twenty minutes old. The same call with a key obtained one minute earlier
succeeds, and a key two minutes old also succeeds.

## What it is not

* Not concurrency. `asyncio.gather` with a semaphore of 6 failed; a serial loop over three
  twelve-minute-old keys failed the same way, in under a second each.
* Not the file. The same document re-uploaded and converted immediately works.
* Not Drive's rate limit. The failure is in fetching the staged bytes, before Drive is called.

## What to do instead

Upload and convert in the same small batch - six to nine documents - so no key is more than a couple of
minutes old when it is used:

    upload(path=..., tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")   # per document, in the turn
    run_program: GOOGLEDRIVE_CREATE_FILE(file_to_upload=<that key>) -> GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE

That is nine upload calls and one program per batch, about four minutes per nine documents. The
one-upload-per-document ceiling is unchanged; what this rules out is a bulk upload followed by one bulk
convert.

## Second finding, same run: the LibreOffice half is not stamp-checked

`collect_lo()` returns "already have it" when `benchmarks/gverify-lo/<name>.json` exists, whatever engine
wrote it. After the engine moved, all two hundred and thirteen committed LibreOffice results carried the
old stamp and `--lo` would not re-measure any of them. They were refreshed this run by calling the same
two steps `collect_lo()` calls - `soffice --headless --convert-to pdf`, then `verify_google.py --docx ...
--json ...` - writing into `/scratch/work/p2w/lo-res/` and copying over the committed files. Sixty
documents now carry the current stamp on both sides.

`gverify.py --report` and `stage.py` filter Google results by engine stamp; `collect_lo()` does not, and
`cronreport.py` counts every committed `.json` as measured (it printed "211 of 213 measured" while
`stage.py` printed 60). Both are the same defect `_done()` was written to fix on the Google side.
