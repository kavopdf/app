# The box mechanism is worth ~8 documents, not 166

**Agent A, fixer slot 25 Nov 06:07. Engine b97d8172ce642eb0. Corpus 213/213 fetched and converted.**

## The census

Reader: unzip `word/document.xml`, count characters inside every `<w:txbxContent>`.

```
documents 213   box carriers 61   total box chars 28432   total body chars 433453
```

152 of 213 documents carry **zero** boxed characters. 61 carry any. The distribution is heavily skewed:
5 documents carry 21,743 chars = 76 % of all boxed text (`041122-Account_Opening_Form` 6,789,
`Account_Opening_Form_Fillable_filled` 6,789, `policy-2col-spanning-section-heading` 3,041,
`academic-paper-ieee-2col-abstract` 2,942, `magazine-2col-pullquote-spanning` 2,182).
**44 of the 61 carriers hold under 200 characters** — stamps, tick marks, a footer line
(`305_vaccination_certificate`: 122 chars over 48 boxes). Every `*_stamp*` document is 4-47 chars and is
**invariant under every knob tested**.

## The 2x2 dose over all 61 carriers

| knob | box chars | carriers | docs zeroed |
|---|---:|---:|---:|
| HEAD | **28,432** | 61 | — |
| `-Dp2w.gapcap=20000` (cap off) | 23,905 | 41 | 20 |
| `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0` (latch off) | 8,572 | 61 | **0** |
| both | **2,671** | 41 | 20 |

So the **latch is 19,860 chars (70 %)** and the **cap 4,527 (16 %)**. The published note
(`04_chars_missing-THE-LATCH-NOT-THE-CAP-IS-THE-MULTIPLIER-0225-fixer.md`) says 24,920 / 1,469 — both
terms are wrong: the latch is understated, the cap's own contribution is **3x** what was recorded.
Two corrections the note does not carry: **the two terms are not additive** (both = 2,671, not
8,572 - 4,527) and **the latch alone zeroes no document at all** — only the pair does.

## What flips to CLEAN

Filter: carriers whose entire failing set lies inside the box-attributable set
{04, 45, 13, 44, 17, 25}. Eight candidates, **one Google-proven**:

| rank | document | box chars HEAD -> both | stored Google | failing |
|---:|---|---:|---|---|
| 1 | `66_two_col_footnotes_bottom` | 448 -> 0 | 37/42 | 04,13,17,44,45 |
| 2 | `20_numbered_list_separate_column_txtpos` | 232 -> 0 | 38/42 | 04,17,44,45 |
| 3 | `54_two_column_body_full_width_header_footer` | 92 -> 0 | 37/42 | 04,13,25,44,45 |
| 4 | `62_two_col_newsletter_pull_quote` | 77 -> 0 | 38/42 | 04,25,44,45 |
| 5 | `46_chart_coloured_labels_body_text` | 71 -> 0 | 39/42 | 04,44,45 |
| 6 | `55_sidebar_box_beside_body` | 65 -> 0 | 39/42 | 04,44,45 |
| 7 | `67_two_col_with_sidebar` | 65 -> 0 | 39/42 | 04,44,45 |
| 8 | `27_two_column_left_short_txtpos` | 57 -> 0 | **42/42 PASS** | none |

Rank 8 is **Google-measured**: `GAP-CAP-VS-ZERO-GAP-ANCHOR-BOX-TEXT-DOSE-25NOV.md` records 40/42 stored
-> 42/42 on a real render with `-Dp2w.gapcap=20000 -Dp2w.zganchor=false`. Ranks 1-7 are **inference**
from the Google pass/fail store plus a local box count; nobody has re-rendered them.
`411_nested_xobject_transforms` (28 chars, 40/42) does **not** flip — both flags leave it at 28.

## The correction this run has to carry forward

The FIXER-BRIEF states this construct is "~166 document-failures" and "the largest engine defect anyone
has found". **The measurement does not support that.** 61 carriers, 44 of them under 200 characters,
and the honest ceiling of the mechanism is **~8 documents**. The other 52 carriers each have at least one
failure outside the box set and cannot go clean on this alone: `magazine-2col-pullquote-spanning` goes
2,182 -> 0 and stays at 33/42 on 10/13/17; `policy-2col-spanning-section-heading` goes 3,041 -> 251 and
stays at 34/42.

## Not established

- A valid `regress.py --check` verdict with the instrument patch applied: it printed **nothing** and exited 0
  on a fingerprint-changed engine. A silent gate is worse than a red one. Recorded as an obstacle.
- Google re-render of ranks 1-7.
- Whether `pagepos/anchorkeep` or `gapcap/zganchor` is the intended flag pair; they overlap on `27` and
  nowhere else measured.
