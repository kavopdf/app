# LESSONS — what cost real time, once

Read this before forming a theory. Every line is a mistake somebody already paid
for. A lesson that would not change what the next attempt does does not belong
here — delete it rather than let the list grow into a rule book.

`HYPOTHESES.md` is per class: what was tried on THIS defect. This file is
everything else: what went wrong in the work itself.

- **w:framePr passes LibreOffice and dies in Google Docs.** It is legacy OOXML;
  LibreOffice honours it, Google renders the paragraph as body text at the left
  margin. A fix that only improves LibreOffice is not a fix.
  Cost: shipped as 3.53.5 and broke every stamp on the phone, with every count in
  CI identical.

- **A check can be wrong.** `26_text_overlap` counted absolute overlaps instead of
  new ones, so a stamp printed over text failed a document against itself.
  Cost: the hardest documents were unfixable for days, and a fixer would have been
  pushed to break them in order to make the check pass.
  The control test found it: a document compared with itself must score full marks.

- **Accusing the instrument needs a control test.** The verifier really was wrong
  that time. It usually is not. Run the same document against itself first: if it
  fails, the verifier is broken; if it passes, the fix did not work.
  Cost: 89 rows were once closed CLOSED-UNFIXABLE on an assumption nobody tested,
  and all had to be reopened.

- **Never hardcode a sandbox path.** `audit_sim.py` and `prove_checks.py` both
  shipped with `/scratch/work/...` baked in and could not run anywhere else.
  Cost: two committed tools that proved nothing, and nobody noticed because nobody
  ran them from a fresh clone.

- **Quantify the class's distribution before choosing a patch.** Eight attempts went to the
  table spacer on a class of 187 documents whose render value was below 50 % on 133 of them and
  above 100 pt off on 70: the spacer could only ever reach the 16 near-misses. Bucket the failing
  rows by render value and by page count first, then pick the patch the biggest bucket needs.

- **A class of 126 documents is rarely one cause.** Grouping on a check that fails
  on almost every document produces one unactionable blob. Use `--subclusters`.

- **A number in a report that is not in a file is a guess.** Every figure comes
  from `RESULTS.jsonl` or `BASELINE.md`, or it does not go in the report.

- **The ratchet cannot see a regression in a round whose marks were never taken.**
  `RATCHET.json` was `{}`, so `ratchet.py` printed *208 first marks* and PASS while eight of
  twenty documents had actually fallen, two of them by adding a page. Compare against
  `BASELINE.md` yourself before believing a green ratchet on a fresh round.

- **Writing the family Google substitutes with does not make Google report it back.**
  Mapping Liberation Serif/Mono to Times New Roman/Courier New (the "fix already known"
  in DEFECTS.md) made 53_embedded_faces pass on 2 of 10 documents only; on the other 8
  the export reported kept=0 of 1-8 source faces, including a doc that emitted nothing
  but Courier New. The name we write is not the name that comes back, so check 53 has to
  be calibrated against a docx we know Google renders in that family before the map is
  extended again. Cost: one slot, 10 Drive round trips, engine reverted.

- **A class's median and worst dy do not say WHERE the error starts.** `20_within_10pt` read as a
  line-pitch bug on 203 documents; dumping per-line dy for one of them showed the whole page was
  2.6 pt low and then took one 10 pt step at the top of a table. Two numbers per document cannot
  tell a drift from a step — dump the per-line dy of one document before forming a theory.
  Cost: two attempts spent on line-pitch models that the shape of the error did not support.

- **`w:line` is a multiple of the PARAGRAPH MARK's line height, not the document's.** The table
  spacer is an empty paragraph with `w:sz w:val="2"` (a 1 pt mark), so `w:line="276"` — 13.8 pt
  asked — rendered as 3.16 pt and every table rose 10.6 pt. Charge a measured gap in `w:before`,
  which is honoured exactly and face-independent, and keep `w:line="1"`. Read the spacer's mark
  size before trusting any `w:line` in it.

- **The measurement rig costs more than the theory.** The patched engine was built in 48 s, but
  ConvertOne.class was not in `out/` and `java` was not on PATH until `build-engine.sh`'s JDK at
  /scratch/work/.p2w-jdk/jdk was exported — and the platform `upload` tool refuses any path outside
  /scratch/output, so each docx must be copied there before it can be staged for Drive. Twenty
  minutes of a 45-minute slot went on those three, not on the fix. Do them first, next time, in one
  command, before touching the class.

- **The Drive round must export the Google Doc as PDF, not as docx.** `verify_google.py`'s second
  argument is Google's own render; a docx export is laid out by LibreOffice instead, and it is a
  different instrument. It scored 362_price_list_dense 38/59 with 12 pages where the baseline says
  51/59 and 1 page, and cost six minutes of chasing a phantom regression. Export `application/pdf`.
  Staged upload keys also expire: nineteen uploaded together and used five minutes later all failed
  with a bare "Failed"; a fresh upload converted immediately. Stage, convert, export, repeat.

- **The ratchet reads `BASELINE.md`, not `RESULTS.jsonl`.** A fixer that records its twenty rows and
  runs `ratchet.py` gets PASS on the unchanged baseline — it compares the baseline with itself. Write
  the attempt's rows into `BASELINE.md` first, then run it: on 13 Nov that turned a PASS into
  "REGRESSED: 4" on the same measurement. Cost: a green ratchet that had seen nothing.
- **`classify.py --attempt` counts 'moved' against the PREVIOUS ENGINE, not the baseline.** An attempt that
  only refines a patch the last run reverted scores 0 moved even when it beats the baseline on the same
  documents (362 51->53, balance-sheet 40->44, and 40_devanagari restored to 37), because the row-by-row
  comparison is new engine vs last engine. Read the baseline deltas from `res/*.json` against `RESULTS.jsonl`
  and say in the report which comparison the number is; do not re-record a number the store refuses.

- **Google adds no `w:after` between adjacent exact-line paragraphs.** A hairline box with the
  leftover advance put in `w:after` measured pitch 9.59 pt where 12 was asked: the `after` is
  ignored, so a baseline cannot be placed independently of the pitch. Only `w:before` moves a
  line, and it moves the next one with it. Cost: one calibration round, and it rules out the
  obvious repair of the hairline patch before it reached twenty documents.

- **A saved patch may already have its twenty rows.** `hairline-flow-before-refined.patch` was
  applied, built and measured through Drive before anyone asked the store: the content-hash engine id
  came out `2a68de6-d5215cb`, which already held 20 rows. `git diff ... | sha1sum` is computable
  BEFORE a build - do it, and `grep` the id in `RESULTS.jsonl`, before spending a slot re-measuring
  a state that is already on the record. Cost: one slot's measurement time for zero new rows.
