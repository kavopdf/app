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
