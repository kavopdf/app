# `--force` was not resumable: 75, 75, 75 and the corpus could never be rebuilt in a slot

21 Nov 2026, fixer run claimed 10:02. Measured in this sandbox, not inferred.

## What the brief says, and what the tool did

`FIXER-BRIEF.md` tells a run, after any engine change:

    python3 /scratch/work/p2w.py --force --budget 250   # --force AFTER ANY ENGINE CHANGE
    python3 /scratch/work/p2w.py --budget 250        # repeat until it says the corpus is complete

The second line drops `--force`, so the repeat was never meant to carry it. But the first line cannot
be followed either: `--force` is not resumable, and a 250 s budget does not rebuild 211 documents.

`docx()` decides what to rebuild with `_need(p)`, which answered **True for every document** when
`--force` was in `sys.argv`. The loop then walks a sorted list from the top and stops when the budget
runs out, so every call rebuilt the SAME first N documents and never reached document N+1.

## Measured

    call 1   docx 0/211   -- converting 211   ->  75 docx
    call 2   docx 0/211   -- converting 211   ->  75 docx     (the same 75, rewritten)
    call 3   docx 0/211   -- converting 211   ->  75 docx

Three calls, three identical prefixes, 275 s each. A fresh sandbox therefore could not rebuild the
corpus with `--force` at all, and an engine change could not be measured in one slot. This is the same
shape as the `restamp_txt.py --run` bug already written down: a tool that runs, exits 0, and makes no
progress.

## The fix

A document is stale when it is **older than the engine that must write it**, so `--force` now skips a
document whose `.docx` and `.txt` are both newer than `tools/engine-verify/out/.../PdfToWord.class`.
A document converted before the engine changed is still rebuilt - which is the whole purpose of
`--force` - and the loop advances.

    call 4   docx 75/211  -- converting 136   -> 149 docx
    call 5   docx 149/211 -- converting 62    -> 205 docx
    call 6   docx 205/211 -- converting 6     -> 211 docx

**Before: 75, 75, 75. After: 75, 149, 205, 211.** The corpus closes.

## What would overturn this

A document whose `.docx` is newer than the engine class file but was written by a DIFFERENT engine -
only possible if two builds share an output directory, which `p2w.py` does not do (it rebuilds the
engine into `p2w/repo` and converts into `p2w/out`). If that ever becomes possible, the mark must be the
engine's source hash, not its class file's mtime.
