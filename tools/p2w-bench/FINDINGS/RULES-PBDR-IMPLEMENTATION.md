# The rule fix: exact implementation, ready to land

Follows `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` (the cause) and `RULES-PBDR-FIX-MEASURED.md` (the
first attempt, which drew the rules but put them in the wrong place).

## The numbers this is worth

From `benchmarks/DEFECT-CLASSES-GOOGLE.md`, 84 documents with both renders:

    32_stroke_lines    LO 0    Google 53    gap 53
    05_chars_extra     LO 6    Google 54    gap 48

LibreOffice fails `32_stroke_lines` on **zero** documents. Google fails it on 53. **These are one
construct and they are the largest block in the corpus.**

## Why the first attempt failed, exactly

`ruleAsBorder()` emitted a `w:pBdr` paragraph with `w:before="0"` and `w:line="1" exact`. Google drew
both rules — the construct is right — but **both landed at the foot of the page** (y 807 and 808) when
one belongs at the head (y 793) and one mid-page.

A paragraph border is placed by **flow**. This engine positions everything absolutely and carries the
gap between blocks in `w:spacing w:before`, which the first attempt set to zero. So the border fell
wherever the preceding paragraph ended, not at the rule's y.

## The field that fixes it

`DocxWriter.Ctx` already carries the reader's position:

    /** Where the READER will put the last baseline emitted, in points from the page top. */
    float flowY = -1f;      // -1 means unknown - first line of a sheet, or a new column
    /** The height of the last line box AS WRITTEN, in points. */
    float flowBoxPt = 0f;
    boolean newPage = true;

`flowY` is not `lastBaseline`: it is where the page *ends up* after rounding, the clamped gap and the
shortened box, and the existing code already measures every paragraph's space-before from it. **The
border must be measured from the same place.**

## The implementation

In `shape(StringBuilder sb, Shape s, Ctx ctx)`, before the drawing path:

    private static boolean ruleAsBorder(StringBuilder sb, Shape s, Ctx ctx) {
        if (!isHairline(s)) return false;
        if (Math.abs(s.hPt) > Math.abs(s.wPt)) return false;   // vertical rules are not pBdr bottom
        int rgb = s.lineRgb >= 0 ? s.lineRgb : s.fillRgb;
        if (rgb < 0) return false;

        // THE GAP FROM THE LAST FLOWING LINE TO THIS RULE, in twips. This is the line the first
        // attempt left out, and without it the border is placed by flow from the previous
        // paragraph's end instead of at the y the page drew.
        int beforeTw = 0;
        if (!ctx.newPage && ctx.flowY >= 0 && s.topPt > ctx.flowY) {
            float below = ctx.flowBoxPt * (1f - LINE_BASE);     // what is left under the baseline
            beforeTw = Math.max(0, Math.round((s.topPt - ctx.flowY - below) * TWIPS_PER_PT));
        }

        int szEighth = (int) Math.max(2L, Math.round(s.lineWidthPt * 8f));
        int leftTw  = (int) Math.max(0L, Math.round(s.xPt * TWIPS_PER_PT));
        int rightTw = (int) Math.max(0L,
                Math.round((ctx.pageWidthPt - (s.xPt + s.wPt)) * TWIPS_PER_PT));

        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
          .append("<w:pBdr><w:bottom w:val=\"single\" w:sz=\"").append(szEighth)
          .append("\" w:space=\"0\" w:color=\"").append(hex(rgb)).append("\"/></w:pBdr>")
          .append("<w:ind w:left=\"").append(leftTw).append("\" w:right=\"").append(rightTw)
          .append("\" w:firstLine=\"0\"/>")
          .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
          .append(" w:before=\"").append(beforeTw)
          .append("\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
          .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
          .append("<w:r><w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr>")
          .append("<w:t xml:space=\"preserve\"> </w:t></w:r></w:p>");

        // The border IS the flow's new position: the reader is now at the rule's y, and the next
        // paragraph's space-before must be measured from here or every line below it drifts.
        ctx.flowY = s.topPt;
        ctx.flowBoxPt = 0f;
        ctx.newPage = false;
        return true;
    }

and at the top of `shape()`:

    if (ruleAsBorder(sb, s, ctx)) return;

**The `ctx.flowY = s.topPt` line is the part that is easy to forget and expensive to omit.** Without
it the next paragraph measures its gap from the line above the rule, and every line below the rule on
that page moves up by the rule's gap. That is a `18_displacement` regression on every document with a
rule — the second-largest class, made worse by the fix for the largest.

## How to prove it before landing

    1. build                          bash tools/p2w-bench/build-engine.sh
    2. convert one document           ConvertAll on 18_centred_heading_left_body_txtpos
    3. put it through Google          upload -> CREATE_FILE (Google Doc mime) -> DOWNLOAD_FILE(pdf)
                                      -> gverify.py --collect <name> <s3url>
    4. read the two numbers           `32_stroke_lines` must go from lost to not-lost, and
                                      `18_displacement` must NOT get worse

On 19 Nov the first attempt gave `rules drawn 0 -> 2, lost 2 -> 1`. **With `w:before` the lost count
should reach 0 and the positions should match the page's y.** If it does not, the gap formula is wrong
and the `flowBoxPt` term is the first thing to check.

    5. only then the gate             python3 tools/p2w-bench/regress.py --check

**The gate needs the whole corpus re-measured** — 213 renders, nine sandbox calls. It will not fit in
one run; `verify-change.py` measures only the documents the change moved, and the brief says how to
carry a partial measurement across calls.

## If it regresses

`18_displacement` going up means the `flowY` update is missing or the `flowBoxPt` term is wrong. Revert
and record it here. **A fix for the largest class that makes the second-largest worse is not a fix.**

## What this does not touch

The two rules that were still wrong after the first attempt sat at y=797 on a footer. That is the same
construct and the same code path, so it should be fixed by the same change — but check a document with
a header *and* a footer rule, not just one.
