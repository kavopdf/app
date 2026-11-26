# The Google loop works from a fresh pod - and the one step that stopped three runs is a copy

**26 Nov 2026, fixer slot 10:54.** Measured end to end on `31_times_body_arial_headings`.

## What was believed

Three findings and the 26 Nov sub-agent report record that the Google after-side cannot be measured
from the sandbox: `GOOGLEDRIVE_UPLOAD_FILE`, `GOOGLEDRIVE_CREATE_FILE` and a resumable upload all
refuse with *"file key does not belong to this project or session"* (403), from several path forms and
from inside `run_program`. Runs therefore measured LibreOffice and called it a proxy.

## What I measured

The 403 is not a permission problem and not an egress problem. The platform `upload` tool will only
stage a file that is **already a saved file**, and the only saved locations are `/scratch/output`,
`/scratch/input`, `/scratch/saved` and `/scratch/downloads`. A `.docx` staged under
`/scratch/work/p2w/out/` - which is where `gverify.py --stage` puts it - is refused by `upload`
before any Drive call is made, and the refusal surfaces as the Drive tool's 403.

The working sequence, verbatim, one document:

    cp /scratch/work/p2w/out/<name>.docx /scratch/output/<probe>.docx
    upload(path="/scratch/output/<probe>.docx",
           tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
      -> {"name":..., "mimetype":..., "s3key":"project_scope/.../files/xxxx.docx"}
    GOOGLEDRIVE_CREATE_FILE(name=..., mimeType="application/vnd.google-apps.document",
                            parents=["1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij"],
                            file_to_upload={name, mimetype, s3key})
      -> {"id":"1JsEQ...", "display_url":"https://docs.google.com/document/d/.../edit"}
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf")
      -> artifacts[0].workspace_path = "/scratch/downloads/composio/<probe>.pdf"
    python3 tools/p2w-bench/gverify.py --collect <name> /scratch/downloads/composio/<probe>.pdf
      -> 31_times_body_arial_headings  GOOGLE 41/42  fail: 18_displacement

Every step returned `ok:true`. The verdict reproduced the stored verdict for that document exactly
(41/42, `18_displacement`, med_dy 2.6, worst_dy 3.5), so the round trip is measuring the right bytes.

## What is now true

1. **The Google after-side is measurable in this pod.** No permission was granted between the runs
   that recorded the wall and this one; the wall was a staging-path rule, not an access limit.
2. **`gverify.py --stage` writes to a path `upload` refuses.** That is the tool's defect, and it is
   why the loop looked closed. Until `--stage` is changed, every caller must copy to `/scratch/output`
   itself. The docstring now says so.
3. A sub-agent cannot be assumed to find this: the 26 Nov sub-agent burned its Google-after budget
   against the 403. Give it the copy step explicitly.

## What would prove this wrong

A document whose `upload` succeeds from `/scratch/output` and whose Drive create still 403s. Not seen
on the one document measured here.
