# 18_displacement's residual is TWO shapes, and only one of them is a page-wide constant

**27 Nov 2026, 17:25 IST, relay run. Engine `d28ca7516c3f9165`.** Measured after the origin correction
(`18dA-06-ORIGIN-NOT-BBOX-ONE-DOCUMENT-AND-FOUR-REAL-1730-relay.md`), so the ascent term is already out
of these numbers: every value below is a baseline-to-baseline shift.

A throwaway script opens the source PDF and the live Google export, matches spans by `(page, text)` and
subtracts `span["origin"][1]`. It imports nothing from `verify_google.py`.

| Document | runs matched | median dy | p90 abs dy | runs within 1 pt of the median | shape |
|:--|--:|--:|--:|--:|:--|
| `07_stamp_over_table` | 73 | **-3.94** | 3.94 | 68 % | constant page shift |
| `06_rect_paid_stamp_red_transparent` | 85 | **-1.88** | 1.88 | 76 % | constant page shift |
| `364_event_ticket` | 19 | **-3.68** | 3.94 | 63 % | near-constant |
| `72_bank_statement_no_rules_right_amounts` | 76 | -3.12 | 4.62 | 46 % | mixed |
| `16_right_aligned_amounts_txtpos` | 63 | -2.63 | 4.09 | 41 % | mixed |
| `393_spectrum_peak_table` | 24 | -1.25 | 3.25 | 62 % | mixed |
| `71_invoice_space_aligned_no_rules` | 67 | +1.12 | 5.84 | 63 % | mixed |
| `09_stamp_font_not_embedded` | 21 | +1.18 | 2.42 | 67 % | mixed |
| `312_affidavit_stamp_paper` | 25 | +1.65 | 2.20 | 92 % | near-constant, small |
| `mobile-bill` | 91 | +0.18 | 1.96 | 53 % | passes |
| `31_times_body_arial_headings` | 29 | +0.97 | 1.96 | 86 % | passes |
| `320_balance_sheet_statutory` | 68 | +6.25 | **14.68** | **16 %** | VARIABLE, large |

## What the shapes mean for the next attempt

* **`07` and `06` are a page-wide constant.** 68 % and 76 % of every run on the page sit within 1 pt of
  one offset, and the p90 equals the median - the whole body is 3.94 pt and 1.88 pt from where the source
  put it, uniformly. One number moves the whole document; there is nothing per-block to chase. **This is
  the shape the page-top lever acts on**, and it is the one worth re-measuring a page-top change against.
* **`320_balance_sheet_statutory` is the opposite.** 16 % within 1 pt, p90 14.68 pt against a median of
  6.25 - the runs disagree with each other by up to 15 pt on ONE page. No single page offset explains it;
  a uniform shift applied to that document would move the median and leave the p90 untouched. Do not
  spend the page-top lever on it.
* **The rest are mixed** (41-67 % within 1 pt): a real page offset with per-block variation on top. A
  constant-shift fix moves their median and not their verdict.

So "the sole-18 documents" is not one class of defect. Two of the twelve measured are a single constant
number per document; one is per-block placement that a page offset cannot reach. The next run should
separate them with this table before choosing a lever, because the page-top change is worth the constant
half and nothing on `320`.

Not measured: how many of the 25 sole-18 documents have the constant shape. Twelve documents were
rendered this run; the other thirteen were not, and this table must not be read as a population.
