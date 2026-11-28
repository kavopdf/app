# `60_text_column_right_edge`: the font-name lever measured in Google, and `w:jc="both"` measured inert

**28 Nov 2026, fixer slot 09:55 IST.** Repo `kavopdf/app` @ HEAD `bcc0ea0c`. Engine in tree
`a05b20eb05fe0fc8`. Every Google number below is a live round trip: `.docx` → `GOOGLEDRIVE_CREATE_FILE`
as `application/vnd.google-apps.document` in `KavoPDF-Verify` → `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`
as `application/pdf` → local copy → PyMuPDF. The six probe Docs were created in this run and deleted at
its end; nothing outside the folder was touched, nothing else was deleted.

**Why this was run.** `FINDINGS/60_text_column_right_edge-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md` §3 concluded
that "no font name can satisfy both" renderers — but it measured that probe **in LibreOffice only**, and
its own §"What would prove this wrong" asks for the Google render. The gap was one upload wide. This
closes it, and it changes the verdict.

## The document and the numbers that stay fixed

`313_power_of_attorney`, 1 page, 41/42 in the store, failing only `60`. Source PDF (PyMuPDF):

| | source |
|:--|:--|
| pages | 1 |
| text lines (span-lines) | **30** |
| body face @ size | `DejaVuSerif` @ 10.0, `DejaVuSerif-Bold` @ 13.0 |
| body left edge | **56.7 pt** |
| body right edge, widest | **538.63 pt**, reached by **10 of 30 lines** |

`.docx` at HEAD: 29 body paragraphs, `w:ind left="1134"` (56.7 pt), `w:ind right="0"`, page `11906` tw
(595.3 pt) — so the paragraph measure is **538.6 pt, already correct**. `w:jc` appears **once** in the
whole document and it is `center`; there is no `both`, no `w:tab`, and no letter-spacing run.

## 1. The font-name lever, measured in Google (four faces)

Same `.docx`, `word/document.xml` hand-edited so the only change is the declared face name. No engine
rebuild, so the probe measures the **name** and nothing else.

| variant | faces in the Google export | max right edge | gap to 538.63 |
|:--|:--|--:|--:|
| **source** | DejaVuSerif, DejaVuSerif-Bold, Helvetica | **538.63** | — |
| `a_head` (declares `DejaVuSerif`) | ArialMT, Arial-BoldMT, Calibri, Calibri-Bold | 480.14 | **−58.49** |
| `b_georgia` | Calibri, Georgia, Georgia-Bold | 480.49 | −58.14 |
| `c_notoserif` | Calibri, NotoSerif-Regular, NotoSerif-Bold | **505.01** | **−33.62** |
| `d_times` | Calibri, TimesNewRomanPSMT, TimesNewRomanPS-BoldMT | 449.00 | −89.63 |
| `e_libserif` (declares `Liberation Serif`) | ArialMT, Arial-BoldMT, Calibri (no Liberation) | 480.14 | −58.49 |

Three results, none of them assumed:

1. **Naming a face Google has does change the render.** `Noto Serif` reaches 505.01 where HEAD reaches
   480.14 — a **24.9 pt** improvement in the renderer the user opens. The 24 Nov finding's prediction
   that the name is inert in Google is wrong; the name is honoured.
2. **It is not the fix.** The best of four faces closes **33.6 of the 58.5 pt**. `60`'s slack is one word
   of the column's own text (agent census 28 Nov: 17.72 pt on `79`), so 33.6 pt still fails.
3. **`Liberation Serif` is not in Google's library** — it falls back to Arial, byte-for-byte the HEAD
   render (480.14 on both). Any engine change that names a Liberation face buys nothing in Google.

## 2. `w:jc="both"` is inert on this document, and the reason is structural

The obvious lever for a justified column is paragraph justification. `w:jc="both"` was appended to all
**29** body paragraphs (after `w:ind`, which is the schema position), the package rebuilt, and rendered in
Google:

| | HEAD | `w:jc="both"` ×29 |
|:--|--:|--:|
| pages | 1 | 1 |
| lines | 30 | 30 |
| left edge | 57.0 | 57.0 |
| sizes | 10.0, 13.0 | 10.0, 13.0 |
| **all 30 right edges** | — | **identical to 0.1 pt** |

The export is the same render. The reason is arithmetic and it is the useful part: **the document has 29
paragraphs and 30 lines.** The engine emits one paragraph per source line, so nearly every line is its own
paragraph's *last* line — and justification never stretches a last line. `w:jc="both"` therefore has
nothing to act on, in Word or in Google, and no amount of it will widen these lines.

**This is the finding.** For this class the stretch must happen **inside** the line, and the two levers
the engine has for that are both closed by measurement:

* `w:spacing` (letter-spacing) — emitted by `stretchTw()`; already on `google_safe.py`'s measured-ignored
  list.
* `w:jc` in every form — inert here for the structural reason above.

What is left is positioning, not justification: explicit tab stops or a right tab at the column edge with
the line's last word placed on it (`DocxWriter.java:3806-3812` already emits exactly that construct, gated
to table rows; the 28 Nov census measured Google honouring it to **0.11 pt**). That is the next attempt,
and it is the same construct the census named.


## 2b. `w:jc="distribute"` + a per-line right indent is inert too — 60-P's load-bearing assumption is FALSE

`tools/p2w-bench/FINDINGS/18-60-59-THREE-CLASSES-ROOT-CAUSED-AND-THE-LEVER-THAT-CANNOT-REACH-1900-fixer.md`
§6 item 2 asks for exactly one thing: *"60-P falsified in one Google round trip on `302` (does
`distribute` pin a one-line paragraph?)"*. 60-P measured **−42.09 pt → +0.38 pt** and 42/42 on five
documents **in LibreOffice**, and the assumption under it was never tested in Google.

Measured here, on `313`, same `.docx`, `word/document.xml` only. 60-P as specified: `w:jc="distribute"`
plus a right indent that pins the paragraph's measure to the source's column (`w:ind right="1133"` =
595.3 − 538.63 pt, so the measure becomes the source's 481.9 pt).

| | pages | lines | max right edge | lines at 538.63 ± 0.6 |
|:--|--:|--:|--:|--:|
| source | 1 | 30 | **538.63** | **10** |
| HEAD | 1 | 30 | 480.14 | 0 |
| `w:jc="both"` ×29 | 1 | 30 | 480.14 | 0 |
| **60-P: `w:jc="distribute"` ×29 + `w:ind right="1133"`** | 1 | 30 | **480.14** | **0** |

**All three variants export the same render, to 0.1 pt on all 30 lines.** The right indent is consistent
with the measurement rather than contradicting it — the substitute face's longest line is 480.1 pt and
the pinned measure is 481.9 pt, so nothing re-breaks, which is what is seen. But `distribute` had a 1.8 pt
stretch available and took **none** of it.

**Verdict: 60-P must not be landed.** Its whole effect in LibreOffice comes from a construct Google does
not apply to a one-line paragraph. Recording this here so the next run does not spend a slot on it, which
is what §6 item 2 was asking for.

**What this does not establish.** It does not show Google ignores `w:jc` in general — it shows that on a
document where every line is its own paragraph's last line, neither `both` nor `distribute` moves the
right edge in the exported PDF. The mechanism (normalisation on import, or the interaction with
`w:line` exact and `w:snapToGrid w:val="0"`) was not isolated, and a probe that separates them would be
the next step if anyone wants to reopen it.

## 3. What did NOT move, so the next run does not re-measure it

* Line breaking is already exact. Left edge 57.0 vs source 56.7 (**0.3 pt**), the same 30 lines in the
  same order, the same two sizes, 1 page in both. **There is no reflow on this document** — the census's
  "line counts are identical across every solo document" holds on `313` too.
* The paragraph measure is already exact (538.6 pt computed, 538.6 pt in the source). Do not "fix" the
  column width; there is nothing wrong with it.
* The renderer is not re-breaking the text. The only thing missing is the stretch.

## What would prove this wrong

* A Google export of `313` with `w:jc="both"` on 29 paragraphs whose right edges are *not* identical to
  HEAD's — that would put the lever back. Measured here: identical.
* A face name that lands the column at 538.6 ± one word of slack in Google. `Noto Serif` is the best of
  the four tried and lands 33.6 pt short; a fifth face could still close it, and the method is one upload.
* An engine change that emits a right tab at the column edge on full-measure lines and **keeps
  `17_matched_runs`** — the census measured that the tab drops `17` from 34 to 13, which is why the
  change is not landable as it stands. `17` is the binding constraint, not `60`.
