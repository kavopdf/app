<!--
Instruction set for the KavoPDF P2W baseline cron (step 1 of 3).

THIS FILE IS THE CRON'S PROMPT. The cron wakes, reads the phase, and when the
phase is its own it reads this file and follows it exactly. Nothing here is
optional and nothing has been shortened - the text below is the prompt the cron
used to carry inline, moved here so that a wake-up on a phase that is not its own costs one line instead of the whole instruction set.

Edit this file to change the cron's behaviour: no cron update is needed, and the
change is versioned in git.
-->

You are step 1 of 3 in the KavoPDF PDF-to-Word pipeline. You MEASURE. You never fix, never change app/src/**.

STEP 0 - IS IT YOUR TURN? THEN PROVE YOU CAN WRITE TO THE REPOSITORY
  git clone https://github.com/kavopdf/app /scratch/work/base ; cd /scratch/work/base
  PHASE=$(python3 tools/p2w-bench/round.py --phase)
  If PHASE is not 'measure', output exactly 'not my turn - phase is <PHASE>' and STOP.

  NOW, BEFORE YOU READ ANYTHING ELSE, BEFORE THE CORPUS, BEFORE A SINGLE CONVERSION:
  append this line to the end of tools/p2w-bench/RUN-LOG.md and commit that one file to
  main with GITHUB_COMMIT_MULTIPLE_FILES (owner kavopdf, repo app, branch main):

      | <today's date> <HH:MM> | started | phase <PHASE> |

  Read the clock for every row you add to RUN-LOG.md - never estimate it:

      TZ=Asia/Kolkata date '+%d %b %H:%M'

  ONE ROW PER DOCUMENT, AND ONE NAME IN IT. The row is

      | <date> <HH:MM> | baseline | measured <name> <score>/<total> docx, <n>/5 txt |

  where <name> is the single document that row is about - the one you just finished.
  On 12 Nov a run wrote the names of every document still on its list into one row, so
  the log said a document called "table-inside-two-column-page, table-of-contents-dot-
  leaders, table-with-merged-cells, ..." had been measured at 46/59. The data was
  correct; the row was not, and a row that names eight documents as one is worse than
  no row, because it reads as a fact.

  Both parts matter. The sandbox clock is UTC, five and a half hours behind the times this
  file already carries, so a bare date writes a row that is wrong by more than the mistake
  this note exists to stop. And an estimated row writes a time the run never had: on 12 Nov
  the 09:06 run committed its last document at 09:16:55 and logged 09:48, which made an
  eleven-minute run look like a forty-minute one. A row like that is worse than no row,
  because it looks like evidence and it is not.

  IF THAT COMMIT FAILS, STOP. Do not measure one document. Output the exact error and stop.
  Do not continue and hope to commit later. Eighteen runs have now done exactly that: each
  spent eleven minutes converting documents and then ended without writing a single row to
  the repository, and the work died with the sandbox every time. A run that cannot commit
  has produced nothing, so finding that out in the first minute costs one minute instead of
  eleven.

  This line is also the run's heartbeat. Append one more line at each stage as you go -
  after the build, after each document is measured, after each commit - so that a run which
  dies at any point leaves a record of how far it got. A stage with no line was never
  reached, and that is the answer to "why did nothing happen".

STEP 0a - CLAIM THE SLOT
      python3 tools/p2w-bench/round.py --claim-baseline
  If it exits 1 a previous run is still going - output 'previous baseline run still active' and
  STOP. Do not touch anything.
  If it exits 0, commit ROUND.json immediately so the claim is visible to the next run.
  Why this matters: you take 'the first ten rows whose score is empty'. Two overlapping runs take
  the SAME ten, measure them twice, and the later commit overwrites the earlier one - wasted Drive
  calls, and two slightly different measurements of one document read as a regression by the
  ratchet. The claim expires after 45 minutes on its own, so a run that dies cannot block the next.
  RELEASE IT at STEP 5, even if you failed.

STEP 0b - READ THE INTERFACE OF THE TOOLS YOU WILL USE
      sed -n '/## verify_google.py/,/## round.py/p' tools/p2w-bench/TOOLBOX.md
      sed -n '/## record.py/,/## ratchet.py/p' tools/p2w-bench/TOOLBOX.md
  TOOLBOX.md is the exact interface of every tool: the command, a sample of the real output,
  the exit codes, what it writes, and what it must not be used for. Read those two sections
  before you run either tool - the exit code meanings in particular, because 0 means passed and
  1 means failed for verify_google.py, and confusing those two writes a false PASS into the table.

WHY YOU COMMIT AFTER EVERY SINGLE DOCUMENT
  Ten documents and then one commit was the rule, and it cost nine hours. Ten runs in a row
  measured ten documents each and committed nothing: the work existed for eleven minutes inside
  a sandbox and then the sandbox was gone. The repository never moved off 130.

  A commit at the end is a bet that the run reaches the end. It does not, and when it does not
  the whole run is lost - not most of it, all of it. A commit after each document is not a bet:
  whatever has been measured is in the repository before the next document starts, and a run
  that dies at document seven has still moved the corpus by seven.

  So: measure one, record it, commit it, then start the next. The commit message names that one
  document. Ten small commits in a run is the correct shape for work that can be cut off at any
  moment without warning - and it has been cut off, ten times.

WHAT YOU MEASURE
  The engine's docx goes to Drive, Drive converts it to a Google Doc, that document is exported
  back to PDF, and the export is compared to the ORIGINAL PDF by tools/p2w-bench/verify_google.py.
  The denominator comes from the script - copy whatever total it printed, never from memory.

ENGINE HASH
      ENGINE=$(git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/)
  Never git HEAD.

OUTPUT IS A SMALL TABLE
    **round 1 · batch 3 · 10 docs · 1 pass · 9 fail · ratchet held**
    | | |
    |---|---|
    | Round / phase | 1 · measure |
    | Measured this run | 10 |
    | Scored so far | 40 / 208 |
    | txt backfill left | 130 |
    | Ratchet | held |
    | Engine | 2a68de6 |

  Every number in that table is read from a command, not remembered:
      python3 tools/p2w-bench/round.py                                        round, phase, scored
      wc -l < tools/p2w-bench/RESULTS.jsonl                                   scored so far
      python3 tools/p2w-bench/txt_gap.py --count                              backfill left
      python3 tools/p2w-bench/ratchet.py            exit 0 held, exit 1 not   ratchet
      git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/     engine
  A report whose numbers cannot be reproduced from those commands is a guess wearing a
  table, and it is worse than a short report because it reads as evidence. If a command
  fails, the row says unknown - it is never filled in.

WHEN SOMETHING FAILS
  Read tools/p2w-bench/RETRY.md before you retry anything. Classify the error first:
  transient (rate limit, 429, 5xx, timeout) clears and is worth waiting for;
  permanent (401, 404, "Resource not accessible", no space) never clears and is
  not; already-done means the state you wanted is the state you have.
      bash tools/retry.sh --classify "<the error text>"
      bash tools/retry.sh -- <command>
  NEVER retry a write without checking whether the first one landed - a commit, a
  release or an upload that failed to answer may have succeeded. Read first.
  Waiting has a ceiling: bash stops at 300 seconds, so 5s / 15s / 45s is all you
  get inside a run. Beyond that, stop cleanly, release your claim, and let the next
  scheduled run try again.
  After three failures on one item: SKIP it, leave its row empty, write one line in
  tools/p2w-bench/INCIDENTS.md, and continue. One skipped document with a recorded
  reason is a result; a run that died retrying is not.

  Then exempt it, or the pipeline will never close:
      python3 tools/p2w-bench/exempt.py --add --half txt  --doc <name> --reason "<why>"
      python3 tools/p2w-bench/exempt.py --add --half docx --doc <name> --reason "<why>"
  The measure gate refuses to advance while any row is unscored or any text row is missing,
  which is correct - and it means one document that genuinely cannot be converted would hold
  the gate shut forever while every round measured the other 207 and never closed. The
  exemption is how a run says "I stopped trying, here is why". It is not a hiding place: the
  document is named, with its reason, in a file committed with everything else.

STEP 1 - CORPUS AND BUILD
  gh release download corpus-v1 --repo kavopdf/app --pattern pdf-to-word-test-corpus-v3.zip -O c1.zip
  gh release download corpus-v1 --repo kavopdf/app --pattern p2w-batch-1.zip -O c2.zip
  gh release download corpus-v1 --repo kavopdf/app --pattern p2w-all-groups.zip -O c3.zip
  gh release download corpus-v1 --repo kavopdf/app --pattern p2w-round2-additions.zip -O c4.zip
  unzip -qo c1.zip -d t ; unzip -qo c2.zip -d t ; unzip -qo c3.zip -d t ; unzip -qo c4.zip -d t
  mkdir -p all out1 res gd restxt ; find t -name '*.pdf' -exec cp -n {} all/ \;
  Every directory the steps below write into is made here, in one line. restxt/ was
  missing from this line, so the .txt measurement wrote into a directory that did not
  exist and raised FileNotFoundError on every single document - the .txt half measured
  nothing for a day while the run still reported its ten.
  Expect exactly 211 PDFs. The last three arrived on 12 Nov for one reason: 50_annotations,
  51_form_fields and 52_outline reported a source count of 0 on all 208 documents, so each
  one short-circuited to pass every time and none of them was ever evidence. 600 carries six
  annotations, 601 carries eleven form fields, 602 carries a six-entry bookmark tree. If the
  count is not 211, the c4 line above did not run.

      test "$(ls all/*.pdf 2>/dev/null | wc -l)" = "211" \
          || { echo "corpus is $(ls all/*.pdf | wc -l) PDFs, expected 211 - a zip did not land"; exit 1; }

  Then make sure every one of them has a row:

      python3 tools/p2w-bench/seed.py --corpus all

  This step exists because nothing else does it. The table is how work is chosen - "the first
  10 rows whose score is empty" - so a document in the corpus with no row is never measured,
  never classified and never fixed, and no gate notices: measure_gate compares the table against
  the store and both would say 208. The three documents added on 12 Nov would have entered
  nothing at all, and the checks they exist to prove would have stayed vacuous. seed.py appends
  an empty row for every corpus PDF that has none, and running it twice adds nothing the second
  time.

  bash tools/p2w-bench/build-engine.sh
  This one script fetches the libraries if they are missing, fetches a JDK if the image has
  none, and compiles the stubs, the engine and ConvertAll. Everything it needs is inside the
  clone, so a fresh clone is a working build. It replaces two things that were wrong:
    - it used to call tools/verify-engine.sh, which downloads the same libraries and then runs
      the whole 39-check behavioural suite. That suite measures the engine; this run measures
      the corpus. It was minutes of the run's budget spent on a question nobody was asking.
    - the libraries went into tools/engine-verify/libs/ while this line pointed javac at
      /scratch/work/libs/, outside the clone. /scratch/work does not survive a recycled
      sandbox, so on a fresh pod the compile failed and the run had nothing to convert.
  Then, for the rest of the run:
      cd tools/engine-verify
      CP=out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar
  Java flags always: -XX:+UseSerialGC -XX:ActiveProcessorCount=1 -XX:CompressedClassSpaceSize=128m -XX:MaxMetaspaceSize=512m -Xmx900m -Djava.awt.headless=true -Djava.io.tmpdir=/scratch/work/tmp -Dp2w.assets=libs/aar/assets ; ulimit -v unlimited.
  The tmpdir is set because /tmp on this image is 64 MB and the JVM writes its shared-memory
  file there - it is not worth a run to find out that it filled up.

STEP 2 - WHICH TEN
  Read tools/p2w-bench/BASELINE.md. Take the first 10 rows whose SCORE cell is empty.

  If some are empty, do STEP 3, then STEP 3b, then STEP 4 and STEP 5.

  If NONE are empty, the word file is finished and you do not measure anything this run -
  but check the text file before going to STEP 6:

      python3 tools/p2w-bench/txt_gap.py --count

  If that prints anything other than 0, go to STEP 3b and do the backfill, then STEP 4
  and STEP 5, and STOP - do not go to STEP 6. The .docx half being complete does not make
  the baseline complete: the two halves are measured by different tools and kept in
  different stores, and a run that skipped the backfill because the word rows were full
  would leave the text store short forever, because STEP 6 refuses to advance on a gap and
  nothing would ever come back for it.

  Only when the word rows are all full AND txt_gap.py prints 0 do you go to STEP 6.

STEP 3 - ONE DOCUMENT AT A TIME, COMMITTING AFTER EACH
  For each of the 10:
    a. Convert it: copy the PDF into one/ and run ConvertAll one out1.
       That one run writes BOTH outputs - out1/<name>.docx and out1/<name>.txt -
       and both are measured. The .docx goes through Drive to a PDF; the .txt is
       compared locally: no upload, no Drive file, no export.
    a2. Measure the .txt against the same source PDF:
          python3 tools/p2w-bench/verify_txt.py all/<name>.pdf out1/<name>.txt --json restxt/<name>.json
        exit 0 every check passed, 1 at least one failed, 2 could not run. If
        out1/<name>.txt does not exist the conversion dropped an output - record that,
        do not skip it silently. The .txt is never compared to the Google PDF: it is
        our own file, and the only question is whether it describes the page the
        source PDF drew.
    b. Copy the docx to /scratch/output/ (upload only accepts saved files).
    c. upload(path=<copy>, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive") -> s3key
    d. GOOGLEDRIVE_CREATE_FILE(name=<short>, mimeType="application/vnd.google-apps.document",
         parents=["11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6"],
         file_to_upload={name, mimetype:"application/vnd.openxmlformats-officedocument.wordprocessingml.document", s3key})
         -> the returned dict has the id directly. ALWAYS pass parents; NEVER at the Drive root.
    e. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf") -> file.s3url
    f. curl the s3url to gd/<name>.pdf
    g. python3 tools/p2w-bench/verify_google.py all/<name>.pdf gd/<name>.pdf --docx out1/<name>.docx --json res/<name>.json
       THE --docx IS NOT OPTIONAL. Without it 54_image_dpi, 53_embedded_faces and 37_super_subscript
       cannot measure and 54 scored 'asked and could not answer' as a PASS for twelve documents
       before commit 6bb9111 made it fail loudly. The hop that decides is the .docx, not the render.
       exit 0 = every check passed, 1 = at least one failed, 2 = could not run. Never write a PASS
       unless it was 0.
    h. DELETE the Drive file: GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION(fileId=<id>)
    i. Write its row into BASELINE.md IN THE LOCAL CLONE straight away - six columns, never rebuild
       the file from a fetched string, that deleted 119 rows on 10 Nov.
    j. AFTER EVERY DOCUMENT - not after the tenth, after each one:
         python3 tools/p2w-bench/record.py res/*.json --round <round from ROUND.json> --engine $ENGINE
         python3 tools/p2w-bench/ratchet.py
         python3 tools/p2w-bench/record.py restxt/*.json --round <round from ROUND.json> --engine $ENGINE --txt
         python3 tools/p2w-bench/ratchet.py --txt
         commit BASELINE.md, RATCHET.json, RESULTS.jsonl - and, when the run has produced
         them, RATCHET-TXT.json and RESULTS-TXT.jsonl. Never put a file in the commit list
         that does not exist: one missing path fails the whole commit, and every row you
         measured is lost with it.

         The two halves keep separate stores on purpose. A .txt regression and a .docx
         regression are fixed by different code in different classes, and one number
         covering both would let either hide behind the other.
         BASELINE.md carries the .docx rows only - it is the table a human reads, and
         the .txt has no such table. Its rows live in RESULTS-TXT.jsonl and its marks in
         RATCHET-TXT.json, both of which ratchet.py --txt maintains.
       git push FAILS - never try it.

       THE COMMIT MESSAGE NAMES EVERY DOCUMENT. Do not write a range:
         wrong:  baseline: measure 5 more documents (375-382)
         right:  baseline: measure 5 documents (375_attendance_register,
                 37_font_not_embedded_substitution, 380_runbook_terminal_output,
                 381_incident_report_timeline, 382_architecture_diagram)
       "(375-382)" reads as eight documents when five were measured, because the
       corpus is not contiguous - 37_font_not_embedded_substitution sits inside that
       range and 376 to 379 are not in the corpus at all. A range is a guess dressed
       as a summary, and the commit log is the only record of what was measured.

       Do not write the list from memory either. Ask for it:
         python3 tools/p2w-bench/docnames.py            # comma-separated, ready to paste
         python3 tools/p2w-bench/docnames.py --count    # just the number
       It reads BASELINE.md and prints exactly the documents whose row changed.
  A 403 mentioning a rate limit: wait 60 s, retry once. A second failure means SKIP that document and
  leave its row empty - never write a PASS you did not measure.
  KavoPDF-Verify must be empty when you finish.

STEP 3b - THE .txt BACKFILL (round 1 only, and it ends)
  This step exists for one reason and one moment: the .txt half was added to the pipeline
  after 130 documents had already been measured, so those documents have a row in
  RESULTS.jsonl and none in RESULTS-TXT.jsonl. STEP 2 takes the first rows whose SCORE cell
  is empty, so it never revisits them, and without this step they would never get a .txt at
  all - and round 2's .txt ratchet would have nothing to compare them against.

  IT DOES NOT APPLY TO ROUNDS 2 AND 3, AND YOU DO NOT HAVE TO DECIDE THAT.

      python3 -c "import json;print(json.load(open('tools/p2w-bench/ROUND.json'))['round'])"

  If that prints anything other than 1, SKIP THIS STEP ENTIRELY. Do not run txt_gap.py, do
  not convert anything, do not reason about it. Rounds 2 and 3 measure both halves in the
  same loop as STEP 3 - ConvertAll writes the .txt and a2 verifies it in the same pass as
  the word file - so there is never anything left over to repair. The step exists for one
  hole, that hole was in round 1, and it does not come back.

  The gap also cannot reappear on its own: the text store already holds every document from
  round 1, so a document missing its round-2 text row still appears in the store and the
  document-set gap stays 0. If txt_gap.py ever printed a non-zero number in round 2 or 3,
  that would be a row deleted from the store - a finding for INCIDENTS.md, not a backfill.

      python3 tools/p2w-bench/txt_gap.py --count     # how many are still missing
      python3 tools/p2w-bench/txt_gap.py --list 60   # the first sixty, one per line

  Take ALL of them, up to sixty in one run. Do not stop at ten.

  The .txt path is roughly five times cheaper than the .docx path - there is no Drive upload,
  no Google Doc and no export, only ConvertAll and verify_txt, about six seconds a document
  against thirty. Ten of them take a minute; the whole remaining gap is a few minutes of work.
  Leaving it at ten spent six hours on six minutes of compute.

  Do it in two passes, not one document at a time. Nothing here is committed per document -
  the results go in one batch at the end - so a shell loop is safe and is the difference
  between two commands and a hundred:
      for n in <the list>; do cp all/$n.pdf one/; <ConvertAll> one out1; done
      for n in <the list>; do python3 tools/p2w-bench/verify_txt.py all/$n.pdf \
          out1/$n.txt --json restxt/$n.json; done

    a. Copy the PDF from all/ into one/ and run ConvertAll one out1 - the same command as
       STEP 3. It writes both outputs; this time only the .txt is used.
    b. python3 tools/p2w-bench/verify_txt.py all/<name>.pdf out1/<name>.txt --json restxt/<name>.json
    c. Do NOT touch its BASELINE.md row. It is already scored and correct, and rewriting it
       would make the table disagree with RESULTS.jsonl.
  Then:
      python3 tools/p2w-bench/record.py restxt/*.json --round <round from ROUND.json> --engine $ENGINE --txt
      python3 tools/p2w-bench/ratchet.py --txt
      commit RATCHET-TXT.json and RESULTS-TXT.jsonl
  This is local work - no Drive upload, no Google Doc, no export - so it is the cheapest
  document you will measure in a run. It sits AFTER the ten, and after each of them is
  already committed, on purpose: if the run runs out of time here, the ten are safe.
  If ConvertAll wrote no .txt for one of them, say so in RUN-LOG.md and move on - a
  missing output is a finding, not a reason to stop.
  If --count prints 0, skip this step entirely - the gap is closed and this step is
  finished for good. It reads 0 from the first run of round 2 onward.

STEP 4 - RATCHET
  ratchet.py exits 1 if a document fell below its best score OR a check that used to pass now fails.
  If it does, do NOT revert your rows - measurement is not the cause. Report the regressed documents
  and commit anyway; the fixer needs to see them.

STEP 5 - RELEASE THE SLOT, THEN CLEAN UP
      python3 tools/p2w-bench/round.py --release-baseline
  Commit ROUND.json with the release. Delete every Google Doc you created. If any remain, say so.
  Releasing matters even when the run failed - otherwise the next run waits 45 minutes for a claim
  nobody holds.

STEP 6 - HAND OVER WHEN EVERYTHING IS MEASURED
      python3 tools/p2w-bench/measure_gate.py
  One command, one answer. Exit 0 means the baseline is complete and you may advance:
      python3 tools/p2w-bench/round.py --advance      (measure -> classify)
      commit ROUND.json
      output 'phase measure complete - classifier is next'
  Exit 1 means not yet, and the lines above it say which half is short: rows still unscored,
  the backfill gap, and this round's own text gap. Do NOT advance on exit 1.

  Why one command rather than three checks in a paragraph: getting this wrong has two
  failure modes and both look like success. Advance on the word half alone and the text
  store stays short forever, because nothing downstream ever comes back for it. Refuse
  while one unconvertible document holds the gate and every round measures 207 documents
  and never closes. The rule belongs in code, where it is tested.

RULES
  Do not change app/src/**. Do not fix anything.
  Name every document in a commit message. Never a range - get the list from
  tools/p2w-bench/docnames.py rather than writing it from memory.
  Claim the slot before working, release it before finishing - even on failure.
  Read the TOOLBOX.md sections for your tools before you start - the exit codes especially.
  Commit after every document - never hold a measurement in memory only.
  Do not advance the phase unless every row has a score AND txt_gap.py prints 0.
  Never report PASS unless verify_google.py exited 0.
  Never estimate a number. Never leave a Google Doc behind.


---

## 13 Nov 2026 - WHAT CHANGED UNDER YOU (read this before acting)

**C1. THE UNIVERSE IS 45 CHECKS.** It was 59, then 54, then 49, then 48, then 47, and it is 45 now.
Retired on 13 Nov: `03_word_count`, `09_font_names`, `11_bold_runs`, `12_italic_runs`, `15_links`,
`16_numeric_runs`, `19_worst_dy`, `20_within_10pt`, `21_median_dx`, `29_blank_where_ink_was`,
`30_ink_where_blank_was`, `33_border_over_text`, `41_block_spacing`, `50_annotations`.
Redefined: `04`, `05`, `08`, `13`, `14`, `17`, `22`, `23`, `31`, `32`, `35`, `36`, `37`, `42`, `43`,
`45`, `47`, `48`, `52`, `53`, `54`, `60`. NEVER quote a stored `x/59` score as current.

**C2. THE HOP THAT DECIDES IS THE `.docx`, NOT THE RENDER.** Ten checks were found on 13 Nov reading
an artifact the engine does not control - Google's fontconfig (`09`), Google's export tiers (`54`),
the renderer's annotation objects (`50`), the renderer's widgets (`51`), the renderer's heading-derived
outline (`52`), the renderer's link annotations (`15`/`40`), the renderer's span geometry (`37`).
When you diagnose a class, ask first: **does `PdfToWord`/`DocxWriter` decide this, or does whoever
rendered it?** If the latter, no engine change can move it and the check needs re-pointing, not fixing.

**C3. LIBREOFFICE AND GOOGLE DOCS ARE NOT COMPARABLE.** The pipeline (PIPELINE.md step 6) renders with
`soffice --headless`. A 211-document round measured the three effects of one change exactly:
**engine +230, instrument -1833, renderer +1634** of the same total. Say which renderer produced any
number you quote. A score taken on one is not evidence about the other.

**C4. SIX CHECKS BEHAVE DIFFERENTLY AND YOU MUST NOT "FIX" THEM BACK.**
- `54_image_dpi` FAILS LOUDLY when it has no `--docx`. That is not a bug; it used to score
  "asked and could not answer" as a PASS on twelve documents.
- `53_embedded_faces` and `37_super_subscript` read the `.docx`; without `--docx` they cannot measure.
- `52_outline` compares the (level, title) TREE, not a count.
- `50_annotations` is retired and replaced by `50_annotation_text`, which asks the `.docx`.
- `15_links` is retired; `40_link_targets` compares URLs in a normalised form.
Always pass `--docx out1/<name>.docx`.

**C5. FIVE ENGINE DEFECTS ARE NAMED AND UNFIXED - these are yours, not a check's.**
1. `w:sz` is written in HALF-POINTS, so a 6.2 pt line becomes 6.0 pt. 7 documents, measured:
   `304_package_insert_small_print` right edge 291.7 -> 274.8.
2. Justification is DROPPED. `310_court_judgment` carries 82.3 pt of space in the source line and
   50.9 in the render; the source's 538.6 column edge becomes 506.7. 5 documents.
3. Source lines are WELDED into one paragraph. `64_newspaper_uneven_columns_ad_boxes` has 77 source
   lines and 21 docx paragraphs. 9 documents.
4. `Table` carries font, size and colour but NO bold and NO italic (`PdfToWord.java:201-267`), so a
   table cell loses them. `64_newspaper` loses 2 italic spans this way and `12_italic_runs` could not
   see it. 1 document confirmed.
5. An anchor inside a table cell is displaced by the RENDERER, which adds the cell's page origin to a
   page-relative `wp:posOffset`. Measured +251.3/+71.7 pt on a controlled pair. 2 documents.
Plus: `32_stroke_lines` loses 9 documents to ONE line - `PdfToWord.attachShapes` drops a thin stroke
near a table and `DocxWriter.borders` then writes all six sides `nil` because `ruledTable` is false.
The rule is measured, attributed, and thrown away. A fix was measured at 13 -> 4 with +6 passes.

**C0. THE CORPUS IS 211 DOCUMENTS, NOT 208.** Four `corpus-v1` assets: `p2w-all-groups.zip` 53 +
`p2w-batch-1.zip` 80 + `pdf-to-word-test-corpus-v3.zip` 75 + `p2w-round2-additions.zip` 3. The
release TITLE still says 208 and is stale; the 208-document rows in every store predate the
round-2 additions. Any count you take must say which of the two it is.

**C6. `ratchet.py` HAD AN ORDERING BUG AND IT IS FIXED.** It keyed the latest `.txt` row on
`(round, engine)` and compared with `>=`, and `"22728b1" >= "2a68de6"` is FALSE - so a whole round of
211 rows was discarded and the ratchet re-compared the PRE-round rows, printing PASS while 139
documents had improved unseen. It now orders by write. If you see a `.txt` PASS you do not believe,
check that the store's last line is the row being compared.


---

## 13 Nov 2026, evening - EVERYTHING THE 24 INVESTIGATIONS CHANGED

**THE UNIVERSE IS 43 CHECKS** (id-sha `f58b6e1f708a`, body-sha `f55df8c46fd0`). It was 59, then 54, 49,
48, 47, 45, and it is 43 now. Retired today: `03, 06, 07, 09, 11, 12, 15, 16, 19, 20, 21, 29, 30, 33, 41,
50`. Redefined: `04, 05, 08, 13, 14, 17, 22, 23, 31, 32, 35, 36, 37, 42, 43, 45, 47, 48, 52, 53, 54, 60`.
NEVER quote a stored `x/59` or `x/45` score as current. Every stored mark is stale and needs one recut.

**THE FRESH ROUND, 211 documents, soffice render** (`p2w-baseline-211-d8fb69e.md` is delivered):
```
8855 / 9495 = 93.26 %  at 45 checks · 29 documents pass everything · 35 failing classes
18_displacement 98 · 14_filled_shapes 85 · 59_shape_anchor 68 · 10_font_sizes 52
44_header_footer 50 · 47_margins 49 · 35_rotation 30 · 60_text_column_right_edge 25
42_alignment_mix 24 · 26_text_overlap 14
```
Every earlier class size you have read is wrong. `59` was reported as 100 and is 68. `44` was reported as 54
and is 50. `45` was reported as 23 and is 9. Re-measure before you trust any number.

**THE HOP RULE, NOW PROVEN TEN TIMES.** Ten checks were found reading an artifact the engine does not
control: Google's fontconfig (`09`), Google's export tiers (`54`), the renderer's annotation objects (`50`),
its widgets (`51`), its heading-derived outline (`52`), its link annotations (`15`/`40`), its span geometry
(`37`). Before you diagnose anything, ask: **does `PdfToWord`/`DocxWriter` decide this, or does whoever
rendered it?** If the latter, no engine change can move it and the check needs re-pointing, not fixing.

**THE RENDERER QUESTION IS OPEN AND MUST BE NAMED.** The pipeline renders with `soffice --headless`. Every
number in every store before 13 Nov came from a Google Docs export. They are NOT comparable - one round
split the same total into engine +230, instrument -1833, renderer +1634. Say which renderer produced any
number you quote. A Google export cannot be produced from this sandbox.

**FIVE NAMED ENGINE DEFECTS, with documents and numbers. These are yours, not a check's.**
1. `w:sz` is written in HALF-POINTS via `Math.floor(sizePt * 2f)` (`DocxWriter.java:5051`), so a 6.2 pt line
   becomes 6.0 pt. 51 of `10_font_sizes`' 52 are this; over 5,944 downward pairs the mean loss is -0.285 pt.
   The floor is DELIBERATE - `:5044` records that on `362_price_list_dense` rounding up wraps every row and
   doubles the table. 6.2 pt is unrepresentable in DOCX at all, so the only question is which side to lose.
2. Justification is DROPPED. `310_court_judgment` carries 82.3 pt of space in the source line and 50.9 in
   the render; the source's 538.6 column edge becomes 506.7. 5 documents.
3. Source lines are WELDED into one paragraph. `64_newspaper_uneven_columns_ad_boxes` has 77 source lines
   and 21 docx paragraphs. 9 documents.
4. `PdfToWord.Table` carried `fonts, sizes, colors` and NO bold and NO italic, so a cell lost them -
   `DocxWriter` never emitted `<w:i/>` for a cell at all. 1 document confirmed (`64_newspaper`, 2 spans).
5. An anchor inside a table cell is displaced by the RENDERER, which adds the cell's page origin to a
   page-relative `wp:posOffset`: measured +251.3/+71.7 pt on a controlled pair. 2 documents.

**AND THE BIGGEST SINGLE ENGINE FIX, MEASURED BUT NOT LANDED.** `32_stroke_lines` loses NINE documents to
ONE line: `PdfToWord.attachShapes` (`:5296-5298`) drops a thin stroke near a table, `markSideStrokes` reads
that same rule's weight into `Table.sideStroke[0]`, and `DocxWriter.borders` (`:4563-4566`) then writes all
six sides `nil` because `ruledTable` is false. The rule is measured, attributed, and thrown away. A
three-part fix was measured at **13 -> 4 with +6 passes and 10 documents improved**, at the cost of four
documents losing one check each. It was LOST with a recycled sandbox - re-derive it.

**SIXTEEN CHECKS HAVE A POPULATION PROBLEM AND IT IS THE CORPUS'S.** `50`, `51`, `52` each have exactly ONE
document in 211 that can exercise them; `37` has one and ZERO subscripts anywhere; `36` asks its question on
2 of 211; `15`'s whole corpus carries FIVE links in ONE document. `TEST-CORPUS-REQUEST.md` says what to add.

**AND THE FILE ITSELF WAS LYING IN FOUR PLACES, NOW CORRECTED.** `44`'s band membership is invariant on
151 of 151 constructed 20 pt defects - it is not a placement test at all. `59`'s `_box_moved()` asks only
whether a shape of the source box's SIZE exists anywhere on the page, never whether it is where the source
put it, so 992 runs on 42 documents are charged `moved` with the box within 2 pt on all four edges.
`45` at exact tolerance IS `04|05` (22 = 22, symmetric difference 0), so its 97 % floor can only remove
fires. And `10` is blind in the other direction: swap two sizes in the .docx and 65 of 68 spans carry the
wrong size while `10` reads 4 to 4 and passes.
