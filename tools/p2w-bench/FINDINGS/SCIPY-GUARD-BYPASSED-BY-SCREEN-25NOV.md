# The stall was never soffice. It was a missing scipy, in a tool that never calls main().

**25 Nov 2026 · engine `981ff1fa35e2cf67`**

## What was believed

Two runs blamed the renderer. The 11:24 run wrote in `BLOCKERS.md` that `screen.py` "hangs in the
soffice prerender" - 12 documents rendered in the first call, nothing in the second, `prerender 1
docx` and no finish in the third, three 280 s calls, no result, no error. This run's first sub-agent
root-caused it the same way, one layer down: soffice launched with no `-env:UserInstallation`, so
every launch shared one profile, and a soffice orphaned by a call killed at the 280 s ceiling held
that profile and every later call queued behind it. It measured the queue (56.7 s vs 13.9 s) and
wrote a patch.

That diagnosis is wrong about the stall. It is right about a real defect, which is why it survived
so long.

## What was measured

A stack dump at the moment of the stall, `faulthandler.dump_traceback_later(150)`:

```
  File "/scratch/work/CS/benchmarks/p2w.py", line 162 in _dt1d
  File "/scratch/work/CS/benchmarks/p2w.py", line 177 in edt
  File "/scratch/work/CS/benchmarks/p2w.py", line 541 in position
  File "/scratch/work/CS/benchmarks/p2w.py", line 881 in measure_doc
  File "/scratch/work/CS/benchmarks/p2w.py", line 1437 in run
```

`user 2m23s`, `sys 1.3s` - pure CPU, no soffice in the stack. `edt()` had taken its
Felzenszwalb-Huttenlocher fallback because **scipy was not installed on the pod**, and that fallback
is a Python `for` loop over every column and every row of the page.

One real corpus page (`mobile-bill`, 1754x1241 px at 150 DPI), same mask, both paths:

| path | time |
|---|---|
| `scipy.ndimage.distance_transform_edt` | **1.38 s** |
| `exact-fallback` | **66.07 s** |

**48x, for the same answer.** A 23-document class is 23-69 pages, so the class cost 25-76 minutes of
EDT alone - more than one call, which is why the three calls produced 12, then none, then one.

All ten unrendered documents converted in **4.9-6.8 s each** on a fresh soffice profile. No document
wedges the renderer. The renderer was never the problem.

## Why the guard did not fire

`p2w.py` has a scipy guard: check, `pip install`, check again, and write `INSTRUMENT.txt` saying
which mode the numbers came from. It lives at the top of `main()`.

`screen.py` does not run `main()`. It imports `p2w.py` as a module and calls `docx()` and `run()`
directly, so the guard never executed, `edt()` fell through to the fallback, and nothing anywhere
said so. The same is true of every other tool that imports p2w rather than running it.

**A prerequisite that is not called by the thing that needs it is not a prerequisite, it is a
discovery.** That is the line `pod-prep.sh` was written for, and this is the same mistake in Python.

## The fix

`_ensure_scipy()` is called at the top of `edt()` - beside the only thing that needs scipy, so every
caller is covered, including ones not written yet. It imports, installs once, re-imports, and logs
loudly if it still cannot. The exactness gate is unchanged and still passes, including the
`C diag(3,4)->5` case that the old Chebyshev ladder failed.

## Before and after, on the real class

`python3 tools/p2w-bench/screen.py --class "content-present-partly-displaced"`:

| | before | after |
|---|---|---|
| calls | 3 x 280 s | 1 x 82 s |
| documents measured | 12 prerendered, **0 measured** | **23 of 23** |
| verdict | none - killed each time | `SCREEN FAIL - nothing improved` |
| error | none | n/a |

`SCREEN FAIL` is the correct answer here: the engine is unpatched, so nothing should improve. The
point is that the instrument now **answers**. Every rendered attempt on this project was blocked
behind this, which is why runs looked dead from outside while the gates were healthy.

## What would prove this wrong

A pod where scipy is already installed and the class still fails to finish in one call. In that case
the EDT cost is not the only term and the profile patch is doing more of the work than measured.

## Also committed, separately measured, not the cause

soffice now gets a user profile per process. Measured by the sub-agent: one 1-page document took
56.7 s while a 120-page hog held the shared profile and 13.9 s on its own; a SIGKILLed parent leaves
3 soffice processes alive holding the shared profile; a wedged survivor took the shared-profile
prerender from 23 of 23 to **0 of 23 in 90 s with no error**. This is a real failure mode and the
patch is kept, but it is not what stalled the 11:24 run.
