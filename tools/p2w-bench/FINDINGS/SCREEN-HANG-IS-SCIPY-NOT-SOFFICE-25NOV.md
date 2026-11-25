# The screen.py "soffice prerender hang" is not soffice. It is the scipy fallback.

**25 Nov 2026, fixer run 15:58 IST. Engine 85b8735f. Measurement only - no code change landed.**

## The carry-over this closes

The last run's handoff said: *"Fix or bypass the screen.py soffice prerender hang FIRST - it blocks
every rendered attempt."* Two runs have now spent time on the assumption that soffice blocks.

## What I measured

**With scipy importable, screen.py does not hang.**

| class | documents | wall | verdict |
|:--|--:|--:|:--|
| `content-partly-lost-and-displaced` | 5 | 43 s | SCREEN FAIL - 5 measured, 5 same |
| `content-present-partly-displaced` | 23 | 190 s | SCREEN FAIL - 23 measured, 23 same |

soffice converted every chunk (`prerender 5 docx in 12 s`, `12 in 29 s`, `11 in 35 s`).

**With scipy unimportable, the stall reproduces exactly** - and the stack dump lands nowhere near
soffice:

```
[10:47:39] prerender 6 docx in soffice batches of 12
[10:47:39] scipy missing - installing (the fallback transform is ~48x slower per page)
[10:47:41] WARNING: scipy STILL missing - measuring on the exact-fallback transform.
EXIT=124   # killed at 240 s, 0 of 6 measured, no error

  File "benchmarks/p2w.py", line 224 in _dt1d
  File "benchmarks/p2w.py", line 235 in edt
  File "benchmarks/p2w.py", line 776 in invention
  File "benchmarks/p2w.py", line 1128 in measure_doc
  File "tools/p2w-bench/screen.py", line 185 in main
```

Same class, scipy present: **52 s, 6 measured**. Before 240 s timeout / 0 measured -> after 52 s / 6.
Same verdict, same numbers (share5 5.16, max_pt 46.56 - which `benchmarks/RANKING.csv` independently
carries): **the fallback is 9.5x slower, not different.**

Ruled out, each by a direct measurement: soffice daemonising (two sequential conversions, rc=0, PDF
written, 0 lingering soffice), a stale shared profile lock (`~/.config/libreoffice` does not exist;
profiles are per-pid under `/tmp/p2w-lo`), soffice waiting on stdin (`stdin=DEVNULL`, line 514),
`--convert-to` rejecting the extension (all 213 inputs are `.docx`), the `.soffice-fail` ledger
(empty).

## Two real defects this exposed, neither fixed here

1. **`_ensure_scipy()` spends up to 220 s of a 280 s budget inside the measurement call** (p2w.py:108,
   `sh("python3 -m pip install -q scipy", 220)`) and then only **warns**. A screen that cannot finish
   is indistinguishable from a screen that found nothing, and the caller reads it as "no improvement".
   It should refuse, not warn. `pod-prep.sh` already treats scipy as a prerequisite - the guard here
   is the second place the same fact is written down, and it disagrees.
2. **The colour and tone axes are silently dropped on a scipy-less pod.** `p2w.py:1112` does
   `from scipy import ndimage as _nd` *inside* a `try/except: pass`, so `colour_share` goes 75.37 ->
   `None`, `tone_share` 70.80 -> `None`, `coloured_px` 9003 -> 0. `share@5` is unaffected - which is
   why the verdict held - but **a class judged on colour or tone would be measured against nothing.**
   Not stated anywhere in the docs.

## What this means for the pipeline

The blocker named in the carry-over is not a blocker on a prepared pod. `pod-prep.sh` installs scipy,
and the screen then finishes in 43-190 s for a 5-23 document class. **Run `pod-prep.sh` before the
first screen and the class is screenable.** The two defects above are what to fix so that a pod
without scipy fails loudly instead of silently measuring nothing.

## What would prove this wrong

A class where screen.py stalls with scipy importable; a live soffice in `ps` during a stall; or a
stack dump landing inside `soffice_pdf`/`Popen`/`wait` instead of `_dt1d`.
