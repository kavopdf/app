# Does `ROW_RUNG_UNDER_TW` buy Google checks, or is it pure LibreOffice cost?

**Question.** Commit `8fb4f503` ("pitch-bound rows declared 10 twips under", 27 Nov 02:13) introduced
`ROW_RUNG_UNDER_TW = 10` in `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:54`. A later
LibreOffice-only bisect made it the single cause of the table-regression cluster and proposed reverting
it. This file settles, from the committed evidence alone, whether turning the constant off costs Google
checks or only the LibreOffice proxy.

**Method.** Read-only. Repo cloned at `c44c9c19` (27 Nov 23:04 UTC / 28 Nov 04:34 IST), full history.
Nothing built, nothing converted, nothing uploaded, nothing in the clone modified.

---

## 1. What the commit itself claims

`git log -1 8fb4f503`, verbatim body:

```
p2w fixer 27nov: table gap spent as w:before (70%), pitch-bound rows declared 10 twips under, gated on 5 pt of room under the row's own text

mobile-bill 46/47 -> 47/47 and electricity-bill 46/47 -> 47/47 in Google.
price-list-2col byte-identical (the gate), 16_right/74 unchanged.
regress.py --check PASS on engine 74a152e7, docx and txt, google-safe clean.

Measured: 4 declarations on mobile-bill (340/350/360/380 -> 18.15/18.40/19.15/19.90 pt
against a page pitch of 18.40); w:before 1:1 vs w:line 23% on electricity-bill; 70% of the
gap the point where both documents come out clean (60% -0.99 FAIL, 70% +0.49 PASS,
100% +4.70 FAIL). See FINDINGS/TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md
```

`git show --stat 8fb4f503` touches 15 files, including `benchmarks/gverify/mobile-bill.json` and
`benchmarks/gverify/electricity-bill.json` (22 lines each) and
`FINDINGS/TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md` (111 lines).

**Important caveat on that quote.** The commit ships three changes, not one: the rung
(`ROW_RUNG_UNDER_TW`), the foot gate (`FOOT_ROOM_MIN_TW = 100`), and the gap fraction
(`SPACER_SPEND_FRAC = 0.70f`). The `46/47 -> 47/47` sentence is the commit as a whole. It does not
say which of the three bought the check.

---

## 2. What the commit's own measurement file says

`FINDINGS/TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md`, §4, "Measured on `mobile-bill`, rung + gap
together":

| variant | med dy | 18_displacement |
|:--|--:|:--|
| rung only (0 % spent) | −9.65 | FAIL |
| 60 % spent | −0.99 | FAIL |
| **70 % spent** | **+0.49** | **PASS** |
| 100 % spent | +4.70 | FAIL |

So on the committed record, the Google PASS needs the **gap fraction**; the rung alone at 0 % spend is
still a FAIL. That file does not contain a rung-off / 70 %-spent row, so it does not isolate the rung
either. §5 states the outcome: "`mobile-bill` and `electricity-bill` go 46/47 -> **47/47**".

The same file, §3, is the only Google measurement in the commit that varies the rung alone —
`-10 twips` on **every** `w:trHeight`, five documents, before the foot gate existed:

| document | HEAD | −10 every row |
|:--|:--|:--|
| 16_right_aligned_amounts_txtpos | 41/42 | 41/42 |
| 74_balance_sheet_indented_subitems | 41/42 | 41/42 |
| electricity-bill | 41/42 | 41/42 |
| table-with-no-header-row | 41/42 | 41/42 |
| price-list-2col-dense-right-aligned | 41/42 | **40/42** (`46_text_crossing_rule` 0→2) |

That is the rung *on* (not off) moving nothing on `electricity-bill` in Google, and costing
`price-list-2col` a check — which is why the foot gate was added. It is not a rung-off test.
(Note the totals: this table quotes 41/42 while §4 and the gverify JSONs quote 46/47→47/47 for the same
two documents. Why the applicable-check total differs inside one file is **not stated**.)

---

## 3. The mechanism file

`tools/p2w-bench/FINDINGS/ROW-RUNG-26NOV.md`, measured on a real Google render of
`72_bank_statement_no_rules_right_amounts` (engine `a4d8fca469bba636`):

> "Declared row height 17.00 pt. Google draws 17.25 pt. That is `ceil(h / 0.75) * 0.75`, and the
> effect is cumulative down the table: 18 rows x +0.25 pt puts the foot of the table +3.50 pt below
> where the PDF drew it, against a 3.01 pt tolerance."

and its own falsifier:

> "A patched document whose Google `worst_dy` does not fall below 3.0 pt with the rung compensated.
> Do not implement it before that render exists."

The mechanism is one-sided: Google re-quantises a declared row height **up** onto a 0.75 pt ladder and
charges the row rule on top; declaring 10 twips (0.5 pt) under compensates for that. LibreOffice lays
the declaration literally, so the shortfall is pure loss there.

---

## 4. The LibreOffice-only evidence against the rung

`tools/p2w-bench/FINDINGS/RUNG-IS-THE-TABLE-REGRESSION-28NOV.md` (engine `a05b20eb`, HEAD `7415d7ea`):

> "`-Dp2w.rung=0` (rung off) | **0.61** | **2.38**" (against `47.48` / `41.14` at HEAD)

and its six-document table, `rung=0` restoring every document, e.g. `electricity-bill` 36.78 → **1.33**,
`mobile-bill` 30.09 → **1.55**. The same file is explicit that this is proxy evidence and stops there:

> "**NOT measured, and this is the whole decision:** which renderer is right. The rung was landed on
> Google evidence and I have only LibreOffice evidence against it. Under the charter's first
> non-negotiable — *Google is the truth, LibreOffice is a proxy* — a change that is right in Google and
> wrong in soffice is **not** a regression."

Corpus scale, `FINDINGS/ROW-RUNG-IS-A-PER-DOCUMENT-TRADE-NOT-ONE-CONSTANT-28NOV.md`: "better than the
committed table (share@5 down) **4** / worse **63** / unchanged 146" — again LibreOffice `share@5` only.

`tools/p2w-bench/FINDINGS/table-row-placement-IS-THE-RUNG-PROVEN-27NOV-relay.md` states the trade and
names the gap in the record:

> "It may cost them the one gverify check each that the rung bought; that trade is 2 checks against
> 84–96 documents and is worth making, but it is a Google question and this run did not export through
> Drive."

---

## 5. The gverify records

`benchmarks/gverify/mobile-bill.json` and `benchmarks/gverify/electricity-bill.json` **at HEAD
(`c44c9c19`)**, entire content of the scoring fields:

| file | passed / total | failed | engine | at |
|:--|:--|:--|:--|:--|
| `mobile-bill.json` | 47 / 47 | `[]` | `a05b20eb05fe0fc8` | `2026-11-27T14:46:41` |
| `electricity-bill.json` | 47 / 47 | `[]` | `a05b20eb05fe0fc8` | `2026-11-27T14:45:51` |

**They fail no checks now.** Both are `"status": "ok"`, `"rc": 0`, `"failed": []`, with
`displacement` `med_dy` 0.1 / worst 3.2 (mobile-bill) and `med_dy` −0.5 / worst 2.8 (electricity-bill),
`bad_pages: []`.

The files **do record an engine and a date**: `"engine": "a05b20eb05fe0fc8"` and
`"at": "2026-11-27T14:46:41"`. They also carry `"checks": "377699-1795789156"`, which
`tools/p2w-bench/gverify.py` uses as the check-set stamp (line 114: `got = d.get("checks")`). No field
in the JSON names the renderer; that the record is Google's is established by the tool that writes it
(`gverify.py:494`, `"  %-44s GOOGLE %s/%s"`) and by `verify_google.py`, whose usage is
`verify_google.py <source.pdf> <google-export.pdf>`. The renderer is **not stated** in the JSON itself.

At `8fb4f503` the same two files were the diff that bought the claim: `"passed": 46` → `47`,
`"failed": ["18_displacement"]` → `[]`, engine `a4d8fca469bba636` → `74a152e7d3fb3d26`,
`at` `2026-11-26T22:35:22` → `2026-11-27T02:13:33` (electricity-bill) and `22:39:07` → `02:13:30`
(mobile-bill). `git show 8fb4f503 -- benchmarks/gverify/*.json`.

---

## 6. The measurement that decides it — and it was made

`FINDINGS/THE-RUNG-IS-GOOGLE-PROVED-AND-THE-LIBREOFFICE-BASELINE-IS-BACKWARDS-28NOV-fixer.md`
(committed as `6865f403`, 27 Nov 23:01 UTC / 28 Nov 04:00 IST):

> "Measured, both directions, Google, this run. Neither document stays clean."

| document | rung = 10 (HEAD) | rung = 0 (this run) |
|:--|:--|:--|
| `mobile-bill` | **47/47**, 0 failing | **46/47**, fails `18_displacement` |
| `electricity-bill` | **47/47**, 0 failing | **46/47**, fails `18_displacement` |

> "The rung = 10 side is the committed result on `a05b20eb` (27 Nov 14:45–14:46). The rung = 0 side is
> this run: `ROW_RUNG_UNDER_TW = 0`, engine rebuilt, both documents converted with `ConvertOne`, uploaded
> to the KavoPDF-Verify folder as Google Docs, exported as PDF by Drive, scored by `gverify.py --collect`.
> Both probe documents were deleted afterwards; nothing is left in Drive."
>
> "**So `ROW_RUNG_UNDER_TW = 10` is right, and reverting it is a Google regression on 2 of 2 documents.**"

The commit body of `6865f403` repeats it: "rung=0 rebuilt, converted with ConvertOne, uploaded to
KavoPDF-Verify, exported by Drive, scored by gverify --collect: 46/47 on both, failing
18_displacement." `tools/p2w-bench/REPORT.md` and `LAST-MESSAGE.md` carry the same line in the run
table: "REFUTED: the rung revert (ROW_RUNG_UNDER_TW 0) is a Google regression on 2 of 2 documents."

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:54` still reads
`private static final int ROW_RUNG_UNDER_TW = 10;` at HEAD, and
`git log -S "ROW_RUNG_UNDER_TW" -- app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` returns
`8fb4f503` and nothing else: the value has not been changed since it landed.

---

## Verdict

**rung buys Google checks.**

Two of the two documents the constant was landed for lose `18_displacement` in Google when the constant
is set to 0 (47/47 → 46/47 on both), and the only evidence that scores the constant as harmful is
LibreOffice `share@5`, a renderer the charter designates a proxy. The commit that landed it claims the
same pair of checks (`46/47 -> 47/47 in Google`), so the claim and its refutation-test agree; the
refutation-test was run on 28 Nov and did not fire.

What is *not* settled by this verdict, and should not be read into it:

- **Scope.** The Google benefit is proved on **2 documents**, not on the corpus. Whether the rung helps
  or hurts the other 8 documents in the "Google-clean today" group of
  `THE-RUNG-IS-GOOGLE-PROVED-...md` is **not stated** anywhere in the record.
- **Attribution inside `8fb4f503`.** The commit message's `46/47 -> 47/47` covers three changes at once,
  and §4 of its own findings file shows the gap fraction is necessary for the PASS. The 28 Nov probe
  holds the gap fraction at 0.70 and varies only the rung, which is what makes the attribution
  defensible; the rung-off side is not committed as a `benchmarks/gverify/*.json`, only as a findings
  file and run state (probes deleted, `6865f403`).
- **The LibreOffice cost is real and unaddressed.** 84 refusals at HEAD, 4 better / 63 worse under
  `rung=0` (`ROW-RUNG-IS-A-PER-DOCUMENT-TRADE-NOT-ONE-CONSTANT-28NOV.md`). "Not pure LibreOffice cost"
  does not mean "free"; it means the gate is charging a Google-proved construct to a proxy, which is a
  gate question, not an engine question.

---

## What would prove this wrong

1. **A Google re-measurement of `mobile-bill` and `electricity-bill` at `rung=0` that returns 47/47.**
   This is the exact falsifier the 28 Nov run wrote for itself and the one the 03:18 run named:
   "If both stay 47/47 at rung=0, the rung is pure cost and should go"
   (`FINDINGS/RUNG-IS-THE-TABLE-REGRESSION-28NOV.md`). It was run and it did not hold — but the
   `rung=0` renders were deleted, so the only way to overturn this verdict is to redo that conversion
   and get 47/47. A committed `benchmarks/gverify/mobile-bill.json` with `rung=0`, engine and `at`
   stamps, would be the cleanest form.
2. **A rung-off document that Google scores *better*.** No such document appears anywhere in the
   record. `FINDINGS/TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md` §3 has five documents under a
   rung change and none improves (`price-list-2col` loses one). One document going 46/47 → 47/47 with
   the rung off would break the mechanism in §3 above, not just the trade.
3. **A Google `worst_dy` that does not fall with the rung compensated** — `ROW-RUNG-26NOV.md`'s own
   refutation clause: "A patched document whose Google `worst_dy` does not fall below 3.0 pt with the
   rung compensated." That would say the rung is not compensating the 0.75 pt ladder at all, and the
   `46/47` result is coincidence on two documents.
4. **A different applicable-check total that changes which check is lost.** The record quotes both
   41/42 and 46/47 for the same documents in the same commit. If `18_displacement` at `rung=0` is an
   artifact of the check-set version stamped `377699-1795789156`, re-scoring both sides under one
   check set would move the verdict. Not stated anywhere; nobody has done it.
5. **A rung-off measurement on a document outside the pair** that shows a Google gain, which would make
   the trade per-document (as `ROW-RUNG-IS-A-PER-DOCUMENT-TRADE-NOT-ONE-CONSTANT-28NOV.md` argues for
   LibreOffice) rather than a single right answer.

---

## Smallest experiment that decides it, and the Drive question

**Smallest experiment (already specified in the record, and already run once):** two documents,
`mobile-bill` and `electricity-bill`, converted with `ConvertOne` at `ROW_RUNG_UNDER_TW = 0` and at 10,
each export scored by `gverify.py --collect`. `FINDINGS/RUNG-IS-THE-TABLE-REGRESSION-28NOV.md` calls it
"the experiment that decides it, and it is two documents"; the 28 Nov run cost one engine rebuild plus
two conversions plus two exports. The LibreOffice half of the same question is far cheaper and needs no
network at all: `benchmarks/p2w.py::measure_doc` on one document is "5 s to convert and 10 s to score"
(same file) — but it cannot answer the Google question, only the proxy one.

**Can it be done without sending files to Google Drive?** Per the committed tooling, **no** — a Google
check requires Google's own renderer, and every route in the repo reaches it through Drive:

- `verify_google.py` scores "the PDF that Google Docs itself exports" (module docstring); it is a scorer,
  not a renderer. It can be run with no Drive involvement **only if** a Google-exported PDF already
  exists — and no Google export of a `rung=0` build exists, because the 28 Nov probes were deleted
  ("Both probe documents were deleted afterwards; nothing is left in Drive").
- `tools/p2w-bench/refresh-google.py` docstring: it "finds the .docx for every corpus document in the
  Drive folder", "copies each one with mimeType=google-apps.document, which is how Drive converts a
  .docx into a Google Doc", then exports PDF. And: "the ONLY routes a sandbox has for putting them
  there are: the user drops a zip in Drive and extracts it (manual, once) or
  `GOOGLEDRIVE_UPLOAD_FROM_URL` with the .docx at a public URL".

So the decisive experiment is **not** Drive-free as the repo is built. Any substitute would have to
obtain a Google render by some other route — a public URL conversion, or a human opening the two
`.docx` files in Google Docs on the device — and no such route is described in the record. What *is*
Drive-free is everything except the Google render itself: the build, the conversion, and the scoring.
