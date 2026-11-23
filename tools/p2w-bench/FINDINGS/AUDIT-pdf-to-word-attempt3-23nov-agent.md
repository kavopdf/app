# PDF-to-Word — deep audit, attempt 3 of 5

Agent, 23 Nov 2026. Read-only. Attempt 1 was the writers, attempt 2 the page-count gate. This one started as
"do the 42 checks measure what they claim" and ended somewhere more useful: **the answer already exists, and it
is in the wrong place.**

---

## C1 — 15 checks never fail on any of the 190 scored documents

Counted from every scored verdict:

    check ids defined in verify_google.py : 47
    ids that appear as a FAILURE somewhere: 33
    ids that never fail on any document   : 15

    01_page_count   08_image_count   14_filled_shapes   15_links
    34b_span_colour_match   34c_span_weight_match   36_underline_rules
    39_image_position   42_justification_edges   48_image_area
    49_page_size   50_annotation_text   54_image_dpi
    55_orientation_mix   61_blank_not_filled

`01_page_count` is expected — the refused documents are excluded from the scored set, so it cannot fail here.
The other fourteen are the question: do they pass because the tool is right, or because they cannot fail?

---

## C2 — the answer exists, and it says all 47 can fail

`/scratch/saved/FALSIFY-47.md` holds a falsifiability gate over all 47 docx checks — one row each, with the
mutation aimed at it and which side it fired on:

    | `01_page_count` | fired | m_ren_page_dup | render | 0 |
    | `04_chars_missing` | fired | m_ren_erase_all | render | 7 |

    47 rows, status "fired" on every one, 0 not-fired.

So all 47 checks are falsifiable. **C1 is therefore not a defect:** those fourteen pass on these documents
because the conversion is right on them, not because the check is blind. That is worth knowing, and it is the
opposite of what C1 looks like on its own.

---

## C3 — that result is not in the repo, so the fixer cannot read it

    benchmarks/FALSIFY-47.md     does not exist
    benchmarks/FALSIFY-47.json   does not exist
    /scratch/saved/FALSIFY-47.*  exists  (3,306 bytes + 98,760 bytes)

A result that answers the biggest question about the instrument — are its checks real — lives in a session
scratch directory that is wiped, not in the repo every run clones. Any run that asks "can this check be trusted"
has to re-derive it, and nothing tells it the answer is already known.

**This is the same failure as the earlier `LAST-MESSAGE` work:** the artefact exists, the reader does not know.

---

## C4 — `TXT-FALSIFIABILITY.md` still carries the number the gate replaced

The file the fixer reads opens with:

> *"The 47 docx checks were measured at 66 % unfalsifiable passes."*

That was the state **before** the gate in C2 ran. After it, the answer is 0 of 47 unfalsifiable. The two files
disagree, and the one in the repo is the stale one — and it is the one a reader meets first, because it is the
file whose name says falsifiability.

A record that gets edited to match the present is not a record, which is why `TXT-FALSIFIABILITY.md` keeps its
own t13 history intact. But a superseded headline left at the top of a document, with no pointer to the result
that superseded it, is not a record either — it is a trap.

---

## C5 — the verdict cannot distinguish "passed" from "did not run", by name

The verdict records:

    {name, status, engine, total, passed, rc, failed: [...]}

`failed` is a list of ids. `passed` is an **integer**. So a verdict says *36 of 42 passed* and names only the six
that did not.

For auditing a check this is the wrong way round: to ask "did `36_underline_rules` run on this document" you need
its name in the pass list, and there is no pass list. `total` says how many ran; nothing says which.

**This is why C1 could only be stated as "never fails" and not "never runs".** It is a small schema change with a
large effect on what can be audited.

---

## For the fixer

- **C3 first, and it is nearly free:** copy `FALSIFY-47.md` into `benchmarks/` so the answer travels with the
  repo. Verify the file is the one the gate produced before committing it.
- **C4:** point `TXT-FALSIFIABILITY.md`'s opening at the gate result rather than leaving the superseded 66 % as
  the first thing read. Do not delete the history below it.
- **C5:** adding the passed ids to the verdict changes a file every tool reads — regression-check it on a
  document whose page count is right before trusting it.
- **C1 needs nothing.** It is explained by C2.

Verify before changing. This attempt read verdicts and one saved file; it ran nothing.
