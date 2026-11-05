package com.kavopdf.app.engine;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Writes a {@link PdfToWord.Result} as a real .docx - a ZIP of OOXML parts, built here rather
 * than pulled from a library.
 *
 * <p>Two reasons for hand-writing it: a Word library is 12 MB of the APK for one feature, and
 * the output is a handful of XML documents that Word, LibreOffice and Google Docs all read.
 *
 * <p><b>Where the text sits.</b> A .docx has no page grid of its own: a paragraph is placed by
 * the flow, and the only horizontal control a flowing paragraph has is {@code w:ind}. That is
 * why a value set at x=300 pt in the PDF used to arrive at "indent 4" - the paragraph was
 * pinned to the left margin and nudged. Every paragraph here is therefore a floating shape:
 * a {@code wp:anchor} whose {@code positionH}/{@code positionV} are taken straight from the
 * page, {@code relativeFrom="page"}, in EMU (1 pt = 12700 EMU), with the page section set to
 * the PDF's own page box and zero margins, so the anchor offset IS the PDF x.
 *
 * <p>Inside the anchor the text is ordinary WordprocessingML in {@code w:txbxContent} - real
 * characters in real runs with their real {@code rPr}, so the result is selectable, searchable
 * and editable, not a picture of a page. (A {@code a:txBody} would be DrawingML text, which
 * carries {@code a:rPr}, not {@code w:rPr}: bold, italic, size, typeface and colour would all
 * be lost, and Word would not open the shape as a text box at all.)
 *
 * <p>Tables stay tables: a {@code w:tbl} with {@code w:tr}/{@code w:tc} cells, anchored at the
 * table's own top-left corner.
 */
public final class DocxWriter {

    private static final String NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
    private static final String NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships";
    private static final String NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing";
    private static final String NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main";
    private static final String NS_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture";
    private static final String NS_WPS =
            "http://schemas.microsoft.com/office/word/2010/wordprocessingShape";

    /** 1 point in EMU, for wp:posOffset and wp:extent. */
    private static final double EMU_PER_PT = 12700.0;
    /** 1 point in twips, for every w:* length. */
    private static final double TWIPS_PER_PT = 20.0;

    /**
     * Distance from the top of a text box to the baseline of its first line, as a fraction of
     * the font size.
     *
     * <p>A text box positions its top edge, not its baseline, and a PDF gives a baseline. The
     * gap is the face's ascent, but with {@code w:lineRule="exact"} the renderer puts the
     * baseline at the bottom of the line box instead: measured over 377 words of two files,
     * the rendered baseline sat 0.268 * size below where it was asked to be, so the box has to
     * be lifted by 0.90 + 0.27 = 1.17 em. That is the LibreOffice figure; Word's exact-line
     * model puts the baseline a shade higher, so expect the Word baseline within about 1 pt of
     * the PDF's.
     */
    private static final float ASCENT = 1.17f;
    /** docPr ids for shapes start above the picture ids so the two never collide. */
    private static final int SHAPE_ID_BASE = 100000;
    /** Line box height as a multiple of the font size. Generous: a tight exact height clips. */
    private static final float LINE_FACTOR = 1.30f;

    private DocxWriter() {
    }

    public static void write(PdfToWord.Result result, File out) throws IOException {
        Ctx ctx = new Ctx();
        String documentXml = documentXml(result, ctx);
        String rels = documentRels(ctx.media);
        String contentTypes = contentTypes(ctx.media.size());

        try (OutputStream fos = new FileOutputStream(out);
             ZipOutputStream zip = new ZipOutputStream(fos)) {
            put(zip, "[Content_Types].xml", contentTypes);
            put(zip, "_rels/.rels", rootRels());
            put(zip, "word/document.xml", documentXml);
            put(zip, "word/styles.xml", stylesXml());
            put(zip, "word/_rels/document.xml.rels", rels);
            put(zip, "docProps/core.xml", coreXml(result));
            put(zip, "docProps/app.xml", appXml());
            for (int i = 0; i < ctx.media.size(); i++) {
                zip.putNextEntry(new ZipEntry("word/media/image" + (i + 1) + ".png"));
                zip.write(ctx.media.get(i));
                zip.closeEntry();
            }
        }
    }

    private static void put(ZipOutputStream zip, String name, String body) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    /** Mutable state for one write: the shape id counter and the images collected. */
    private static final class Ctx {
        final List<byte[]> media = new ArrayList<>();
        int shapeSeq = 1;
        int anchorCount;
        int flowCount;
    }

    // ------------------------------------------------------------------ document

    private static String documentXml(PdfToWord.Result result, Ctx ctx) {
        StringBuilder sb = new StringBuilder(1 << 18);
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        sb.append("<w:document xmlns:w=\"").append(NS_W).append("\" xmlns:r=\"").append(NS_R)
                .append("\" xmlns:wp=\"").append(NS_WP).append("\" xmlns:a=\"").append(NS_A)
                .append("\" xmlns:wps=\"").append(NS_WPS)
                .append("\" xmlns:pic=\"").append(NS_PIC).append("\"><w:body>");

        // The page box the current section is set to. A section carries one page size, so a
        // file that mixes landscape and portrait pages gets a section break where the size
        // changes; every other page break stays a plain page break.
        float secW = 0, secH = 0;
        boolean first = true;
        for (PdfToWord.Page page : result.pages) {
            float pw = page.width > 0 ? page.width : 595f;
            float ph = page.height > 0 ? page.height : 842f;
            if (first) {
                secW = pw;
                secH = ph;
                first = false;
            } else if (Math.abs(pw - secW) > 0.5f || Math.abs(ph - secH) > 0.5f) {
                // Close the section that just ended. A sectPr lives in the last paragraph of
                // its section, and nextPage starts the new one on a fresh page - which is the
                // page break this page needed anyway.
                sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                        .append("<w:sectPr>").append(sectPrXml(secW, secH))
                        .append("<w:type w:val=\"nextPage\"/></w:sectPr>")
                        .append("</w:pPr></w:p>");
                secW = pw;
                secH = ph;
            } else {
                // A page with nothing on it still has to advance the page counter, or every
                // anchor after it lands one page too early.
                sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                        .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr>")
                        .append("<w:r><w:br w:type=\"page\"/></w:r></w:p>");
            }
            if (page.blocks.isEmpty()) continue;
            for (Object block : page.blocks) {
                if (block instanceof PdfToWord.Para) {
                    para(sb, (PdfToWord.Para) block, ctx);
                } else if (block instanceof PdfToWord.Table) {
                    table(sb, (PdfToWord.Table) block);
                } else if (block instanceof Picture) {
                    picture(sb, (Picture) block, ctx);
                } else if (block instanceof Shape) {
                    shape(sb, (Shape) block, ctx);
                }
            }
        }
        // The section properties must be the LAST child of w:body.
        sb.append("<w:sectPr>").append(sectPrXml(secW <= 0 ? 595f : secW, secH <= 0 ? 842f : secH))
                .append("</w:sectPr>");
        sb.append("</w:body></w:document>");
        return sb.toString();
    }

    /**
     * A page the size of the PDF page, with no margins.
     *
     * <p>Zero margins are not cosmetic: they make the page box and the text box the same
     * coordinate system, so a paragraph anchored {@code relativeFrom="page"} at 300 pt is at
     * 300 pt from the edge of the paper and from the start of the text area alike.
     */
    private static String sectPrXml(float wPt, float hPt) {
        int w = Math.max(1, Math.round((float) (wPt * TWIPS_PER_PT)));
        int h = Math.max(1, Math.round((float) (hPt * TWIPS_PER_PT)));
        String orient = wPt > hPt ? " w:orient=\"landscape\"" : "";
        return "<w:pgSz w:w=\"" + w + "\" w:h=\"" + h + "\"" + orient + "/>"
                + "<w:pgMar w:top=\"0\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""
                + " w:header=\"0\" w:footer=\"0\" w:gutter=\"0\"/>"
                + "<w:cols w:space=\"0\"/>"
                + "<w:docGrid w:linePitch=\"360\"/>";
    }

    /** An image lifted out of the PDF and placed where it was. */
    public static final class Picture {
        public final byte[] png;
        public final int widthEmu;
        public final int heightEmu;
        public float top;
        public int column;
        /**
         * Where the image sat on its page, in points from the page's top-left.
         *
         * <p>An image the PDF drew is not part of the text flow - it is pinned to a place on
         * the paper. {@link #placed} says the position is known, and then the writer pins the
         * picture there instead of dropping it into the flow at the end of the page.
         */
        public boolean placed;
        public float xPt, topPt, wPt, hPt;

        public Picture(byte[] png, int widthEmu, int heightEmu) {
            this.png = png;
            this.widthEmu = widthEmu;
            this.heightEmu = heightEmu;
        }

        public Picture(byte[] png, float xPt, float topPt, float wPt, float hPt) {
            this.png = png;
            this.xPt = xPt;
            this.topPt = topPt;
            this.wPt = wPt;
            this.hPt = hPt;
            this.placed = true;
            this.widthEmu = (int) Math.max(1L, Math.round(wPt * EMU_PER_PT));
            this.heightEmu = (int) Math.max(1L, Math.round(hPt * EMU_PER_PT));
        }
    }

    private static void picture(StringBuilder sb, Picture p, Ctx ctx) {
        ctx.media.add(p.png);
        int id = ctx.media.size();
        if (p.placed) {
            anchoredPicture(sb, p, id, ctx);
            return;
        }
        sb.append("<w:p><w:r><w:drawing><wp:inline distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\">")
                .append("<wp:extent cx=\"").append(p.widthEmu).append("\" cy=\"")
                .append(p.heightEmu).append("\"/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Picture ").append(id)
                .append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"")
                .append("http://schemas.openxmlformats.org/drawingml/2006/picture\">")
                .append("<pic:pic><pic:nvPicPr><pic:cNvPr id=\"").append(id)
                .append("\" name=\"image").append(id).append(".png\"/><pic:cNvPicPr/></pic:nvPicPr>")
                .append("<pic:blipFill><a:blip r:embed=\"rIdImg").append(id)
                .append("\"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>")
                .append("<pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"")
                .append(p.widthEmu).append("\" cy=\"").append(p.heightEmu).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>")
                .append("</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>");
    }

    /**
     * An image pinned to the page at the place the PDF drew it.
     *
     * <p>{@code behindDoc="1"} puts it behind the text: a scan is the page's background and a
     * stamp image is a mark on top of a page whose words are already there as text boxes. A
     * picture in front of them would hide words, which is worse than the picture being under
     * a stamp that does not overlap it.
     */
    private static void anchoredPicture(StringBuilder sb, Picture p, int id, Ctx ctx) {
        long cx = Math.max(1, p.widthEmu);
        long cy = Math.max(1, p.heightEmu);
        long offX = Math.round(p.xPt * EMU_PER_PT);
        long offY = Math.round(p.topPt * EMU_PER_PT);
        int relHeight = 251658240 + (id & 0xFFFF);
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Picture ").append(id)
                .append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"")
                .append("http://schemas.openxmlformats.org/drawingml/2006/picture\">")
                .append("<pic:pic><pic:nvPicPr><pic:cNvPr id=\"").append(id)
                .append("\" name=\"image").append(id).append(".png\"/><pic:cNvPicPr/></pic:nvPicPr>")
                .append("<pic:blipFill><a:blip r:embed=\"rIdImg").append(id)
                .append("\"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>")
                .append("<pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"")
                .append(cx).append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>")
                .append("</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>");
    }

    // ------------------------------------------------------------------ shapes

    /**
     * A rectangle the page paints: a masthead band, a coloured block, a table header strip,
     * a sidebar box, a drawn rule, a page border.
     *
     * <p>Nothing used to carry these, so a document whose own name is white text on a navy
     * band converted to white text on white paper - the words were there and could not be
     * seen. The geometry is the path's own bounding box in points from the page's top-left;
     * {@code fillRgb} is -1 for an outline only and {@code lineRgb} is -1 for a fill only.
     */
    public static final class Shape {
        public float xPt, topPt, wPt, hPt;
        /** Fill colour 0xRRGGBB, or -1 when the path is only stroked. */
        public int fillRgb = -1;
        /** Fill opacity 0..1, from the PDF's own {@code ca}. */
        public float fillAlpha = 1f;
        /** Outline colour 0xRRGGBB, or -1 when the path is only filled. */
        public int lineRgb = -1;
        public float lineWidthPt;

        public Shape(float xPt, float topPt, float wPt, float hPt) {
            this.xPt = xPt;
            this.topPt = topPt;
            this.wPt = wPt;
            this.hPt = hPt;
        }
    }

    private static String hex(int rgb) {
        String h = Integer.toHexString(rgb & 0xFFFFFF).toUpperCase(java.util.Locale.ROOT);
        while (h.length() < 6) h = "0" + h;
        return h;
    }

    /**
     * A shape pinned to the page, behind the text.
     *
     * <p>{@code behindDoc="1"} is what makes a masthead band a background instead of a lid:
     * the band carries white words, and a shape in front of them would hide the very title
     * it exists to make visible. A rule drawn behind text is still a rule.
     */
    private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
        int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
        long cx = Math.max(1, Math.round(s.wPt * EMU_PER_PT));
        long cy = Math.max(1, Math.round(s.hPt * EMU_PER_PT));
        long offX = Math.round(s.xPt * EMU_PER_PT);
        long offY = Math.round(s.topPt * EMU_PER_PT);
        int relHeight = 100000000 + (id & 0xFFFF);
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Shape ").append(id)
                .append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"").append(NS_WPS).append("\">")
                .append("<wps:wsp><wps:cNvSpPr/><wps:spPr>")
                .append("<a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"").append(cx)
                .append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>");
        if (s.fillRgb >= 0) {
            sb.append("<a:solidFill><a:srgbClr val=\"").append(hex(s.fillRgb)).append("\">");
            if (s.fillAlpha < 0.999f) {
                int a = Math.max(0, Math.min(100000, Math.round(s.fillAlpha * 100000f)));
                sb.append("<a:alpha val=\"").append(a).append("\"/>");
            }
            sb.append("</a:srgbClr></a:solidFill>");
        } else {
            sb.append("<a:noFill/>");
        }
        if (s.lineRgb >= 0) {
            long lw = Math.max(0, Math.round(s.lineWidthPt * EMU_PER_PT));
            sb.append("<a:ln w=\"").append(lw).append("\"><a:solidFill><a:srgbClr val=\"")
                    .append(hex(s.lineRgb)).append("\"/></a:solidFill></a:ln>");
        } else {
            sb.append("<a:ln><a:noFill/></a:ln>");
        }
        sb.append("</wps:spPr><wps:bodyPr anchor=\"t\" anchorCtr=\"0\"><a:noAutofit/></wps:bodyPr>")
                .append("</wps:wsp></a:graphicData></a:graphic>")
                .append("</wp:anchor></w:drawing></w:r></w:p>");
    }

    // ------------------------------------------------------------------ paragraphs

    /**
     * One paragraph. Every line the PDF drew becomes its own anchored text box at its own
     * x and y - a paragraph in the PDF is a group of lines, but the lines are not at one x,
     * and it is the x of each line that the reader sees.
     */
    private static void para(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        if (!p.boxes.isEmpty()) {
            for (PdfToWord.Box b : p.boxes) {
                if (b.runs.isEmpty()) continue;
                StringBuilder inner = new StringBuilder(256);
                lineParagraph(inner, p, b);
                // How wide the box has to be to hold the line unwrapped.
                //
                // A rotated line is measured along its own baseline, not across the page: on
                // the 90-degree stamp b.right-b.x is the height of the text, so "31-03-2026"
                // was given a 22 pt box, wrapped, and reached Word as "31-". The other lines
                // get 12 % of slack, because the page's advance is measured in the font the
                // PDF embedded and the same string set in the substituted face is a few per
                // cent wider - enough to wrap the last word and clip it.
                float advance = b.rotated && b.length > 0f ? b.length : b.right - b.x;
                // The page's own advance is not always there to be trusted. A line whose glyphs
                // all report zero width measures 0 pt wide, the 4 pt floor below then wins, and
                // the box clips everything after the first character or two: file 69's clause
                // "8. The job worker shall carry out the processes of desizing," reached Word as
                // a 19 pt box holding 60 characters, and the render showed "8. " and nothing
                // else. When the measured advance is less than half what the characters need at
                // their own size, the measurement is the broken thing, so the character count
                // decides the width instead.
                int chars = 0;
                for (PdfToWord.Run r : b.runs) chars += r.text.length();
                float needed = chars * b.size * 0.5f;
                if (advance < needed * 0.6f) advance = needed;
                float wPt = b.rotated && b.length > 0f
                        ? Math.max(b.length, advance) + b.size * 1.5f
                        : Math.max(4f, advance) * 1.12f + b.size * 1.5f;
                float hPt = Math.max(4f, b.size * LINE_FACTOR);
                anchor(sb, ctx, b.x, b.y - ASCENT * b.size, wPt, hPt, inner.toString());
            }
            return;
        }
        // No page coordinates: an OCR block, an annotation, a filled form value. There is no
        // x to restore, so it goes into the flow rather than pretending to a position.
        flowParagraph(sb, p, ctx);
    }

    /** One drawn line, as the single paragraph inside its own text box. */
    private static void lineParagraph(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b) {
        int lineTw = Math.max(1, Math.round((float) (Math.max(4f, b.size * LINE_FACTOR) * TWIPS_PER_PT)));
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"").append(lineTw)
                .append("\" w:lineRule=\"exact\"/>")
                // The anchor already put this line at its x; an indent here would move it off.
                .append("<w:ind w:left=\"0\" w:right=\"0\" w:firstLine=\"0\"/>");
        int half = Math.round(b.size * 2f);
        if (half > 0) {
            sb.append("<w:rPr><w:sz w:val=\"").append(Math.min(3276, Math.max(2, half)))
                    .append("\"/></w:rPr>");
        }
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : b.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    /** A paragraph with no page coordinates of its own: the old flowing behaviour. */
    private static void flowParagraph(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        String text = p.text();
        if (text.trim().isEmpty()) return;
        ctx.flowCount++;
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>");
        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
        if (p.indent > 0) {
            sb.append("<w:ind w:left=\"").append(p.indent * 420).append("\"/>");
        }
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : p.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    /** One run with the properties the PDF drew it with. */
    private static void runXml(StringBuilder sb, PdfToWord.Run run) {
        sb.append("<w:r><w:rPr>");
        // The typeface and colour the PDF used. Without these every document came out in
        // the default font in black, and "the Word file should look like the PDF" had no
        // way to be measured - both benchmarks read 0 %.
        if (run.font != null && !run.font.isEmpty()) {
            String face = esc(faceName(run.font));
            sb.append("<w:rFonts w:ascii=\"").append(face)
                    .append("\" w:hAnsi=\"").append(face)
                    .append("\" w:cs=\"").append(face).append("\"/>");
        }
        if (run.color >= 0) {
            sb.append(String.format("<w:color w:val=\"%06X\"/>", run.color & 0xFFFFFF));
        }
        if (run.bold) sb.append("<w:b/>");
        if (run.italic) sb.append("<w:i/>");
        int half = Math.round(run.sizePt * 2f);
        if (half > 0) {
            sb.append("<w:sz w:val=\"").append(Math.min(3276, Math.max(2, half))).append("\"/>");
            sb.append("<w:szCs w:val=\"").append(Math.min(3276, Math.max(2, half)))
                    .append("\"/>");
        }
        sb.append("</w:rPr><w:t xml:space=\"preserve\">").append(esc(run.text))
                .append("</w:t></w:r>");
    }

    // ------------------------------------------------------------------ the anchor

    /**
     * Wraps a block of WordprocessingML in a floating text box at (xPt, yTopPt).
     *
     * <p>The child order of {@code wp:anchor} is fixed by the schema - simplePos, positionH,
     * positionV, extent, effectExtent, wrap*, docPr, cNvGraphicFramePr, graphic - and Word
     * refuses the whole file if it is wrong, so it is written in one place, in order.
     */
    private static void anchor(StringBuilder sb, Ctx ctx, float xPt, float yTopPt,
                               float wPt, float hPt, String inner) {
        int id = ctx.shapeSeq++;
        long cx = Math.max(1, Math.round(wPt * EMU_PER_PT));
        long cy = Math.max(1, Math.round(hPt * EMU_PER_PT));
        long offX = Math.round(xPt * EMU_PER_PT);
        long offY = Math.round(yTopPt * EMU_PER_PT);
        int relHeight = 251658240 + (id & 0xFFFF);

        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"0\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"KavoPDF text ")
                .append(id).append("\"/>")
                .append("<wp:cNvGraphicFramePr/>")
                .append("<a:graphic><a:graphicData uri=\"").append(NS_WPS).append("\">")
                .append("<wps:wsp><wps:cNvSpPr txBox=\"1\"/>")
                .append("<wps:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"").append(cx)
                .append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>")
                .append("<a:noFill/><a:ln><a:noFill/></a:ln></wps:spPr>")
                .append("<wps:txbx><w:txbxContent>").append(inner).append("</w:txbxContent></wps:txbx>")
                // wrap="none": the box must not re-wrap the line it holds, or a long line
                // would break at the box width and the second half would land under the first.
                .append("<wps:bodyPr wrap=\"none\" lIns=\"0\" tIns=\"0\" rIns=\"0\" bIns=\"0\"")
                .append(" anchor=\"t\" anchorCtr=\"0\"><a:noAutofit/></wps:bodyPr>")
                .append("</wps:wsp></a:graphicData></a:graphic>")
                .append("</wp:anchor></w:drawing></w:r></w:p>");
        ctx.anchorCount++;
    }

    // ------------------------------------------------------------------ tables

    /**
     * A table stays a table: {@code w:tbl} with real rows and cells, inside a text box so it
     * keeps the position it had on the page. Turning the cells into loose text boxes would
     * place the text and destroy the table, which is the one thing a conversion must not do.
     */
    private static void table(StringBuilder sb, PdfToWord.Table t) {
        int cols = 0;
        for (List<String> row : t.rows) cols = Math.max(cols, row.size());
        if (cols == 0) return;
        // The column edges the page actually used, when the pass that found the table knew
        // them. Even columns put a right-aligned figure 60 pt from where the reader saw it.
        int[] colTw = new int[cols];
        float x0 = t.left;
        boolean exact = t.colX != null && t.colX.length == cols + 1;
        if (exact) {
            x0 = t.colX[0];
            for (int c = 0; c < cols; c++) {
                colTw[c] = Math.max(1, Math.round((float) ((t.colX[c + 1] - t.colX[c])
                        * TWIPS_PER_PT)));
            }
        } else {
            float wPt = Math.max(40f, t.right - t.left);
            int width = Math.max(1, Math.round((float) (wPt * TWIPS_PER_PT / cols)));
            for (int c = 0; c < cols; c++) colTw[c] = width;
        }
        // A cell whose text is exactly as wide as its column still wraps: the page drew
        // "58,750.00" flush against the right border of a 49.5 pt column and the renderer put
        // the last digit on the next line. There is no empty cell to the right of the LAST
        // column to widen over, so that column gets the room its own text needs. The text is
        // anchored at its indent, not at the right border, so widening the column moves the
        // table's right rule and leaves the words where the page put them.
        if (exact && cols > 0) {
            long[] edges = new long[cols + 1];
            for (int c = 0; c < cols; c++) edges[c + 1] = edges[c] + colTw[c];
            int need = 0;
            for (int r = 0; r < t.rows.size(); r++) {
                float textR = cellRTw(t, r, cols - 1);
                if (Float.isNaN(textR)) continue;
                int inset = insetTw(t, r, cols - 1, x0, edges[cols - 1]);
                need = Math.max(need, inset + Math.round(textR) + 20);
            }
            if (need > colTw[cols - 1]) colTw[cols - 1] = need;
        }
        int totalTw = 0;
        for (int c = 0; c < cols; c++) totalTw += colTw[c];

        StringBuilder inner = new StringBuilder(512);
        // The table floats at its own page position - w:tblpPr takes page-relative
        // coordinates - instead of sitting inside a text box.
        //
        // A text box has a fixed height and clips what does not fit: on file 80 the box was
        // 44 pt tall, so of each dealer's six rows only the first two survived and the CIN,
        // IFSC and Address rows were gone from the document. Worse, the box is carried by a
        // wrapper paragraph, and that paragraph's own text is every cell of the table run
        // together with no separator - which is the "1.SUNRISE FASTENERS PVT LTDGSTIN
        // 29AABCS4821K1Z6..." a reader of the XML sees. A floating table is a table and
        // nothing else: one w:p per cell, no wrapper, no clip.
        inner.append("<w:tbl><w:tblPr>")
                .append("<w:tblpPr w:leftFromText=\"0\" w:rightFromText=\"0\"")
                .append(" w:topFromText=\"0\" w:bottomFromText=\"0\"")
                .append(" w:vertAnchor=\"page\" w:horzAnchor=\"page\"")
                .append(" w:tblpX=\"").append(tw(x0)).append("\"")
                .append(" w:tblpY=\"").append(tw(t.top)).append("\"/>")
                .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tblBorders>")
                .append("<w:top w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:left w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:bottom w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:right w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:insideH w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:insideV w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("</w:tblBorders>")
                .append("<w:tblLayout w:type=\"fixed\"/>")
                // Word's default cell margin is 0.19 cm (108 twips) on each side. Left at the
                // default, every cell's text sat 6 pt right of where the page had it - a
                // measured 120 twips of error on every cell in the batch.
                .append("<w:tblCellMar><w:top w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:left w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:right w:w=\"0\" w:type=\"dxa\"/></w:tblCellMar>")
                .append("</w:tblPr><w:tblGrid>");
        for (int c = 0; c < cols; c++) {
            inner.append("<w:gridCol w:w=\"").append(colTw[c]).append("\"/>");
        }
        inner.append("</w:tblGrid>");

        // The laid-out left edge of each cell, in twips from the table's own x0. Word stacks the
        // column widths it is given, so this - not t.colX - is where a cell's box really starts;
        // the two differ by the rounding of each width to a whole twip.
        long[] edgeTw = new long[cols + 1];
        for (int c = 0; c < cols; c++) edgeTw[c + 1] = edgeTw[c] + colTw[c];

        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            inner.append("<w:tr>");
            int c = 0;
            while (c < cols) {
                String cell = c < row.size() ? row.get(c) : "";
                String face = r < t.fonts.size() && c < t.fonts.get(r).size()
                        ? t.fonts.get(r).get(c) : "";
                // How far into its own box this cell's text was drawn. A cell's text does not
                // start at its border: the page padded it, centred it or right-aligned it, and
                // in a right-aligned column the distance changes row by row. Word's cell margin
                // is one number for the whole cell, so the offset goes on the paragraph, which
                // is per cell and is what w:ind means.
                int insetTw = insetTw(t, r, c, x0, edgeTw[c]);
                // A text that starts further right than its own cell is wide cannot be in that
                // cell alone: the page merged it with the columns to its right. The depot
                // report's "SCHEDULED" header begins 74 pt into a 66 pt column. Clamping the
                // indent to the column width puts the first letter at the right x and stacks the
                // rest one character per line - a vertical word. The cell is widened over the
                // empty cells beside it instead, which is what the page drew, and w:gridSpan is
                // how OOXML says it: no cell has to be split, and every later cell in the row
                // keeps its own left edge.
                // A cell is also too narrow when the words drawn in it are wider than the
                // cell is - the same merge, seen from the other side. File 80's dealer name
                // starts at the left edge of a 52 pt column and runs 176 pt, so it stayed in
                // that column and Word wrapped it as "SUNRISE / FASTENE / RS PVT / LTD".
                // The page never wrapped it; the cell is widened over the empty cells beside
                // it, and the line is left whole.
                float textR = cellRTw(t, r, c);
                int span = 1, spanTw = colTw[c];
                while (c + span < cols && cellAt(t, r, c + span).isEmpty()) {
                    boolean startsOutside = insetTw >= spanTw;
                    boolean tooWide = !Float.isNaN(textR) && insetTw + textR > spanTw;
                    if (!startsOutside && !tooWide) break;
                    spanTw += colTw[c + span];
                    span++;
                }
                if (insetTw > spanTw - 1) insetTw = Math.max(0, spanTw - 1);
                inner.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(spanTw)
                        .append("\" w:type=\"dxa\"/>");
                if (span > 1) inner.append("<w:gridSpan w:val=\"").append(span).append("\"/>");
                inner.append("</w:tcPr>")
                        .append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
                        .append("<w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"200\" w:lineRule=\"exact\"/>");
                if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
                inner.append("</w:pPr>");
                if (!cell.isEmpty()) {
                    inner.append("<w:r><w:rPr>");
                    // The size the page drew this cell at. The paragraph style carries one
                    // number for every table in the document - 10 pt - and the batch's tables
                    // are drawn at 7.5 to 12 pt, so without this every cell is set at a size
                    // the page never used. On file 22 the amounts are 8.5 pt: at the style's
                    // 10 pt they are 17.6 % too wide for their column and Word wraps
                    // "2,18,770.00" into "2,18,770.0" and "0".
                    float sz = r < t.sizes.size() && c < t.sizes.get(r).size()
                            ? t.sizes.get(r).get(c) : Float.NaN;
                    if (!Float.isNaN(sz) && sz > 0f) {
                        int half = Math.max(2, Math.round(sz * 2f));
                        inner.append("<w:sz w:val=\"").append(half)
                                .append("\"/><w:szCs w:val=\"").append(half).append("\"/>");
                    }
                    if (!face.isEmpty()) {
                        String f = esc(faceName(face));
                        inner.append("<w:rFonts w:ascii=\"").append(f)
                                .append("\" w:hAnsi=\"").append(f)
                                .append("\" w:cs=\"").append(f).append("\"/>");
                    }
                    // The colour the page drew this cell in. A cell is written as a string and
                    // a font name, so without this every coloured table - a grey label column,
                    // a navy header row - arrived in black.
                    if (r < t.colors.size() && c < t.colors.get(r).size()) {
                        int cellColor = t.colors.get(r).get(c);
                        if (cellColor >= 0) {
                            inner.append(String.format("<w:color w:val=\"%06X\"/>",
                                    cellColor & 0xFFFFFF));
                        }
                    }
                    if (r == 0 && t.header) inner.append("<w:b/>");
                    // A cell can hold two lines of the page: a numbered item's marker sits on
                    // its own line above the name, and the page drew them eight points apart.
                    // One w:t would flatten them into "1. SUNRISE" again.
                    inner.append("</w:rPr>");
                    String[] parts = cell.split("\n");
                    for (int q = 0; q < parts.length; q++) {
                        if (q > 0) inner.append("<w:br/>");
                        inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
                                .append("</w:t>");
                    }
                    inner.append("</w:r>");
                }
                inner.append("</w:p></w:tc>");
                c += span;
            }
            inner.append("</w:tr>");
        }
        inner.append("</w:tbl>");
        sb.append(inner);
        // A table must be followed by a paragraph of its own: Word inserts one if it is not
        // there, and a paragraph the writer did not place is a paragraph it cannot measure.
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
    }

    /** The text of cell (r, c), or "" when the row does not reach that far. */
    private static String cellAt(PdfToWord.Table t, int r, int c) {
        if (r >= t.rows.size()) return "";
        List<String> row = t.rows.get(r);
        if (c >= row.size()) return "";
        String s = row.get(c);
        return s == null ? "" : s;
    }

    /**
     * How wide this cell's text is, in twips: from where it starts to where the page stopped
     * drawing it. {@code Float.NaN} when the pass that built the table did not measure it.
     */
    private static float cellRTw(PdfToWord.Table t, int r, int c) {
        if (r >= t.cellR.size()) return Float.NaN;
        List<Float> rs = t.cellR.get(r);
        if (c >= rs.size()) return Float.NaN;
        Float right = rs.get(c);
        if (right == null || right.isNaN()) return Float.NaN;
        if (r >= t.cellX.size()) return Float.NaN;
        List<Float> xs = t.cellX.get(r);
        if (c >= xs.size()) return Float.NaN;
        Float left = xs.get(c);
        if (left == null || left.isNaN()) return Float.NaN;
        return (float) (Math.max(0f, right - left) * TWIPS_PER_PT);
    }

    /**
     * How far into the cell, in twips, this cell's text was drawn.
     *
     * <p>Zero when the page did not record where the text went, or when the glyphs put it left
     * of the cell's own left edge - in both cases the border is the safer answer.
     */
    private static int insetTw(PdfToWord.Table t, int r, int c, float x0, long edgeTw) {
        if (r >= t.cellX.size()) return 0;
        List<Float> xs = t.cellX.get(r);
        if (c >= xs.size()) return 0;
        Float textX = xs.get(c);
        if (textX == null || textX.isNaN()) return 0;
        double leftPt = x0 + edgeTw / TWIPS_PER_PT;
        int tw = (int) Math.round((textX - leftPt) * TWIPS_PER_PT);
        return Math.max(0, tw);
    }

    /**
     * The typeface name without the PDF's subset tag.
     *
     * <p>A PDF names a subset face "KLGWYD+Liberation Sans Bold", and the style is part of the
     * name rather than of the family. Written straight into {@code w:rFonts} it names a face no
     * machine has: fontconfig resolves "Liberation Serif Regular" and "Liberation Sans Bold" to
     * Noto Sans, a different face with different advances, and every word after the first drifts
     * along the line. Measured on file 51, word starts inside a line were up to 12.2 pt out
     * while the line start itself was 0.1 pt out. Dropping the subset tag and the style suffix
     * lets the family resolve to the face the PDF was drawn with; bold and italic are already
     * carried by {@code w:b} and {@code w:i}, so no styling is lost by removing them from the
     * name.
     */
    static String faceName(String font) {
        if (font == null) return "";
        String f = font;
        if (f.length() > 7 && f.charAt(6) == '+') {
            boolean tag = true;
            for (int i = 0; i < 6; i++) {
                char c = f.charAt(i);
                if (!(c >= 'A' && c <= 'Z')) { tag = false; break; }
            }
            if (tag) f = f.substring(7);
        }
        // The fourteen faces every PDF viewer must provide are named by their PostScript
        // names, and no word processor has a face called "Times-Roman": Word substitutes
        // Times New Roman and LibreOffice substitutes a wide default sans, so the line was
        // set in a different face from the one the PDF was drawn with. On file 31 that put
        // the closing note 60 pt wider than its box - and the box does not wrap, it clips -
        // so "…to the meeting." came out as "…to the ". Mapped, the same line renders at
        // 56.1-359.8 pt against the PDF's 56.0-360.2, whole. The three families here are
        // metrically identical to the PostScript originals, which is why the widths hold.
        String base = f;
        int dash = base.indexOf('-');
        if (dash > 0) base = base.substring(0, dash);
        String family = BASE14.get(base.toLowerCase(Locale.ROOT));
        if (family != null) return family;
        String[] suffixes = {" Bold Italic", " Bold Oblique", " Italic", " Oblique",
                " Bold", " Regular", " Roman", " Normal"};
        for (String suf : suffixes) {
            if (f.length() > suf.length() && f.endsWith(suf)) {
                return f.substring(0, f.length() - suf.length());
            }
        }
        return f;
    }

    /** PostScript's fourteen standard faces, keyed by family, to the family a Word file names. */
    private static final Map<String, String> BASE14 = new HashMap<>();

    static {
        BASE14.put("times", "Times New Roman");
        BASE14.put("helvetica", "Arial");
        BASE14.put("courier", "Courier New");
    }

    /** Points to whole twips, the unit every w:* length uses. */
    private static int tw(float pt) {
        return Math.max(0, Math.round((float) (pt * TWIPS_PER_PT)));
    }

    private static String esc(String s) {
        StringBuilder sb = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '&': sb.append("&amp;"); break;
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\'': sb.append("&apos;"); break;
                default:
                    // Control characters are not legal in XML 1.0 and make Word refuse the file.
                    if (c < 0x20 && c != '\t' && c != '\n' && c != '\r') sb.append(' ');
                    else sb.append(c);
            }
        }
        return sb.toString();
    }

    // ------------------------------------------------------------------ package parts

    private static String contentTypes(int images) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
                .append("<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">")
                .append("<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>")
                .append("<Default Extension=\"xml\" ContentType=\"application/xml\"/>")
                .append("<Default Extension=\"png\" ContentType=\"image/png\"/>")
                .append("<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>")
                .append("<Override PartName=\"/word/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml\"/>")
                .append("<Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>")
                .append("<Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>")
                .append("</Types>");
        return sb.toString();
    }

    private static String rootRels() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                + "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
                + "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" Target=\"docProps/core.xml\"/>"
                + "<Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" Target=\"docProps/app.xml\"/>"
                + "</Relationships>";
    }

    private static String documentRels(List<byte[]> media) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
                .append("<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">")
                .append("<Relationship Id=\"rIdStyles\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>");
        for (int i = 0; i < media.size(); i++) {
            sb.append("<Relationship Id=\"rIdImg").append(i + 1)
                    .append("\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\" Target=\"media/image")
                    .append(i + 1).append(".png\"/>");
        }
        sb.append("</Relationships>");
        return sb.toString();
    }

    private static String stylesXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<w:styles xmlns:w=\"" + NS_W + "\">"
                + "<w:docDefaults><w:rPrDefault><w:rPr>"
                + "<w:rFonts w:ascii=\"Calibri\" w:hAnsi=\"Calibri\" w:cs=\"Calibri\"/>"
                + "<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr></w:rPrDefault>"
                + "<w:pPrDefault><w:pPr><w:spacing w:after=\"120\"/></w:pPr></w:pPrDefault>"
                + "</w:docDefaults>"
                + "<w:style w:type=\"paragraph\" w:default=\"1\" w:styleId=\"Normal\">"
                + "<w:name w:val=\"Normal\"/></w:style>"
                + heading(1, 32, 1) + heading(2, 28, 2) + heading(3, 24, 3)
                + "<w:style w:type=\"paragraph\" w:styleId=\"TableText\">"
                + "<w:name w:val=\"Table Text\"/><w:basedOn w:val=\"Normal\"/>"
                + "<w:pPr><w:spacing w:after=\"0\" w:before=\"0\"/></w:pPr>"
                + "<w:rPr><w:sz w:val=\"20\"/></w:rPr></w:style>"
                + "</w:styles>";
    }

    private static String heading(int level, int halfPoints, int before) {
        return "<w:style w:type=\"paragraph\" w:styleId=\"Heading" + level + "\">"
                + "<w:name w:val=\"heading " + level + "\"/><w:basedOn w:val=\"Normal\"/>"
                + "<w:next w:val=\"Normal\"/><w:qFormat/>"
                + "<w:pPr><w:keepNext/><w:spacing w:before=\"" + (before * 120)
                + "\" w:after=\"60\"/><w:outlineLvl w:val=\"" + (level - 1) + "\"/></w:pPr>"
                + "<w:rPr><w:b/><w:sz w:val=\"" + halfPoints + "\"/></w:rPr></w:style>";
    }

    private static String coreXml(PdfToWord.Result result) {
        String title = result.title == null ? "" : result.title;
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\""
                + " xmlns:dc=\"http://purl.org/dc/elements/1.1/\">"
                + "<dc:title>" + esc(title) + "</dc:title>"
                + "<dc:creator>KavoPDF</dc:creator>"
                + "</cp:coreProperties>";
    }

    private static String appXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\">"
                + "<Application>KavoPDF</Application></Properties>";
    }
}
