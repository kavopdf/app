# 60_text_column_right_edge — the cause is the face Google substitutes, and Verdana fixes it

**28 Nov 2026, fixer slot 11:59.** Class `60_text_column_right_edge`. Five documents have this as
their **only** Google failure, so it is worth five clean documents — the largest single-check
target outside `18_displacement`. Outcome recorded: **lead**, 0 moved (the corpus-wide `.docx`
re-measure that a landed change owes does not fit this slot).

Every number below is from a **real Google round trip**, not a LibreOffice proxy. Two of the five
documents are now **42 of 42 in Google** on a face-name substitution and nothing else.

---

## 1. What was refuted, in Google

`FINDINGS/60-FONT-NAME-HONOURED-JC-INERT-28NOV-fixer.md` established that Google substitutes a
narrower face and that `w:jc` is inert on a one-line paragraph. A sub-agent this run built the
obvious next step — a `ctx.colRight` band map plus a "pin" that sets `w:ind w:right` to the band's
widest line, adds `w:jc="both"`, and adds a trailing `<w:br/>` so the line is no longer a *last*
line and justification has something to stretch.

Measured on a face-substituted LibreOffice render it reported all five going `(0,1) → (0,0)`.
**In Google it does not work, and it makes the document worse.**

| `313_power_of_attorney` | HEAD | justify-pin |
|:--|:--|:--|
| Google result | **41/42** | **40/42** |
| `60_text_column_right_edge` | FAIL (0,1) | **FAIL (0,1)** |
| `18_displacement` | pass | **FAIL** |
| column edge in Google | 477.66 | 480.71 |
| under-run vs source 538.63 | **60.97 pt** | **57.92 pt** |

The pin bought **3.05 pt of the 60.97 pt it needed**, and paid a new `18_displacement` for it. The
trailing `<w:br/>` gives the paragraph an empty final line, and Google does not stretch the line
before it the way LibreOffice does. This patch must not land. That is the whole value of the
measurement: the proxy said "land it", Google said "it costs a document".

## 2. What the cause actually is

`313_power_of_attorney`'s source PDF is `DejaVuSerif` 10.0 pt (1577 of 1638 characters). The engine
declares exactly that: `w:ascii="DejaVuSerif"`, `w:sz w:val="20"`. **The engine is faithful and the
renderer is not.** Google Docs has no DejaVu, substitutes a face ~14.6 % narrower at the same size
(widest line 481.93 → 420.66 pt), and every line stops short of the source's column.

So the "stretch the line to the measure" family — `w:jc`, `w:spacing`, `w:ind right` — is aimed at
the wrong variable. The variable is **the advance width of the face Google actually draws with.**

## 3. Three substitutions, measured in Google

Each probe is HEAD's `.docx` for the document with one attribute changed and nothing else, put
through upload → Google Doc → export PDF → `verify_google.py`.

| probe on `313_power_of_attorney` | column edge | widest line | `60` | whole document |
|:--|--:|--:|:--|:--|
| source PDF | 538.63 | 481.93 | — | — |
| HEAD (`DejaVuSerif` 10 pt) | 477.66 | 420.66 | FAIL | 41/42 |
| face → `Georgia` | 478.01 | 421.01 | FAIL | 41/42 |
| `w:sz` 20 → 23 (10 → 11.5 pt) | 540.78 | 483.78 | **pass** | 40/42 — new `18_displacement` and `34a_span_size_match` |
| face → `Verdana` | **536.15** | **479.15** | **pass** | **42/42 PASS** |

Two things fall out.

- **Georgia is not wide.** It moved the edge 0.35 pt, which is the same as no change: Georgia's
  advance widths at 10 pt are within a rounding error of whatever Google was already substituting.
  A face swap that "looks about right" is not evidence; this is the control that proves the probe
  mechanism works and that the width difference is real.
- **The face name is honoured, and Verdana is the width DejaVu Serif has.** Verdana at 10 pt lands
  2.5 pt from the source column, inside a tolerance of `8.0 + 38.99 = 47.0` pt, and **every other
  check stays passing**. Nothing but the font name changed.

## 4. It generalises

`302_radiology_report` is the second of the five, and it is not a single-face document: its source
is `DejaVuSerif` (567 chars) **and** `DejaVuSans` (491) **and** `DejaVuSans-Bold` (137). Both
declared families were mapped to Verdana and nothing else was touched.

| `302_radiology_report` | HEAD | face → Verdana |
|:--|:--|:--|
| Google result | 41/42 (`60` only) | **42/42 PASS** |

Two of the five, two different declared families, both clean. The three remaining
(`316_contract_with_schedules`, `321_auditors_report`, `370_offer_letter`) were not round-tripped
this run — that is the first thing the next run does, and it is ~4 tool calls each.

## 5. The change the next run should make

In the engine's font-name mapping, when the declared face is a DejaVu family that Google Docs does
not carry, declare a face Google carries with the **same advance widths at the same size**.
Verdana is measured to be that face for `DejaVuSerif` and `DejaVuSans` at 10 pt on these two
documents. Do **not** touch `w:sz`: the size probe above shows `34a_span_size_match` exists
precisely to forbid it, and it fired at 3 of 100 spans.

**This is a `.docx` change and owes the full-corpus `.docx` re-measure — ~54 minutes.** That is the
cost that kept this a lead, and it is the first thing the next slot should budget. The gate is not
what blocked it; the clock was.

**Falsifier:** any document whose Google result falls below HEAD's, or whose `share@5` rises. A
face that is right for `DejaVuSerif` at 10 pt may be wrong at 8 or 14 pt, and may be wrong for
documents whose source face is not DejaVu at all — so the mapping must be keyed on the source
family and size, not applied globally. `313` and `302` are the two probes that must still read
42/42 after the corpus pass.

## 6. The instrument this run proved

The Google round trip is four tool calls per document and it worked first time on all six probes:

    cp <docx> /scratch/output/<name>.docx                     # MANDATORY, or Drive answers 403
    upload(path=..., tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
    GOOGLEDRIVE_CREATE_FILE(mimeType="application/vnd.google-apps.document",
                            parents=["KavoPDF-Verify"], file_to_upload=<upload result>)
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf")
    python3 tools/p2w-bench/verify_google.py <source.pdf> <exported.pdf>

Nothing was created in the user's Drive root; every probe went into the existing `KavoPDF-Verify`
folder and was deleted after measurement. At four calls a document this is now cheap enough that
**no check-60 claim should ever be made from a LibreOffice number again** — the proxy said the
justify-pin worked and Google said it cost a document.

## 7. Not done

No engine change was made, so no `app/` commit and no `regress.py --check` was owed. The five
documents are still open. The three remaining probes, the engine mapping, and the corpus pass are
the next run's work, in that order.
