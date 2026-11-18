package com.kavopdf.app.engine;

import java.util.ArrayList;
import java.util.List;

/**
 * The order a reader takes the page's blocks in - decided once, on the document.
 *
 * <p><b>NOT IN THE SHIPPING PATH.</b> Two callers matter and neither calls this:
 * {@code ToolsActivity} (what the app runs) and {@code ConvertOne} (what {@code p2w.py} runs to
 * produce {@code benchmarks/RANKING.csv}) both go straight from {@code classifyHeadings} to a
 * writer. Only {@code ConvertAll} calls {@code apply}, and that class exists for the measurement
 * in {@code tools/p2w-bench/SECTOR19.md} and for {@code check-writer-independence.py}.
 *
 * <p>That is not a defect in the output, and the reason is in {@code DocxWriter.stampBox}: the
 * stamp is written as one anchored text box whose {@code wp:positionH} and {@code wp:positionV} are
 * both {@code relativeFrom="page"}. Its place in the block list decides which page it is attached
 * to, not where on that page it lands.
 *
 * <p>So the pass can only matter when the anchor's page and the stamp's page differ, which needs a
 * document longer than one page. In {@code benchmarks/RANKING.csv} every stamp document's score
 * equals its score in {@code RANKING-BASELINE.csv}, so nothing has needed it so far. <b>A
 * multi-page stamp document is the case to re-check</b> before trusting that: if one is added, or
 * if a stamp document's score ever moves, measure it with this pass on and off rather than
 * assuming.
 *
 * <p><b>DO NOT "FIX" THE SIDE EFFECT BY MOVING {@code DocxWriter.orderStamps} INTO THE DOCX
 * BRANCH.</b> There is no side effect to fix - this class is the only caller of that method, so
 * while it is not called, nothing is reordered. Moving the call into the branch would give the
 * .docx the relocation and withhold it from the .txt, and SECTOR19.md's §3 measurement H is
 * exactly that configuration: it changes the .txt. The .docx and the .txt would then disagree
 * about the order of the same page, which is the property SECTOR19 exists to hold.
 *
 * <p>If this pass is ever put into the shipping path, it must go into <b>both</b>
 * {@code ToolsActivity} and {@code ConvertOne} in the same change. Wiring one and not the other
 * makes {@code RANKING.csv} a measurement of something the app does not do.
 *
 * <p>SECTOR 19. The engine reads a stamp after the page's own words, because a stamp is an
 * overlay and not part of the page's grid. That is right for detecting a stamp and wrong for a
 * paragraph: a paragraph can only follow the paragraph before it, so a stamp line left at the end
 * of the block list lands below the last line of the page, 200 pt under its own frame. Putting it
 * where its own y falls is what lets {@code w:ind} and {@code w:before} do their job.
 *
 * <p>That placement is a READING-ORDER decision, and it used to be made inside
 * {@code DocxWriter.write}, on {@code page.blocks} itself. The .txt writer then walked the same
 * list, so the .txt described a page whose stamp paragraphs had been moved by the .docx writer -
 * and a .txt produced without the .docx write described the page the PDF drew. The same PDF gave
 * two different .txt files depending on call order, and no check could see it because every text
 * check pairs by text, and a reordering of lines pairs just as well one way as the other.
 *
 * <p>So the decision lives here, in the model, and it runs BEFORE either writer:
 *
 * <pre>
 *   Result r = PdfToWord.convert(pdf, "", null);
 *   PdfToWord.classifyHeadings(r);
 *   ReadingOrder.apply(r);                 // one order, for every consumer
 *   DocxWriter.write(r, docx);             // reads it
 *   PdfToWord.writeTxt(r, txt);            // reads the same order
 * </pre>
 *
 * <p>Both writers are then functions of the document, and the order is the one the engine
 * intends rather than a side effect of which writer ran first. The measurement behind keeping
 * this pass rather than dropping the relocation: see {@code tools/p2w-bench/SECTOR19.md} - with
 * the pass, the .txt is byte-identical to what the shipped pipeline produced (docx first) on all
 * 211 documents; without it, 11 documents' .txt files change order, and the .txt checks score
 * them identically either way, so nothing would have told us.
 *
 * <p>It is idempotent: a page whose stamps are already at their y has nothing to move, because
 * each stamp is removed and re-inserted at the index its own top falls at, which is where it
 * already is.
 */
public final class ReadingOrder {

    private ReadingOrder() {
    }

    /** Puts each page's stamp lines where their own y falls. One pass, before any writer. */
    public static void apply(PdfToWord.Result result) {
        if (result == null || result.pages == null) return;
        for (PdfToWord.Page page : result.pages) {
            if (page == null || page.blocks == null || page.blocks.isEmpty()) continue;
            List<DocxWriter.Shape> outlines = new ArrayList<>();
            for (Object b : page.blocks) {
                if (b instanceof DocxWriter.Shape) outlines.add((DocxWriter.Shape) b);
            }
            if (outlines.isEmpty()) continue;
            // A stamp's frame is drawn as one geometry before the placement asks which frame a
            // line sits in - the same order the writer used, so the answer is the same answer.
            DocxWriter.stampFrames(outlines);
            DocxWriter.orderStamps(page, outlines);
        }
    }
}
