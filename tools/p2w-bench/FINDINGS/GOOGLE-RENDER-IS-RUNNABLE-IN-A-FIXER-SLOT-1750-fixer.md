# The Google render IS runnable from a fixer slot, and PENDING-NOW.md says it is not

**Recorded:** 2026-11-23 17:50 IST, fixer slot 17:00. Measured, not argued.

## The claim this refutes

`tools/p2w-bench/PENDING-NOW.md` opens with:

> The short version: **nothing on this list can be closed without `java`.** The agent's sandbox
> has no `java` and no `scipy`, so it cannot build the engine, cannot convert, and therefore
> cannot measure.

and `LESSONS.md` treats the JDK as a lucky find:

> `java` was not on PATH until `build-engine.sh`'s JDK at /scratch/work/.p2w-jdk/jdk was exported

Both read as "a run may or may not be able to measure". A run can always measure. The sandbox has
no `java`, but it has network to `github.com` and to `repo1.maven.org`, and that is enough.

## The recipe, end to end, timed on this slot

Every step below was run in this run's sandbox. Times are wall clock.

    1. JDK 17, 34 s
       curl -sSL -o jdk.tar.gz https://github.com/adoptium/temurin17-binaries/releases/download/\
         jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz     # 192 MB
       mkdir -p /scratch/work/.p2w-jdk && tar xzf jdk.tar.gz -C /scratch/work/.p2w-jdk
       mv /scratch/work/.p2w-jdk/jdk-17* /scratch/work/.p2w-jdk/jdk

    2. PDFBox + BouncyCastle, from repo1.maven.org, ~10 s
       the four curl lines already in tools/verify-engine.sh, into tools/engine-verify/libs
       (plus `unzip -oq libs/pdfbox.aar -d libs/aar`)

    3. Android stubs + engine, 28 s
       javac -nowarn -d out $(find stubs -name '*.java')
       javac -nowarn -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
             -d out $(find ../../app/src/main/java -name '*.java')

    4. ConvertOne + ConvertAll, ~5 s, and one document converts in ~15 s
       java -cp "$CP" ConvertOne <in.pdf> <outDir>

    5. The corpus, from the corpus-v1 release, ~30 s
       gh release download corpus-v1 --repo kavopdf/app --pattern '*.zip'
       -> 211 PDFs

    6. THE GOOGLE RENDER, 3 Drive calls per document, ~60 s
       a. upload(path=<docx in /scratch/output>, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
       b. GOOGLEDRIVE_CREATE_FILE(mimeType="application/vnd.google-apps.document",
                                  parents=["11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6"], file_to_upload=...)
       c. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=..., mimeType="application/pdf")
          -> artifacts[0].workspace_path, a LOCAL path (not an s3url)
       d. python3 tools/p2w-bench/gverify.py --collect <name> <that path>
       e. GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION(fileId=...)

    The upload in (a) refuses any path outside /scratch/output — that is the one platform rule
    that has to be respected, and it is one `cp`.

## Two things that are easy to get wrong

- **`gverify.py --collect` needs `/scratch/work/p2w/corpus/<name>.pdf` and
  `/scratch/work/p2w/out/<name>.docx` to exist** (gverify.py:48-49). Without them it prints
  "missing source or docx" and exits 2, which reads like a credential problem and is not one.
- **`_write()` in gverify.py drops the provenance fields.** A collected row loses
  `engine_fingerprint`, `export_sha256`, `measured` and `method` that a hand-recorded row carries.
  Restore them after the collect or the table loses the only record of what was measured.

## What it bought, in this slot

Two rows re-measured on HEAD `b7699196` (both were on `462353f`/`462353f9`):

| document | was | now | cleared |
|---|---|---|---|
| `bank-statement-5-pages` | 40/47 | **42/47** | `05_chars_extra`, `32_stroke_lines` |
| `mobile-bill` | 46/47 | 46/47 | — (confirmed on HEAD, no change) |

`bank-statement-5-pages` moving 40 -> 42 on HEAD is a real two-check gain the pipeline did not know
it had, because the table was reporting the old engine. It also says HEAD is not worse on either
document, which is the check `regress.py` cannot do without a fresh row.

`mobile-bill` is worth noting for a second reason: at HEAD it fails **one** check, `18_displacement`,
and nothing else. It is a clean single-construct test case for the largest class in the corpus.

## The next run should

Not re-derive this. Run step 1-3 once at the top of the slot (about 90 s in total), then measure
every candidate change in Google before recording it, on 2-3 documents, instead of measuring in
soffice and hoping. A fixer run that measures in Google is a fixer run whose numbers are the truth.
