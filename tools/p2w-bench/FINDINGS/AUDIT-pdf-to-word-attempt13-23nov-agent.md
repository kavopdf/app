# PDF-to-Word — deep audit, attempt 13 of 15

Agent, 23 Nov 2026. Read-only. Third of five on `DocxWriter`. The target was the positioner, against
`18_displacement` — 100 of 190 scored documents, the largest class by a wide margin and about position, which is
the property the user names first.

---

## M1 — the invariant is stated twice in prose and enforced nowhere

    976:   "the measurement the one-positioner-per-page invariant is stated against, so it is …"
    4201:  "It is what the one-positioner-per-page invariant is stated against, and it is off unless
            -Dp2w.census=<file> names an output."

**Both occurrences are comments.** There is no assertion, no counter consulted at runtime, no refusal, no note in
`Report`. The tool says, in two places, that one writer positions a page's lines — and nothing in the code checks
that it is true.

**That is the shape of every finding in this series, at its largest scale.** If two writers both move the flow's
`y` on one page, the second one wins and the first one's lines land somewhere else. That is displacement. And the
tool neither prevents it nor records it.

---

## M2 — the measurement for exactly this defect exists, and it is switched off

The census counts, per page, which writer wrote the page's lines and which of them moved the flow's y:

    CENSUS  docName  page=  pass=  flow=  row=  col=  tbl=  anchor=  stamp=
            anchorRule=  anchorPos=  flowYset=  absYset=  rewind=  rewindWorst=
            cellYset=  rewindWho=

**`rewind` is the displacement metric.** From `cenSetY` (4228):

    if (ctx.flowY >= 0f && y < ctx.flowY - 0.01f) {
        ctx.cenRewind++;
        if (back > ctx.cenRewindWorst) ctx.cenRewindWorst = back;
        ctx.cenRewindWho.append(who + ":" + …);
    }

So a **rewind** is an assignment that moved the flow's y *up* the page — a line placed above where the flow had
already reached. That is displacement, counted exactly, with the worst amount in points and the name of the writer
that caused it.

**`-Dp2w.census=<file>` turns it on. Nothing turns it on.** No run, no cron, no measurement in `p2w-bench` passes
it — attempt 12 confirmed the flag list is not documented anywhere the fixer reads.

**So the tool has a per-page, per-writer, in-points measurement of the largest defect class in the corpus, and it
is off.**

---

## M3 — what a run would learn in one pass, and what it cannot learn today

With the census on, a single document produces one line per page naming:

- **how many lines each of eight writers wrote** (`pass`, `flow`, `row`, `col`, `tbl`, `anchor`, `stamp`,
  `anchorRule`);
- **how many assignments moved the flow's y** (`flowYset`, `absYset`, `cellYset`);
- **how many moved it backwards** (`rewind`), **by how much at worst** (`rewindWorst`), and **who did it**
  (`rewindWho`).

That is the answer to "why is this document displaced" written per page, in the tool's own vocabulary.

**Today a run cannot answer it at all.** It knows only that `18_displacement` failed on 100 documents — a count of
symptoms with no attribution. That is why the class has stayed at 100 across every attempt in this series: the
number is visible and the mechanism is not.

---

## M4 — what this attempt did NOT do

**It did not run the census.** There is no Android runtime here, and the census writes to a file named by a system
property that only the app process can set.

**So M1 and M2 are read from code and are certain; M3 is an inference about what the output would contain, drawn
from the field names and from `cenSetY`'s own logic.** To settle it: one device run with `-Dp2w.census=/tmp/c.txt`
on three of the 100 displaced documents. If `rewind` is non-zero, M1 is confirmed as the mechanism and `rewindWho`
names the writer to fix.

---

## For the fixer

**M2 first, and it costs nothing but a flag:** turn the census on for the 100 displaced documents and read
`rewind`, `rewindWorst`, `rewindWho`. That converts the largest class in the corpus from "100 documents fail" into
"these writers rewind the flow, by these amounts, on these pages".

**M1 second:** once the census names the writers, the invariant can be enforced where the census counts — a
rewind in production is either a bug in that writer or a legitimate re-layout, and the census data is what tells
the two apart.

**Do not enforce the invariant before reading the census.** A rewind is not automatically wrong — a page with a
stamp at the top legitimately resets the flow. Enforcing first would break the documents that work.

Verify before changing. This attempt read code; M4 says plainly what it did not run.
