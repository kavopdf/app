# The problem names - what each one means, and where it comes from

Every scored document in `RANKING.csv` carries a `problem` beside its `signature`. Both are
computed by `benchmarks/p2w.py` from the numbers alone - never from opening a rendered image and
never from anyone's opinion about what the engine did.

`signature()` reads the SHAPE of the tolerance sweep. `problem_name()` reads the two axes together:
how much ink is missing, how much is in the wrong place, and how far the worst of it is.

    signature(p):
      clean          share@5px < 1.0            nothing to see
      content-loss   share@10 > 0.8 * share@5   the ink is ABSENT, not moved - a wider
                                                tolerance does not recover it
      displacement   share@10 < 0.6 * share@5   the ink MOVED - a wider tolerance recovers it
      mixed          otherwise                  both on one page

    problem_name(sig, share5, invent5, max_pt):
      none                                   share@5 < 1.0, or signature is clean
      unmeasured                             signature is MEASURE-ERROR
      content-missing-nothing-in-its-place   content-loss, invent5 < 2
      content-missing-partly-replaced        content-loss, invent5 >= 2
      content-partly-lost-and-displaced      mixed, invent5 > 0.7 * share5
      content-partly-lost                    mixed, otherwise
      single-element-far-out                 share5 < 8 and max_pt > 30
      content-present-wholly-displaced       |share5 - invent5| < 0.3 * max(share5, 1)
      content-present-partly-displaced       everything else

`share@N` is the percentage of source ink that lands within N pixels of where it belongs.
`invent5` is the percentage of our ink that has no source ink near it - text we put somewhere the
PDF never had it.

## The names, in order of how much they hurt a user

1. **content-missing-nothing-in-its-place** - content is GONE and nothing was put in its place.
   The worst outcome: the page is simply short of what it should say, and nothing looks wrong.
2. **content-missing-partly-replaced** - content is gone, and something else sits where it was.
   Worse to look at than the first, because it reads as a wrong document rather than a short one.
3. **content-partly-lost-and-displaced** - two defects on one page: some text lost, the rest moved.
4. **content-partly-lost** - some text lost, the remainder displaced.
5. **content-present-wholly-displaced** - everything is there and all of it has moved. Recoverable
   by moving it back; not by finding it.
6. **content-present-partly-displaced** - most of it is right, a part has moved.
7. **single-element-far-out** - one small thing (a stamp, a seal, a signature) far from home,
   with the rest of the page correct. Visually the most obvious, textually the least damaging.
8. **none** - nothing to do. A `none` document is `FIXED` in `DEFECT-CLASSES.md`, not `OPEN`.
9. **unmeasured** - the instrument could not read this document. It is never dropped: it becomes
   a MEASURE-ERROR row, and if it genuinely cannot be measured it is listed in
   `tools/p2w-bench/EXEMPT.json` with a reason.

## Two things this file is not

It is not a diagnosis. A name says what the output looks like, never why - two documents can share
a name and have entirely different causes in the engine.

It is not a ranking of work. The fixer takes the class with the MOST DOCUMENTS, because one
mechanism fixed once clears every document under it, and the most damaging class is not always the
largest one.
