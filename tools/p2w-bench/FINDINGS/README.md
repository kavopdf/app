# FINDINGS — what a subagent proved, written so it survives the run that asked for it

A subagent's final message goes to the run that deployed it. If that run has already ended -
and a subagent can easily outlive a 45-minute run - the message arrives nowhere and the work is
gone. That is why this directory exists.

**A subagent's deliverable is a committed file, not a message.**

Every agent deployed by the fixer writes one file here and commits it. The next fixer run reads
this directory before it forms any theory, so a question asked at 11:15 can be answered at 14:40
by an agent nobody is waiting for, and the run that finds it starts from the answer instead of
from the question.

## The file

`tools/p2w-bench/FINDINGS/<class>-<angle>-<HHMMSS>-<4 hex>.md`

```
# content-missing-nothing-in-its-place / A - the engine code path

Asked: which code path decides where an inline image is placed, and does it use the page
       coordinate space or the text-matrix space?

Claim: PdfToWord.java:1840 places inline images using the text matrix (Tm) without multiplying
       by the CTM, so an image inside a scaled text object lands at the wrong scale. This would
       produce the "content present but displaced" signature the census reports on 415_inline_images.

Evidence: PdfToWord.java:1820-1865 (read). The same file multiplies by the CTM for vector
       strokes at line 1902 but not for images at 1840. No test yet - this is from reading.

How to test it: patch line 1840 to multiply by the CTM, build, then
       python3 benchmarks/p2w.py --diagnose 1
       and compare 415_inline_images__p1__src.png with __ours.png. If the claim is right the
       image lands inside its box; if wrong, nothing moves or something else breaks.

Confidence: medium. The asymmetry with line 1902 is real; whether it is the cause of THIS class
       is not yet shown.

Ruled out: the font-substitution path (checked, 415 uses an embedded face).
Status: complete
```

## Filename

`<class>-<angle>-<HHMMSS>-<4 hex>` - the seconds and the random suffix are there because two
agents on the same class and angle can finish in the same minute, and one would have overwritten
the other. Never reuse a name; never append to a file that is not yours.

## If your commit is rejected

Three agents and the fixer all commit to the same branch. If your commit comes back rejected or
non-fast-forward, retry once. If it fails again, re-read the file at that path - someone else may
have just written it - and commit yours under a new name with a different suffix. Never drop a
finding because the commit raced.

## Rules

- **Commit before you finish, not after.** A finding that exists only in your final message does
  not exist. If you are running long, commit a partial file with `Status: partial` and say what is
  missing, then keep going and commit again.
- **One file per question.** Do not append to another agent's file.
- **Touch nothing else.** Not the engine, not DEFECT-CLASSES.md, not ATTEMPTS.json, not
  HYPOTHESES.md, not RANKING.csv. Your file under FINDINGS/ is the only thing you write.
- **Falsifiable or it is not a finding.** "The layout looks wrong" is not a finding. "Line 1840
  omits the CTM multiply, so a scaled image lands at 1/scale" is.
- **A root cause, not a patch.** Your claim must name the mechanism, not suggest a repair. The
  test: a root cause predicts which OTHER documents change; a patch only fixes the one in front
  of you. "Skip this document's table", "raise the threshold", "add a fallback", "special-case
  this page", "wrap it in a try" are not findings - they make a number move and teach nobody
  anything. If you cannot name the mechanism, say so plainly: "I could not find the root cause,
  and here is what I ruled out" is a better file than a plausible-sounding patch.
- **Suspect the instrument too.** If the number you were handed could itself be wrong - the
  measurement, the check, the benchmark - say so with evidence. Several of this pipeline's real
  bugs were in the instrument and the checks, not the engine, and the agent that noticed was
  worth more than the one that patched around it.
- **Say what you ruled out.** That is worth as much as the claim, because it stops the next agent
  walking the same path.
- **Never state a result you did not run.** Reading the code is evidence and should be labelled as
  reading. Only a build and a measurement make a claim tested.

## For the fixer reading this directory

Read it at STEP 2b, before you form a theory. If a finding names your class:

1. Verify the claim yourself. A finding is a hypothesis, never proof - even a confident one.
2. If it holds, act on it and record the attempt.
3. If it does not, say what you tested and why it failed, in your own FINDINGS file. Do not
   silently discard it - the next agent needs to know it was tried.

A class with three findings and no fix is still progress: three paths are now closed.
