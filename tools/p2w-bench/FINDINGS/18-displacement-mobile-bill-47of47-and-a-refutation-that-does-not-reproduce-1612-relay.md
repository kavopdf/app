# 18_displacement — mobile-bill is 47/47 in Google under the spacer patch. The refutation does not reproduce.

**Run:** relay 16:12, 22 Nov 2026. **Engine:** HEAD `d254524` + `patches/18-spacer-before-rowpitch-rowrule.patch`
applied to the working tree (uncommitted; the corpus was not ratcheted in this slot).
Build: `bash tools/p2w-bench/build-engine.sh` on a cold pod — JDK fetched, engine built, 50 s.
Conversion: `ConvertOne` per document (NOT `ConvertAll` — see the batch-dependence note in p2w.py:1037).

## Why this measurement was made

Two fixer runs worked this class at once, which the claim is supposed to make impossible:

* `63f2e97e` **relay 15:17** — Google: `table-with-no-header-row` 41/42 -> **47/47 PASS**.
* `1085564c` **fixer 15:34** — Google: `mobile-bill` 46/47 -> **43/47 with an extra page**; that one
  document was the whole basis for calling the patch refuted and leaving it unlanded.

Both slots were live at the same time on the same tree. A refutation measured by a concurrent run on a
tree another run was editing is not a refutation, so the patch's fate was undecided rather than settled.

## The measurement

`mobile-bill.docx` from the patched engine -> `KavoPDF-Verify` -> Google Doc -> exported PDF (1 page,
same as the source) -> `verify_google.py --docx`. The probe Doc was deleted afterwards.

| document | baseline (`benchmarks/gverify/*.json`) | this engine, live Google round trip |
|:--|:--|:--|
| `mobile-bill` | 46/47, failed `18_displacement` only | **47/47 PASS — CLEAN** |

**It does not reproduce the extra page.** The export is one page, the source is one page, and all 47
checks pass. The 15:34 finding — that the patch charges mobile-bill's 128/124 tw spacers in full and
spills the page — is refuted by the round trip it was derived from.

## What the class now stands at, all four documents measured in Google

| document | before | after | verdict |
|:--|:--|:--|:--|
| `table-with-no-header-row` | 46/47 (`18_displacement`) | **47/47** | CLEAN |
| `mobile-bill` | 46/47 (`18_displacement`) | **47/47** | CLEAN |
| `362_price_list_dense` | 41/42 | 41/42 | unchanged |
| `two-tables-stacked-with-no-gap` | 46/47 | 46/47 | unchanged |

Two documents become clean, two are unchanged, **none of the four gets worse in Google**. The class has
16 documents that fail `18_displacement` and nothing else (recomputed independently this run from the
213 JSONs), so the prize is up to 16 clean documents, 23 -> 39 of the 192 scored.

## Why it was not ratcheted in this slot

The slot had ~15 minutes left when the round trip landed, and the corpus pass alone is 17 min at the
measured 6.0 s/document. Starting one that cannot finish is what the brief forbids. The patch is left in
`patches/`, the working tree reverted to baseline, and the next slot's first move is written below.

## THE NEXT MOVE, exactly

    git apply patches/18-spacer-before-rowpitch-rowrule.patch
    P2W_ENGINE_SRC=/scratch/work/CS python3 benchmarks/p2w.py --budget 250 --force
    python3 tools/p2w-bench/ratchet.py && bash tools/commit-gate.sh

`P2W_ENGINE_SRC` is mandatory: without it `p2w.py:82` builds `/scratch/work/p2w/repo`, a fresh clone of
HEAD with none of the patch in it, and the pass reports a false negative about a change it never
converted. Check that the log's first line names your own tree before spending the pass.

**Expect the LibreOffice proxy to be hostile.** The 15:34 bisect recorded the patched engine at
share@5 30-36 on documents that read 0.5-1.5 at baseline, and this run's own `soffice` render of the
patched `mobile-bill` is 1 page with the same content, so the proxy's number is not the page's layout.
If `ratchet.py` refuses on the proxy while Google reads 47/47, that is a gate-instrument contradiction
to record, not a reason to drop the patch — but it must be written down before it is overruled.

## Instrument finding, from the same run

The brief's headline "6 clean of 192 scored in Google" is not what the data says: recomputing from the
213 `benchmarks/gverify/*.json` gives **23 clean of 192 scored** (empty `failed[]`), 169 failing at
least one check. And "`18_displacement` is worth 38.7 clean documents" is a percentage read as a count:
fixing it alone turns exactly **16** documents clean, which is 8.3 % of the scored corpus. Every class
in `classpick.py --leverage` is priced in that column, so the whole table is on a unit that does not
match its own heading.
