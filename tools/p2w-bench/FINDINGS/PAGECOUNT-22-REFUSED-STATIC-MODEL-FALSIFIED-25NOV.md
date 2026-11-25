# The 22 page-count refusals: this attempt re-derived work that was already done, and the handover channel is why

> **Read `FINDINGS/00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md` first. It already root-caused
> this class** — Google bills the flow for page-positioned floating shapes at 0.10-0.96 pt each (median 0.57),
> the prize is 5 clean documents and not 23, and `350_question_paper` is a genuine one-line overflow.
> **Nothing in this file contradicts it.** What this file adds is one falsified hypothesis and one process
> defect, and the process defect is the more expensive of the two.

**Fixer slot 25 Nov 06:07. My own attempt. Hypothesis formed, instrument built, hypothesis NOT confirmed.**

## The population

`benchmarks/gverify/*.json`, status `page_count_refused`: **22 documents**. All 22 are one-page sources that
our `.docx` renders one page longer — 20 at `pages=2`, and the two nine-page bank forms
(`041122-Account_Opening_Form`, `Account_Opening_Form_Fillable_filled`) at `pages=14`.

`classpick.py --leverage` puts `00_page_count` at **22.0 clean documents** — the second-highest single check
after `18_displacement` (39.7). These 22 are not "failing"; they are **unscorable**, which is worse: the whole
Google layer is blind to them.

## What I measured

Converted with `ConvertOne` at HEAD (`b97d8172ce642eb0`) and rendered with LibreOffice:

| document | ConvertOne | LibreOffice pages | Google |
|---|---|---|---|
| `60_page_border` | pages=1, 15 paragraphs | **1** | refused, pages=2 |
| `350_question_paper` | pages=1, 70 paragraphs | **1** | refused, pages=2 |

**So the extra page is Google-only.** LibreOffice renders both at one page. This is the exact class of defect
the charter warns about — a renderer that hides what the user's phone shows — and it means the page-count
question **cannot be measured with the proxy at all**.

## The hypothesis, and why it failed

Hypothesis: Google enforces a minimum line height on degenerate `w:line ... w:lineRule="exact"` values. The
engine tunes a page to fit with sub-point line heights (`minline` 0.05 pt on `60_page_border`, 0.55 pt on
`350_question_paper`, 0.05 pt on `320_balance_sheet_statutory`), so if Google clamps each to ~1 pt a page
tuned at 804 pt overflows to 863 pt and breaks.

Test: a cumulative-flow model over `word/document.xml` — sum `w:before + max(w:line, floor)` per paragraph,
skipping anchored paragraphs — computed at floor 0.0 and floor 1.0 for 8 documents (5 refused, 3 scored-ok).

**The model does not discriminate.** `300_prescription_rx` is scored **ok** on Google and renders one page,
yet sums to **1058.8 pt** — 216.8 pt over a 842 pt page — even at floor 0.0. The refused set and the ok set
overlap completely in the model's output.

| document | verdict | flow @0.0 | flow @1.0 |
|---|---|---:|---:|
| `350_question_paper` | REFUSED | 827.2 | 858.2 |
| `60_page_border` | REFUSED | 801.9 | 807.4 |
| `314_tender_rfp_boq` | REFUSED | 1009.0 | 1049.0 |
| `320_balance_sheet_statutory` | REFUSED | 1101.7 | 1152.5 |
| `341_shipping_manifest` | REFUSED | 2850.4 | 3016.8 |
| `17_three_column_widths_txtpos` | ok | 436.1 | 443.3 |
| `19_hanging_indent_txtpos` | ok | 640.0 | 647.8 |
| `300_prescription_rx` | **ok** | **1058.8** | **1084.1** |

The reason is structural, not a bug in the script: tables consume flow height and I skipped them, and a
one-page document legitimately runs past 842 pt when its content is positioned rather than flowed. **A sum
over the docx cannot answer "how many pages will Google draw".**

## What this leaves

- **Confirmed:** the extra page is a Google-only behaviour; LibreOffice says one page on both witnesses.
- **Falsified:** the degenerate-line-height hypothesis is *not* supported by any measurement I could take
  here. Do not spend a run on it without a Google render.
- **The real instrument** for this question is the Google render itself. The blocker is that
  `GOOGLEDRIVE_CREATE_FILE` rejects a sandbox path (`s3key ... belongs to another project or session`, 403)
  unless a platform `upload` step mints the s3key first. **Whoever next works `00_page_count` should mint the
  s3key with `upload(path=...)` before claiming the Google half is unmeasurable.**
- Nothing was changed in the engine. No document moved. Outcome recorded as `lead`.
