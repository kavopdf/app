# 18_displacement: the page-top lever cannot reach the class, and `pageFirst` was dead code

**26 Nov 2026, fixer slot 11:20 IST, relay.** Measurement only. `app/` reverted, nothing committed
but this file and the patch beside it.

## 1. All 23 documents that fail ONLY `18_displacement` are SINGLE-PAGE

Measured with PyMuPDF over `/scratch/work/p2w/corpus/<name>.pdf` for every document whose stored
`benchmarks/gverify/<name>.json` has `failed == ["18_displacement"]`:

    23 of 23 have page_count = 1

Why it matters: the two levers the last two runs worked - `TOPGAP_ROW` (a 1x1 `w:trHeight` row
carrying a page's top gap, `PATCH-topgap-row-MEASURED-0654.patch`) and Google's drop of `w:before`
on the first paragraph after a page break - act **only on pages after the first**. `TOPGAP_ROW`'s own
guard is `ctx.pageNo > 1 || ctx.brokePage > 0`. On a one-page document that guard is never true, so
the patch is byte-inert: verified, `document.xml` of a flag-on and a flag-off build of
`electricity-bill` are identical. The class's remaining solo failures are **within-page** vertical
drift, not a page-top offset.

## 2. `spacing()`'s `pageFirst` argument was false in every build

`DocxWriter.java` `spacing(..., boolean pageFirst)` compensates the first line of a page in the
`lineRule="auto"` construct (`:165`, `b += (1-LINE_BASE) * (boxTw - lineTw)`). Both flow call sites
passed `ctx.newPage` **after** clearing it, so the argument was always false and that compensation
never ran. This confirms the 25 Nov proposal's claim 2 independently, in the tree as it stands.

Patch: capture `boolean pageFirst = ctx.newPage;` immediately before each clear and pass it.
Saved as `patches/PATCH-pagefirst-autoflow-1200-relay.patch`. **Inert at the default
`-Dp2w.lineRule=exact`**: `spacing()` returns in the `if (!auto)` branch before `pageFirst` is read,
so the default corpus output is unchanged by construction.

## 3. With the fix, `-Dp2w.lineRule=autoflow` removes the constant offset but not the failure

One document, one Google export, engine built from this tree with both patches, flag
`-Dp2w.lineRule=autoflow`. Source `electricity-bill.pdf`, exported PDF scored with `verify_google.py`
(and `--docx` so the denominator is the full 47).

| | before (stored gverify, engine a4d8fca4) | after (this run, Google export) |
|:--|--:|--:|
| checks | 46/47 | 46/47 |
| failing | `18_displacement` | `18_displacement` |
| page 0 median dy | **-7.2 pt** | **+0.08 pt** |
| worst dy | **10.4 pt** | **6.56 pt** |
| runs out of tolerance | - | 26 of 125 |
| dy span | - | 9.94 pt |

So the systematic upward shift the `exact` construct produces (Google charges
`2.7466 x max(L/240, 0.06)` for an exact box, `FINDINGS/w-line-exact-GOOGLE-CHARGE-075617-f0cc.md`)
is **gone** - the median moves 7.3 pt, from -7.2 to +0.08 - but the check still fails on the tail:
26 of 125 runs, max +6.56 pt against a 2.24 pt tolerance.

**Falsifier for the next run:** if `autoflow` does not move the median on a second document by the
same order, this reading is wrong and the -7.2 was not the exact-line charge.

**What would make it a kept change:** the tail is per-run, not per-page, so it is not the line box.
The next attempt should read the 26 failing runs by size and font (`dy.py` prints them) and check
whether they are one construct - a table row, a `w:before` clamp, or the anchored-box text
`lineParagraph` puts on its own y.

## 4. THE FALSIFIER FIRED: `autoflow` is not a general lever

Second document, same build, same flag, one Google export - `72_bank_statement_no_rules_right_amounts`:

| | before (stored gverify) | after (autoflow, Google export) |
|:--|--:|--:|
| checks | 41/42 | 41/42 |
| failing | `18_displacement` | `18_displacement` |
| page 0 median dy | **+1.1 pt** | **+3.51 pt** |
| worst dy | **4.8 pt** | **8.44 pt** |
| runs out of tolerance | - | **52 of 80** |

The median moved the WRONG way by 2.4 pt and the worst by 3.6 pt. So the 7.3 pt median improvement on
`electricity-bill` was not the exact-line charge being corrected in general - it is per document, and
on this one `autoflow` introduces a positive bias where `exact` had almost none.

**Verdict: `-Dp2w.lineRule=autoflow` is NOT a keeper.** Two documents, opposite signs, neither clean.
The class's displacement is not one line construct; a global construct change trades one document's
error for another's, which is why the whole-corpus regression exists.

**What survives and is worth the next run:** the `pageFirst` dead-code fix (inert at the default
`exact`, a real bug regardless), and the arithmetic that all 23 solo-`18_displacement` documents are
one page, so no page-top or per-page lever can clear any of them.
