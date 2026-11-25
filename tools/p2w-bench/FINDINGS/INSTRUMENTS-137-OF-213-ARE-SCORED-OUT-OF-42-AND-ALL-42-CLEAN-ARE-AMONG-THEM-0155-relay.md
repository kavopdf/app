# All 42 "clean" documents are scored out of 42, and the five checks they are missing are the table checks

**26 Nov 2026, relay fixer slot 01:25 IST · read-only audit by a sub-agent, re-checked by this run
against `benchmarks/gverify/*.json` · no code changed.**

## The claim

`benchmarks/gverify/*.json` carries `offered` (the 47 ids) on all 213 verdicts, and `total` (what
actually ran):

| `total` | documents | missing ids |
|---:|---:|---|
| 42 | 137 | 62, 63, 64, 65, 66 — the table checks |
| 44 | 2 | 64, 65, 66 |
| 47 | 74 | none |

**Every one of the 42 documents the report calls "clean" is in the 137.** So the headline "42 of 213
clean" and the brief's "6 clean of 192" are both true of different denominators, and the honest one is
the smaller: **0 of the 74 documents offered all 47 checks passes**, because no document whose tables
were actually checked has ever been clean.

## Why the five vanish

`tools/p2w-bench/tablechecks.py:225` returns `{}` when the page has no grid under any table. An empty
dict does not fail the check — it removes it from the denominator, so `total` drops and the document
scores a pass it was never offered. The one-line change the audit proposes:

```python
return {cid: (n_docx, 0, not n_docx) for cid in CHECKS}   # CHECKS at :208, n_docx = len(dtabs) at :205
```

A document whose `.docx` genuinely carries no table still passes; one whose `.docx` carries tables the
source never gridded fails as "asked and could not answer" instead of disappearing.

## The same shape elsewhere (unfired, but it is the same defect)

| check | why it cannot fail | file:line |
|---|---|---|
| `61_blank_not_filled` | source side hard-coded to 0; Google rasterises every band | `verify_google.py:2934` |
| `50_annotation_text` | no-`.docx` branch returns literal `True` | `:1703` |
| `36_underline_rules` | `… if s_u else True` | `:3298` |
| `54_image_dpi` | `s_d == 0` → constant `True` | `:2227` |
| `08/39/48` image checks | source 0 on 196 documents | `:4767`, `:3496`, `:4365` |

`53_embedded_faces:2119` is the same defect as 50, and the file says so at `:28`.

**Not measured this run: what each document's score becomes when the abstention is made honest.** The
audit gives an upper bound of 42 flips and says explicitly that this is exposure, not verdict. The next
run that takes this should run it as an attempt with a before/after on the whole corpus — it changes
the denominator for 137 documents, so it is a `regress.py` question, not a local edit.
