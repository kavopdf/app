# The two knobs, separated by measurement - and only one of them can ship

**Run:** 25 Nov 2026, fixer slot 05:09 IST. Engine `b7699196` (HEAD), corpus 213.
**Supersedes the "next run" instruction** in `GAP-CAP-VS-ZERO-GAP-ANCHOR-BOX-TEXT-DOSE-25NOV.md`,
which proposed taking *the pair* to Google on two documents. The pair was measured first, and it fails.

## What was measured

The previous run found that two knobs together remove 86 % of the characters the engine writes into
anchored DrawingML text boxes (`<w:txbxContent>`). Both knobs are instruments, not defaults:
`-Dp2w.zganchor=false` exists on HEAD (`DocxWriter.java:303`), and `-Dp2w.gapcap=<twips>` is added by
`patches/gapcap-instrument.patch`. Every number below is a real conversion of the real corpus PDF, then
`benchmarks/p2w.py:measure_doc` - the project's own position statistic (share@5px, max_pt), not one
invented for this run.

### Box characters, by build

| build | `27_two_column_left_short_txtpos` | `65_two_col_full_width_figure_caption` | `policy-2col-spanning-section-heading` | corpus total | documents changed |
|---|---:|---:|---:|---:|---:|
| HEAD (cap 2400tw, anchor on) | 57 | 627 | 3046 | 28,553 | - |
| anchor off | 57 | 627 | **49** | 7,726 | 10 |
| cap 20000tw | **0** | 624 | 3046 | 24,026 | 23 |
| both (the pair) | 0 | **0** | **0** | 1,684 | 33 |

Box counts for the three probe documents were re-derived independently in this run with
`boxscan.py` over freshly built `.docx` files and reproduce the previous run's census exactly
(57 / 627 / 49 / 624 / 0), so the dose table is not a transcription error.

### Position, by build - the part that decides the ship

| document | HEAD share@5px / max_pt | anchor off | cap 20000tw | both |
|---|---|---|---|---|
| `27_two_column_left_short_txtpos` | 1.62 / 7.7 | not measured (57 box chars unchanged) | **1.62 / 7.7** | 1.62 / 7.7 |
| `65_two_col_full_width_figure_caption` | 1.75 / 8.6 | **1.75 / 8.6** | **1.75 / 8.6** | **7.75 / 31.7** |
| `policy-2col-spanning-section-heading` | 2.36 / 14.4 | **48.34 / 57.1** | not measured | not measured |

`problem` signature flips on two of these:
`65` HEAD/`cap`/`anchor-off` = `content-present-partly-displaced`; pair = `content-missing-partly-replaced`.
`policy-2col` HEAD = `content-present-wholly-displaced`; anchor off = `content-partly-lost-and-displaced`.

## What this means

**1. The pair must not ship.** The previous run's own proposal was to check the bill on a document that
passes `18_displacement` and carries box text. `65_two_col_full_width_figure_caption` is exactly that
document: it passes today, and under the pair it goes from 1.75 % to 7.75 % displaced with a 31.7 pt
worst-case move and a worse `problem` signature. The bill arrives on the first document anyone looked at.

**2. The anchor is load-bearing and must stay on.** Turning it off removes 72.9 % of the box text and is
catastrophic where it acts: `policy-2col-spanning-section-heading` goes from 2.36 % to 48.34 % displaced,
worst case 14.4 pt -> 57.1 pt, and starts losing content. Those 3,046 characters were not trapped in a
box - they were the two-column body correctly placed by the anchored flow. Reading a falling box-character
count as a gain is what made the pair look attractive; on this document the same drop is the defect.

**3. The cap alone is the only knob with evidence behind it, and it is benign on both witnesses.**
It zeroes `27`'s 57 box characters - the document the previous run proved goes 40/42 -> **42/42 in Google**
under the pair, where the anchor contributed nothing (57 -> 57) - and on `65` it leaves 624 of 627
characters in place with displacement **bit-identical to HEAD** (1.75 / 8.6). It cannot cause `65`'s
regression, because `65`'s box text is only zeroed when both knobs are on: 627 (HEAD) -> 627 (anchor off)
-> 624 (cap) -> 0 (both). The interaction, not either knob, is what reflows that caption - which is
consistent with its 25 separate anchored boxes: the caption is fragmented per fragment, and only the pair
lets the fragments out.

**4. `27` is unchanged by the cap in position and emptied of box text.** 1.62 / 7.7 before and after, 57
characters -> 0. That is the shape of a free win, and it is the same document that already has a Google
verdict.

## The honest gap

- **21 of the 23 documents the cap changes have not been measured for position.** Two were measured, both
  benign. The cap's blast radius is 23 documents and this run has evidence on 2 of them.
- `policy-2col` was not measured under the cap alone or under the pair; only anchor-off.
- No Google render was produced in this run. Every Google statement above is the previous run's stored
  verdict for `27` (40/42 -> 42/42) and the `benchmarks/gverify` store for the rest.
- Page count was not compared on the cap build for anything except the engine's own counter.

## What the next run does

1. Apply `patches/gapcap-instrument.patch`, build with `-Dp2w.gapcap=20000`, convert the corpus
   (`corpus-convert.py --force`), and take the **cap alone** to Google on `27` (expect 42/42 - it is the
   stored verdict) and on 3 of the 21 unmeasured carriers, chosen for having a stored verdict that
   currently PASSES `18_displacement`.
2. Only if those hold: ship the cap as a default and restamp. The anchor stays on.
3. `65_two_col_full_width_figure_caption` is the regression witness for any future attempt to reflow
   full-width spanning captions. It must never be traded for a box-character count.

## Reproduce

```
# anchor off - no patch needed, the flag is on HEAD
java -Xmx700m -Dp2w.zganchor=false -cp out:... ConvertAll <shard-dir> /scratch/work/p2w/out-zg
# cap only
git apply tools/p2w-bench/patches/gapcap-instrument.patch && javac ... && \
java -Xmx700m -Dp2w.gapcap=20000 -cp out:... ConvertAll <shard-dir> /scratch/work/p2w/out-cap
# box census, and position
python3 boxscan.py /scratch/work/p2w/out-cap
python3 dispm.py cap 65_two_col_full_width_figure_caption
```
JVM needs `-Xmx700m -XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=256m` on this pod: the default
reserves 1 GB of compressed class space and dies on a 2 GB cgroup.
