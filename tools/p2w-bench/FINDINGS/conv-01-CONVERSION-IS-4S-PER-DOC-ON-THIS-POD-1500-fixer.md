# Conversion cost on this pod is ~4 s/document, not 11 s - the 11 s figure was measured on a contended pod

**24 Nov 2026, fixer slot 14:17.** Answers pending item 3 / agent `conv-01`.

The 0650 finding measured 11 s/document and concluded a full `--force` pass costs ~105 minutes.
That number is pod-specific, not a property of the converter. Measured here, on a pod with
`cpu.cfs_quota_us=105000` (1.05 cores) like the other:

    chunk 1: 35 documents converted + 26 measured inside a 250 s window
    chunk 2: 213/213 converted, 212/212 measured, whole pass across 12 chunks of <=285 s

The rate depends on which documents are reached first: sorted order starts with small synthetic
documents and ends with the nine-page bank forms, and the per-document cost rises as the pass
proceeds. A single `--force` pass closed in this slot once the scheduling defect below was fixed.

    python3 tools/p2w-bench/build-engine.sh on an unchanged tree: 0.9 s
        (prints "engine unchanged - skipping compile"), so engine()'s unconditional
        rebuild costs the pass nothing per chunk.

Two consequences for future runs: a full pass DOES fit a 90-minute slot, and the per-chunk build
guard proposed by the conversion-cost analysis is unnecessary because the build script already
skips an unchanged tree.
