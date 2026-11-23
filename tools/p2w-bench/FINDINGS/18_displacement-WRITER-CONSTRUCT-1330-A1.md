# 18_displacement — the writer construct, its measured reach, and the minimal change

**23 Nov 2026 · slot 13:30 IST · clone at HEAD `kavopdf/app` (depth 1) · engine built from this clone
(`build-engine.sh`, 38 s) · corpus fetched whole (213/213) · every number below is a measurement made
in this sandbox on this engine, except where a line is explicitly marked "recorded"**

---

## 0. Verdict in one paragraph

The construct is **the table-gap spacer paragraph, which carries its entire height in `w:line` with
`w:lineRule="exact"` and `w:before="0"`**. Google Docs does not lay `w:line` as a length: it charges a
multiple of the substitute face's line height with a 0.069 em floor, so the declared gap arrives at
roughly a fifth of its value. The table under that spacer, every row in it, and every block below it
are then drawn too high by ~80 % of the gap — which is exactly what `18_displacement` charges.
**It reaches 7 of the 13 documents that fail `18_displacement` alone in Google. It cannot reach the
other 6, and it cannot reach the 34.5-document leverage figure.** The 34.5 is the price of the whole
check, not of this construct; the repository has measured three distinct mechanisms in this class and
this run re-confirms the split rather than a single fault.

---

## 1. The construct, exactly

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:6067-6072` (the `else` arm of the spacer
emission, reached when the page has no slack):

```xml
<w:p><w:pPr><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="0" w:after="0" w:line="2880" w:lineRule="exact"/>
  <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>
```

The spacer exists because OOXML gives a table no before-spacing of its own: the gap between the last
line of prose and the table's top rule has to be carried by an empty paragraph. The writer computes
that gap correctly (`spacerTw`, `DocxWriter.java:5984-6007`) and then puts it in the wrong property.

**Mechanism, in the renderer that matters.** LibreOffice and Word advance a paragraph by
`w:before + w:line/20`. Google advances by `w:before + max((w:line/240) * lineHeight(face, size),
0.069 * size)` — a *multiple of the substitute face's line height* with a floor, not a length. The
engine's own comment at `DocxWriter.java:75-107` states the law and the one value (`w:line = 1.38 *
size`) at which the two renderers agree. A 2880-twip `w:line` is 144 pt to LibreOffice and ~30.2 pt
to Google (recorded: `FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-...-1005-f1x.md`,
`FINDINGS/18_displacement-DITHER-REFUTED-AND-THE-GUARD-THAT-REPLACES-IT-0030-fixer.md` §"The spacer
is still the best lead"). The gap is drawn ~80 % short, the table rides up, and the displacement is
not a wobble: it is one constant per page, the size of the missing gap.

`w:before` on the same empty paragraph is delivered **1:1** by Google (measured 22 Nov, quoted in the
same finding; and the engine's guarded branch at `:6057-6066` exists because of it). That is the whole
difference between the two arms of the `if`.

## 2. Why it is not the other three constructs in this class

The class has been worked for a week; four constructs have been proposed and three have been refuted
by measurement. Keeping them apart is the point of this section.

| candidate | status | evidence |
|:--|:--|:--|
| **the table-gap spacer in `w:line`** | **live, and this finding** | 6 documents 42/42 in Google when spent as `w:before` (recorded, 10:05) |
| row pitch / `w:trHeight` (the 0.75 pt quantum, "dither") | **refuted** | Google stores the declared `w:trHeight` and lays the cell's line box instead; a change to the declaration is inert in Google and a 0.75 pt regression per row in LibreOffice (`18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`, `-CORRECTION-1045-relay.md`) |
| first row's cell `w:before` (`balance-sheet-two-columns-of-figures`) | **real, 1 document, unfixed** | 248 tw where 174 is right; `w:trHeight` on row 0 moves the rows below and not its own text (`18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md`) |
| `w:before` at the top of a page | **different check, same family** | Google renders 0.33 pt of 55.15 pt (`google_safe.py` entry `w:before-page-top`) |

Also excluded by construction, and worth saying because it is the mistake the last three slots nearly
made twice: **`w:trHeight` is not the height.** Google normalises `hRule="exact"` to `atLeast` on
import and lays `max(declared, cell content)`. A fix aimed at the row declaration moves LibreOffice
only. The spacer fix does not touch a row at all.

## 3. Reach, measured this run at HEAD

Population: `benchmarks/gverify/*.json`, 192 scored documents. 26 fail exactly one check; **13 of
those 26 fail `18_displacement` and nothing else** — the task's "13+", confirmed from the files, not
from a table. (This matches `18_displacement-SOLO-DOCS-16-142500-agentB.md` in kind; the set is 13 on
the current JSON set, 16 in the earlier slot's count.)

Each of the 13 was converted with the engine built from this clone, and its `word/document.xml` read
for spacer paragraphs (`<w:sz w:val="2">` mark, no text run) whose whole height is in `w:line`:

| document | Google score | tables | dropped-gap spacers (pt, in `w:line`) | gap it never draws |
|:--|:--|--:|:--|--:|
| `68_journal_wide_table_spanning` | 41/42 | 1 | 144.0 | ~115 pt |
| `insurance-policy-schedule` | 46/47 | 3 | 14.4, 6.4, 6.0 | ~21 pt |
| `mobile-bill` | 46/47 | 3 | 12.4, 6.4, 6.2 | ~20 pt |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | 1 | 18.3 | ~15 pt |
| `two-tables-stacked-with-no-gap` | 46/47 | 1 | 12.35 | ~10 pt |
| `table-with-no-header-row` | 46/47 | 1 | 12.35 | ~10 pt |
| `bus-timetable-station-left-times-right` | 41/42 | 1 | 6.35 | ~5 pt |
| `16_right_aligned_amounts_txtpos` | 41/42 | 1 | none | — |
| `362_price_list_dense` | 41/42 | 1 | none | — |
| `36_embedded_subset_font` | 41/42 | 1 | none | — |
| `71_invoice_space_aligned_no_rules` | 41/42 | 2 | none | — |
| `balance-sheet-two-columns-of-figures` | 41/42 | 2 | none | — |
| `31_times_body_arial_headings` | 41/42 | 0 | none | — |

**7 of 13 carry the construct; 6 do not.** And a second measurement, which is the uncomfortable one:

> **the guarded `w:before` arm fired on 0 of the 13 documents at HEAD.** Every spacer in the
> population is written in the dropped form. The fix landed at 00:51 is in the tree
> (`DocxWriter.java:6050-6069`) but its guard is refusing every one of these pages — which is why the
> class still reads 101 open.

Two of the six with no spacer are worth naming: `31_times_body_arial_headings` has **zero tables**
(its displacement is a block placement offset, group C in
`18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md`), and
`balance-sheet-two-columns-of-figures` is the first-row `w:before` case in §2. Neither can be moved by
this construct, and any claim that "the spacer cleans the class" is false on those two alone.

## 4. Which documents would go CLEAN

Two populations, and they must not be added together.

**(a) Already measured in Google, by earlier slots, on the unguarded split** — 6 documents to
`42/42`, recorded in `18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md` group A
and in the 10:05 finding: `16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`,
`29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`,
`73_marksheet_subject_marks_grade`. Two cost documents: `mobile-bill` and
`insurance-policy-schedule` — exactly-full pages that overflow to two pages, 46/47 -> 43/47, content
lost.

Note what that list proves about *my* population: three of those six (`16`, `22`, `29`, `41`, `73` —
four of them, in fact) do not appear in §3's dropped-spacer column on this engine, so they are clean
on a build that differs from this HEAD. The numbers in (a) are recorded, not re-measured here.

**(b) What this run's build can support** — the ceiling is **7 documents**, the seven in §3's upper
block, and only where the page has the slack to hold the gap. That is the honest answer to "which
documents become CLEAN if this is fixed": **at most 7, never 13, never 34.5.** The 34.5 from
`classpick.py --leverage` (re-run this slot: `18_displacement 34.5`) is the count of documents where
this check is one of several failures; it is a price list, not a fix.

## 5. The minimal writer change

The guard at `:6055` is binary: spend the whole gap, or spend none of it. The two documents it
protects are protected because Google, having been given the gap, has nowhere to put it. The minimal
change is to make the spend **partial** — spend what the page can still hold, leave the rest in
`w:line`. The sum `before + line` is unchanged in every case, so LibreOffice and Word render the page
they always rendered, and Google draws `min(gap, slack)` instead of 0.

`DocxWriter.java:6050-6069` — measured diff (this run, applied to the clone, no commit):

```java
             int spacerHairTw = 1;
             int rowExcessTw = 15 * Math.max(0, ctx.pageRowCount);
             int slackTw = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * (float) TWIPS_PER_PT);
             int roomWantTw = Math.max(0, spacerTw - 20);
             int wantTw = Math.max(0, spacerTw - spacerHairTw);
+            // PARTIAL SPEND: spend as much of the gap as the page can still hold and
+            // leave the remainder in w:line. The sum is unchanged, so LibreOffice and
+            // Word see the same page; Google draws min(gap, slack) instead of none of it.
+            int partialTw = Math.max(0, Math.min(wantTw,
+                    slackTw - ctx.spacerSplitTw - rowExcessTw));
             boolean spendable = slackTw > 0
-                    && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw;
+                    && partialTw > 0;
+            int spentTw = partialTw;
             if (spendable) {
                 ... .append(wantTw)                       -> .append(spentTw)
                 ... .append(Math.min(spacerHairTw, spacerTw))
-                ... .append("" w:lineRule="exact"...)
-                ctx.spacerSplitTw += roomWantTw;
+                       -> .append(Math.max(spacerHairTw, spacerTw - spentTw))
+                ctx.spacerSplitTw += spentTw;
```

One `if`, three integers, no new construct, no new attribute. It is the same shape as the landed
guard and is strictly between the two existing arms.

**Alternative, if the guard is not to be touched at all:** the emission at `:6067-6072` could write
`w:before="spacerTw - 20"` and `w:line="20"` unconditionally, accepting the two overflows. That is the
10:05 build: 6 clean, 2 cost. The partial spend exists to buy the 6 without paying the 2.

## 6. Measurements before and after

Engine built three times from this clone: HEAD (no change), `-Dp2w.spacerSplitAlways=true`
(unconditional split, the 10:05 shape), `-Dp2w.spacerPartial=true` (this proposal). The two switches
are temporary system properties added for the experiment; the default behaviour of the tree is
unchanged.

**6.1 The construct changes (structural, from the emitted `.docx`)**

| document | HEAD `(before, line)` pt | split-all | partial |
|:--|:--|:--|:--|
| `68_journal_wide_table_spanning` | (0.00, **144.00**) | spent, hairline 0.05 | spent, hairline 0.05 |
| `mobile-bill` | (0.00, **12.40**) | (12.35, 0.05) | **(1.00, 11.40)** |
| `insurance-policy-schedule` | (0.00, **14.40**) | (14.35, 0.05) | **(2.50, 11.90)** |
| `two-tables-stacked-with-no-gap` | (0.00, **12.35**) | (12.30, 0.05) | **(9.25, 3.10)** |

The dose tracks the page's slack, as designed: the two exactly-full pages are spent 1.0 pt and 2.5 pt,
the two with room are spent in full or nearly.

**6.2 LibreOffice, before vs after — identical, on all seven**

Rendered with `soffice --headless`, scored with `verify_google.py` against the source PDF (it is a
two-PDF comparator; the renderer is whatever produced the second PDF):

| document | pages src/before/after | HEAD | after split |
|:--|:--|:--|:--|
| `two-tables-stacked-with-no-gap` | 1 / 1 / 1 | 47/47 PASS | 47/47 PASS |
| `mobile-bill` | 1 / 1 / 1 | 47/47 PASS | 47/47 PASS |
| `insurance-policy-schedule` | 1 / 1 / 1 | 47/47 PASS | 47/47 PASS |
| `table-with-no-header-row` | 1 / 1 / 1 | 47/47 PASS | 47/47 PASS |
| `72_bank_statement_no_rules_right_amounts` | 1 / 1 / 1 | 42/42 PASS | 42/42 PASS |
| `bus-timetable-station-left-times-right` | 1 / 1 / 1 | 42/42 PASS | 42/42 PASS |
| `68_journal_wide_table_spanning` | 1 / 1 / 1 | 40/42 (`18`, `59`) | 40/42 (`18`, `59`) |

And for the partial build, on the four documents converted: `mobile-bill` 47/47, `insurance` 47/47,
`two-tables-stacked` 47/47, `68_journal` 40/42 — **byte-for-byte the same verdicts and the same page
counts as HEAD.**

**This is the result that matters for landing it.** The dither patch was refused because it moved 14
of 16 documents the wrong way in the proxy. This change moves **none** of them: the gap is not added,
it is moved from `w:line` to `w:before`, and LibreOffice sums the two. `regress.py --check` has
nothing to refuse, and the waiver at `regress.py:docx_regressions()` (a LibreOffice regression is
allowed when Google improved) is not even needed.

**6.3 Google — NOT measured by this run**

No round trip was made. `GOOGLEDRIVE_CREATE_FILE` will not accept a sandbox path as its file:

    IO error ... files/download returned HTTP 403: The file key does not belong to this project or
    session. The file with s3key '/scratch/output/probe/probeA-two-tables-stacked-with-no-gap.docx'
    belongs to another project or session; use a file uploaded by this project.

The connector now requires a platform file key, and the earlier slots' route (upload from
`/scratch/output` into folder `11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`) is not open to this sandbox. So the
direction and magnitude of the fix in Google are **recorded from earlier round trips and named in
§4(a)**, not re-measured here. Everything in §6.1 and §6.2 is measured; the Google half is inferred
from those records plus the engine's own statement of Google's `w:line` law.

## 7. What would prove this wrong

1. A document where spending the gap in `w:before` makes Google **worse** — none is known, and the
   guard's own history (mobile-bill, insurance) is about overflow, not displacement, so the partial
   spend is aimed at exactly that.
2. A document whose LibreOffice page moves under the split. None of the seven did; the arithmetic says
   none can, because `before + line` is preserved to the twip.
3. The 7-of-13 reach being wrong: `36_embedded_subset_font` is the one to check first, because it
   carries a table and no spacer, which means its displacement is either the first-row `w:before`
   family or a block offset, and no one has classified it.

## 8. Reproduction

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
bash tools/p2w-bench/build-engine.sh                       # 38 s, fetches JDK + PDFBox
bash tools/p2w-bench/corpus-fetch.sh                       # 213/213
cd tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -Dp2w.spacerPartial=true -cp "$CP" ConvertOne /scratch/work/p2w/corpus/mobile-bill.pdf /tmp/o
# unzip word/document.xml and read the spacer's w:before / w:line
soffice --headless --convert-to pdf --outdir /tmp/lo /tmp/o/mobile-bill.docx
python3 ../p2w-bench/verify_google.py /scratch/work/p2w/corpus/mobile-bill.pdf /tmp/lo/mobile-bill.pdf
```

Nothing was committed, nothing pushed, nothing deleted. The only file written outside `/scratch/work`
is this finding.
