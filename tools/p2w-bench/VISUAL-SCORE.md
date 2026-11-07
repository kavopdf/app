# Visual score

Share of documents whose every page answers all eight questions. The questions and
their criteria are in the P2W brief; the tool that answers them is
`tools/p2w-bench/visual.py`.

## How a document passes

    A question is N/A - and passes - when the PDF has nothing of that kind on the page.
    A page passes when every applicable question passes.
    A document passes when every page passes.

## The ratchet

    score fell    -> the change is reverted
    score same    -> fine
    score rose    -> accept, and record the new baseline

## History

| Date | Passing | Measured | What changed |
|------|---------|----------|--------------|
| 7 Nov | 0 / 3 | 3 | first real run of visual.py |

The three documents measured were 301_lab_report_panel, 302_radiology_report and
303_discharge_summary. All three failed, all three on reading order.

## What the first run answered, question by question

| Question | Verdict |
|----------|---------|
| reading order | **no** on all three |
| overlap | no on one, yes on two |
| inside page | yes on all three |
| images | yes on one, n/a on two |
| tables | yes on all three |
| charts | yes on two, n/a on one |
| QR / barcode | **not measurable** - no decoder in the sandbox, looked at by eye |
| emphasis | yes on all three |

## The reading-order defect

On 301 the PDF reads label, value, label, value:

    patient -> ananya rao -> age / sex -> 34 / female -> referred by -> dr. meera

and the docx reads every label first, then every value:

    patient -> age / sex -> referred by -> collected -> 34 / female -> dr. meera

Every word is present and in the right place. Only the sequence is wrong, which is
exactly the class of defect no count-based gate can see.

## Why this is separate from the regression gate

`gate.py` counts words, blocks, pages and lines. A document can pass all of those and
still look wrong: text in the wrong reading order, a chart drawn as grey rectangles, a
QR code rendered too small to scan, an image region that is an empty white box.
