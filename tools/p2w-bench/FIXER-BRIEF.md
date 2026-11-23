# THE CHARTER

**You own this. Not the procedure - the outcome.**

---

## THE GOAL

**Every document in the corpus matches its original at 99% or better in Google Docs, in both the .docx
and the .txt.**

That is the whole job. Everything below this charter is a means to it, and any means that does not move a
document towards 99% is wasted time however tidy it looks.

    corpus      213 PDFs
    today       6 clean of 192 scored in Google;  186 clean of 213 in txt
    the gap     186 documents, and they are the reason this exists

## WHAT DONE LOOKS LIKE

A document is done when **all 42 Google checks pass** on it and its `.txt` describes the same document.
Not "improved", not "moved", not "the class was worked" - **that document, in the renderer the user
opens.**

## A RULE IS A METHOD. IT NEVER NAMES A CLASS.

The user, 22 Nov: *"koi bhi rules kisi ek specific class ke liye nhi hona chahiye yeh iska kaam karne ka tareeka hona chahiye"*

**Every rule in this file is a way of deciding, not a thing to do to one class.** The difference matters,
because a class-specific rule is dead the moment that class is fixed, and it takes a run to notice.

| a method (right) | a class rule (wrong) |
|---|---|
| "fix the construct the checks share, not one check of five" | "fix `32_stroke_lines`" |
| "ask which documents become CLEAN if this works" | "work `18_displacement` next" |
| "a measured lead outranks everything" | "finish `w:tblpPr`" |
| "the biggest class with no verdict is the biggest prize" | "`47_margins` is 26 documents" |
| "an unmeasured change is not a pass" | "re-stamp the table after `47_margins`" |

**So no rule here may be written in terms of a class name.** Evidence may be - a measurement of
`32_stroke_lines` on 21 Nov is a fact and belongs in the file - but a rule must be stateable without naming
any class, because the class it names is the class that will not exist next month.

**And if you find yourself writing a rule that only makes sense for one class, you have found a symptom, not
a rule. Write it in `FINDINGS/` as a measurement and leave the method alone.**

**The tools already obey this: no script in `tools/p2w-bench/` branches on a class name.** Class names
appear in `verify_google.py` and `verify_txt.py` because those files ARE the check catalogue, and in tests
because a test asserts a specific check catches a specific mutation. Neither is a rule about what to work on.

## THE ONLY THINGS THAT ARE NOT YOURS TO DECIDE

Six, and they are not preferences - each one is a mistake this project has already paid for.

1. **Google is the truth.** LibreOffice is a fast local proxy that hides what the phone shows. A change
   that only improves LibreOffice is not a fix. (That one shipped as 3.53.5 and broke every stamp.)
2. **Nothing changes without a measurement before and after.** A change you cannot measure is a guess;
   write it into `FINDINGS/` as a proposal instead of committing it.
3. **No document may get worse.** `regress.py --check` must pass, and it now refuses a Google regression
   as well as a LibreOffice one.
4. **No construct Google ignores.** `google_safe.py` lists them; the gate refuses a commit that spreads
   one. A construct LibreOffice honours and Google drops IS the defect, not the fix.
5. **Never delete anything** - not a file, a row, a branch, a release asset or a Drive file. Deleting is
   how evidence disappears and how the next run repeats this one.
6. **No secret in the repo, and nothing in the user's Drive root.**

**Everything else is yours.** Which class, which construct, which approach, which tool, which document to
prove it on, whether to write a new tool, whether to change a table, whether the rotation is right, whether
the instrument is lying - all of it. There is no person behind this pipeline to ask. Decide on evidence,
record what you decided and why, and move.

## WHAT YOU HAVE

The whole repository read and write, `git push`, bash, Python and the doc libraries, the engine toolchain,
Google Drive yourself with the three calls for a Google verification, two sub-agents a run, the corpus,
every measurement, and the whole history in `FINDINGS/`, `LESSONS.md`, `SETTLED.md`, `HYPOTHESES.md`,
`BLOCKERS.md` and `git log`.

**If a tool you need does not exist, write it.** Sixty in `tools/p2w-bench/` were written by runs that
needed one.

## HOW TO DECIDE, WHEN NOBODY TELLS YOU

**Research the repository first** - most of what you are about to try has been tried and written down.
**Verify by measurement** - a claim you have not measured is an opinion. **Prove with a number before and
after, and say which evidence.** When the evidence does not settle it, take the reversible decision and
record what would overturn it.

**And ask the only question that matters before every attempt: if this works, which documents become
CLEAN?** If the answer is none, it cannot be a fix, whatever the class table says.

## WHAT THE REST OF THIS FILE IS

**A record of what has already been learned, and one way of working that has produced results.**

**It is not a checklist and not a script.** The steps below are numbered because that is how they were
written down, not because a run must perform them in that order or at all. A run that reads the situation,
decides what is worth doing, and does it - and gets documents to 99% - has followed this file better than
one that performs every step and moves nothing.

**When a step here contradicts the evidence in front of you, the evidence wins.** Say so in the report, so
the next run inherits the correction instead of the contradiction.

---

# HOW TO THINK ABOUT A DEFECT. THIS IS THE PART THAT MATTERS.

A check failing is not the problem. It is the symptom. **A run that fixes the symptom has done nothing that
survives the next document.** This is how to get from the symptom to the thing that causes it.

## 1. Three things, not one

For any defect, look at all three before you touch code:

| | what it is | how to look |
|---|---|---|
| **the page** | what the PDF actually draws - position, colour, width, the order things are in | render the page, and read the PDF's own operators; the text layer is not the page |
| **the engine** | what our `.docx` says about it | unzip the `.docx`, find the construct, read the numbers it wrote |
| **the renderer** | what Google does with that construct | upload, convert, export, look. LibreOffice does not count here |

**The defect is the gap between the first and the third, and the second is the only thing you can change.**
A run that looks at one of the three is guessing.

## 2. The cause has to explain every symptom, not the loudest one

If a document fails `32_stroke_lines` and `05_chars_extra`, **that is one cause with two symptoms, not two
defects.** Find the thing that produces both - on 21 Nov it was one floating `<w:drawing>` per rule: Google
drops the shape (the rule is lost) and leaves the anchor (a `U+200B` appears).

**A hypothesis that explains one symptom and ignores the other is wrong, however well the fix works on the
one you looked at.** Check the shapes:

    python3 tools/p2w-bench/classpick.py --leverage

Checks that always travel together share a cause. One fix clears all of them; fixing one of five has done a
fifth of the work and reported a success.

## 3. Three places a defect can live, and they need different fixes

* **The engine is wrong** - it emits something the page did not draw, or the wrong number. Fix the engine.
* **The instrument is wrong** - the check fails a document against itself, or counts what the page never
  drew. Fix the instrument, with a finding and a re-measurement. `26_text_overlap` counted absolute overlaps
  instead of new ones for days and made the hardest documents unfixable.
* **Google cannot do it** - the construct is not honoured, or honoured differently. **That is not a fix, it
  is a finding.** Write it down, use the construct Google does honour, or park the class with the proof.

**Getting this wrong is the most expensive mistake in this repository.** Four attempts at the same rule
went in as "engine fixes" when the answer was "Google drops it". Eighteen attempts at `32_stroke_lines` went
in as paragraph-border fixes when 36 of 39 rules were inside table rows and could never reach a paragraph
border.

## 4. A fix that needs a special case is not a fix

**If your change needs "and for this document, do X instead", you have not found the cause.** The corpus is
213 documents; a special case per document is 213 patches and a codebase nobody can reason about.

The right shape is: one rule that is true of every document, applied once. If you cannot state it that way,
you are still at the symptom.

## 5. Prove it on the hardest document, not the easiest

Pick the document where the construct is the **whole** defect - `bank-statement-horizontal-rules-only` is 39
rules and nothing else. If the fix works there it is a real fix. If you prove it on a document where the
construct is one of eleven problems, you have learned nothing: the other ten hide the result.

**And then prove it on a second document of a different shape.** A fix that works on one and not the other
means the cause was wrong, and you found out for the price of one build.

## 6. When a fix does not work, find out WHY before trying another

**The second attempt must be informed by the first, or it is a coin flip.** After every failed attempt,
answer one of these in writing:

* the construct never reached the output - the code path was not taken (add a print, look at the `.docx`)
* the construct reached the output and Google ignored it (that is a finding, not a bug)
* the construct reached the output, Google honoured it, and the numbers were wrong (measure the number)
* the construct reached the output, Google honoured it, and something else moved to compensate

**"It did not work" is not an answer.** It is the absence of one, and the next run pays for it again.

## 7. The one question before every attempt

**If this works, which documents become CLEAN?**

If the answer is none - because every document that carries this check also carries four others - then the
attempt cannot move the goal, whatever it does to the table. Go and find the cause the checks share instead.

## 8. And when you are finished, say what you now know that you did not know before

A run's value is not its commits. It is the understanding it leaves behind. **One measured sentence in
`FINDINGS/` that saves the next run an hour is worth more than three commits that move one document.**

Write it as: what you believed, what you measured, what is now true, and what would prove it wrong.

---

---

## THE REST OF WHAT USED TO BE HERE IS NOW `FIXER-REFERENCE.md`

This file used to be 134 KB and `cat`ing it was the first thing a run did. The measured cost was
**20.3 minutes of silence before the first attempt** (17:58 run, 23 Nov), which left one attempt in a
90-minute budget. So the charter and the way of thinking stayed here - 10.6 KB - and the 123.7 KB
step-by-step reference moved to **`tools/p2w-bench/FIXER-REFERENCE.md`**, unchanged.

**Nothing was deleted.** Every line that was here is there.

**Read it when you need it, not before you start:**

    grep -n '^## ' tools/p2w-bench/FIXER-REFERENCE.md     # the index, in one call
    sed -n '/## STEP 0 /,/## STEP 1 /p' tools/p2w-bench/FIXER-REFERENCE.md

It holds: STEP 0 (is it your turn), STEP 0b (the two questions), the class-selection rules, the
attempt loop, the measurement commands, the report shape, and the record of what has already been
tried and refuted. **A run that picks one section and moves a document has followed this better than
one that reads all of it and moves nothing** - which is what the section above this one already says.
