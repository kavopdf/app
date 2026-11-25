# `18_displacement`: 108 of its 122 failures are exactly +1.0, and not one is negative

**Measured 25 Nov 11:57 IST from the 213 Google verdicts in `benchmarks/gverify/`, attempt 3 of the
10:56 fixer slot.** Lead: a signature, not a fix. No engine code was touched.

## The measurement

`classpick.py --leverage` puts `18_displacement` at **54.8 clean documents** - more than the next three
checks combined - so the question worth asking first is whether its failures share a signature. Read
straight out of the stored verdicts (`checks["18_displacement"]`, source and render values):

| | |
|:--|--:|
| documents with the check measured | 213 |
| failing | **122** |
| failing with `render - source > 0` | **122** |
| failing with `render - source < 0` | **0** |
| median absolute error | 1.0 |
| largest | 299.0 (`416_many_tiny_pages`) |

The error distribution:

| error | documents |
|--:|--:|
| **+1.0** | **108** |
| +2.0 | 5 |
| +3.0 | 2 |
| +4.0 | 2 |
| +5.0 | 1 |
| +7.0 | 1 |
| +9.0 | 2 |
| +299.0 | 1 |

**A hundred and eight documents miss one check by one unit, in the same direction.** That is not 108
independent placement defects; it is one construct with a constant, and the other 14 are a different
problem (`416_many_tiny_pages` at 299 is its own defect and should be parked separately).

## The two hypotheses, and the discriminator

1. **A boundary in the check, not in the page.** If the check's tolerance is `abs(d) < 1` while the
   values are quantised to whole units, then every document that lands exactly on 1.0 fails by
   arithmetic. This is an INSTRUMENT question and it must be answered against the page, not by
   loosening the check: `verify_google.py`'s `18_displacement` threshold and the quantisation of the
   source/render values are the two things to read.
2. **A genuine one-unit placement offset in the engine.** A half-unit rounding in the y coordinate
   (PDF points to twips is x20, to EMU x12700 - both exact, so the suspect is a `round()` applied to a
   half) would show as +1.0 after quantisation on every document with a fractional source y.

**Discriminator:** take three of the 108 (`600_reviewed_invoice_with_annotations` is one - it fails
this check on its fresh verdict, 37/44) and compare the engine's y for one line against the page's y
in PDF points, before any quantisation. If the raw difference is 0.5 and quantisation lifts it to 1.0,
it is (2) with a rounding amplifier; if the raw difference is 0.0 and only the quantised values differ,
it is (1). One document answers it, and it needs the engine's intermediate values, not Google.

## Why it did not land

Both hypotheses end in code that moves a fingerprint - the check's threshold (`verify_google.py`) or
the writer's rounding (`PdfToWord.java`) - and this slot was 60 minutes in with two engine fixes
already queued behind the same 213-document re-measure (the annotation `/Contents` patch and the
ligature/glyph-name fallback). Measuring the signature is the work that makes the next run's first
attempt cheap; guessing at the fix would have been the fourth lead with no measurement.

## What would falsify this

A failing document whose `render - source` is negative, or a pass whose difference is exactly 1.0.
Both are one grep of the same store, and both came back empty above.
