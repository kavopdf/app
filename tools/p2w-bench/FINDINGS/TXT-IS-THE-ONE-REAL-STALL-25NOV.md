# txt is the one stall that is not an instrument problem

Everything else found on 25 Nov was a measurement that lied. This one is not.

    txt: stopped | 199 clean, 14 failing | age 27.3 h

The .txt state file names the current engine, and a previous pass confirmed the 14 are a measurement of
today's engine rather than a stale table. So the row is red for the reason health.py intends: fourteen
documents genuinely fail a .txt check, and no attempt in 27 hours has closed one.

## Why it stayed open while everything else moved

The fixer's rotation reached the txt side and chose otherwise each time - 18_displacement, then
04_chars_missing, then the annotation construct - because each of those had a fresh measurement behind it
and the txt classes did not. That is defensible per-run and wrong across a day: a stage that is nobody's
first choice is a stage that never runs.

The most common failure is t12_word_invention at 8 of the 14. The 11:24 run closed part of it with a real
root cause - annotationRuns() at PdfToWord.java:2456 hoists every annotation's /Contents as body text, so
a note that draws nothing prints as words, and its sibling annotationContentsOf() at :2475 already states
the correct rule. That patch is measured on its one document and blocked only by the gate.

## What would move it

Land the annotation patch. It is proved: 600_reviewed_invoice_with_annotations goes 8/12 to 8/12 with 8
passed instead of 7, t12 stops reporting, paragraphs 14 to 12, and the population is one document out of
213 with six annotations, verified by scanning every corpus PDF rather than sampling.

That closes 1 of the 14 and, more importantly, proves the txt side can be moved at all - which nothing
in 27 hours has done.

## Not changed

No instrument edited and no engine touched. Recorded because the one stage that has not moved is the one
whose fix is already written and measured.
