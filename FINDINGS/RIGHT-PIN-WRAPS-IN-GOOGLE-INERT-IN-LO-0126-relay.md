# THE RIGHT-EDGE PIN WRAPS IN GOOGLE AND IS INVISIBLE IN LIBREOFFICE

**26 Nov 2026, 01:26 IST · relay run · engine `ae01e26d12ea9ac0` · reverted, not committed**

## What was proposed

`FINDINGS/../SHORTLIST.md` ranked this first and priced it at **+5 of the 6 solo-60 documents**:

> A left-aligned body line's right extent is never written. `flowFromBox` sets `rightTw = 0` for
> `align == 0` and emits no `w:jc`, so the line's right edge is whatever Google's substitute face
> makes it. Fix: pin the extent (`w:jc="distribute"` + `w:ind w:right` at the source ink edge).

The one untested assumption was stated as a yes/no: *does Google honour `w:jc="distribute"` on a
one-line paragraph, or normalise it to `both` and leave the line ragged?*

## What was built

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, `flowFromBox`, after the three `w:jc`
branches: for `align == 0`, non-rotated, not `inColumn`, and with `stretchTw(b) == 0` (a justified
line is already stretched, so it must not be stretched twice), write
`w:ind w:right = pageWidth - b.right` and `w:jc="distribute"`.

Gated by `p2w.rightpin` (default 1) with a width gate: pin only where the file's own 0.5 em character
average (`chars * 0.5 * size`, the estimate `cellWrapLines` uses) already fits inside the page's own
measure `b.right - b.x`, so the pin can never cut a line below the width it was drawn in. Arm 2 pins
regardless of that gate.

The whole patch is `git diff` of that build; the tree is reverted to HEAD and nothing is committed.

## The measurement — one document, one variable, both renderers

`302_radiology_report`: 1 page, fails `60_text_column_right_edge` only in the store, `.txt` clean,
store direction `under`. Same engine build for both arms; the only difference is `-Dp2w.rightpin`.

| renderer | arm | checks | `60` | `17_matched_runs` | `26_text_overlap` | `18` med_dy |
|---|---|---|---|---|---|---|
| **Google** | 0 (control) | **41/42** | `(0,1,False)` | 33/33 PASS | 2 PASS | −1.5 |
| **Google** | 1 (pin) | **39/42** | `(0,1,False)` | 21/33 **FAIL** | **28 wrapped** FAIL | +2.0 |
| LibreOffice | 0 (control) | 42/42 | `(0,0,True)` | 33/33 PASS | 0 PASS | — |
| LibreOffice | 1 (pin) | 42/42 | `(0,0,True)` | 33/33 PASS | 0 PASS | — |

Arm 1 wrote 21 `w:jc="distribute"` paragraphs and 21 non-zero `w:ind w:right` on this document
(counted in `word/document.xml`), so the construct reached the file; the paragraph count was unchanged
at 38 in both arms.

## What it refutes

1. **The pin does not move the column edge.** `60` reads `(0,1,False)` in both arms: the render's
   column is still short by the same amount with the right extent written explicitly. Whether Google
   normalised `distribute` to `both` or filled to a different frame, the edge it reports did not move.
   The yes/no the shortlist named is answered **no** — `distribute` + `w:ind w:right` does not pin the
   edge on a one-line paragraph.
2. **The pin wraps.** 28 lines wrapped under the pin (`26_text_overlap` detail `wrap: 28`, against 2
   in the control), and `17_matched_runs` fell 33 → 21. So the width gate at 0.5 em is far too loose:
   the render's own natural width exceeds the page's ink width on this document even though the 0.5 em
   average says it should fit. Pinning to the ink edge is a *compression* on these lines, and
   `distribute` cannot compress — it re-breaks.
3. **LibreOffice cannot see this change at all.** Both arms are byte-for-byte equal in every check in
   LO — 42/42, 33/33, 0 overlaps. The change is invisible to the proxy by construction, which is what
   the shortlist claimed as its virtue. It is also its danger: **`regress.py --check` and the whole
   LibreOffice corpus pass cannot protect this class of change.** A pin that wraps 28 lines in Google
   and costs two checks is a 42/42 PASS in LibreOffice. This is the concrete case behind charter rule 1,
   and it means the pin can only ever be shipped after a Google round trip on every document it touches.

## What it does not refute

The mechanism — the right extent of a left-aligned line is a property of the resolved face — is not
touched by this result. What is refuted is this *implementation*: pinning to the source ink edge with
`w:jc="distribute"`. A variant that pins to a width the render's text actually fits (i.e. one that
widens the available measure rather than matching the source's) would fix nothing, because the fix
*is* the edge.

## What the next run should try, if it tries this again

Measure the render's own natural line width first and pin only where it is **strictly narrower** than
the source ink edge. The engine has no face metrics today, so the width gate must come from a
measurement, not from a 0.5 em average: render the document in the substitute face (LibreOffice's is
not Google's, but it is closer than 0.5 em) and compare per-line widths before writing the pin. A
per-line gate derived from `w:spacing` — spread the measured shortfall over the characters, the
mechanism `stretchTw` already implements — is the alternative that cannot wrap, and it is the same
machinery one branch above, so it is a smaller change than this one was.
