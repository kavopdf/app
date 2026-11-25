# The Google loop, and the one thing a sandbox cannot do

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
