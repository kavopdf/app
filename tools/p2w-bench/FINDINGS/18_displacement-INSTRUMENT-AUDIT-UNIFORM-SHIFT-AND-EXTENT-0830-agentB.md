# Instrument audit: `18_displacement` and `60_text_column_right_edge`

24 Nov 2026. Audited against the tree in `CS-repo.zip`, unpacked read-only in spirit: the archive
carries no `.git`, and no file in it was edited — every code claim below is a quotation with a line
number, and every number is either measured in this sandbox (the E-numbers) or read out of a named
file in the tree.

The precedent I was asked to match is `tools/p2w-bench/FINDINGS/25_invisible_text-CHECK-READ-THE-SHEET-0710-fixer.md`:
`_visual_counts()` (`tools/p2w-bench/verify_google.py:800`) took the first filled rect containing a
run's corner, a Google export opens with a page-sized white rect, and white type on an orange band
counted as invisible. The check read the **paper**. The question here is whether `18` or `60` does
the same thing.

Short answer: **`60` does, and I reproduced it in one page of code. `18` does something of the same
family but it is not the fault the brief describes — the brief's premise about `18` is out of date,
and the rule it names is not the rule that decides.** Both are established below with numbers I ran
in this sandbox plus the stored measurements, and nothing else.

---

## 1. What actually decides `18_displacement`

### 1.1 The brief's premise does not hold on this tree

The brief says the verdict "comes from `med_dy` and `worst_dy` against a threshold". It does not.
`med_dy` and `worst_dy` are computed and then **never scored**:

```
5658	        dys.append(g["ry"] - r["ry"])
...
5670	    med_dy = round(median(dys), 1)
5671	    worst_dy = round(max((abs(d) for d in dys), default=0), 1)
```
`tools/p2w-bench/verify_google.py:5658`, `:5670-5671`

and they leave the function as the fourth element of the check tuple, i.e. as *detail*:

```
5781	    checks["18_displacement"] = (0, len(bad_pages), not bad_pages, {
5782	        "med_dy": med_dy, "worst_dy": worst_dy, "med_dx": med_dx,
```
`verify_google.py:5781-5782`

with the source saying so in as many words at `verify_google.py:5774`: *"WHAT THE COUNT IS MADE OF,
reported and never scored (the fourth element …)"*. The median-against-a-threshold rule is the rule
this check **used to have and had retired**, and the file records why:

```
5686	    # 18 as it stood was a POOLED MEDIAN against a fixed 3 pt, and a median is a majority rule:
5687	    # 10 of 21 lines 20 pt out reads 0.0 and PASSED, and so did 9 of 10 pages 20 pt low.
```
`verify_google.py:5686-5687`

So there is **no `med_dy` threshold to find**. Anyone reading `med_dy: -2.8` out of
`benchmarks/gverify/362_price_list_dense.json` and calling it "the number the check failed on" is
reading a diagnostic, not the verdict. I say this plainly because it changes the answer to question 2.

### 1.2 The rule that does decide it

```
5740	    def _tol(size):
5741	        return min(max(0.35 * size, 1.5), 4.5)
...
5746	    TAIL_FACTOR = 2.0
...
5765	        n_out = sum(1 for d, sz in ds if abs(d) > _tol(sz))
...
5769	        worst_here = max(abs(d) / _tol(sz) for d, sz in ds)
5770	        if (n_out > max(2, -(-len(ds) * 5 // 100)) or n_out == len(ds)
5771	                or worst_here > TAIL_FACTOR):
5772	            bad_pages.append(pg)
```
`verify_google.py:5740-5741`, `:5746`, `:5765-5772`

| property | value | line |
|:--|:--|:--|
| statistic | count of upright source runs whose \|dy\| exceeds their own tolerance, **per page** | `:5765`, inside the page loop at `:5748` |
| tolerance | `clamp(0.35 × size, 1.5, 4.5)` pt, `size` = the **source** run's font size | `:5740-5741` |
| floor / cap | 1.5 pt below 4.29 pt type; 4.5 pt above 12.86 pt type | from `:5741` |
| per-page budget | `n_out > max(2, ceil(0.05 × n))` | `:5770` |
| block clause | `n_out == len(ds)` — every run on the page out | `:5770` |
| tail clause | `max(|dy| / tol) > 2.0` — one run more than **2×** its tolerance out | `:5746`, `:5771` |
| median or mean? | **neither** — a count of runs. `med_dy` exists but is not scored | `:5765` vs `:5781` |
| per page or per document? | **per page**; the document fails if any page is in `bad_pages` | `:5748-5772` |

Tolerance as a table (from `:5741`, arithmetic only): 5 pt → 1.75; 6 → 2.10; 6.5 → 2.275; 7 → 2.45;
8 → 2.80; 9 → 3.15; 10 → 3.50; 12 → 4.20; ≥12.86 → 4.50.

One further fact that matters for reading the stored numbers: `dy` is
`g["ry"] - r["ry"]` (`:5658`), and `ry` is the baseline origin projected into reading space
**minus the span's own ascent** (`runs()`, `verify_google.py:233-234`), which for an upright run is the bbox top.
`dys` at `:5658` is appended for **every matched pair**, while the verdict's `ds` is filtered to
upright runs by the `flat` set (`:5737-5738`, `:5751-5752`). So the reported `worst_dy` covers a
**wider population than the verdict** — `360_restaurant_menu` reports `worst_dy: 109.9` with the
check failing on `bad_pages: [0]`, i.e. the 109.9 pt is not what the check judged. `med_dy` and
`worst_dy` are therefore also not a faithful summary of the verdict, only of the population.

---

## 2. Is the threshold calibrated against something real?

Two separate questions hide in that one, and they get different answers.

**(a) The anchor is real.** `_tol` is `0.35 em` of the source run's own size, applied to `dy` against
the **source PDF's own run positions** — not against a normalised page, not against a proxy render.
The file states the intent at `:5681-5683`: *"the only one of the three calibrated against what a
user SEES … Measured on rendered pages: 2 pt 3.4 % ink contact, 3 pt 5.3 % (the knee), 4 pt 15.8 %,
10 pt 59.7 %"* (`verify_google.py:5682-5683`). Whatever else is wrong, the check is not comparing
against a foreign page.

**(b) The statistic is not the one that curve was measured on, and that is the fault.**

Ink contact is a *relative* quantity: it happens when ink approaches other ink. A **rigid
translation of a whole page** produces **zero** change in ink contact — every gap is preserved — yet
it is exactly what the block clause (`n_out == len(ds)`) charges. I measured this on the repo's own
checker, on a real corpus document.

### 2.1 E1 — a real document against itself, translated rigidly

`benchmarks/realworld/041122-Account_Opening_Form.pdf`, 9 pages, 1 344 matched runs. The "render" is
the source with one `1 0 0 1 0 -dy cm` prepended to each page's first content stream: vector text,
every glyph in the same position relative to every other glyph. Scored by `compare()` from this repo
(`verify_google.py:4593`), unmodified. Ink = non-white pixels at 150 dpi; gap = the smallest vertical
gap between two adjacent line ink boxes.

| rigid dy | `18` passes? | `med_dy` | `worst_dy` | pages failed | ink pixels | min line gap |
|--:|:--|--:|--:|--:|--:|--:|
| 0.0 | yes | 0.0 | 0.0 | 0 | — | — |
| 0.5 | yes | 0.5 | 0.5 | 0 | −0.30 % | **0.00 pt** |
| 1.0 | yes | 1.0 | 1.0 | 0 | −0.44 % | **0.00 pt** |
| 1.5 | yes | 1.5 | 1.5 | 0 | −0.38 % | **0.00 pt** |
| **2.0** | **no** | 2.0 | 2.0 | **1** | −0.13 % | **0.00 pt** |
| **2.5** | **no** | 2.5 | 2.5 | **7** | −0.30 % | **0.00 pt** |
| **2.8** | **no** | 2.8 | 2.8 | **7** | −0.29 % | **0.00 pt** |
| 3.0 | no | 3.0 | 3.0 | 7 | −0.40 % | **0.00 pt** |
| 4.0 | no | 4.0 | 4.0 | 9 | −0.55 % | **0.00 pt** |

Read the two right-hand columns: **the page is unchanged in every respect a reader perceives** — the
small ink deltas are rasterisation and antialias noise, and the minimum gap between adjacent lines of
ink is *identical to the hundredth of a point at every displacement*. The document fails anyway.

Also note `med_dy == worst_dy == dy` exactly at every step: the matcher is exact here, so nothing in
this table is pairing noise. And the crossover is where the page's own type size says it should be —
this form is set overwhelmingly in 6.0 pt and 6.5 pt type (21 190 characters at 6.5 pt, 17 193 at
6.0 pt, measured from the file), so tolerance is 2.10-2.275 pt and the first failure lands at 2.0 pt
(the 5.0 pt runs, tolerance 1.75 pt).

### 2.2 E4 — the control: the defect the check exists for

Same method, a controlled pair: 12 lines, 10 pt Liberation Sans, 12 pt pitch, minimum ink gap between
lines 0.84 pt in the source. (a) one line displaced; (b) all twelve displaced.

| dy | one line moved | all lines moved | ink gap, one line moved |
|--:|:--|:--|--:|
| 0.5 | pass | pass | 0.34 pt |
| 1.0 | pass | pass | −0.16 pt |
| 1.5 | pass | pass | −0.66 pt |
| 2.0 | pass | pass | −1.16 pt |
| 2.5 | pass | pass | −1.66 pt |
| 2.8 | pass | pass | −1.96 pt |
| 3.0 | pass | pass | −2.16 pt |
| 4.0 | **pass** | **fail** | −3.16 pt |
| 6.0 | **pass** | **fail** | **−5.16 pt** |

At 6.0 pt one line is **printed on its neighbour** — the ink boxes overlap by 5.16 pt, which is more
than half the 10 pt em, and it is the most visible thing that can happen to a line of text — and
`18_displacement` **passes**. It passes because one run out is inside the 2-run grace (`:5770`) and
`worst_here = 6.0 / 3.5 = 1.71 < 2.0` (`:5771`). The single-line crossover is 2× tolerance: **7.0 pt
at 10 pt type**. Meanwhile a page whose ink has not moved relative to itself at all fails at 4.0 pt
(10 pt type) or 2.0 pt (6 pt type).

**That is the fault, and it is the precedent's family.** The check's sensitivity is inverted with
respect to what a reader sees:

* a **uniform** displacement — the page's text block sitting lower in the export, i.e. a property of
  the **paper**, invisible because nothing moved relative to anything — is charged at the tolerance
  (2.10 pt at 6 pt type, 1.5 pt at the floor);
* a **relative** displacement — ink colliding with ink, the one thing the stated calibration curve
  is about — is forgiven up to **2× tolerance** (7.0 pt at 10 pt type, and up to 9.0 pt at the cap).

The comment at `:5682-5683` defends the tolerance with an ink-contact curve, and the clause that
convicts a rigid shift is measured by nothing in that curve. `n_out == len(ds)` is, literally, "the
page's frame moved".

### 2.3 What 2.8 pt is, physically

1 pt = 0.3528 mm, so **2.8 pt = 0.99 mm** — one millimetre.

| document | its own type size | its own line pitch | 2.8 pt as | source |
|:--|:--|:--|:--|:--|
| `362_price_list_dense` | 6.5–7 pt | **8.40 pt** (29 rows) | 0.40–0.43 em; **33 % of a row pitch** | `FINDINGS/18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md:65` |
| `041122-Account_Opening_Form` (measured here) | 6.0 / 6.5 pt | 12.00 pt median | 0.43–0.47 em; 23 % of pitch | measured from the file |
| `two-tables-stacked-with-no-gap` | not stated | **18.40 pt** | 15 % of pitch | `FINDINGS/…` (source pitch 18.40 pt) |
| `71_invoice_space_aligned_no_rules` | not stated | **18.00 pt** | 16 % of pitch | `FINDINGS/…` (pitch: the 18.00 pt) |

So the brief's framing needs one correction and one confirmation:

* **Confirmation**: 2.8 pt is below anything a reader resolves as "wrong" when it is a *uniform*
  shift. One millimetre of block offset on an A4 page, with every gap intact, is not visible without
  an overlay. E1 shows the check cannot tell that case from a real one.
* **Correction**: for `362_price_list_dense` specifically, `med_dy = −2.8` is the median of a **ramp**,
  not a constant. This repo's own per-run profile of that document reads: *"inside every table each
  row is laid 0.75 pt too tall … 24 rows x 0.75 = 18 pt of ramp"* (`tools/p2w-bench/HANDOFF.md:29`)
  and *"21.75 pt over 362_price_list_dense's 29 rows"* (`HANDOFF.md:33`). At an 8.40 pt pitch with
  6.5–7 pt type the leading is ~1.4–1.9 pt, so a 0.75 pt row growth eats 40–54 % of the leading and
  21.75 pt of accumulated drift by the foot of the table is 7.7 mm. **That document is genuinely
  displaced, and the median hid it.** The number is not evidence of an invisible fault there; it is
  evidence that `med_dy` is a bad summary (which is what `:5774-5780` says).

### 2.4 Is `dy` an artefact of Google's substituted font? No — measured

`ry` is baseline minus the span's declared ascent (`runs()`, `verify_google.py:233-234`), so a face
substitution could in principle move `ry` with no glyph moving. Measured, same string, same baselines,
same 10 pt size, six lines:

| source face | render face | dy |
|:--|:--|--:|
| Liberation Sans | Liberation Serif | **+0.14 pt** |
| Liberation Sans | DejaVu Sans | **−0.23 pt** |
| Liberation Sans | DejaVu Serif | **−0.23 pt** |

The face contributes at most 0.23 pt at 10 pt — 6.6 % of the 3.50 pt tolerance and below the 1.5 pt
floor. **The ascent-contamination hypothesis is refuted.** `18`'s `dy` is a position, not a font
metric. This is the discriminator that separates `18` from `60` (§3): the same face pair that leaves
`18` unmoved fails `60`.

---

## 3. `60_text_column_right_edge`: does it conflate "more ink" with "ink in the wrong place"?

**Yes. The conflation is in the statistic, not in the tolerance.**

The deciding code:

```
2654	    over = under = 0
2655	    for i in range(min(src.page_count, gd.page_count)):
...
2674	            if rg > rs + RIGHT_OVERRUN + slack:
2675	                over += 1
2676	                break
2677	            if rg < rs - RIGHT_UNDERRUN - slack:
2678	                under += 1
2679	                break
...
2684	        s_max = max((b[2] for b in page_lines(src[i])), default=0)
2685	        far = sum(1 for b in page_lines(gd[i]) if b[2] > s_max + 3 * RIGHT_OVERRUN)
2686	        if far >= 2 and not over:
2687	            over += 1
2690	    c["60_text_column_right_edge"] = (over, under, over == 0 and under == 0)
```
`verify_google.py:2654-2690`, with `RIGHT_OVERRUN = 6.0` and `RIGHT_UNDERRUN = 8.0` at `:2558-2559`

`rs` and `rg` are **the widest line's right edge** in the source and the render column —
`edge()` returns `v[-1], min(SLACK_CAP, one_word)` where `v = sorted(b[2] for b in col)`
(`:2608`, `:2649-2652`). So the quantity is an **extent**: how far right the ink reaches.

An extent is a function of two independent things — *where the line starts and breaks*, and *how wide
each glyph is*. A change in advance widths moves the extent with the ink in exactly the right place.
That is "more ink" (here: less ink per line) being read as "ink in the wrong place", which is the
conflation already ruled on for `share@5px`:

> "`share@5px` conflates 'more ink, some of it far' with 'the same ink, further' … Same shape as
> `25_invisible_text`, which was a check reading the paper." — `tools/p2w-bench/BLOCKERS.md:257`

### 3.1 E5 — the check against a pure advance-width change

Two pages, identical text, identical left edge (x = 72), identical baselines, identical 10 pt size.
The only difference is the face. Scored by this repo's `compare()`.

| source face | render face | widest line | `60` result |
|:--|:--|:--|:--|
| DejaVu Sans | Liberation Sans | 483.9 → 431.4 pt (−10.8 %) | **over=0, under=1 → FAIL** |
| DejaVu Serif | Liberation Serif | 488.1 → 398.7 pt (−18.3 %) | **over=0, under=1 → FAIL** |
| DejaVu Sans | DejaVu Sans | 483.9 → 483.9 pt (0.0 %) | over=0, under=0 → pass |

Nothing moved. Not one left edge, not one baseline. The check fires — and it fires on the **UNDER**
branch, which is not even the fault the check is named for.

This reproduces, from the rule side, what the repo already measured from the document side: the four
documents that fail `60` **alone** in Google (`302_radiology_report`, `313_power_of_attorney`,
`316_contract_with_schedules`, `321_auditors_report`) all report `over=0, under=1`, land on a
**−58.5 / −65.6 / −65.6 pt** shortfall, two unrelated documents landing on the same tenth of a point,
and all four **pass** in LibreOffice. The recorded cause is the writer declaring `DejaVuSerif` /
`DejaVuSans` and Google rendering `ArialMT` (`FINDINGS/60_text_column_right_edge-IT-FIRES-UNDER-AND-THE-CAUSE-IS-FONT-SUBSTITUTION-2322-fixer.md:26-28`, `:40-43`).

### 3.2 The second conflation, in the safety net

`:2684-2687` widens the same question off-column: any **two** render lines whose right edge exceeds
the source page's widest line by `3 × 6.0 = 18 pt` fails the page. That is a pure "more ink to the
right" count — it has no reference to a column, to a left edge, or to where anything should be. A
renderer that sets the same text in a wider face trips it with nothing misplaced. It is the same
fault as the main clause, in a form that cannot even claim to be about a column.

---

## 4. The documents that fail only `18_displacement`

From `benchmarks/gverify/*.json`, 190 measurable, `failed == ["18_displacement"]` on **14** — the
number the leverage table claims. LibreOffice passes `18` on **11** of the 14 (fails it on
`68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`,
`balance-sheet-two-columns-of-figures`), from `benchmarks/gverify-lo/*.json`.

| document | `med_dy` | `worst_dy` | runs | bad pages | within a tolerance a user cannot see? |
|:--|--:|--:|--:|--:|:--|
| `362_price_list_dense` | −2.8 | 5.4 | 257 | [0] | **No** — 2.8 pt is 33 % of its 8.40 pt pitch, and the repo's per-run profile records a 21.75 pt ramp (`HANDOFF.md:29,33`) |
| `36_embedded_subset_font` | 1.7 | 3.5 | 29 | [0] | **Yes, probably** — no run exceeds 3.5 pt, below the check's own 4.5 pt cap |
| `71_invoice_space_aligned_no_rules` | 1.1 | 6.7 | 72 | [0] | Median yes, tail no — 6.7 pt is 37 % of its 18.00 pt pitch |
| `72_bank_statement_no_rules_right_amounts` | −13.0 | 28.2 | 80 | [0] | **No** — 28 pt is visible |
| `74_balance_sheet_indented_subitems` | 2.2 | 4.2 | 54 | [0] | **Yes, probably** — worst 4.2 pt, below the 4.5 pt cap |
| `balance-sheet-two-columns-of-figures` | −2.3 | 5.1 | 94 | [0] | Borderline — worst just over the cap |
| `bus-timetable-station-left-times-right` | −3.0 | 4.9 | 177 | [0] | Borderline — worst 4.9 pt |
| `insurance-policy-schedule` | −7.7 | 47.8 | 107 | [0] | **No** |
| `table-with-no-header-row` | −0.5 | 9.0 | 215 | [0] | **No** — 9.0 pt is half its 18.40 pt row pitch |
| `two-tables-stacked-with-no-gap` | −4.7 | 10.2 | 72 | [0] | **No** — 10.2 pt on an 18.40 pt pitch |
| `16_right_aligned_amounts_txtpos` | *not stated* | *not stated* | — | — | **not stated** |
| `31_times_body_arial_headings` | *not stated* | *not stated* | — | — | **not stated** |
| `68_journal_wide_table_spanning` | *not stated* | *not stated* | — | — | **not stated** |
| `mobile-bill` | *not stated* (−6.7 recorded elsewhere) | *not stated* (10.0) | — | — | **No**, on the `HANDOFF.md:29` figures |

The four "not stated" rows are documents whose stored JSON predates the detail field: they carry
`passed`/`failed`/`engine` and nothing else. Their numbers exist in the repo in one case only —
`HANDOFF.md:29` records live round trips reading *"med_dy −2.8 (362_price_list_dense), −3.0
(bus-timetable), −6.7 (mobile-bill), −13.0 (72_bank_statement); worst_dy 5.4/4.9/10.0/28.2"* — which
is where `mobile-bill`'s −6.7 / 10.0 comes from. For the other three the repo holds no measurement.

**My stated tolerance, and why.** Two thresholds, both derived from this repo's own numbers rather
than invented:

1. **Uniform component ≤ 1.5 pt** — the check's own floor (`:5741`), i.e. the smallest displacement it
   ever charges. E1 measured that a uniform shift of 1.5 pt changes nothing a reader sees (min line
   gap identical to 0.00 pt).
2. **Differential component ≤ 3.0 pt, or ≤ ¼ of the page's own line pitch, whichever is smaller** —
   3.0 pt is the check's own ink-contact "knee" (`:5683`: 3 pt = 5.3 % ink contact); ¼ pitch is the
   point at which a line moves a quarter of the way toward its neighbour.

By those: **2 of the 10 measured documents** (`36_embedded_subset_font`, `74_balance_sheet_indented_subitems`)
are inside a tolerance a user could not see on the stored numbers, and 2 more
(`balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-times-right`) are borderline at
the 4.5 pt cap. The other 6 are displaced by amounts no reader would miss.

Note what this does **not** say: it does not say the other 12 are instrument failures. `362`,
`72_bank`, `insurance-policy-schedule`, `table-with-no-header-row`, `two-tables-stacked` and
`mobile-bill` are all displaced by 5–48 pt at a pitch where that is a visible collision or drift.
Those are the engine's or Google's, and the check is right about them.

---

## 5. Verdicts

### `18_displacement` — (ii) the instrument, for one specific population; (i)/(iii) for the rest

The discriminating evidence:

| observation | number | what it discriminates |
|:--|:--|:--|
| a real corpus document rigidly translated 2.0 pt fails, with min line gap unchanged to 0.00 pt | E1, 9 pages | the rule charges a **uniform** shift, which is the page frame — the paper |
| one line displaced 6.0 pt — 5.16 pt of ink overlap — passes | E4 | the rule forgives the **differential** shift, the only thing its own calibration curve measures |
| single-line crossover = 2 × tolerance (7.0 pt at 10 pt type) | E4 | the tail clause's `TAIL_FACTOR = 2.0` (`:5746`) is the whole reason |
| a face substitution moves `dy` by ≤ 0.23 pt | E3 | `dy` is not a font-metric artefact — the fault is not ascent contamination |
| 84 of 103 Google failures pass in LibreOffice | `gverify-lo` | *consistent* with an instrument fault, but does not prove one — Google's layout genuinely differs and this proxy cannot see it |

So: **the instrument is at fault** in that it cannot separate "the text block sits 1–2 pt lower on the
page" from "the lines are colliding", and it fails documents on the former while passing the latter
up to 2× tolerance. That is the same shape as `25_invisible_text` — a check whose deciding statistic
is a property of the page rather than of the ink. It is **not** true that the 103 failures are false:
the repo's own per-run census finds most failing pages displaced 48.5–67.6 pt
(`FINDINGS/18_displacement-dy-shape-101323-4fa7.md`, uniform-shift census), and E1's own document
fails for real reasons at 4.0 pt on 10 pt type. On the 14 sole-failure documents the instrument can be
convicted from the stored numbers on **2** (`36_embedded_subset_font`, `74_balance_sheet_indented_subitems`)
and suspected on 2 more.

A corollary worth stating for whoever fixes this: the check's leverage (40.1 clean documents) is not
40.1 layout bugs. At least two of the 14 are one tolerance change away from passing and have no layout
fault at all, and the rule's real defect — the 2× forgiveness of a genuine collision — is a *false
negative* that no leverage table counts.

### `60_text_column_right_edge` — (ii) the instrument

The discriminating evidence is E5, and it is a one-page construction: identical text, identical left
edge, identical baselines, **face changed**, and the check fires on the `under` branch. The statistic
is the column's widest right edge (`edge()`, `:2608-2652`), an **extent**, so it cannot distinguish
"the ink is wider/narrower" from "the ink is in the wrong place". This is precisely the `share@5px`
conflation that `BLOCKERS.md:257` already ruled on, and the `far` net (`:2684-2687`) is the same
conflation with no column in it at all.

What the underlying fault *is* — a writer declaring `DejaVuSerif`/`DejaVuSans` that Google renders as
`Arial` (`FINDINGS/60_…-IT-FIRES-UNDER-…:33-43`) — belongs to the engine, and to `53_embedded_faces`,
not to a column-edge check. `60`'s 19.8 leverage should therefore not be read as 19.8 layout bugs: on
the 5 documents that fail it alone, 4 are a font-selection decision wearing a layout check's name, and
those 4 pass in LibreOffice (the fifth, `79_inr_indian_digit_grouping_table`, fails `60` in
LibreOffice too and is not one of the four). Corpus-wide the check fails 56 of 190 measurable
documents, 41 of which pass it in LibreOffice, and it co-fails with `18_displacement` on **36** — the
two travel together far more than the brief's "8+4" suggests, which is consistent with both being
driven by the same face/row-height differences rather than by two independent layout faults. Verdict: **(ii) the instrument** — it asks the wrong question of the wrong
statistic, and it reports the answer under a name ("right edge") that is the opposite of what it
measured.

---

## 6. What would settle the rest, and what I predict

1. **Per-run `dy` for the 4 documents with no stored detail** (`16_right_aligned_amounts_txtpos`,
   `31_times_body_arial_headings`, `68_journal_wide_table_spanning`, `mobile-bill`) and for `36` and
   `74`. One probe on the exported PDFs, reusing `pairs`/`flat`/`_tol` exactly as
   `FINDINGS/18_displacement-dy-shape-101323-4fa7.md` did, printing `dy` against page depth. I predict
   `36` and `74` fit `dy = a + 0` with `|a| < 4.5 pt` (a uniform offset, instrument), and `362` fits
   `dy = a + b·y` with `b > 0` (a ramp, real).
2. **Split the uniform component out of `dy`** before the count: score `dy − median(dy_page)` with the
   same `_tol`, and score the residual separately. I predict this clears `36` and `74` and moves no
   document that is currently clean — the change can only remove counts, and it is falsifiable
   corpus-wide exactly as the `25_invisible_text` fix was (the source count must not fall while the
   render's does).
3. **Whether Google honours docx font embedding** — one round trip on `313_power_of_attorney` with
   `w:embedRegular` in `fontTable.xml`. I predict the `60` shortfall closes and `18` does not move,
   because E3 already shows the face is worth 0.23 pt to `18` and 58 pt to `60`.

No file in the repository was changed.

---

## Open questions

* Font size and line pitch for 8 of the 14 sole-failure documents are not recorded anywhere in the
  repository, so "2.8 pt is X % of its own pitch" can be stated only for `362`, `71`, `two-tables`,
  `table-with-no-header-row` and `041122-Account_Opening_Form`. Settling this needs the source PDFs,
  which are not in the zip.
* `med_dy` / `worst_dy` for `16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings` and
  `68_journal_wide_table_spanning` are not in `benchmarks/gverify/*.json` and not in any note I could
  find. `mobile-bill`'s are in `HANDOFF.md:29` only.
* Whether the 8.40 pt / 18.40 pt pitches quoted from `FINDINGS/` are the *source* pitches or the
  emitted ones — the notes say source, but I could not verify against a PDF.
