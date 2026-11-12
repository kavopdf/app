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
  unzip -qo c1.zip -d t ; unzip -qo c2.zip -d t ; unzip -qo c3.zip -d t
  mkdir -p all out1 res gd restxt ; find t -name '*.pdf' -exec cp -n {} all/ \;
  Every directory the steps below write into is made here, in one line. restxt/ was
  missing from this line, so the .txt measurement wrote into a directory that did not
  exist and raised FileNotFoundError on every single document - the .txt half measured
  nothing for a day while the run still reported its ten.
  Expect exactly 208 PDFs.
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
    g. python3 tools/p2w-bench/verify_google.py all/<name>.pdf gd/<name>.pdf --json res/<name>.json
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
