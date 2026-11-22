# patches/ - fixes that are measured but not shipped

A patch lands here when its mechanism is PROVED and its numbers are MEASURED, but it
cannot be kept yet: the class does not pass, or the corpus-wide ratchet it needs has
not run. Keeping it as a file is the whole point - a hypothesis that names a patch the
repository does not carry makes every later run re-derive it from scratch.

This directory was missing on 17 Nov. `HYPOTHESES.md` referenced
`patches/run-size-from-sizePt-not-Tf.patch` and `patches/ruled-band-by-overlap-not-centre.patch`
and neither existed, so the 17 Nov 10:50 run re-derived the font-size bug from a cold
start and recorded two `reverted` attempts against work that was already done. Restored:

    run-size-from-sizePt-not-Tf.patch   the confirmed one. See HYPOTHESES.md.
    ruled-band-by-overlap-not-centre.patch   reverted in place; NOT restored, its
                                        mechanism is fully described in HYPOTHESES.md
                                        and it moves nothing, so rebuilding it would
                                        only invite someone to apply it again.

Apply with `git apply patches/<name>.patch` from the repository root, then rebuild with
`bash tools/p2w-bench/build-engine.sh`.

## REFUTED 22 Nov 14:58 - `18-spacer-before-rowpitch-rowrule.patch`

Read this before you apply it. Measured on engine `462353f9`, fresh builds, both renderers:

    full patch, Google   two-tables-stacked-with-no-gap  46/47  (baseline 46/47, same check)
    spacer only, Google  two-tables-stacked-with-no-gap  46/47  (no change)
    spacer only, Google  mobile-bill                     43/47  page_count 1 -> 2  REGRESSION
    full patch, LibreOffice  4 of 6 documents +29 .. +36 share@5

The 13:56 handoff's "41/42 -> 42/42 PASS, n_out 55 -> 0" does not reproduce. The row/cell hunks
(3-7) are the LibreOffice regression; hunk 3 alone takes mobile-bill 1.55 -> 12.66.
Evidence and the mechanism that IS proved (`w:before` = exactly V/20 pt in Google, `w:line` = 0.2156x):
`FINDINGS/18_displacement-PATCH-REFUTED-AND-WBEFORE-LAW-1005-fixer.md`.
The lead is NOT `flowTw`: line 5875 already charges the declared value and `w:before` now renders
exactly that, so model and render agree after the patch. mobile-bill's extra page is a REAL surplus -
it only fitted before because Google under-charged that gap by ~4.9 pt. Keep the spacer half (it is a
correctness fix and LibreOffice-neutral) and go find what else on that page is over-tall.

## CORRECTION 22 Nov 17:05 - that refutation is about a DIFFERENT patch

The REFUTED block above measures `18-spacer-before-rowpitch-rowrule.patch` (this directory, seven
hunks). It does not measure
`tools/p2w-bench/patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`, which carries only
two mechanisms - the spacer moved to `w:before`, and error-diffusion of the row pitch onto Google's
0.75 pt grid. The three hunks the 15:34 bisection blames for the LibreOffice regression (row pitch from
the table average, row rule outside `trHeight`, cell pitch rescale) are not in the dither patch.

Measured 22 Nov 17:05 on the dither patch, live Google round trip:

    two-tables-stacked-with-no-gap   46/47 (fails 18_displacement)  ->  47/47 PASS, CLEAN
    LibreOffice proxy, same document  0.77  ->  29.51

So the dither patch is **not refuted - it is proved correct in the renderer the user opens, and it is
unshippable because the LibreOffice ratchet refuses it.** 14 of the 16 documents that fail
`18_displacement` alone regress in the proxy; a variant build that leaves the rule pitch on the row's
own height produces byte-identical proxy scores, so the row height is the term and no LO-neutral form
of the fix exists (Google adds a 0.75 pt quantum LibreOffice does not).

Evidence: `tools/p2w-bench/FINDINGS/18_displacement-DITHER-IS-GOOGLE-CLEAN-AND-LO-CATASTROPHIC-170500-fixer.md`.
Do not screen it again. The open question is the instrument, not the construct.
