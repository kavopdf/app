# The Google loop, and the one thing a sandbox cannot do

> **CORRECTED 25 Nov 2026, fixer slot 16:26 IST — there is no missing step. Read this box before the rest of
> the file, which is kept because its measurements of steps 2-4 still hold.**
>
> Two measurements, both taken this run:
>
> 1. **The `.docx` are already in Drive.** `GOOGLEDRIVE_FIND_FILE` over the corpus folder
>    `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` returns **213 distinct `.docx` names, 213 files**, created
>    04:46 IST today. Step 1 of `refresh-google.py` is satisfied. Nothing has to be uploaded for the loop
>    to run; `python3 refresh-google.py --folder 1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` is the whole loop.
> 2. **The platform `upload` tool does return an `s3key` from a sandbox path**, which is what the section
>    below says no sandbox can get. Measured end to end on `303_discharge_summary.docx`:
>    `upload(toolkit="googledrive", tool_slug="GOOGLEDRIVE_UPLOAD_FILE", path=<a file in /scratch/output>)`
>    -> `s3key: project_scope/ok_MI5WEzhyITR7/pr_qSx6sTyshHxf/files/gtabbu3786i1.docx` ->
>    `GOOGLEDRIVE_UPLOAD_FILE(file_to_upload={name, mimetype, s3key}, folder_to_upload_to=<corpus folder>)`
>    -> a real Drive file id. Two constraints: the path must be a **saved** file (`/scratch/output`; a path in
>    `/scratch/work` is rejected), and `folder_to_upload_to` must be given or the file lands in the Drive root,
>    which the rules forbid.
>
> That upload created a **duplicate** of a name that already existed, because the file was already there. The
> duplicate was trashed again (recoverable) and the folder is back to 213. **Do not upload a document that is
> already in the folder** — check `GOOGLEDRIVE_FIND_FILE` first, or you will hand `refresh-google.py` two files
> with one name.
>
> See `FINDINGS/18_displacement-25-SOLO-A-B-C-CENSUS-25NOV-1626-fixer.md` for the raw numbers.

## One command now does the whole thing

    python3 tools/p2w-bench/refresh-google.py --folder 1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA

It finds every corpus document whose verdict is not stamped with the engine on disk, copies the .docx
with `mimeType=application/vnd.google-apps.document` (which is how Drive converts it into a Google Doc),
exports each as a PDF render, scores source against render, and writes the verdict with the engine hash.
Measured end to end today: 213 of 213 converted, 213 of 213 exported, 212 of 213 scored, 1 refused.

That is the loop that was missing. It is why the verdicts said `0 of 191 are from this engine` and why
no patch could ever show an improvement.

## The one step a sandbox cannot do

Putting the .docx INTO the Drive folder. Every upload tool demands `file_to_upload.s3key`, described as
"returned from a previous download action that stored the file in S3". A local path is rejected outright:

    The file key does not belong to this project or session.
    The file with s3key '/scratch/work/p2w/out/72_....docx' ...

A Drive download returns `artifacts[].workspace_path` and no s3key, so nothing the sandbox creates can
be uploaded. Measured, not assumed.

The only route that works without platform work is `GOOGLEDRIVE_UPLOAD_FROM_URL`, which needs the .docx
at a publicly reachable HTTPS URL and takes `mime_type=google-apps.document` to convert on arrival. A
Netlify site exists for exactly this - `p2w-gverify-tmp`, id `42cd33c4-8a6a-4823-882f-4dbefc5a6b5f` - but
it has `requiresSSOTeamLogin: true`, so a server-side fetch is refused. The Netlify API is also not on the
sandbox egress allowlist (`network:host:api.netlify.com` -> not_allowlisted), so it cannot be deployed to
from bash either.

## What that means in practice

    .docx in Drive  ->  everything after that is one command, no human
    .docx not in Drive  ->  one of these is needed:
        - visitor access opened on p2w-gverify-tmp (one toggle, then fully automatic)
        - platform staging of a local file into an s3key
        - the zip dropped into Drive by hand

Nothing else in the loop touches a human, and no file leaves the user's own Drive on the current path.
