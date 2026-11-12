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

- **A check that never fires is not evidence.** 26 of 58 checks fired on twelve
  real documents; the rest had to be proven by value variation or targeted
  mutation. A check that silently always passes hides the defect it was written
  for.

- **A median hides the defect.** A fix can raise the median and lower the worst
  case. Read `19_worst_dy`, not only `18_median_dy`.

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
