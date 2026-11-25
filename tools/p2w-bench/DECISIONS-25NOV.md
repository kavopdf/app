# Three decisions, taken 25 Nov

## 1. The upload path: the user drops the .docx into their own Drive (option E)

**Why this matters.** `preflight.py` reports `0 of 191 verdicts are from this engine`. The verdicts
describe b7699196; the corpus on disk is 981ff1fa. So a fixer patch changes the engine, the corpus
rebuilds, the verdicts are not re-measured, the clean count cannot move, and the attempt reads as
`moved=0` whether it helped or not. This is the most likely mechanical reason 218 attempts produced 0
kept changes.

**Options that were rejected, and why:**

- *Publish the .docx at a public URL* (GOOGLEDRIVE_UPLOAD_FROM_URL). The corpus IS the benchmark.
  Publishing it hands over the test set - more than the 1% competitive edge the user's rule protects.
- *Publish three files* for the `w:line="1"` experiment. Not needed: the repository already answers it
  (240ths of a line, ~0.78 pt, and `18_displacement-CORRECTION-1045-relay.md` withdrew the 14.4 pt
  reading). Three files of exposure for a question that is closed.
- *Wait for platform staging of the s3key.* Zero exposure, but indefinite. The user has said they will
  not keep exchanging access back and forth.

**Chosen:** the user unzips `kavopdf-verify-213-docx.zip` into their own private `KavoPDF-Verify`
Drive folder. Zero exposure - the files stay in the user's own Drive - no platform work, and it
unblocks today. Then the exports and the checks are run from the sandbox, which already works (213 of
213 renders were exported that way).

## 2. The 43 overlay documents: accept them for now

43 documents carry overlays that would need a NEGATIVE before-gap - 96 to 446 pt on the certificates
and ring text - and a flow cannot express a negative gap. Route (c) does not cover them.

**Chosen: accept.** There is no measured route, and spending two or three days on a mechanism that may
not exist is the wrong priority while 170 documents have clean work left on them. Revisit after the
170 are done.

## 3. The APK: not yet

The rule is "fix everything, then ship". Docs are 36 of 191 clean and the median pixel SSIM is 88.59%.
An APK now would ship a product that half works.

**Chosen: not yet.**

## What these three decisions change

Decision 1 unblocks the verdict restamp, which unblocks route (c) landing and the `18_displacement`
table-row fix. Decision 2 removes 43 documents from the plan. Decision 3 leaves the APK where it was.
