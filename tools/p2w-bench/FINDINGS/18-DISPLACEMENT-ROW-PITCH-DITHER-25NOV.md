# 18_displacement - the row-pitch dither, measured and NOT committed

25 Nov 2026, fixer slot 11:24. Engine `85b8735f` + working-tree patch (uncommitted).
Outcome: **lead**. The patch changes output; it was not committed because the instrument that
would judge it (soffice prerender) hung, and because the repo already records the same idea
failing once.

## What was proposed

A sub-agent (Explore) read `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md`, the 18_displacement findings and
`DocxWriter.java`, and proposed a two-part patch:

1. **Spacer** - always write the vertical gap as `w:before` on a hairline `w:line`, never as the
   refused branch that carried the whole gap in `w:line ... exact`; drop the budget guard
   (`spendable`). Justification: `w:before` is 1:1 in Google at every value tested (9 probes,
   14.4 to 576 pt, slope 1.000, residual 0.00 pt) while `w:line exact` on an `sz=2` empty
   paragraph is the lever that under-delivers.
2. **Row pitch** - error-diffuse the declared `w:trHeight`: carry each row's rounding error into
   the next declaration so a long table's foot cannot drift, and subtract a `ROW_RULE_CHARGE_PT`
   of 0.875 pt because the renderer charges the row's own `w:sz="7"` border on top of the
   declared height.

Part 1 was **not applied** at all in this run. Part 2 was applied alone (guard:
`exactRows && rowCapTw < 0 && !t.recut && ctx.squeeze == 1f && ruleTwHere > 0`).

## The measurement - A/B on the engine's own output

Same three documents, converted with `ConvertAll` from two builds that differ only by this patch,
`word/document.xml` row heights read straight out of the .docx:

| document | declared `w:trHeight`, unpatched (tw) | declared, patched (tw) | pt |
|---|---|---|---|
| `mobile-bill` | 360, 360, 380, 360, 380, ... | 343, 343, 363, 343, 363, ... | 18.0/19.0 -> 17.15/18.15 |
| `salary-slip-corporate` | 380, 360, 380, 360, 360, 380, 320, 252 | 363, 343, 363, 343, 343, 363, 320, 252 | -0.85 pt per ruled row |
| `very-long-single-column-table` | 360, 380, 360, 380, ... | 343, 363, 343, 363, ... | 18.0/19.0 -> 17.15/18.15 |

So the patch is **not inert**: it fires on every ruled row of these three documents and subtracts
exactly 0.85 pt (343 tw = 17.15 pt where the pre-patch engine declared 18.0 pt). The alternation
itself is preserved - the dither is spreading rounding, as designed - but the whole ladder is
shifted down by the asserted rule charge.

## Why that shift is the risk, and why it was not committed

The 0.85 pt is correct **only if the renderer adds the row's rule on top of the declared height**,
and the repo's own history says the opposite is possible on at least one renderer:

- `DocxWriter.java:6455` (the comment directly above the patched line) records a previous attempt
  that shortened every row: *"on electricity-bill's 18.4 pt rows (0.5 pt rules) that turned an
  18.0/19.0 alternation into 17.5/18.5 - 18_displacement gained more documents than it fixed."*
  That attempt subtracted 0.5 pt; this one subtracts 0.85 pt on the same documents.
- The 0.875 pt figure comes from one live Google round trip (22 Nov). LibreOffice is the fast
  local proxy the gate uses, and nothing in the repository measures its rule charge.

A change that subtracts a constant from every ruled row either removes a systematic foot-drift or
adds one; the sign depends on a renderer charge that is known for Google and unknown for the
proxy. That is a measurement question, and the measurement did not run.

## What blocked the measurement

`screen.py --class "content-present-partly-displaced"` (23 documents) converts fine and then
**hangs in the soffice prerender**: 12 docx prerendered in the first call, then "prerender 1 docx
in soffice batches of 12" repeated across two further 280 s calls with no completion. See
`BLOCKERS.md`, 25 Nov entry. Without a render there is no share@5 before/after, so no attempt can
be kept and no regression can be ruled out - `regress.py --check` cannot be satisfied for a
rendered table change either.

## What the next run should do first

1. Fix or bypass the prerender hang (it blocks every screen, so it blocks every attempt).
2. Then judge this patch by share@5 on `mobile-bill`, `electricity-bill`, `salary-slip-corporate`
   and `very-long-single-column-table` - the four documents whose rows are ruled and whose pitch
   the dither moves - before spending a corpus pass.
3. Keep part 1 (the spacer) separate from part 2 (the row pitch). They were proposed together and
   they are independent: part 1 removes a budget guard, part 2 shifts a ladder. One build must not
   carry both, or neither can be attributed.

## Also recorded, and worth a run of its own

The repo holds **three mutually inconsistent laws** for the same construct - `w:line ... exact` on
an `sz=2` empty paragraph:

| source | law |
|---|---|
| 22 Nov, `18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md` | 2.5873 x max(L/240, 0.06) pt, about 21.5 % of the ask |
| 24 Nov, `DOCS-ROOT-CAUSES-24NOV.md:616` | a flat 5-10 pt regardless of the ask |
| 23 Nov, `FINDINGS/refused-spacer-before-lever-1458-relay.md` (13 probes) | 91.0 % at 14.4 pt, 95.3 % at 144 pt |

They cannot all be true. Until one is reproduced, any patch that leans on this construct is
betting on an unknown - which is why part 1 was left unapplied.
