# The instruction sets were written for the previous pipeline

## What the sweep found

Every active instruction file was scanned for the artefacts the old pipeline used. The
method in them is still current and still hard-won. The tool names are not.

| file | lines | old references found |
|---|---|---|
| FIXER-BRIEF.md | 786 | 7x verify_google, 10x record.py, 10x classify.py, 5x BASELINE.md, 3x "208", 3x RATCHET.json |
| BASELINE-BRIEF.md | 497 | 8x txt_gap.py, 8x ratchet.py, 6x BASELINE.md, 5x verify_google, 5x "208" |
| CLASSIFIER-BRIEF.md | 247 | 8x classify.py, 6x ratchet.py, 3x BASELINE.md, 2x "208" |
| TOOLBOX.md | 678 | 17x ratchet.py, 12x BASELINE.md, 11x classify.py, 6x RATCHET.json |

The crons' prompts say "read FIXER-BRIEF.md and follow it exactly". So the fixer was being
told, in 786 lines of detail, to measure with `verify_google.py`, record with `record.py`,
classify with `classify.py`, and close with `ratchet.py` - none of which is the score any
more. A fixer following that brief would have produced numbers that look real and describe
nothing, and the phase machine would never have seen them.

## What was done

**Three code-level old-rule references, fixed:**

- `benchmarks/gate.py` still cited the **withdrawn** "66 % of verify_google's passes were
  unfalsifiable" figure in its own docstring. That number is retracted in LAYER-POLICY.md
  and contradicted by FALSIFY-47-RESULT.md; it is now corrected where it was still quoted.
- `tools/p2w-bench/round.py` described its advance condition as "when classify.py reports
  no OPEN class". `classify.py` is retired; the condition is now `--close-round`.
- `tools/commit-gate.sh` told the agent to "run classify.py --attempt". That is a live
  instruction, printed at the moment the fixer is about to commit, naming a retired tool.

**One authoritative command list, `tools/p2w-bench/INSTRUMENT.md`:** the exact command for
every step of the new pipeline, what each number means, which tools are still live and why
(`verify_txt.py` is gate.py's advisory layer; `ratchet.py` is the APK's Gate B), and which
are retired as measurements.

**A hard banner at the top of all four briefs**, before any command, naming the retired
tools, the dead files and the corpus size (213, not 208), and stating that INSTRUMENT.md
wins where they disagree about which command to run.

**The same retired list at the top of `benchmarks/PIPELINE.md`**, which the baseline and
fixer prompts both tell their runs to read.

## Verified

    bash -n tools/commit-gate.sh        ok
    gate.py, round.py parse             ok
    measure_gate                        exit 1 (correct: 211 vs 213, no round stamp yet)
    classify_gate                       exit 1 (correct: class file has no header yet)
    dry run through 3 rounds            phase done, APK may ship: YES

## What is NOT done, stated plainly

The four briefs were **bannered, not rewritten**. Roughly 2,200 lines of body text still
describe the old tools step by step. The banner makes the correct instrument authoritative
and names the retired commands explicitly, and `INSTRUMENT.md` gives the replacement for
each - but an agent that reads past the banner and follows a body command will still run a
retired tool.

Rewriting those bodies properly is the next piece of work, and it is not a mechanical
find-and-replace: each old command sits inside a paragraph of reasoning about why that step
exists, and the reasoning has to be re-derived against the new instrument rather than
word-swapped.
