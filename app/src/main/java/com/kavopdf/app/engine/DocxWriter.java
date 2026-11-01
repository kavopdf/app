package com.kavopdf.app.engine;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Writes a {@link PdfToWord.Result} as a real .docx - a ZIP of OOXML parts, built here rather
 * than pulled from a library.
 *
 * <p>Two reasons for hand-writing it: a Word library is 12 MB of the APK for one feature, and
 * the output is a handful of XML documents that Word, LibreOffice and Google Docs all read.
 *
 * <p>What comes out is a <em>document</em>, not a picture of one: real paragraphs with real
 * runs, heading styles Word understands, and tables with cells you can type into. Absolutely
 * positioned text boxes would look closer to the page and be useless to edit, which is the one
 * thing this tool must not do.
 */
public final class DocxWriter {

    private static final String NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
    private static final String NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships";
    private static final String NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing";
    private static final String NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main";
    private static final String NS_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture";

    private DocxWriter() {
    }

    public static void write(PdfToWord.Result result, File out) throws IOException {
        List<byte[]> media = new ArrayList<>();
        String documentXml = documentXml(result, media);
        String rels = documentRels(media);
        String contentTypes = contentTypes(media.size());

        try (OutputStream fos = new FileOutputStream(out);
             ZipOutputStream zip = new ZipOutputStream(fos)) {
            put(zip, "[Content_Types].xml", contentTypes);
            put(zip, "_rels/.rels", rootRels());
            put(zip, "word/document.xml", documentXml);
            put(zip, "word/styles.xml", stylesXml());
            put(zip, "word/_rels/document.xml.rels", rels);
            put(zip, "docProps/core.xml", coreXml(result));
            put(zip, "docProps/app.xml", appXml());
            for (int i = 0; i < media.size(); i++) {
                zip.putNextEntry(new ZipEntry("word/media/image" + (i + 1) + ".png"));
                zip.write(media.get(i));
                zip.closeEntry();
            }
        }
    }

    private static void put(ZipOutputStream zip, String name, String body) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    // ------------------------------------------------------------------ document

    private static String documentXml(PdfToWord.Result result, List<byte[]> media) {
        StringBuilder sb = new StringBuilder(1 << 16);
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        sb.append("<w:document xmlns:w=\"").append(NS_W).append("\" xmlns:r=\"").append(NS_R)
                .append("\" xmlns:wp=\"").append(NS_WP).append("\" xmlns:a=\"").append(NS_A)
                .append("\" xmlns:pic=\"").append(NS_PIC).append("\"><w:body>");

        // A4 portrait, 2 cm margins - a page the reader will recognise.
        sb.append("<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/>")
                .append("<w:pgMar w:top=\"1134\" w:right=\"1134\" w:bottom=\"1134\" w:left=\"1134\" ")
                .append("w:header=\"709\" w:footer=\"709\" w:gutter=\"0\"/></w:sectPr>");

        boolean first = true;
        for (PdfToWord.Page page : result.pages) {
            if (page.blocks.isEmpty()) continue;
            if (!first) {
                sb.append("<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>");
            }
            first = false;
            for (Object block : page.blocks) {
                if (block instanceof PdfToWord.Para) {
                    para(sb, (PdfToWord.Para) block);
                } else if (block instanceof PdfToWord.Table) {
                    table(sb, (PdfToWord.Table) block);
                } else if (block instanceof Picture) {
                    picture(sb, (Picture) block, media);
                }
            }
        }
        sb.append("</w:body></w:document>");
        return sb.toString();
    }

    /** An image lifted out of the PDF and placed where it was. */
    public static final class Picture {
        public final byte[] png;
        public final int widthEmu;
        public final int heightEmu;
        public float top;
        public int column;

        public Picture(byte[] png, int widthEmu, int heightEmu) {
            this.png = png;
            this.widthEmu = widthEmu;
            this.heightEmu = heightEmu;
        }
    }

    private static void picture(StringBuilder sb, Picture p, List<byte[]> media) {
        media.add(p.png);
        int id = media.size();
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

    private static void para(StringBuilder sb, PdfToWord.Para p) {
        String text = p.text();
        if (text.trim().isEmpty()) return;

        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
        if (p.indent > 0) {
            sb.append("<w:ind w:left=\"").append(p.indent * 420).append("\"/>");
        }
        sb.append("</w:pPr>");

        for (PdfToWord.Run run : p.runs) {
            if (run.text.isEmpty()) continue;
            sb.append("<w:r><w:rPr>");
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
        sb.append("</w:p>");
    }

    private static void table(StringBuilder sb, PdfToWord.Table t) {
        int cols = 0;
        for (List<String> row : t.rows) cols = Math.max(cols, row.size());
        if (cols == 0) return;
        int width = 9638 / cols;                       // content width in twips, split evenly

        sb.append("<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>")
                .append("<w:tblBorders>")
                .append("<w:top w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:left w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:bottom w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:right w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:insideH w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("<w:insideV w:val=\"single\" w:sz=\"6\" w:color=\"999999\"/>")
                .append("</w:tblBorders></w:tblPr><w:tblGrid>");
        for (int c = 0; c < cols; c++) sb.append("<w:gridCol w:w=\"").append(width).append("\"/>");
        sb.append("</w:tblGrid>");

        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            sb.append("<w:tr>");
            for (int c = 0; c < cols; c++) {
                String cell = c < row.size() ? row.get(c) : "";
                sb.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(width).append("\" w:type=\"dxa\"/>")
                        .append("</w:tcPr><w:p><w:pPr><w:pStyle w:val=\"TableText\"/></w:pPr>");
                if (r == 0 && t.header && !cell.isEmpty()) {
                    sb.append("<w:r><w:rPr><w:b/></w:rPr><w:t xml:space=\"preserve\">")
                            .append(esc(cell)).append("</w:t></w:r>");
                } else if (!cell.isEmpty()) {
                    sb.append("<w:r><w:t xml:space=\"preserve\">").append(esc(cell))
                            .append("</w:t></w:r>");
                }
                sb.append("</w:p></w:tc>");
            }
            sb.append("</w:tr>");
        }
        sb.append("</w:tbl>");
        sb.append("<w:p/>");
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
