# 18_displacement — the waiver the last three slots asked for already exists, and the dither patch is refuted as a class fix

**22 Nov 2026 · relay slot 17:12 · engine HEAD `462353f9` · one live Google round trip on `mobile-bill` ·
one engine build with the dither patch · one falsification of the gate with a control · probe Doc
deleted, Drive root empty, engine reverted to HEAD**

Two results, in order of what they change.

## 1. The instrument question is already answered in the code, and the answer works

The 15:55 report's next move was: *"Either the ratchet gains a documented path for a change that is
clean in Google and regressed in the proxy (a waiver whose evidence is the Google round trip), or the
class is parked."* That path exists and has since the Google-is-the-truth change of 20 Nov.
`tools/p2w-bench/regress.py`, `docx_regressions()`:

```python
# A LIBREOFFICE REGRESSION IS ALLOWED WHEN GOOGLE IMPROVED ON THE SAME DOCUMENT.
for _it in worse:
    ...
    if g_after[_d] < g_before[_d]:
        _allowed.append((_d, _b, _c, g_before[_d], g_after[_d]))
```

`g_before` is the committed `benchmarks/gverify/<doc>.json`, `g_after` the working-tree copy. So the
waiver is not a policy decision anyone has to make: it is a measurement the run must produce, per
document, and it is refused when Google did not improve.

**Falsified, with a control, in a copy of the repo** (`/scratch/work/gatetest`, nothing committed from
it). `RANKING.csv` edited so `mobile-bill` reads the patched `share5` of 39.21 (baseline 1.55, 15 Nov
baseline 18.48):

| case | gverify for mobile-bill | `regress.py --check --allow-engine-change --only docx` |
|:--|:--|:--|
| A control | committed, 1 failing (`18_displacement`) | `docx: 1 REGRESSION(S)` → **REFUSED** |
| B | working tree, 0 failing | `docx: ALLOWED mobile-bill 18.48 -> 39.21 in LibreOffice, Google 1 -> 0 failing` → **PASS** |

The control is what makes this a test: a proxy regression with no Google gain is still refused. The
15:55 run read `ratchet.py` (the legacy 59-check tool that reads `BASELINE.md`) and concluded there was
no path. `regress.py` is the gate — `tools/install-gate.sh` installs it as the pre-commit hook — and it
has the path.

## 2. And the dither patch cannot use it, because it does not generalise

The 15:55 run measured the patch on `two-tables-stacked-with-no-gap` only (46/47 → 47/47 in Google,
0.77 → 29.51 in LibreOffice). This run built the same patch (`git apply` clean, engine built in 42 s,
`build-engine.sh`) and measured the **worst** of the 14 proxy regressions instead — `mobile-bill`,
1.55 → 39.21 — in both renderers.

| `mobile-bill` | LibreOffice share@5 | Google |
|:--|--:|:--|
| committed baseline | 1.55 | 46/47, fails `18_displacement` |
| dither patch | **39.21** | **46/47, fails `18_displacement`** |

The LibreOffice number reproduces the 15:55 figure to the hundredth, which proves the patch was live in
this build. The Google number does not move at all. Export
`/scratch/downloads/composio/mobile-bill-dither-probe.pdf`, scored with
`verify_google.py /scratch/work/p2w/corpus/mobile-bill.pdf <export> --docx <patched docx>`
(`18_displacement source=0 render=1`). Probe Doc `1jFSZr3JbWMKnQDr8sMPayIpGUEnJDCjH0IOAL78L4yQ`
deleted after scoring.

So on this document the patch takes 37.66 of proxy damage and buys nothing where the user looks. Under
the waiver above it is refused, and rightly: there is no Google improvement to weigh against the proxy.

**This refutes "the largest class is one build from 16 clean documents".** The patch fixes the document
it was measured on. It does not fix the class. At least one of the 14 proxy-regressed documents gains
nothing in Google, so a corpus pass spent on this patch would end at the gate with `mobile-bill` named.

## 3. Why the class still needs a mechanism, not a ship

`18_displacement` is a vertical displacement of up to 4.5 pt accumulating down a table. The dither
attacks the row pitch, which is where the 15:55 run located it, and it works on a document whose rows
sit off Google's 0.75 pt grid. `mobile-bill` is one page with a table whose rows are already on it, so
the dither has nothing to diffuse and the displacement is coming from somewhere else — most likely the
page-top flow (the spacer-to-`w:before` half of the same patch, which is the other mechanism in it, and
which was never measured alone on this document).

That is the next test, and it is cheap: apply the patch **without** the spacer hunk and measure
`mobile-bill` in Google again. If the spacer half is what loses the document, the dither can ship on
its own, and the waiver above is how it lands.

## 4. An obstacle cleared, recorded because it looked like a blocker

The gate REFUSED every commit on this pod for the first ten minutes:

    ENGINE CHANGED (docx): table measured on 6c6cf642e13b7ed2, the tree is 226f7f2df3013ad7
    REFUSED. This commit would land a regression or an unmeasured engine.

It was the clone, not the repo. `git clone --depth 1` leaves `462353f9^` absent, so `scope.py`'s
fallback `git diff <sha>^ <sha>` fails, the scope comes back empty, `regress.py` goes **strict**, and the
docx stamp is compared against a tree the txt-only commit legitimately moved. `git fetch --unshallow`
and the same gate on the same tree says `PASS - nothing got worse in the .txt only`. A run that starts
from a shallow clone and does not read this will spend its slot believing main carries an unmeasured
engine.

## What would prove this wrong

A Google round trip on `mobile-bill` with the spacer hunk alone removed, showing 47/47. If that passes,
the dither is shippable and this finding is about the patch's packaging rather than its construct.
