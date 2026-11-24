# KEPT: a chunk's conversion share was defeated by one slow document, so measurement got nothing

**24 Nov 2026, fixer slot 14:17.** `benchmarks/p2w.py`, `docx()`.

## The defect, measured

The 11:15 run added `CONVERT_SHARE=0.55` so conversion and measurement would both progress in
every chunk. It does not hold. The stop test was `if time.time() > end - 6`, checked BETWEEN
documents, and one document may run for up to 90 s. Measured on this run's chunk at 09:16:

    09:16:54  docx 87/213 -- converting 126     conv_end was 09:19:02
    09:20:43  prerender 12 docx in soffice batches of 12
    09:20:46  chunk 1: measured 85 of 213       <- ONE document measured

Conversion ran 100 s past its share and the measurement phase got a deadline that had gone.

## The change

The headroom is now twice the median cost of the documents this chunk has already converted
(a variance allowance, not a tuned constant), floored at the original 6 s. The first document of
a chunk always starts. No engine code, no check, no measurement touched.

## Before and after, same pod, same budget, same corpus

| chunk | documents measured | documents converted |
|:--|--:|--:|
| before (budget 250) | 85 → **86** (+1) | 87 → 101 (+14) |
| after (budget 250) | 115 → **145** (+30) | 101 → 121 (+20) |

+1 to +30 documents measured per 250-second chunk on identical hardware. The pass then closed
213/213 converted and 212/212 measured in this slot.
