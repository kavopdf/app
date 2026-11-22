# 18_displacement — the constant residual on 22_invoice and 16_right: local arithmetic

Engine clone `e6c12db`, corpus 213 PDFs (`corpus-fetch.sh`), built with `build-engine.sh`,
converted with `ConvertOne` run from `tools/engine-verify/` (from the repo root the asset path
is not found and the writer emits an empty body — silent, exit 0). No Google round trip was
possible in this session (see §5); every Google figure below is the repo's recorded one, and
every other number was measured here.

## 1. What the engine emitted (measured)

| | `22_invoice_four_columns_txtpos` | `16_right_aligned_amounts_txtpos` |
|:--|:--|:--|
| table-1 spacer | `w:before="113" w:line="20" w:lineRule="exact"`, `sz=2` | `w:before="73" w:line="20"`, `sz=2` |
| declared gap | 133 tw = **6.65 pt** | 93 tw = **4.65 pt** |
| split fired | yes (guard passed) | yes |
| second spacer | `before="195" line="20"` (215 tw) | none |
| `w:tblpPr` / `tblpY` | **absent** | **absent** |
| `w:tblCellMar` top | **0** | **0** |
| `w:tblBorders` | all `nil` | all `nil` |
| row height | `trHeight 380 atLeast` (19 pt), 12 rows | `380 atLeast`, 13 rows |
| cell paragraph | `before=152 line=190 sz=18` (9 pt) on 10 of 12 rows; `294/12` on rows 4 and 10 | `152/190` on 12 of 13 rows; `294/12` on row 0 |

Source geometry (PyMuPDF): `22` table-1 top rule y=174.0, 12 row baselines at pitch **19.00**,
first row text top 183.98; `16` top rule 140.0, 13 rows at pitch **19.00**, first text top 147.98.
LibreOffice: unpatched build scores **42/42** on both (reproduces `benchmarks/gverify-lo/`), 71 and
64 text lines.

## 2. Google laws used (all from this repo's own measured findings)

* `w:before` on an empty paragraph: **V/20 pt, exactly**, no floor, no cap; 25-point sweep,
  max residual 0.000000 pt (V=124 laid 6.2000, V=128 laid 6.4000 — no point snapping).
* `w:line` exact on mark `sz=2`: `h = 2.5873 * max(L/240, 0.06)`; L=20 → **0.2156**, L=1 → 0.1552.
* Cell paragraph on an `sz` mark: `before + max((L/240)*1.1499*size, 0.069*size)`.

## 3. The candidates, with arithmetic

| candidate | term on `22` | term on `16` | constant? | verdict |
|:--|--:|--:|:--|:--|
| (a) `w:before` dropped / rounded | −5.65 / −0.65 | −3.65 / −0.65 | no | **killed** |
| (b) table `tblpY` / cell margin | 0.00 | 0.00 | — | **killed** |
| (c) hairline `line=20` | **−0.7844** | **−0.7844** | yes | **supported** |
| (c′) companion: cell line box `line=190` | **−1.307** | **−1.307** | yes | supported |
| (d) check baseline / tolerance | — | — | — | explains the tail, not the constant |

(a) is not dropped: both spacers are mid-page-1, preceded by a header paragraph, so neither the
page-top nor the after-page-break case applies; and a drop is not constant.
(b) needs a 50-tw fixed term and the XML carries no vertical table property at all.
(c) the 1.00 pt the hairline is credited with in `spacerTw` is laid as 0.2156 pt: −0.7844.
(c′) the cell box is declared 7.60+9.50 = 17.10 pt and laid 7.60+8.193 = 15.793: −1.307 per row,
identical in both documents because the construct is identical, and not absorbed by the 19 pt
`atLeast` floor (it is the row's content, and the text sits at the top of it).
Sum of the two constants: **−2.09**. Adding the flow above the table (+0.305 on `22`, +0.263 on
`16`) gives table-top −0.479 / −0.521 and cell text **−1.79 / −1.83**, against the recorded
medians −2.76 / −2.45. Bracketed, not reproduced: 0.7–1.0 pt is unaccounted for by local geometry.
(d) tolerance is `clamp(0.35*size,1.5,4.5)` = 3.15 pt at 9 pt, 2.975 at 8.5, 2.80 at 8 — a uniform
−2.5 is inside every one of those, so a single constant cannot fail the check. The recorded
"median −2.5 with 21/71 out" is therefore bimodal: a constant plus a larger tail.

## 4. The patch (one constant, `DocxWriter.java:5947`)

```
-            int spacerHairTw = 20;
+            int spacerHairTw = 1;
```

Laid gap: 5.8656 → 6.7552 pt on `22`, 3.8656 → 4.7552 on `16` (+0.8896 on both); error
−0.7844 → +0.1052. `wantTw = spacerTw - 1` and `line = 1` keep `before + line = spacerTw` to the
twip, so LibreOffice and Word see the same page: measured max |dy| **0.000 pt** over all 71 and 64
lines between the two builds, and 42/42 in LibreOffice for all five documents rebuilt
(`22`, `16`, `29_dot_leaders`, `41_coloured_headings`, `73_marksheet`).

* Aimed at newly 42/42 (predicted, Google-side): `22_invoice_four_columns_txtpos`,
  `16_right_aligned_amounts_txtpos` — residual −1.87 / −1.56, inside the 3.15 pt tolerance at 9 pt.
* Byte-identical: every document where the guard refuses (`spendable == false`, the `else` branch
  is untouched) — `mobile-bill`, `insurance-policy-schedule`, `68_journal_wide_table_spanning`,
  `72_bank_statement_no_rules_right_amounts` (58 tw short of the guard) — and every document with
  no table gap.
* Byte-changed, geometrically identical: the three wins (`73`, `41`, `29`).
* Not claimed: if the failing tail is the cell box (c′) rather than the hairline, `22`/`16` stay
  at 41/42 and the next lever is the row emitter, not the spacer.

## 5. Verified vs not

Verified here: build, conversion, emitted spacer/table XML, source geometry, LO 42/42 on both
builds, zero LO geometry change under the patch, `git apply --check` clean, tree restored clean at
`e6c12db` (nothing committed, pushed, or left modified).

Not verified: any Google number. The Drive tools are reachable, but every upload path needs a file
registered to this session — `/scratch/downloads` is root-owned and read-only, and
`GOOGLEDRIVE_CREATE_FILE` rejects `/scratch/work` and `/scratch/output` paths with 403 "the file key
does not belong to this project". The only hosting path available was a deploy to the user's own
Netlify site, which was not done unasked. Consequently −2.76 / −2.45 are quoted from
`FINDINGS/18_displacement-SPACER-SPLIT-LANDS-4-COSTS-2-REVERTED-2320-relay.md`, not re-measured.

Also unverified: whether Google anchors the cell baseline to the top or the bottom of its shrunken
line box. That decides whether (c′) is a text-position term at all or only a row-height term, and
it is one Google export away.
