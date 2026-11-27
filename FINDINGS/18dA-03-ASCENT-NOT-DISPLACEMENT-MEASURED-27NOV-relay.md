# 18dA-03: `18_displacement`'s dy is a bbox top, so a matched baseline is charged as a moved line

**27 Nov 2026, fixer slot 11:15-, repo `kavopdf/app` @ HEAD of this commit.** Engine at HEAD (the agent that
probed this reverted both of its changes; `DocxWriter.java` is at `c910d164`). Corpus 213/213, JDK, engine
compiled, gate installed on the pod this ran on.

Two things happened: a sub-agent built and measured two engine changes against the "0.312 em baseline
deficit" recorded in `FINDINGS/18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md`, both were refuted; and the
fixer then verified the refutation in the instrument itself and with its own code. **Both halves are below.
The second half is the result.**

---

## 1. The premise this started from, and why it is wrong

`18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md` measured, on `31_times_body_arial_headings`, that the
built line sits +2.70 pt (median) below the source, and read that as the renderer putting the baseline
0.312 em below the top of a hairline line box against the engine's 0.050 em.

The charge is real. The reading of it is not.

## 2. The instrument: `dy` compares BBOX TOPS, not baselines

Read from `tools/p2w-bench/verify_google.py` (this tree):

```
268    ryb = rproj(ox, oy, fr)[1] - ascent
269    ...
293    "ry": round(ryb, 2),
...
5874   ds = [(g["ry"] - r["ry"], g["size"]) for r, g in pairs
```

and the ascent on line 268 is `ascent = oy - b[1]` (`:267`) — **PyMuPDF's own ascent for the face that was
actually rendered**. The comment at `:260-266` is explicit that for an upright line `ry` is identical to the
bbox top. So `18_displacement`'s `dy` is

    dy = (bbox_top of the built face) - (bbox_top of the source face)
       = (origin + ascent) difference  =  baseline difference  +  ascent difference

**A document whose baselines coincide exactly, but whose built face has a smaller ascent than the source's
face, is charged the ascent difference as displacement.** No amount of moving the line can clear it: moving
the line up by that amount moves the baseline off, which is what the two refuted attempts did.

## 3. The measurement, made independently of the sub-agent's tool

`/scratch/work/relay_ascent.py` (this run's own code: PyMuPDF `rawdict`, match by `(page, text, nearest x
within 4 pt)`, medians over matched spans; LibreOffice proxy, labelled as such) on the corpus PDFs against
the HEAD `.docx` in `/scratch/work/p2w/out`:

| document | pairs | dy(origin) med / max | dy(bbox top) med | dy(ascent) med |
|:--|--:|:--|:--|:--|
| `31_times_body_arial_headings` | 29 | **+0.07** / 0.96 | **+2.70** | **−2.66** |
| `16_right_aligned_amounts_txtpos` | 64 | **+0.00** / 0.01 | **+0.82** | **−0.82** |
| `320_balance_sheet_statutory` | 68 | +0.35 / 0.75 | +0.05 | +0.30 |

The faces, by size, median ascent in points (same run):

| document | source face @ size | source ascent | built face @ size | built ascent |
|:--|:--|--:|:--|--:|
| `31_times` | `Helvetica-Bold@12` | 12.84 | `LiberationSans-Bold@12` | 9.60 |
| `31_times` | `Times-Roman@10.5` | 11.06 | `LiberationSerif@10.5` | 8.40 |
| `16_right` | `Liberation Sans Bold@12` | 10.86 | `LiberationSans-Bold@12` | 9.60 |
| `320_balance` | `DejaVuSans@7` | 5.32 | `DejaVuSans@7` | 5.60 |

The third row is the control that matters: when the source and the built document carry the **same face**,
`dy(top)` and `dy(origin)` agree to 0.3 pt. On `31_times` the source's embedded Helvetica reports an ascent of
**1.07 em** and the built Arial (rendered as Liberation Sans by this proxy) reports **0.80 em**; 0.27 em at
10.5 pt is 2.8 pt, and that is the +2.70 pt the check charges. On `16_right` the same mechanism is worth
0.82 pt because the source face and the built face differ only in name.

## 4. The two engine changes that were built and refuted

Both in `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, both measured with
`verify_google.py` on the LibreOffice proxy, both reverted (tree at HEAD):

| change | `31_times` | `16_right` | `320_balance` | `306_clinical_protocol_synopsis` |
|:--|:--|:--|:--|:--|
| HEAD | med_dy +2.7 | +0.8 | +0.0 | −4.6 |
| hairline floor at the 0.312 em fixed point (`hairlinePt()` `:4148`) | +2.6 | unchanged | unchanged | unchanged |
| `beforeTw -= 0.253·size·20` on every flowed line (`:4642`) | **−21.3**, breaks 23_line_pitch | **+9.2 worst**, fails 18 | **+7.2 worst**, fails 18 | worse |
| same, gated to the first line of a page | −0.4 | +0.8 | **+3.2 worst** | unchanged |

**Nothing was kept.** A one-paragraph probe (six exact box heights 0.65-20 pt at 10.5 pt type) put the
baseline at `0.769, 0.800, 0.805, 0.800, 0.800, 0.800` of the box — `LINE_BASE = 0.8` is correct as a
baseline model, including at a hairline box, so the "0.050 em" in the premise was a misreading of the same
quantity on the other side.

## 5. What this means for the goal, and the next measurement

* **`18_displacement` cannot be cleared by geometry on a document whose baselines already match.** On
  `31_times` the built baselines are within 0.07 pt median of the source; the check still charges 2.70 pt.
  The only engine-side lever is the declared face: the built `.docx` already says `Arial` / `Times New Roman`
  (26 + 3 `w:rFonts` runs on `31_times`), which is the faithful choice, and the source's embedded Helvetica
  is the outlier at 1.07 em ascent. There is no face to declare that would match it and stay faithful.
* **The instrument-side question is open and is the next run's job.** `verify_google.py` already computes
  `ox, oy` (the baseline origin, `:264`) and its own comment argues the baseline is the point that transforms
  exactly. Recomputing check 18 on origins instead of bbox tops would not change a single document that is
  genuinely displaced, and would drop the charge on documents like `31_times` and `16_right`. **Nobody should
  flip that without measuring how many verdicts move in each direction** — that count, on the corpus, is the
  experiment to run, and it is a change to the truth instrument, not a pass to be taken.
* **`18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md` should not be read as a work queue any more.** Its
  0.312 em figure is the ascent difference between two faces, not a placement deficit.

## 6. Not done, and why

* `regress.py --check` was not completed on this pod (it exceeded a 280 s call). Nothing in `app/` is
  modified, so the tree is the one the gate was installed against — but that is an inference, not a
  measurement, and it is recorded as one.
* No Google render: the platform `upload` tool was not reachable from the sub-agent's session, so every
  per-span number above is **LibreOffice proxy**. The claim does not depend on which renderer is used —
  `dy` is computed the same way on both — but it was not confirmed in Google.
* No second sub-agent was deployed this run. The first one ran inline and returned after 29 minutes of a
  90-minute slot; a second inline agent would have cost the report. Recorded here rather than papered over.
