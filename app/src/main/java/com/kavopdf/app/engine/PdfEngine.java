package com.kavopdf.app.engine;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import com.tom_roush.pdfbox.cos.COSBase;
import com.tom_roush.pdfbox.cos.COSDictionary;
import com.tom_roush.pdfbox.cos.COSName;
import com.tom_roush.pdfbox.io.MemoryUsageSetting;
import com.tom_roush.pdfbox.multipdf.PDFMergerUtility;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDDocumentInformation;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.PDPageContentStream;
import com.tom_roush.pdfbox.pdmodel.PDPageContentStream.AppendMode;
import com.tom_roush.pdfbox.pdmodel.PDResources;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.common.PDMetadata;
import com.tom_roush.pdfbox.pdmodel.encryption.AccessPermission;
import com.tom_roush.pdfbox.pdmodel.interactive.documentnavigation.outline.PDDocumentOutline;
import com.tom_roush.pdfbox.pdmodel.interactive.documentnavigation.outline.PDOutlineItem;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotation;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationWidget;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAppearanceDictionary;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAppearanceStream;
import com.tom_roush.pdfbox.pdmodel.interactive.action.PDAction;
import com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI;
import com.tom_roush.pdfbox.pdmodel.encryption.StandardProtectionPolicy;
import com.tom_roush.pdfbox.pdmodel.font.PDFont;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.pdmodel.graphics.PDXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.image.JPEGFactory;
import com.tom_roush.pdfbox.pdmodel.graphics.image.LosslessFactory;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.state.PDExtendedGraphicsState;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDAcroForm;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDCheckBox;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDComboBox;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDField;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDListBox;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDNonTerminalField;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDRadioButton;
import com.tom_roush.pdfbox.pdmodel.interactive.form.PDTextField;
import com.tom_roush.pdfbox.util.Matrix;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

/**
 * KavoPDF — the offline document-processing core.
 *
 * <p>Every method is a pure file-in / file-out operation built on the Apache PDFBox
 * port for Android. No UI, no network: the whole engine is offline and deterministic,
 * which is what lets it be unit-tested on the JVM as well as on-device.</p>
 */
public final class PdfEngine {

    private PdfEngine() { }

    // ---------------------------------------------------------------------
    // Small value types
    // ---------------------------------------------------------------------

    public static final class TextStamp {
        public int page;
        public float x, y, size;
        public int color;
        public String text;
        public TextStamp(int page, float x, float y, float size, int color, String text) {
            this.page = page; this.x = x; this.y = y; this.size = size; this.color = color; this.text = text;
        }
    }

    public static final class ImageStamp {
        public int page;
        public float x, y, w, h;
        public File image;
        public ImageStamp(int page, float x, float y, float w, float h, File image) {
            this.page = page; this.x = x; this.y = y; this.w = w; this.h = h; this.image = image;
        }
    }

    public static final class HighlightStamp {
        public int page;
        public float x, y, w, h;
        public int color;
        public HighlightStamp(int page, float x, float y, float w, float h, int color) {
            this.page = page; this.x = x; this.y = y; this.w = w; this.h = h; this.color = color;
        }
    }

    public static final class FormField {
        public String name;
        public String type;
        public String value;
        public List<String> options = new ArrayList<>();
        public boolean readOnly;
        public boolean required;
        public boolean multiline;
        /** The human label the PDF gives the field, when it has one. */
        public String label;
        /** 1-based page the field sits on, or 0 when it could not be worked out. */
        public int page;
        /** Distance from the top of its page, used to list fields in reading order. */
        public Float top;
        /** The pdfbox field itself; not part of the public data, only used while listing. */
        transient PDField field;
    }

    /** Options for {@link #watermarkText}. */
    public static final class WatermarkOptions {
        public String text = "CONFIDENTIAL";
        /** 0 = choose automatically from the page size. */
        public float fontSize = 0f;
        public float opacity = 0.25f;
        public int color = 0xFFFF0000;
        public float angle = 45f;
        /** Helvetica | Times | Courier */
        public String font = "Helvetica";
        public boolean bold = true;
        public boolean italic = false;
        /** Place each page's mark at a different random spot. */
        public boolean randomPosition = false;
    }

    // ---------------------------------------------------------------------
    // Loading helpers
    // ---------------------------------------------------------------------

    private static PDDocument open(File f) throws Exception {
        return PDDocument.load(f);
    }

    private static PDDocument open(File f, String password) throws Exception {
        if (password == null || password.isEmpty()) return PDDocument.load(f);
        return PDDocument.load(f, password);
    }

    /** Never decode an image larger than this many pixels (guards against hostile files). */
    private static final long MAX_IMAGE_PIXELS = 40_000_000L;
    /** Bound recursion through nested form XObjects / form fields. */
    private static final int MAX_XOBJECT_DEPTH = 32;
    private static final int MAX_FIELD_DEPTH = 64;

    /** True if the file is encrypted at all (even if it opens without a password). */
    public static boolean isEncrypted(File f) {
        try (PDDocument d = PDDocument.load(f)) {
            return d.isEncrypted();
        } catch (Exception e) {
            return true;
        }
    }

    /**
     * True only when the file cannot be opened without a password.
     *
     * <p>A PDF that is not encrypted never mentions /Encrypt in its trailer, so the
     * common case is answered by reading the last few KB instead of parsing the whole
     * document — which is what makes opening files feel instant.</p>
     */
    public static boolean needsPassword(File f) {
        if (!trailerMentionsEncrypt(f)) return false;
        try (PDDocument d = PDDocument.load(f)) {
            return false;
        } catch (Exception e) {
            return true;
        }
    }

    private static boolean trailerMentionsEncrypt(File f) {
        try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(f, "r")) {
            long len = raf.length();
            int n = (int) Math.min(8192L, len);
            byte[] buf = new byte[n];
            raf.seek(len - n);
            raf.readFully(buf);
            return new String(buf, java.nio.charset.StandardCharsets.ISO_8859_1).contains("/Encrypt");
        } catch (Exception e) {
            return true; // be conservative
        }
    }

    /**
     * Crop one page (or every page) to a rectangle expressed in the page's
     * <em>displayed</em> frame: origin at the top-left, y downwards, in points.
     */
    public static void cropPages(File src, int page1based, float dx, float dy, float dw, float dh,
                                 boolean allPages, File out) throws Exception {
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            for (int i = 0; i < total; i++) {
                if (!allPages && i != page1based - 1) continue;
                PDPage page = d.getPage(i);
                PDRectangle box = page.getCropBox();
                float w = box.getWidth(), h = box.getHeight();
                int r = ((page.getRotation() % 360) + 360) % 360;

                float[][] corners = {{dx, dy}, {dx + dw, dy}, {dx, dy + dh}, {dx + dw, dy + dh}};
                float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
                float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
                for (float[] c : corners) {
                    float xd = c[0], yd = c[1];
                    float px, py;
                    switch (r) {
                        case 90:  px = yd;      py = xd;      break;
                        case 180: px = w - xd;  py = yd;      break;
                        case 270: px = w - yd;  py = h - xd;  break;
                        default:  px = xd;      py = h - yd;  break;
                    }
                    minX = Math.min(minX, px); maxX = Math.max(maxX, px);
                    minY = Math.min(minY, py); maxY = Math.max(maxY, py);
                }
                minX = Math.max(box.getLowerLeftX(), minX);
                minY = Math.max(box.getLowerLeftY(), minY);
                maxX = Math.min(box.getUpperRightX(), maxX);
                maxY = Math.min(box.getUpperRightY(), maxY);
                if (maxX - minX < 12f || maxY - minY < 12f) continue;
                PDRectangle crop = new PDRectangle(minX, minY, maxX - minX, maxY - minY);
                page.setCropBox(crop);
                page.setMediaBox(crop);
            }
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Basic information
    // ---------------------------------------------------------------------

    public static int pageCount(File f) throws Exception {
        try (PDDocument d = open(f)) {
            return d.getNumberOfPages();
        }
    }

    public static int pageCount(File f, String password) throws Exception {
        try (PDDocument d = open(f, password)) {
            return d.getNumberOfPages();
        }
    }

    public static List<float[]> pageSizes(File f) throws Exception {
        List<float[]> out = new ArrayList<>();
        try (PDDocument d = open(f)) {
            for (PDPage p : d.getPages()) {
                PDRectangle r = p.getCropBox();
                out.add(new float[]{r.getWidth(), r.getHeight()});
            }
        }
        return out;
    }

    /** Page sizes as they appear on screen, i.e. taking /Rotate into account. */
    public static List<float[]> pageDisplaySizes(File f) throws Exception {
        List<float[]> out = new ArrayList<>();
        try (PDDocument d = open(f)) {
            for (PDPage p : d.getPages()) {
                PDRectangle r = p.getCropBox();
                int rot = ((p.getRotation() % 360) + 360) % 360;
                if (rot == 90 || rot == 270) out.add(new float[]{r.getHeight(), r.getWidth()});
                else out.add(new float[]{r.getWidth(), r.getHeight()});
            }
        }
        return out;
    }

    /**
     * Stamp a transparent overlay that was produced in the page's <em>displayed</em>
     * frame (after /Rotate) onto each page, so annotations land where the user saw them.
     */
    public static void stampDisplayRasters(File src, List<Integer> pages1based,
                                          List<File> rasters, File out) throws Exception {
        if (pages1based.size() != rasters.size()) {
            throw new IllegalArgumentException("pages and rasters must line up");
        }
        try (PDDocument d = open(src)) {
            for (int i = 0; i < pages1based.size(); i++) {
                File raster = rasters.get(i);
                if (raster == null || !raster.exists()) continue;
                PDPage page = d.getPage(pages1based.get(i) - 1);
                PDRectangle box = page.getCropBox();
                float w = box.getWidth(), h = box.getHeight();
                int rot = ((page.getRotation() % 360) + 360) % 360;
                float wd = (rot == 90 || rot == 270) ? h : w;
                float hd = (rot == 90 || rot == 270) ? w : h;
                PDImageXObject img = PDImageXObject.createFromFile(raster.getAbsolutePath(), d);
                Matrix m;
                switch (rot) {
                    case 90:  m = new Matrix(0, 1, -1, 0, w, 0); break;
                    case 180: m = new Matrix(-1, 0, 0, -1, w, h); break;
                    case 270: m = new Matrix(0, -1, 1, 0, 0, h); break;
                    default:  m = new Matrix(1, 0, 0, 1, 0, 0); break;
                }
                try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                    cs.saveGraphicsState();
                    cs.transform(m);
                    cs.drawImage(img, 0, 0, wd, hd);
                    cs.restoreGraphicsState();
                }
            }
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Merge
    // ---------------------------------------------------------------------

    public static void merge(List<File> inputs, File out) throws Exception {
        if (inputs == null || inputs.size() < 2) throw new IllegalArgumentException("Need at least two PDFs to merge");
        PDFMergerUtility merger = new PDFMergerUtility();
        for (File f : inputs) merger.addSource(f);
        merger.setDestinationFileName(out.getAbsolutePath());
        merger.mergeDocuments(MemoryUsageSetting.setupTempFileOnly());
    }

    // ---------------------------------------------------------------------
    // Page organisation
    // ---------------------------------------------------------------------

    public static void keepPages(File src, List<Integer> pages1based, File out) throws Exception {
        try (PDDocument in = open(src); PDDocument outDoc = new PDDocument()) {
            int total = in.getNumberOfPages();
            for (int p : pages1based) {
                // Ignore anything out of range instead of failing the whole operation.
                if (p < 1 || p > total) continue;
                outDoc.importPage(in.getPage(p - 1));
            }
            if (outDoc.getNumberOfPages() == 0) {
                throw new IllegalArgumentException("No valid pages were selected");
            }
            outDoc.save(out);
        }
    }

    public static void removePages(File src, List<Integer> pages1based, File out) throws Exception {
        try (PDDocument in = open(src)) {
            int total = in.getNumberOfPages();
            Set<Integer> drop = new HashSet<>(pages1based);
            List<Integer> keep = new ArrayList<>();
            for (int i = 1; i <= total; i++) if (!drop.contains(i)) keep.add(i);
            if (keep.isEmpty()) throw new IllegalArgumentException("Cannot remove every page");
            keepPages(src, keep, out);
        }
    }

    public static void reorderPages(File src, List<Integer> order1based, File out) throws Exception {
        try (PDDocument in = open(src)) {
            int total = in.getNumberOfPages();
            if (order1based.size() != total) throw new IllegalArgumentException("Order must list all " + total + " pages");
            keepPages(src, order1based, out);
        }
    }

    public static void rotatePages(File src, List<Integer> pages1based, int degrees, File out) throws Exception {
        int d = ((degrees % 360) + 360) % 360;
        try (PDDocument in = open(src)) {
            int total = in.getNumberOfPages();
            Set<Integer> set = (pages1based == null || pages1based.isEmpty()) ? null : new HashSet<>(pages1based);
            for (int i = 1; i <= total; i++) {
                if (set != null && !set.contains(i)) continue;
                PDPage p = in.getPage(i - 1);
                p.setRotation((p.getRotation() + d) % 360);
            }
            in.save(out);
        }
    }

    /** Reorder pages and apply a per-output-page rotation delta in one pass. */
    public static void rebuild(File src, List<Integer> order1based, List<Integer> rotationDeltas, File out) throws Exception {
        try (PDDocument in = open(src); PDDocument outDoc = new PDDocument()) {
            int total = in.getNumberOfPages();
            for (int i = 0; i < order1based.size(); i++) {
                int p = order1based.get(i);
                if (p < 1 || p > total) throw new IllegalArgumentException("Page " + p + " out of range (1.." + total + ")");
                outDoc.importPage(in.getPage(p - 1));
                PDPage imported = outDoc.getPage(outDoc.getNumberOfPages() - 1);
                int delta = (rotationDeltas != null && i < rotationDeltas.size()) ? rotationDeltas.get(i) : 0;
                if (delta != 0) imported.setRotation(((imported.getRotation() + delta) % 360 + 360) % 360);
            }
            outDoc.save(out);
        }
    }

    public static List<File> splitToFiles(File src, List<int[]> ranges1based, File outDir, String baseName) throws Exception {
        List<File> created = new ArrayList<>();
        try (PDDocument in = open(src)) {
            int total = in.getNumberOfPages();
            int idx = 1;
            for (int[] r : ranges1based) {
                int from = Math.max(1, Math.min(r[0], r[1]));
                int to = Math.min(total, Math.max(r[0], r[1]));
                if (from > to) continue;
                File dest = new File(outDir, baseName + "_part" + (idx++) + ".pdf");
                try (PDDocument part = new PDDocument()) {
                    for (int i = from; i <= to; i++) part.importPage(in.getPage(i - 1));
                    part.save(dest);
                }
                created.add(dest);
            }
        }
        return created;
    }

    // ---------------------------------------------------------------------
    // Content editing
    // ---------------------------------------------------------------------

    public static void addText(File src, int page1based, String text, float x, float y,
                               float size, int argbColor, File out) throws Exception {
        try (PDDocument d = open(src)) {
            PDPage page = d.getPage(page1based - 1);
            try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, size);
                cs.setNonStrokingColor((argbColor >> 16) & 0xFF, (argbColor >> 8) & 0xFF, argbColor & 0xFF);
                cs.newLineAtOffset(x, y);
                cs.showText(winAnsi(text));
                cs.endText();
            }
            d.save(out);
        }
    }

    public static void addImage(File src, int page1based, File image, float x, float y,
                                float w, float h, File out) throws Exception {
        try (PDDocument d = open(src)) {
            PDPage page = d.getPage(page1based - 1);
            PDImageXObject img = PDImageXObject.createFromFile(image.getAbsolutePath(), d);
            float dw = w > 0 ? w : img.getWidth();
            float dh = h > 0 ? h : img.getHeight();
            try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                cs.drawImage(img, x, y, dw, dh);
            }
            d.save(out);
        }
    }

    public static void applyStamps(File src, List<TextStamp> texts, List<ImageStamp> images,
                                   List<HighlightStamp> highlights, File out) throws Exception {
        try (PDDocument d = open(src)) {
            if (texts != null) {
                for (TextStamp t : texts) {
                    PDPage page = d.getPage(t.page - 1);
                    try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                        cs.beginText();
                        cs.setFont(PDType1Font.HELVETICA, t.size);
                        cs.setNonStrokingColor((t.color >> 16) & 0xFF, (t.color >> 8) & 0xFF, t.color & 0xFF);
                        cs.newLineAtOffset(t.x, t.y);
                        cs.showText(winAnsi(t.text));
                        cs.endText();
                    }
                }
            }
            if (images != null) {
                for (ImageStamp s : images) {
                    PDPage page = d.getPage(s.page - 1);
                    PDImageXObject img = PDImageXObject.createFromFile(s.image.getAbsolutePath(), d);
                    float dw = s.w > 0 ? s.w : img.getWidth();
                    float dh = s.h > 0 ? s.h : img.getHeight();
                    try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                        cs.drawImage(img, s.x, s.y, dw, dh);
                    }
                }
            }
            if (highlights != null) {
                for (HighlightStamp hs : highlights) {
                    PDPage page = d.getPage(hs.page - 1);
                    try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                        PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
                        gs.setNonStrokingAlphaConstant(0.35f);
                        cs.setGraphicsStateParameters(gs);
                        cs.setNonStrokingColor((hs.color >> 16) & 0xFF, (hs.color >> 8) & 0xFF, hs.color & 0xFF);
                        cs.addRect(hs.x, hs.y, hs.w, hs.h);
                        cs.fill();
                    }
                }
            }
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Watermarks
    // ---------------------------------------------------------------------

    public static void watermarkText(File src, WatermarkOptions o, File out) throws Exception {
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            String safe = winAnsi(o.text);
            for (int i = 0; i < total; i++) {
                PDPage page = d.getPage(i);
                PDRectangle box = page.getCropBox();
                float size = o.fontSize > 0 ? o.fontSize
                        : Math.max(20f, Math.min(box.getWidth(), box.getHeight()) / 8f);
                PDType1Font font = pickFont(o.font, o.bold, o.italic);
                float w = font.getStringWidth(safe) / 1000f * size;
                float h = size;

                // The mark is drawn at an angle, so the box it actually occupies is
                // wider and taller than the text itself. Fit that box inside the page
                // and the mark can never be clipped, however it is placed.
                double rad = Math.toRadians(o.angle);
                float bw = (float) (Math.abs(w * Math.cos(rad)) + Math.abs(h * Math.sin(rad)));
                float bh = (float) (Math.abs(w * Math.sin(rad)) + Math.abs(h * Math.cos(rad)));
                float pad = 12f;
                float minX = box.getLowerLeftX() + pad;
                float maxX = box.getUpperRightX() - bw - pad;
                float minY = box.getLowerLeftY() + pad;
                float maxY = box.getUpperRightY() - bh - pad;
                // a mark wider than the page still gets centred rather than pinned
                if (maxX < minX) { minX = maxX = box.getLowerLeftX() + (box.getWidth() - bw) / 2f; }
                if (maxY < minY) { minY = maxY = box.getLowerLeftY() + (box.getHeight() - bh) / 2f; }

                float x, y;
                if (o.randomPosition) {
                    Random rnd = new Random((i + 1) * 7919L + safe.hashCode());
                    x = minX + (maxX > minX ? rnd.nextFloat() * (maxX - minX) : 0f);
                    y = minY + (maxY > minY ? rnd.nextFloat() * (maxY - minY) : 0f);
                } else {
                    // no random: dead centre
                    x = minX + (maxX - minX) / 2f;
                    y = minY + (maxY - minY) / 2f;
                }

                try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                    PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
                    gs.setNonStrokingAlphaConstant(Math.max(0.05f, Math.min(1f, o.opacity)));
                    cs.setGraphicsStateParameters(gs);
                    cs.setNonStrokingColor((o.color >> 16) & 0xFF, (o.color >> 8) & 0xFF, o.color & 0xFF);
                    cs.beginText();
                    cs.setFont(font, size);
                    if (o.angle != 0f) cs.setTextMatrix(Matrix.getRotateInstance(Math.toRadians(o.angle), x, y));
                    else cs.newLineAtOffset(x, y);
                    cs.showText(safe);
                    cs.endText();
                }
            }
            d.save(out);
        }
    }

    /** Kept for convenience; centres a red diagonal text mark on every page. */
    public static void watermarkText(File src, String text, float fontSize, float opacity,
                                     int argbColor, float angleDeg, File out) throws Exception {
        WatermarkOptions o = new WatermarkOptions();
        o.text = text; o.fontSize = fontSize; o.opacity = opacity;
        o.color = argbColor; o.angle = angleDeg;
        watermarkText(src, o, out);
    }

    public static void watermarkImage(File src, File image, float opacity, float scale, File out) throws Exception {
        watermarkImage(src, image, opacity, scale, false, out);
    }

    /**
     * @param random when true the picture lands in a different spot on every page,
     *               like the text watermark's random option. Before this the picture
     *               was always dead centre, whatever the switch said.
     */
    public static void watermarkImage(File src, File image, float opacity, float scale,
                                      boolean random, File out) throws Exception {
        watermarkImage(src, image, opacity, scale, scale * 0.5f, 0, random, out);
    }

    /**
     * @param scaleX width as a fraction of the page, scaleY height as a fraction
     * @param wmPlace 0 centre (default), 1 top, 2 bottom, 3 left, 4 right, 5 top-left,
     *                6 top-right, 7 bottom-left, 8 bottom-right
     */
    public static void watermarkImage(File src, File image, float opacity,
                                      float scaleX, float scaleY, int wmPlace,
                                      boolean random, File out) throws Exception {
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            PDImageXObject img = PDImageXObject.createFromFile(image.getAbsolutePath(), d);
            for (int i = 0; i < total; i++) {
                PDPage page = d.getPage(i);
                PDRectangle box = page.getCropBox();
                // Empty width means "leave the picture at its own size" (96dpi -> points).
                // Empty height means "keep the picture's proportions": it is derived from
                // the width, so the image can never be stretched out of shape.
                float naturalW = img.getWidth() * 0.75f;
                float naturalH = img.getHeight() * 0.75f;
                float targetW = scaleX > 0 ? box.getWidth() * scaleX : naturalW;
                float targetH;
                if (scaleY > 0) {
                    targetH = box.getHeight() * scaleY;
                } else if (scaleX > 0) {
                    targetH = targetW * img.getHeight() / (float) Math.max(1, img.getWidth());
                } else {
                    targetH = naturalH;
                }
                float x, y;
                float maxX = Math.max(0f, box.getWidth() - targetW);
                float maxY = Math.max(0f, box.getHeight() - targetH);
                if (random) {
                    java.util.Random r = new java.util.Random(i * 7919L + 13);
                    x = box.getLowerLeftX() + r.nextFloat() * maxX;
                    y = box.getLowerLeftY() + r.nextFloat() * maxY;
                } else {
                    switch (wmPlace) {
                        case 1:  x = box.getLowerLeftX() + maxX / 2f; y = box.getLowerLeftY() + maxY; break;
                        case 2:  x = box.getLowerLeftX() + maxX / 2f; y = box.getLowerLeftY(); break;
                        case 3:  x = box.getLowerLeftX(); y = box.getLowerLeftY() + maxY / 2f; break;
                        case 4:  x = box.getLowerLeftX() + maxX; y = box.getLowerLeftY() + maxY / 2f; break;
                        case 5:  x = box.getLowerLeftX(); y = box.getLowerLeftY() + maxY; break;
                        case 6:  x = box.getLowerLeftX() + maxX; y = box.getLowerLeftY() + maxY; break;
                        case 7:  x = box.getLowerLeftX(); y = box.getLowerLeftY(); break;
                        case 8:  x = box.getLowerLeftX() + maxX; y = box.getLowerLeftY(); break;
                        default: x = box.getLowerLeftX() + maxX / 2f; y = box.getLowerLeftY() + maxY / 2f;
                    }
                }
                try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                    PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
                    gs.setNonStrokingAlphaConstant(opacity);
                    cs.setGraphicsStateParameters(gs);
                    cs.drawImage(img, x, y, targetW, targetH);
                }
            }
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Page numbers
    // ---------------------------------------------------------------------

    public static void addPageNumbers(File src, String format, float fontSize, int argbColor, File out) throws Exception {
        addPageNumbers(src, format, fontSize, argbColor, 1f, out);
    }

    /** Where the page number sits. */
    public static final int PLACE_BOTTOM_CENTRE = 0;
    public static final int PLACE_TOP_CENTRE = 1;
    public static final int PLACE_BOTTOM_LEFT = 2;
    public static final int PLACE_BOTTOM_RIGHT = 3;
    public static final int PLACE_TOP_LEFT = 4;
    public static final int PLACE_TOP_RIGHT = 5;

    public static void addPageNumbers(File src, String format, float fontSize, int argbColor,
                                      float opacity, File out) throws Exception {
        addPageNumbers(src, format, fontSize, argbColor, opacity, PLACE_BOTTOM_CENTRE, out);
    }

    public static void addPageNumbers(File src, String format, float fontSize, int argbColor,
                                      float opacity, int place, File out) throws Exception {
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            float alpha = Math.max(0.05f, Math.min(1f, opacity));
            for (int i = 0; i < total; i++) {
                PDPage page = d.getPage(i);
                PDRectangle box = page.getCropBox();
                String label = format.replace("{n}", String.valueOf(i + 1)).replace("{total}", String.valueOf(total));
                label = winAnsi(label);
                float size = fontSize > 0 ? fontSize : 10f;
                float w = PDType1Font.HELVETICA.getStringWidth(label) / 1000f * size;
                float margin = 24f;
                float x, y;
                switch (place) {
                    case PLACE_TOP_CENTRE:
                        x = box.getLowerLeftX() + (box.getWidth() - w) / 2f;
                        y = box.getUpperRightY() - margin - size;
                        break;
                    case PLACE_BOTTOM_LEFT:
                        x = box.getLowerLeftX() + margin;
                        y = box.getLowerLeftY() + margin;
                        break;
                    case PLACE_BOTTOM_RIGHT:
                        x = box.getUpperRightX() - margin - w;
                        y = box.getLowerLeftY() + margin;
                        break;
                    case PLACE_TOP_LEFT:
                        x = box.getLowerLeftX() + margin;
                        y = box.getUpperRightY() - margin - size;
                        break;
                    case PLACE_TOP_RIGHT:
                        x = box.getUpperRightX() - margin - w;
                        y = box.getUpperRightY() - margin - size;
                        break;
                    default:
                        x = box.getLowerLeftX() + (box.getWidth() - w) / 2f;
                        y = box.getLowerLeftY() + margin;
                }
                try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                    if (alpha < 1f) {
                        PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
                        gs.setNonStrokingAlphaConstant(alpha);
                        cs.setGraphicsStateParameters(gs);
                    }
                    cs.beginText();
                    cs.setFont(PDType1Font.HELVETICA, size);
                    cs.setNonStrokingColor((argbColor >> 16) & 0xFF, (argbColor >> 8) & 0xFF, argbColor & 0xFF);
                    cs.newLineAtOffset(x, y);
                    cs.showText(label);
                    cs.endText();
                }
            }
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Security
    // ---------------------------------------------------------------------

    /** What the reader is allowed to do with a protected document. */
    public static final int PERM_PRINT = 1;
    public static final int PERM_COPY = 2;
    public static final int PERM_EDIT = 4;

    public static void encrypt(File src, String userPassword, String ownerPassword, File out) throws Exception {
        encrypt(src, userPassword, ownerPassword, PERM_PRINT | PERM_COPY, out);
    }

    /**
     * Password-protect with real AES-256 (PDF 2.0, security-handler revision 6).
     *
     * <p>The password is used here and nowhere else: it is never written into the
     * file, never logged and never stored. Nothing about it leaves the device, so a
     * lost password really is unrecoverable - that is the point of the format.
     *
     * @param perms any OR of PERM_PRINT / PERM_COPY / PERM_EDIT
     */
    public static void encrypt(File src, String userPassword, String ownerPassword,
                               int perms, File out) throws Exception {
        try (PDDocument d = open(src)) {
            boolean print = (perms & PERM_PRINT) != 0;
            boolean copy = (perms & PERM_COPY) != 0;
            boolean edit = (perms & PERM_EDIT) != 0;
            AccessPermission ap = new AccessPermission();
            ap.setCanPrint(print);
            ap.setCanPrintDegraded(print);
            ap.setCanExtractContent(copy);
            ap.setCanExtractForAccessibility(copy);
            ap.setCanModify(edit);
            ap.setCanModifyAnnotations(edit);
            ap.setCanFillInForm(edit);
            ap.setCanAssembleDocument(edit);
            String owner = (ownerPassword == null || ownerPassword.isEmpty()) ? userPassword : ownerPassword;
            StandardProtectionPolicy policy = new StandardProtectionPolicy(
                    owner, userPassword == null ? "" : userPassword, ap);
            policy.setEncryptionKeyLength(256);      // AES-256
            policy.setPermissions(ap);
            d.protect(policy);
            d.save(out);
        }
    }

    /**
     * Remove protection. Works for files that open without a password (owner-only
     * protection) and for files whose user password is supplied.
     */
    public static void decrypt(File src, String password, File out) throws Exception {
        try (PDDocument d = open(src, password)) {
            d.setAllSecurityToBeRemoved(true);
            d.save(out);
        }
    }

    // ---------------------------------------------------------------------
    // Compression
    // ---------------------------------------------------------------------

    /** level: 0 = light, 1 = balanced, 2 = strong. */
    public static void compress(File src, File out, int level) throws Exception {
        int maxDim;
        float quality;
        switch (level) {
            case 0: maxDim = 2200; quality = 0.78f; break;
            case 2: maxDim = 1200; quality = 0.48f; break;
            default: maxDim = 1600; quality = 0.62f; break;
        }
        compress(src, out, maxDim, quality);
    }

    public static void compress(File src, File out) throws Exception {
        compress(src, out, 1600, 0.62f);
    }

    public static void compress(File src, File out, int maxDimension, float jpegQuality) throws Exception {
        long before = src.length();
        compressInto(src, out, maxDimension, jpegQuality);
        // A tiny or already-optimised file can come out larger once the images are
        // re-encoded. When that happens the original is simply kept, so compressing
        // never costs the user space.
        if (out.length() >= before) {
            java.nio.file.Files.copy(src.toPath(), out.toPath(),
                    java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static void compressInto(File src, File out, int maxDimension, float jpegQuality) throws Exception {
        try (PDDocument d = open(src)) {
            IdentityHashMap<COSBase, Boolean> seenImages = new IdentityHashMap<>();
            IdentityHashMap<COSBase, Boolean> seenResources = new IdentityHashMap<>();
            for (PDPage page : d.getPages()) {
                // embedded page thumbnails are pure dead weight
                page.getCOSObject().removeItem(COSName.THUMB);
                PDResources res = page.getResources();
                if (res != null) compressResources(d, res, seenImages, seenResources, maxDimension, jpegQuality, 0);
            }
            // strip identifying metadata (small but free)
            PDDocumentInformation info = d.getDocumentInformation();
            info.setTitle(null);
            info.setSubject(null);
            info.setKeywords(null);
            d.save(out);
        }
    }

    private static void compressResources(PDDocument d, PDResources res,
                                          IdentityHashMap<COSBase, Boolean> seenImages,
                                          IdentityHashMap<COSBase, Boolean> seenResources,
                                          int maxDimension, float jpegQuality, int depth) {
        if (res == null) return;
        if (depth > MAX_XOBJECT_DEPTH) return;
        if (seenResources.put(res.getCOSObject(), Boolean.TRUE) != null) return;
        List<COSName> names = new ArrayList<>();
        for (COSName n : res.getXObjectNames()) names.add(n);
        for (COSName name : names) {
            PDXObject xo;
            try { xo = res.getXObject(name); } catch (Exception e) { continue; }
            if (xo instanceof PDFormXObject) {
                try { compressResources(d, ((PDFormXObject) xo).getResources(), seenImages, seenResources, maxDimension, jpegQuality, depth + 1); }
                catch (Exception ignore) { }
            } else if (xo instanceof PDImageXObject) {
                PDImageXObject img = (PDImageXObject) xo;
                if (seenImages.put(img.getCOSObject(), Boolean.TRUE) != null) continue;
                try {
                    if (!safeToDecode(img)) continue;
                    Bitmap original;
                    try { original = img.getImage(); } catch (OutOfMemoryError | Exception e) { continue; }
                    if (original == null) continue;
                    boolean hasAlpha = original.hasAlpha();
                    int w = original.getWidth(), h = original.getHeight();
                    Bitmap scaled = null;
                    Bitmap toEncode = original;
                    if (maxDimension > 0 && Math.max(w, h) > maxDimension) {
                        float s = maxDimension / (float) Math.max(w, h);
                        scaled = Bitmap.createScaledBitmap(original, Math.max(1, Math.round(w * s)),
                                Math.max(1, Math.round(h * s)), true);
                        toEncode = scaled;
                    }
                    PDImageXObject replacement = hasAlpha
                            ? LosslessFactory.createFromImage(d, toEncode)
                            : JPEGFactory.createFromImage(d, toEncode, jpegQuality);
                    res.put(name, replacement);
                    if (scaled != null) scaled.recycle();
                    original.recycle();
                } catch (Throwable ignore) {
                    // leave the original image untouched
                }
            }
        }
    }

    // ---------------------------------------------------------------------
    // Metadata
    // ---------------------------------------------------------------------

    /** All editable document properties. */
    public static final class MetadataInfo {
        public String title, author, subject, keywords, creator, producer;
        /** yyyy-MM-dd HH:mm, or null to leave unchanged. */
        public String creationDate, modDate;
    }

    private static final java.text.SimpleDateFormat META_DATE =
            new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.US);

    public static Map<String, String> getMetadata(File src) throws Exception {
        Map<String, String> m = new LinkedHashMap<>();
        try (PDDocument d = open(src)) {
            PDDocumentInformation info = d.getDocumentInformation();
            m.put("title", nullToEmpty(info.getTitle()));
            m.put("author", nullToEmpty(info.getAuthor()));
            m.put("subject", nullToEmpty(info.getSubject()));
            m.put("keywords", nullToEmpty(info.getKeywords()));
            m.put("creator", nullToEmpty(info.getCreator()));
            m.put("producer", nullToEmpty(info.getProducer()));
            m.put("creationDate", info.getCreationDate() == null ? "" : META_DATE.format(info.getCreationDate().getTime()));
            m.put("modDate", info.getModificationDate() == null ? "" : META_DATE.format(info.getModificationDate().getTime()));
            m.put("pages", String.valueOf(d.getNumberOfPages()));

            // A PDF carries document properties in TWO places: the Info dictionary read
            // above, and an XMP packet. Many files written by modern tools fill only the
            // XMP one, which is why the screen used to look empty on a file that clearly
            // had a title. Anything still blank is filled from XMP - never overwriting a
            // value that Info already gave.
            try {
                Map<String, String> xmp = xmpFields(d);
                for (Map.Entry<String, String> e : xmp.entrySet()) {
                    if (m.get(e.getKey()) == null || m.get(e.getKey()).isEmpty()) {
                        m.put(e.getKey(), e.getValue());
                    }
                }
                m.put("xmp", xmp.isEmpty() ? "" : "yes");
            } catch (Throwable ignored) {
                m.put("xmp", "");
            }
        }
        return m;
    }

    /** The handful of XMP fields that map onto the properties this screen edits. */
    private static Map<String, String> xmpFields(PDDocument d) throws Exception {
        Map<String, String> out = new LinkedHashMap<>();
        PDMetadata md = d.getDocumentCatalog().getMetadata();
        if (md == null) return out;
        byte[] raw;
        try (java.io.InputStream in = md.createInputStream()) {
            raw = readAll(in);
        }
        if (raw == null || raw.length == 0) return out;
        String xml = new String(raw, "UTF-8");
        String title = firstXmp(xml, "dc:title");
        if (title != null) out.put("title", title);
        String author = firstXmp(xml, "dc:creator");
        if (author != null) out.put("author", author);
        String subject = firstXmp(xml, "dc:description");
        if (subject != null) out.put("subject", subject);
        String keywords = firstXmp(xml, "pdf:Keywords");
        if (keywords != null) out.put("keywords", keywords);
        String creator = firstXmp(xml, "xmp:CreatorTool");
        if (creator != null) out.put("creator", creator);
        String producer = firstXmp(xml, "pdf:Producer");
        if (producer != null) out.put("producer", producer);
        String created = firstXmp(xml, "xmp:CreateDate");
        if (created != null) out.put("creationDate", xmpDate(created));
        String modified = firstXmp(xml, "xmp:ModifyDate");
        if (modified != null) out.put("modDate", xmpDate(modified));
        return out;
    }

    /** Text of the first element with this name, whatever its nesting, or null. */
    private static String firstXmp(String xml, String tag) {
        java.util.regex.Matcher m = java.util.regex.Pattern.compile(
                "<" + java.util.regex.Pattern.quote(tag) + "[^>]*>(.*?)</"
                        + java.util.regex.Pattern.quote(tag) + ">",
                java.util.regex.Pattern.DOTALL).matcher(xml);
        while (m.find()) {
            String v = m.group(1);
            // XMP often wraps the value: <rdf:li>the title</rdf:li>
            java.util.regex.Matcher li = java.util.regex.Pattern
                    .compile("<rdf:li[^>]*>(.*?)</rdf:li>",
                             java.util.regex.Pattern.DOTALL).matcher(v);
            if (li.find()) v = li.group(1);
            v = v.replaceAll("<[^>]+>", " ")
                 .replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                 .replace("&quot;", "\"").replace("&apos;", "'")
                 .replaceAll("\\s+", " ").trim();
            if (!v.isEmpty()) return v;
        }
        return null;
    }

    /** 2026-10-30T12:00:00+05:30 -> yyyy-MM-dd HH:mm */
    private static String xmpDate(String v) {
        java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("(\\d{4})-(\\d{2})-(\\d{2})T(\\d{2}):(\\d{2})").matcher(v);
        if (m.find()) return m.group(1) + "-" + m.group(2) + "-" + m.group(3)
                + " " + m.group(4) + ":" + m.group(5);
        return v;
    }

    private static byte[] readAll(java.io.InputStream in) throws java.io.IOException {
        java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
        byte[] b = new byte[8192];
        int n;
        while ((n = in.read(b)) > 0) bo.write(b, 0, n);
        return bo.toByteArray();
    }

    public static void setMetadata(File src, MetadataInfo in, File out) throws Exception {
        try (PDDocument d = open(src)) {
            PDDocumentInformation info = d.getDocumentInformation();
            info.setTitle(emptyToNull(in.title));
            info.setAuthor(emptyToNull(in.author));
            info.setSubject(emptyToNull(in.subject));
            info.setKeywords(emptyToNull(in.keywords));
            info.setCreator(emptyToNull(in.creator));
            info.setProducer(emptyToNull(in.producer));
            java.util.Calendar c = parseDate(in.creationDate);
            if (c != null) info.setCreationDate(c);
            java.util.Calendar m = parseDate(in.modDate);
            if (m != null) info.setModificationDate(m);
            d.save(out);
        }
    }

    /** Remove every document property, including the XMP metadata stream. */
    public static void clearMetadata(File src, File out) throws Exception {
        try (PDDocument d = open(src)) {
            d.setDocumentInformation(new PDDocumentInformation());
            d.getDocumentCatalog().getCOSObject().removeItem(COSName.METADATA);
            d.save(out);
        }
    }

    private static java.util.Calendar parseDate(String s) {
        if (s == null || s.trim().isEmpty()) return null;
        try {
            java.util.Calendar c = java.util.Calendar.getInstance();
            c.setTime(META_DATE.parse(s.trim()));
            return c;
        } catch (Exception e) {
            return null;
        }
    }

    // ---------------------------------------------------------------------
    // AcroForm fields
    // ---------------------------------------------------------------------

    /**
     * True when the form is XFA (Adobe LiveCycle). XFA keeps its fields in an XML
     * stream instead of AcroForm widgets, so there is nothing for us to fill - but
     * we can say so instead of pretending the file is not a form at all.
     */
    public static boolean hasXfa(File src) {
        try (PDDocument d = open(src)) {
            // Do not go through getAcroForm(): on an XFA-only form pdfbox can hand
            // back null there, which is exactly how the SBI form slipped through and
            // was reported as "no fields" instead of "this is an XFA form".
            COSDictionary cat = d.getDocumentCatalog().getCOSObject();
            COSBase acro = cat.getDictionaryObject(COSName.ACRO_FORM);
            if (acro instanceof COSDictionary) {
                if (((COSDictionary) acro).getDictionaryObject(COSName.XFA) != null) return true;
            }
            // a few files declare XFA straight on the catalog
            return cat.getDictionaryObject(COSName.getPDFName("XFA")) != null;
        } catch (Throwable t) {
            return false;
        }
    }

    public static List<FormField> listFormFields(File src) throws Exception {
        List<FormField> out = new ArrayList<>();
        try (PDDocument d = open(src)) {
            PDAcroForm form = d.getDocumentCatalog().getAcroForm();
            if (form == null) return out;
            for (PDField f : form.getFields()) collect(f, out);

            // Which page a field is on comes from its own widget rectangle, not from its
            // name. Reading "txt_p3_Address_1" only ever worked for the one generator
            // that names its fields that way; every other form got page 0 and lost its
            // page headings. The widget is an annotation that sits on a page, so the
            // page is simply where it lives. The key is still read as a fallback for the
            // rare field whose widget is missing.
            // keyed by the underlying COS dictionary: pdfbox hands out a new wrapper for
            // the same annotation on every call, so identity would never match
            java.util.HashMap<Object, Integer> pageOf = new java.util.HashMap<>();
            java.util.HashMap<Object, Float> topOf = new java.util.HashMap<>();
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                PDPage pg = d.getPage(i);
                for (PDAnnotation a : pg.getAnnotations()) {
                    if (!(a instanceof PDAnnotationWidget)) continue;
                    pageOf.put(a.getCOSObject(), i + 1);
                    PDRectangle r = a.getRectangle();
                    if (r != null) topOf.put(a.getCOSObject(), r.getUpperRightY());
                }
            }
            for (FormField ff : out) {
                Integer pg = null;
                Float top = null;
                try {
                    java.util.List<PDAnnotationWidget> ws = ff.field == null
                            ? null : ff.field.getWidgets();
                    if (ws != null && !ws.isEmpty()) {
                        Object key = ws.get(0).getCOSObject();
                        pg = pageOf.get(key);
                        top = topOf.get(key);
                    }
                } catch (Throwable ignored) {
                }
                ff.page = pg != null ? pg : pageFromKey(ff.name);
                if (top != null) ff.top = top;
            }
            // Put the list in the order a person reads the document: page first, then
            // from the top of the page down. Only when every field is placed, so a form
            // we could not place keeps the order the file gave us.
            boolean placed = true;
            for (FormField ff : out) if (ff.top == null) { placed = false; break; }
            if (placed) {
                out.sort((a, b) -> {
                    int c = Integer.compare(a.page, b.page);
                    return c != 0 ? c : Float.compare(b.top, a.top);
                });
            }
        }
        return out;
    }

    private static void collect(PDField f, List<FormField> out) {
        collect(f, out, 0);
    }

    private static void collect(PDField f, List<FormField> out, int depth) {
        if (depth > MAX_FIELD_DEPTH) return;
        if (f instanceof PDNonTerminalField) {
            for (PDField k : ((PDNonTerminalField) f).getChildren()) collect(k, out, depth + 1);
            return;
        }
        FormField ff = new FormField();
        ff.field = f;                       // kept so its page and position can be read
        ff.name = f.getFullyQualifiedName();
        ff.readOnly = f.isReadOnly();
        try { ff.required = f.isRequired(); } catch (Throwable t) { ff.required = false; }
        try { ff.label = f.getAlternateFieldName(); } catch (Throwable t) { ff.label = null; }
        // Many forms (the SBI one included) ship no alternate name, so the app used to
        // show the raw key - "chk_p1_New", "txt_p1_Date". Fall back to the key with its
        // page prefix stripped and the underscores turned into spaces.
        if (ff.label == null || ff.label.trim().isEmpty()) ff.label = readableName(f.getFullyQualifiedName());
        if (f instanceof PDTextField) {
            try { ff.multiline = ((PDTextField) f).isMultiline(); } catch (Throwable t) { ff.multiline = false; }
        }
        try { ff.value = f.getValueAsString(); } catch (Exception e) { ff.value = ""; }
        if (f instanceof PDTextField) {
            ff.type = "text";
        } else if (f instanceof PDCheckBox) {
            ff.type = "checkbox";
            try { ff.options.add(((PDCheckBox) f).getOnValue()); } catch (Exception ignore) { }
        } else if (f instanceof PDRadioButton) {
            ff.type = "radio";
            try { ff.options.addAll(((PDRadioButton) f).getExportValues()); } catch (Exception ignore) { }
        } else if (f instanceof PDComboBox) {
            ff.type = "combo";
            try { for (String o : ((PDComboBox) f).getOptionsExportValues()) ff.options.add(o); } catch (Exception ignore) { }
        } else if (f instanceof PDListBox) {
            ff.type = "list";
            try { for (String o : ((PDListBox) f).getOptionsExportValues()) ff.options.add(o); } catch (Exception ignore) { }
        } else {
            ff.type = "other";
        }
        out.add(ff);
    }

    public static void fillForm(File src, Map<String, String> values, File out) throws Exception {
        try (PDDocument d = open(src)) {
            PDAcroForm form = d.getDocumentCatalog().getAcroForm();
            if (form == null) throw new IllegalArgumentException("This PDF has no fillable form fields");
            for (PDField f : form.getFields()) applyField(f, values);
            // Values alone are not enough: a viewer draws a field from its appearance
            // stream, and setNeedAppearances(true) only asks the viewer to build one.
            // Android viewers ignore that request, so the form looked empty even though
            // the values were in the file. Building the streams here makes them visible
            // in every reader.
            try {
                form.refreshAppearances();
            } catch (Throwable t) {
                // older or unusual forms may refuse; the values are still stored
                form.setNeedAppearances(true);
            }
            // pdfbox refuses to build an appearance for some forms - a missing or
            // unusual /DA, a font it cannot load, a field with no widget rectangle.
            // When that happens the value IS in the file but no viewer draws it, which
            // is exactly "I filled the form and nothing shows". Every value is checked
            // here, and any field still without a visible appearance gets its text
            // drawn onto the page directly.
            paintMissingValues(d, form, values);
            d.save(out);
        }
    }

    /**
     * Draw the value onto the page for any field whose appearance stream is missing or
     * does not actually contain the text. This is the safety net that makes a filled
     * form visible in every reader, whatever the form's own /DA or fonts look like.
     */
    private static void paintMissingValues(PDDocument d, PDAcroForm form,
                                           Map<String, String> values) {
        try {
            // which page each widget sits on, and where
            java.util.HashMap<Object, Integer> pageOf = new java.util.HashMap<>();
            java.util.HashMap<Object, PDRectangle> boxOf = new java.util.HashMap<>();
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                PDPage pg = d.getPage(i);
                for (PDAnnotation a : pg.getAnnotations()) {
                    if (a instanceof PDAnnotationWidget) {
                        pageOf.put(a.getCOSObject(), i);
                        PDRectangle r = a.getRectangle();
                        if (r != null) boxOf.put(a.getCOSObject(), r);
                    }
                }
            }
            for (PDField f : form.getFields()) paintField(d, f, values, pageOf, boxOf);
        } catch (Throwable t) {
            // never let the safety net break a save that already worked
        }
    }

    private static void paintField(PDDocument d, PDField f, Map<String, String> values,
                                   java.util.HashMap<Object, Integer> pageOf,
                                   java.util.HashMap<Object, PDRectangle> boxOf) {
        if (f instanceof PDNonTerminalField) {
            try {
                for (PDField k : ((PDNonTerminalField) f).getChildren()) {
                    paintField(d, k, values, pageOf, boxOf);
                }
            } catch (Throwable ignored) {
            }
            return;
        }
        String name = f.getFullyQualifiedName();
        if (!values.containsKey(name)) return;
        String v = values.get(name);
        if (v == null || v.isEmpty()) return;
        // a checkbox or radio draws its own tick; only text can be re-drawn safely
        if (!(f instanceof PDTextField)) return;
        try {
            java.util.List<PDAnnotationWidget> ws = f.getWidgets();
            if (ws == null || ws.isEmpty()) return;
            PDAnnotationWidget w = ws.get(0);
            // Android's own PdfRenderer - which this app reads PDFs with - draws page
            // CONTENT only and ignores annotations entirely. A form value normally lives
            // in an annotation appearance, so a filled form looked empty in KavoPDF while
            // Google Drive showed it. The value is therefore always drawn onto the page,
            // and the annotation appearance is dropped so a viewer that does draw
            // annotations does not show the same text twice.
            Integer pi = pageOf.get(w.getCOSObject());
            PDRectangle r = boxOf.get(w.getCOSObject());
            if (pi == null || r == null) return;
            PDPage page = d.getPage(pi);
            float size = 10f;
            try {
                String da = ((PDTextField) f).getDefaultAppearance();
                if (da != null) {
                    java.util.regex.Matcher m = java.util.regex.Pattern
                            .compile("([0-9]+(?:\\.[0-9]+)?)\\s+Tf").matcher(da);
                    if (m.find()) size = Float.parseFloat(m.group(1));
                }
            } catch (Throwable ignored) {
            }
            float boxH = Math.abs(r.getHeight());
            if (boxH > 0f) size = Math.min(size, boxH * 0.75f);
            if (size < 4f) size = 4f;
            try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, size);
                cs.setNonStrokingColor(0f, 0f, 0f);
                float x = r.getLowerLeftX() + 2f;
                float y = r.getLowerLeftY() + (boxH - size) / 2f + size * 0.15f;
                cs.newLineAtOffset(x, y);
                cs.showText(v);
                cs.endText();
            }
            // the value now lives on the page, so the annotation must stop drawing it
            try {
                w.setAppearance(null);
            } catch (Throwable ignored) {
            }
        } catch (Throwable ignored) {
            // one awkward field must not stop the rest
        }
    }

    private static void applyField(PDField f, Map<String, String> values) throws Exception {
        if (f instanceof PDNonTerminalField) {
            for (PDField k : ((PDNonTerminalField) f).getChildren()) applyField(k, values);
            return;
        }
        String name = f.getFullyQualifiedName();
        if (!values.containsKey(name)) return;
        String v = values.get(name);
        if (f instanceof PDCheckBox) {
            PDCheckBox cb = (PDCheckBox) f;
            if ("true".equalsIgnoreCase(v) || "on".equalsIgnoreCase(v) || "yes".equalsIgnoreCase(v) || "1".equals(v)) cb.check();
            else cb.unCheck();
        } else {
            f.setValue(v == null ? "" : v);
        }
    }

    // ---------------------------------------------------------------------
    // Images <-> PDF
    // ---------------------------------------------------------------------

    /** One page per image, page sized to the image. Images are down-scaled to a sane bound. */
    public static void imagesToPdf(List<File> images, File out) throws Exception {
        imagesToPdf(images, out, 3000, false);
    }

    /**
     * @param maxDimension longest edge kept when decoding (0 = full size)
     * @param fitToA4    fit each image inside an A4 page instead of sizing the page to it
     */
    public static void imagesToPdf(List<File> images, File out, int maxDimension, boolean fitToA4) throws Exception {
        if (images == null || images.isEmpty()) throw new IllegalArgumentException("Pick at least one image");
        try (PDDocument d = new PDDocument()) {
            for (File image : images) {
                Bitmap bmp = decodeBounded(image, maxDimension);
                if (bmp == null) throw new IllegalArgumentException("Could not read image: " + image.getName());
                PDImageXObject img = bmp.hasAlpha()
                        ? LosslessFactory.createFromImage(d, bmp)
                        : JPEGFactory.createFromImage(d, bmp, 0.85f);

                PDRectangle pageSize;
                if (fitToA4) {
                    pageSize = PDRectangle.A4;
                } else {
                    float pw = Math.max(1f, bmp.getWidth());
                    float ph = Math.max(1f, bmp.getHeight());
                    // keep pages to a sensible size (max 2000pt on the long edge)
                    float longest = Math.max(pw, ph);
                    if (longest > 2000f) { float s = 2000f / longest; pw *= s; ph *= s; }
                    pageSize = new PDRectangle(pw, ph);
                }
                bmp.recycle();

                PDPage page = new PDPage(pageSize);
                d.addPage(page);
                float iw = img.getWidth(), ih = img.getHeight();
                float scale = Math.min(pageSize.getWidth() / iw, pageSize.getHeight() / ih);
                if (fitToA4) {
                    float dw = iw * scale, dh = ih * scale;
                    try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                        cs.drawImage(img, (pageSize.getWidth() - dw) / 2f, (pageSize.getHeight() - dh) / 2f, dw, dh);
                    }
                } else {
                    try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                        cs.drawImage(img, 0, 0, pageSize.getWidth(), pageSize.getHeight());
                    }
                }
            }
            d.save(out);
        }
    }

    // ------------------------------------------------------------------
    // OCR text layer
    // ------------------------------------------------------------------

    /** One recognised word, in the pixel coordinates of the raster the OCR ran on
     *  (origin at the top-left). */
    public static final class OcrWord {
        public final String text;
        public final float x, y, w, h;

        public OcrWord(String text, float x, float y, float w, float h) {
            this.text = text;
            this.x = x; this.y = y; this.w = w; this.h = h;
        }
    }

    /** Everything recognised on one page. */
    public static final class PageText {
        public final int page;      // 1-based
        public final int imgW, imgH;
        public final List<OcrWord> words;

        public PageText(int page, int imgW, int imgH, List<OcrWord> words) {
            this.page = page; this.imgW = imgW; this.imgH = imgH; this.words = words;
        }
    }

    /** Where the text baseline sits inside a word box (fraction from the top). */
    private static final float BASELINE_FRACTION = 0.82f;
    /** Glyph size relative to the box height. */
    private static final float FONT_HEIGHT_FRACTION = 0.92f;

    /**
     * Add an invisible, selectable text layer built from OCR results, so a scanned
     * PDF becomes searchable and its text can be copied. The page looks identical:
     * the glyphs are drawn in rendering mode 3 ("neither fill nor stroke").
     */
    public static void addTextLayer(File src, List<PageText> pages, File out) throws Exception {
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            for (PageText pt : pages) {
                if (pt == null || pt.page < 1 || pt.page > total) continue;
                if (pt.words.isEmpty() || pt.imgW <= 0 || pt.imgH <= 0) continue;
                PDPage page = d.getPage(pt.page - 1);
                PDRectangle box = page.getCropBox();
                float w = box.getWidth(), h = box.getHeight();
                int r = ((page.getRotation() % 360) + 360) % 360;
                // Displayed page size (the raster was produced in the displayed frame).
                float dw = (r == 90 || r == 270) ? h : w;
                float dh = (r == 90 || r == 270) ? w : h;

                try (PDPageContentStream cs =
                             new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                    cs.setRenderingMode(com.tom_roush.pdfbox.pdmodel.graphics.state.RenderingMode.NEITHER);
                    cs.beginText();
                    for (int wi = 0; wi < pt.words.size(); wi++) {
                        OcrWord word = pt.words.get(wi);
                        // Characters Helvetica cannot encode (Hindi, rupee sign, em dash)
                        // used to be written as "?" - which put a fake word in the search
                        // index. Such a word is now skipped instead: no junk, and the words
                        // that can be encoded are still there.
                        String txt = ocrEncodable(word.text);
                        if (txt.isEmpty()) continue;
                        float xd = word.x / pt.imgW * dw;
                        float yd = (word.y + word.h * BASELINE_FRACTION) / pt.imgH * dh;
                        float hd = word.h / pt.imgH * dh;
                        float targetW = word.w / pt.imgW * dw;
                        // Derive the size from the box WIDTH so the placed run matches the
                        // ink width (that is what selection and highlighting follow). Fall
                        // back to the box height, and keep the result sane.
                        float emWidth = PDType1Font.HELVETICA.getStringWidth(txt) / 1000f;
                        float byHeight = hd * FONT_HEIGHT_FRACTION;
                        float size;
                        if (emWidth > 0.02f && targetW > 0.5f) {
                            size = targetW / emWidth;
                            size = Math.max(byHeight * 0.5f, Math.min(byHeight * 1.6f, size));
                        } else {
                            size = byHeight;
                        }
                        size = Math.max(1f, size);
                        // displayed point -> page point (same mapping the cropper uses)
                        float px, py;
                        switch (r) {
                            case 90:  px = yd;      py = xd;      break;
                            case 180: px = w - xd;  py = yd;      break;
                            case 270: px = w - yd;  py = h - xd;  break;
                            default:  px = xd;      py = h - yd;  break;
                        }
                        cs.setFont(PDType1Font.HELVETICA, size);
                        // rotate the run so it reads upright once the page /Rotate is applied
                        cs.setTextMatrix(Matrix.getRotateInstance(Math.toRadians(r), px, py));
                        cs.showText(txt);
                    }
                    cs.endText();
                }
            }
            d.save(out);
        }
    }

    // ------------------------------------------------------------------
    // Text search and hyperlinks
    // ------------------------------------------------------------------

    /** A text match, located on the page in DISPLAY points (origin top-left, y down),
     *  i.e. the same frame the page is rendered in. */
    public static final class Match {
        public final int page;          // 1-based
        public final float x, y, w, h;
        public final String context;

        public Match(int page, float x, float y, float w, float h, String context) {
            this.page = page; this.x = x; this.y = y; this.w = w; this.h = h;
            this.context = context;
        }
    }

    /** A detected or added hyperlink. */
    public static final class FoundLink {
        public final int page;
        public final float x, y, w, h;   // display points
        public final String url;

        public FoundLink(int page, float x, float y, float w, float h, String url) {
            this.page = page; this.x = x; this.y = y; this.w = w; this.h = h;
            this.url = url;
        }
    }

    /**
     * Walks the WHOLE document once, keeping every glyph with its position and the
     * page it belongs to. Doing this in a single pass is what makes search fast:
     * re-parsing per page turned a 100-page search into a hundred parses.
     */
    private static final class PositionedText extends com.tom_roush.pdfbox.text.PDFTextStripper {
        final List<String> chars = new ArrayList<>();
        final List<com.tom_roush.pdfbox.text.TextPosition> pos = new ArrayList<>();
        final List<Integer> page = new ArrayList<>();

        PositionedText() throws java.io.IOException {
            super();
            setSortByPosition(true);
        }

        @Override
        protected void writeString(String text,
                                   List<com.tom_roush.pdfbox.text.TextPosition> tps) {
            if (tps == null) return;
            int pg = getCurrentPageNo();
            for (com.tom_roush.pdfbox.text.TextPosition tp : tps) {
                String u = tp.getUnicode();
                if (u == null || u.isEmpty()) continue;
                chars.add(u);
                pos.add(tp);
                page.add(pg);
            }
            chars.add(" ");
            pos.add(null);          // marks a word break
            page.add(pg);
        }

        String text() {
            StringBuilder b = new StringBuilder(chars.size());
            for (String c : chars) b.append(c);
            return b.toString();
        }

        /** The page of the first real glyph at or after [from]. */
        int pageAt(int from) {
            for (int k = Math.max(0, from); k < pos.size(); k++) {
                if (pos.get(k) != null) return page.get(k);
            }
            return -1;
        }
    }

    private static PositionedText positionedText(PDDocument d) throws Exception {
        PositionedText pt = new PositionedText();
        pt.setSortByPosition(true);
        pt.getText(d);          // one pass over the whole document
        return pt;
    }

    /** Crop-box size and /Rotate for every page, so results can be mapped cheaply. */
    private static float[][] pageGeom(PDDocument d) throws Exception {
        int n = d.getNumberOfPages();
        float[][] g = new float[n + 1][3];
        for (int p = 1; p <= n; p++) {
            PDPage pg = d.getPage(p - 1);
            PDRectangle cb = pg.getCropBox();
            g[p][0] = cb.getWidth();
            g[p][1] = cb.getHeight();
            g[p][2] = ((pg.getRotation() % 360) + 360) % 360;
        }
        return g;
    }

    /** Union of the glyph boxes in [from, to) as (x, yTop, w, h) in display points. */
    private static float[] boxOf(PositionedText pt, int from, int to) {
        float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
        float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
        int seen = 0;
        for (int k = from; k < to && k < pt.pos.size(); k++) {
            com.tom_roush.pdfbox.text.TextPosition tp = pt.pos.get(k);
            if (tp == null) continue;
            float x = tp.getXDirAdj();
            float h = tp.getHeightDir();
            // getYDirAdj() is the baseline; the ink sits above it
            float yTop = tp.getYDirAdj() - h;
            minX = Math.min(minX, x);
            minY = Math.min(minY, yTop);
            maxX = Math.max(maxX, x + tp.getWidthDirAdj());
            maxY = Math.max(maxY, yTop + h);
            seen++;
        }
        if (seen == 0) return null;
        return new float[]{minX, minY, maxX - minX, maxY - minY};
    }

    /** PDFTextStripper reports unrotated page coordinates; the UI works in the
     *  displayed frame, so convert. Both are y-down. */
    private static float[] unrotatedToDisplay(float w, float h, int r,
                                              float x, float y, float bw, float bh) {
        switch (r) {
            case 90:  return new float[]{h - y - bh, x, bh, bw};
            case 180: return new float[]{w - x - bw, h - y - bh, bw, bh};
            case 270: return new float[]{y, w - x - bw, bh, bw};
            default:  return new float[]{x, y, bw, bh};
        }
    }

    /** A word on a page, in display points. */
    public static final class Word {
        public final int page;
        public final String text;
        public final float x, y, w, h;

        public Word(int page, String text, float x, float y, float w, float h) {
            this.page = page; this.text = text; this.x = x; this.y = y; this.w = w; this.h = h;
        }
    }

    /**
     * The text of a document, already measured. Building this once makes repeated
     * searches instant and lets the reader look up the word under a finger.
     * Only plain values are kept, so the document can be closed afterwards.
     */
    public static final class TextIndex {
        public final String text;
        final float[] gx, gy, gw, gh;   // per glyph, unrotated frame, y down
        final int[] pageOf;
        final float[][] geom;           // per page: {cropW, cropH, rotation}
        final int[] spaces;             // glyph index just after a whitespace char

        TextIndex(String text, float[] gx, float[] gy, float[] gw, float[] gh,
                  int[] pageOf, float[][] geom, int[] spaces) {
            this.text = text; this.gx = gx; this.gy = gy; this.gw = gw; this.gh = gh;
            this.pageOf = pageOf; this.geom = geom; this.spaces = spaces;
        }
    }

    /** Measure the whole document once. */
    public static TextIndex indexText(File src) throws Exception {
        try (PDDocument d = open(src)) {
            PositionedText pt = positionedText(d);
            float[][] geom = pageGeom(d);
            int n = pt.chars.size();
            float[] gx = new float[n], gy = new float[n], gw = new float[n], gh = new float[n];
            int[] pageOf = new int[n];
            StringBuilder b = new StringBuilder(n);
            List<Integer> breaks = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                com.tom_roush.pdfbox.text.TextPosition tp = pt.pos.get(i);
                b.append(pt.chars.get(i));
                pageOf[i] = pt.page.get(i);
                if (tp == null) {
                    breaks.add(i);
                    continue;
                }
                gx[i] = tp.getXDirAdj();
                gh[i] = tp.getHeightDir();
                gy[i] = tp.getYDirAdj() - gh[i];
                gw[i] = tp.getWidthDirAdj();
            }
            int[] spaces = new int[breaks.size()];
            for (int i = 0; i < breaks.size(); i++) spaces[i] = breaks.get(i);
            return new TextIndex(b.toString(), gx, gy, gw, gh, pageOf, geom, spaces);
        }
    }

    /** Box of the glyphs in [from, to) in the unrotated frame. */
    private static float[] indexBox(TextIndex idx, int from, int to) {
        float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
        float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
        int seen = 0;
        for (int k = from; k < to && k < idx.gx.length; k++) {
            if (idx.gw[k] <= 0f && idx.gh[k] <= 0f) continue;   // whitespace marker
            minX = Math.min(minX, idx.gx[k]);
            minY = Math.min(minY, idx.gy[k]);
            maxX = Math.max(maxX, idx.gx[k] + idx.gw[k]);
            maxY = Math.max(maxY, idx.gy[k] + idx.gh[k]);
            seen++;
        }
        return seen == 0 ? null : new float[]{minX, minY, maxX - minX, maxY - minY};
    }

    /** Search a pre-built index. Empty query returns nothing. */
    public static List<Match> searchIndex(TextIndex idx, String query, boolean matchCase) {
        List<Match> out = new ArrayList<>();
        if (idx == null || query == null || query.trim().isEmpty()) return out;
        String hay = matchCase ? idx.text : idx.text.toLowerCase();
        String needle = matchCase ? query : query.toLowerCase();
        int from = 0;
        while (true) {
            int i = hay.indexOf(needle, from);
            if (i < 0) break;
            int pg = -1;
            for (int k = i; k < idx.pageOf.length; k++) {
                if (idx.gw[k] > 0f || idx.gh[k] > 0f) { pg = idx.pageOf[k]; break; }
            }
            float[] b = indexBox(idx, i, i + needle.length());
            if (b != null && pg >= 1 && pg < idx.geom.length) {
                float[] db = unrotatedToDisplay(idx.geom[pg][0], idx.geom[pg][1],
                        (int) idx.geom[pg][2], b[0], b[1], b[2], b[3]);
                int cs = Math.max(0, i - 28);
                int ce = Math.min(idx.text.length(), i + needle.length() + 28);
                out.add(new Match(pg, db[0], db[1], db[2], db[3],
                        idx.text.substring(cs, ce).replace('\n', ' ').trim()));
            }
            from = i + Math.max(1, needle.length());
        }
        return out;
    }

    /** Every word on a page, in display points, for tap-to-copy. */
    public static List<Word> wordsOnPage(TextIndex idx, int page) {
        List<Word> out = new ArrayList<>();
        if (idx == null) return out;
        int start = -1;
        for (int i = 0; i <= idx.text.length(); i++) {
            boolean blank = i == idx.text.length() || Character.isWhitespace(idx.text.charAt(i))
                    || (idx.gw[i] <= 0f && idx.gh[i] <= 0f);
            if (!blank && start < 0) start = i;
            if (blank && start >= 0) {
                int pg = -1;
                for (int k = start; k < i; k++) {
                    if (idx.gw[k] > 0f || idx.gh[k] > 0f) { pg = idx.pageOf[k]; break; }
                }
                if (pg == page) {
                    float[] b = indexBox(idx, start, i);
                    if (b != null) {
                        float[] db = unrotatedToDisplay(idx.geom[pg][0], idx.geom[pg][1],
                                (int) idx.geom[pg][2], b[0], b[1], b[2], b[3]);
                        out.add(new Word(pg, idx.text.substring(start, i),
                                db[0], db[1], db[2], db[3]));
                    }
                }
                start = -1;
            }
        }
        return out;
    }

    /** All the text on one page, as a reader would read it. */
    public static String pageText(File src, int page1) throws Exception {
        try (PDDocument d = open(src)) {
            if (page1 < 1 || page1 > d.getNumberOfPages()) return "";
            com.tom_roush.pdfbox.text.PDFTextStripper st =
                    new com.tom_roush.pdfbox.text.PDFTextStripper();
            st.setStartPage(page1);
            st.setEndPage(page1);
            st.setSortByPosition(true);
            String t = st.getText(d);
            return t == null ? "" : t.trim();
        }
    }

    /** Find every occurrence of [query]. Empty query returns nothing. */
    public static List<Match> search(File src, String query, boolean matchCase) throws Exception {
        if (query == null || query.trim().isEmpty()) return new ArrayList<>();
        return searchIndex(indexText(src), query, matchCase);
    }

    /** URL / e-mail shapes worth turning into links. */
    /**
     * Anything that looks like an address: with or without a scheme, any common
     * top-level domain, with or without a path - plus plain e-mail addresses.
     * Deliberately permissive; the page geometry check throws out the nonsense.
     */
    private static final java.util.regex.Pattern URL_PATTERN = java.util.regex.Pattern.compile(
            "(?i)((?:https?://|ftp://|www\\.)[^\\s<>\"')]+"
            + "|(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+"
            + "(?:com|net|org|in|io|co|edu|gov|info|biz|me|app|dev|xyz|online|site|store|club|live|tv|cc|us|uk|de|fr|jp|au|ca|ru|ai|link|top|win|bid|download|stream"
            // second-level names that matter in India and the UK, so a link like
            // nic.in or co.uk is found instead of being read as two words
            + "|co\\.in|org\\.in|net\\.in|ac\\.in|gov\\.in|nic\\.in|edu\\.in|res\\.in|firm\\.in|gen\\.in|ind\\.in"
            + "|co\\.uk|org\\.uk|ac\\.uk|gov\\.uk|me\\.uk|co\\.jp|com\\.au|com\\.br|co\\.za|com\\.sg)"
            + "(?:/[^\\s<>\"')]*)?"
            + "|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,})");

    /** Every URL / e-mail address found in the document's text, with its position. */
    public static List<FoundLink> findLinks(File src) throws Exception {
        List<FoundLink> out = new ArrayList<>();
        try (PDDocument d = open(src)) {
            PositionedText pt = positionedText(d);
            float[][] g = pageGeom(d);
            String text = pt.text();
            java.util.regex.Matcher m = URL_PATTERN.matcher(text);
            while (m.find()) {
                String raw = m.group();
                String url = raw.replaceAll("[.,;:!?]+$", "");
                if (url.length() < 4) continue;
                int pg = pt.pageAt(m.start());
                if (pg < 1 || pg >= g.length) continue;
                float[] b = boxOf(pt, m.start(), m.start() + url.length());
                if (b == null) continue;
                float[] db = unrotatedToDisplay(g[pg][0], g[pg][1], (int) g[pg][2],
                        b[0], b[1], b[2], b[3]);
                // a link must cover its own text, never swallow the page
                if (db[2] * db[3] > g[pg][0] * g[pg][1] * 0.25f) continue;
                out.add(new FoundLink(pg, db[0], db[1], db[2], db[3], url));
            }
            // and the real link annotations already in the file - those have no
            // visible URL text, which is why plain text scanning missed them
            for (FoundLink l : linkAnnotations(d, g)) {
                boolean dup = false;
                for (FoundLink e : out) {
                    if (e.page == l.page && Math.abs(e.x - l.x) < 2f && Math.abs(e.y - l.y) < 2f) { dup = true; break; }
                }
                if (!dup) out.add(l);
            }
        }
        return out;
    }

    /** Every /Link annotation with a URI action, in the page's display frame. */
    private static List<FoundLink> linkAnnotations(PDDocument d, float[][] g) throws Exception {
        List<FoundLink> out = new ArrayList<>();
        int n = d.getNumberOfPages();
        for (int i = 0; i < n; i++) {
            PDPage page = d.getPage(i);
            int pg = i + 1;
            if (pg >= g.length) continue;
            for (PDAnnotation a : page.getAnnotations()) {
                if (!(a instanceof PDAnnotationLink)) continue;
                PDAction act = ((PDAnnotationLink) a).getAction();
                String uri = null;
                if (act instanceof PDActionURI) uri = ((PDActionURI) act).getURI();
                if (uri == null || uri.trim().isEmpty()) continue;
                PDRectangle r = a.getRectangle();
                if (r == null) continue;
                float[] db = pageToDisplay(g[pg][0], g[pg][1], (int) g[pg][2],
                        r.getLowerLeftX(), r.getLowerLeftY(), r.getWidth(), r.getHeight());
                if (db[2] <= 0 || db[3] <= 0) continue;
                if (db[2] * db[3] > g[pg][0] * g[pg][1] * 0.5f) continue;   // not a whole-page link
                out.add(new FoundLink(pg, db[0], db[1], db[2], db[3], uri.trim()));
            }
        }
        return out;
    }

    /** Every link on every page, keyed by 1-based page number, in one pass. */
    public static java.util.Map<Integer, List<FoundLink>> allPageLinks(File src) {
        java.util.Map<Integer, List<FoundLink>> out = new java.util.HashMap<>();
        try (PDDocument d = open(src)) {
            float[][] g = pageGeom(d);
            for (FoundLink l : linkAnnotations(d, g)) {
                List<FoundLink> list = out.get(l.page);
                if (list == null) { list = new ArrayList<>(); out.put(l.page, list); }
                list.add(l);
            }
        } catch (Exception ignored) {
        }
        return out;
    }

    /** The link targets on one page (1-based), for tapping in the reader. */
    public static List<FoundLink> pageLinks(File src, int page) {
        List<FoundLink> out = new ArrayList<>();
        try (PDDocument d = open(src)) {
            float[][] g = pageGeom(d);
            if (page < 1 || page > d.getNumberOfPages()) return out;
            for (FoundLink l : linkAnnotations(d, g)) if (l.page == page) out.add(l);
        } catch (Exception ignored) {
        }
        return out;
    }

    /** Turn a display-frame box into a page rectangle, honouring /Rotate. */
    private static PDRectangle displayBoxToPage(PDRectangle crop, int r,
                                                float xd, float yd, float wd, float hd) {
        float w = crop.getWidth(), h = crop.getHeight();
        float[][] corners = {{xd, yd}, {xd + wd, yd}, {xd, yd + hd}, {xd + wd, yd + hd}};
        float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
        float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
        for (float[] c : corners) {
            float px, py;
            switch (r) {
                case 90:  px = c[1];      py = c[0];      break;
                case 180: px = w - c[0];  py = c[1];      break;
                case 270: px = w - c[1];  py = h - c[0];  break;
                default:  px = c[0];      py = h - c[1];  break;
            }
            minX = Math.min(minX, px); maxX = Math.max(maxX, px);
            minY = Math.min(minY, py); maxY = Math.max(maxY, py);
        }
        return new PDRectangle(minX, minY, maxX - minX, maxY - minY);
    }

    /**
     * The exact inverse of {@link #displayBoxToPage}.
     *
     * displayBoxToPage turns a box the user drew (y measured down from the top) into
     * a page rectangle (y measured up from the bottom). Reading a link back has to
     * undo that flip, or the link sits mirrored down the page and a tap on it never
     * matches. Kept separate from unrotatedToDisplay so text lookups are untouched.
     */
    private static float[] pageToDisplay(float w, float h, int r,
                                         float x, float y, float bw, float bh) {
        switch (r) {
            // displayBoxToPage maps a corner (c0,c1) to (px,py); these undo it exactly
            case 90:  return new float[]{y, x, bh, bw};
            case 180: return new float[]{w - x - bw, y, bw, bh};
            case 270: return new float[]{h - y - bh, w - x - bw, bh, bw};
            default:  return new float[]{x, h - y - bh, bw, bh};
        }
    }

    /** Attach real link annotations for the given links. Returns how many were added. */
    public static int addLinks(File src, List<FoundLink> links, File out) throws Exception {
        int added = 0;
        try (PDDocument d = open(src)) {
            int total = d.getNumberOfPages();
            for (FoundLink l : links) {
                if (l == null || l.page < 1 || l.page > total) continue;
                String url = normaliseUrl(l.url);
                if (url == null) continue;
                PDPage page = d.getPage(l.page - 1);
                PDRectangle crop = page.getCropBox();
                int r = ((page.getRotation() % 360) + 360) % 360;
                // never let a link cover a large part of the page
                if (l.w * l.h > crop.getWidth() * crop.getHeight() * 0.25f) continue;
                PDRectangle rect = displayBoxToPage(crop, r, l.x, l.y, l.w, l.h);
                // a link needs a little padding to be comfortably tappable
                rect.setLowerLeftX(rect.getLowerLeftX() - 1f);
                rect.setLowerLeftY(rect.getLowerLeftY() - 1f);
                rect.setUpperRightX(rect.getUpperRightX() + 1f);
                rect.setUpperRightY(rect.getUpperRightY() + 1f);

                com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink link =
                        new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink();
                link.setRectangle(rect);
                link.setBorderStyle(new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDBorderStyleDictionary());
                link.getBorderStyle().setWidth(0f);
                com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI action =
                        new com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI();
                action.setURI(url);
                link.setAction(action);
                page.getAnnotations().add(link);
                added++;
            }
            d.save(out);
        }
        return added;
    }

    /** Add a single link over a rectangle given in display points. */
    /**
     * Draw a picture on a page AND put the link exactly on it, in one pass - so the
     * file is written once and the picture is never re-compressed. Coordinates are
     * the same displayed frame as addLink: xd/yd from the top-left, wd/hd as a
     * fraction of the page.
     */
    /**
     * The picture's own size as a fraction of the page, so an empty width or height
     * field can mean "leave it as it is". Same 96dpi -> 72dpi conversion the picture
     * watermark uses, so both tools treat "original size" identically.
     *
     * @return { widthFraction, heightFraction }
     */
    public static float[] imageNaturalFraction(File src, int page1, File image) throws Exception {
        try (PDDocument d = open(src)) {
            PDPage page = d.getPage(page1 - 1);
            PDRectangle box = page.getCropBox();
            PDImageXObject img = PDImageXObject.createFromFile(image.getAbsolutePath(), d);
            float w = img.getWidth() * 0.75f / Math.max(1f, box.getWidth());
            float h = img.getHeight() * 0.75f / Math.max(1f, box.getHeight());
            return new float[]{w, h};
        }
    }

    public static void addImageLink(File src, int page1, File image,
                                    float xd, float yd, float wd, float hd,
                                    float opacity, String url, File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        try (PDDocument d = open(src)) {
            PDPage page = d.getPage(page1 - 1);
            PDRectangle box = page.getCropBox();
            float px = box.getLowerLeftX() + xd * box.getWidth();
            float py = box.getLowerLeftY() + (1f - yd - hd) * box.getHeight();
            float pw = Math.max(1f, wd * box.getWidth());
            float ph = Math.max(1f, hd * box.getHeight());
            PDImageXObject img = PDImageXObject.createFromFile(image.getAbsolutePath(), d);
            try (PDPageContentStream cs = new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                if (opacity < 0.999f) {
                    PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
                    gs.setNonStrokingAlphaConstant(Math.max(0.05f, opacity));
                    cs.setGraphicsStateParameters(gs);
                }
                cs.drawImage(img, px, py, pw, ph);
            }
            PDAnnotationLink link = new PDAnnotationLink();
            link.setRectangle(new PDRectangle(px, py, pw, ph));
            PDActionURI uri = new PDActionURI();
            uri.setURI(u);
            link.setAction(uri);
            page.getAnnotations().add(link);
            d.save(out);
        }
    }

    public static void addLink(File src, int page1, float xd, float yd, float wd, float hd,
                               String url, File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        FoundLink l = new FoundLink(page1, xd, yd, wd, hd, u);
        addLinks(src, java.util.Collections.singletonList(l), out);
    }

    /**
     * Draw a VISIBLE link icon at a spot in the displayed frame and put the link
     * exactly on the icon, so only a tap on the icon opens it.
     */
    public static void addLinkIcon(File src, int page1, float xd, float yd, float size,
                                   File iconPng, String url, float opacity,
                                   File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        try (PDDocument d = open(src)) {
            drawIcon(d, page1, xd, yd, size, iconPng, u, opacity);
            d.save(out);
        }
    }

    /** Put the same icon at the same spot on EVERY page, saving once. */
    public static void addLinkIconAllPages(File src, float xd, float yd, float size,
                                           File iconPng, String url, float opacity,
                                           File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        try (PDDocument d = open(src)) {
            for (int p = 1; p <= d.getNumberOfPages(); p++) {
                try {
                    drawIcon(d, p, xd, yd, size, iconPng, u, opacity);
                } catch (Exception ignore) { }
            }
            d.save(out);
        }
    }

    private static void drawIcon(PDDocument d, int page1, float xd, float yd, float size,
                                 File iconPng, String url, float opacity) throws Exception {
        if (page1 < 1 || page1 > d.getNumberOfPages()) {
            throw new IllegalArgumentException("No such page");
        }
        PDPage page = d.getPage(page1 - 1);
        PDRectangle crop = page.getCropBox();
        float w = crop.getWidth(), h = crop.getHeight();
        int r = ((page.getRotation() % 360) + 360) % 360;
        float dw = (r == 90 || r == 270) ? h : w;
        float dh = (r == 90 || r == 270) ? w : h;

        float s = Math.max(10f, Math.min(size, Math.min(dw, dh) * 0.5f));
        xd = Math.max(0f, Math.min(xd, dw - s));
        yd = Math.max(0f, Math.min(yd, dh - s));

        if (iconPng != null && iconPng.exists()) {
            PDImageXObject icon = PDImageXObject.createFromFile(iconPng.getAbsolutePath(), d);
            Matrix m;
            switch (r) {
                case 90:  m = new Matrix(0, 1, -1, 0, w, 0); break;
                case 180: m = new Matrix(-1, 0, 0, -1, w, h); break;
                case 270: m = new Matrix(0, -1, 1, 0, 0, h); break;
                default:  m = new Matrix(1, 0, 0, 1, 0, 0); break;
            }
            try (PDPageContentStream cs =
                         new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
                cs.saveGraphicsState();
                cs.transform(m);
                applyOpacity(cs, opacity);
                cs.drawImage(icon, xd, dh - yd - s, s, s);
                cs.restoreGraphicsState();
            }
        }

        PDRectangle rect = displayBoxToPage(crop, r, xd, yd, s, s);
        com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink link =
                new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink();
        link.setRectangle(rect);
        link.setBorderStyle(new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDBorderStyleDictionary());
        link.getBorderStyle().setWidth(0f);
        com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI action =
                new com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI();
        action.setURI(url);
        link.setAction(action);
        page.getAnnotations().add(link);
    }

    /** Apply a non-stroking alpha, used for the opacity of drawn link art. */
    private static void applyOpacity(PDPageContentStream cs, float opacity) throws java.io.IOException {
        float a = Math.max(0.05f, Math.min(1f, opacity));
        if (a >= 1f) return;
        PDExtendedGraphicsState gs = new PDExtendedGraphicsState();
        gs.setNonStrokingAlphaConstant(a);
        cs.setGraphicsStateParameters(gs);
    }

    /** The standard PDF fonts offered for custom link text. */
    public static final String[] LINK_FONTS = {
            "Helvetica", "Helvetica Bold", "Times", "Times Bold", "Courier"
    };

    private static PDType1Font pickFont(String name) {
        if (name == null) return PDType1Font.HELVETICA;
        switch (name) {
            case "Helvetica Bold": return PDType1Font.HELVETICA_BOLD;
            case "Times":          return PDType1Font.TIMES_ROMAN;
            case "Times Bold":     return PDType1Font.TIMES_BOLD;
            case "Courier":        return PDType1Font.COURIER;
            default:               return PDType1Font.HELVETICA;
        }
    }

    /**
     * Write VISIBLE custom text on a page in the chosen font, size and colour, and
     * make that text a link. Tapping the text opens the address; tapping anywhere
     * else does nothing.
     */
    public static void addTextLink(File src, int page1, float xd, float yd, float size,
                                   String text, String fontName, int argb,
                                   String url, float opacity, File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        String safe = winAnsi(text);
        if (safe == null || safe.trim().isEmpty()) {
            throw new IllegalArgumentException("Enter the text to show");
        }
        try (PDDocument d = open(src)) {
            drawText(d, page1, xd, yd, size, safe, fontName, argb, u, opacity);
            d.save(out);
        }
    }

    /** Write the same link text at the same spot on EVERY page, saving once. */
    public static void addTextLinkAllPages(File src, float xd, float yd, float size,
                                           String text, String fontName, int argb,
                                           String url, float opacity, File out) throws Exception {
        String u = normaliseUrl(url);
        if (u == null) throw new IllegalArgumentException("Not a valid link");
        String safe = winAnsi(text);
        if (safe == null || safe.trim().isEmpty()) {
            throw new IllegalArgumentException("Enter the text to show");
        }
        try (PDDocument d = open(src)) {
            for (int p = 1; p <= d.getNumberOfPages(); p++) {
                try {
                    drawText(d, p, xd, yd, size, safe, fontName, argb, u, opacity);
                } catch (Exception ignore) { }
            }
            d.save(out);
        }
    }

    private static void drawText(PDDocument d, int page1, float xd, float yd, float size,
                                 String safe, String fontName, int argb,
                                 String url, float opacity) throws Exception {
        if (page1 < 1 || page1 > d.getNumberOfPages()) {
            throw new IllegalArgumentException("No such page");
        }
        float sz = Math.max(6f, Math.min(size, 144f));
        PDPage page = d.getPage(page1 - 1);
        PDRectangle crop = page.getCropBox();
        float w = crop.getWidth(), h = crop.getHeight();
        int r = ((page.getRotation() % 360) + 360) % 360;
        float dw = (r == 90 || r == 270) ? h : w;
        float dh = (r == 90 || r == 270) ? w : h;

        PDType1Font font = pickFont(fontName);
        float tw = font.getStringWidth(safe) / 1000f * sz;
        float th = sz * 1.3f;
        xd = Math.max(0f, Math.min(xd, Math.max(0f, dw - tw)));
        yd = Math.max(0f, Math.min(yd, Math.max(0f, dh - th)));
        float baseY = yd + sz * 0.82f;

        float px, py;
        switch (r) {
            case 90:  px = baseY;      py = xd;         break;
            case 180: px = w - xd;     py = baseY;      break;
            case 270: px = w - baseY;  py = h - xd;     break;
            default:  px = xd;         py = h - baseY;  break;
        }
        try (PDPageContentStream cs =
                     new PDPageContentStream(d, page, AppendMode.APPEND, true, true)) {
            applyOpacity(cs, opacity);
            cs.beginText();
            cs.setFont(font, sz);
            cs.setNonStrokingColor((argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF);
            cs.setTextMatrix(Matrix.getRotateInstance(Math.toRadians(r), px, py));
            cs.showText(safe);
            cs.endText();
        }

        PDRectangle rect = displayBoxToPage(crop, r, xd, yd, tw, th);
        com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink link =
                new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink();
        link.setRectangle(rect);
        link.setBorderStyle(new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDBorderStyleDictionary());
        link.getBorderStyle().setWidth(0f);
        com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI action =
                new com.tom_roush.pdfbox.pdmodel.interactive.action.PDActionURI();
        action.setURI(url);
        link.setAction(action);
        page.getAnnotations().add(link);
    }

    /** "example.com" -> "https://example.com"; mail addresses become mailto:. */
    public static String normaliseUrl(String raw) {
        if (raw == null) return null;
        String s = raw.trim();
        if (s.isEmpty()) return null;
        String lower = s.toLowerCase();
        if (lower.startsWith("http://") || lower.startsWith("https://")) return s;
        if (s.contains("@") && !s.contains(" ")) return "mailto:" + s;
        if (lower.startsWith("www.")) return "https://" + s;
        if (lower.matches("[a-z0-9.-]+\\.[a-z]{2,}(/.*)?")) return "https://" + s;
        return null;
    }

    // ------------------------------------------------------------------
    // Bookmarks (the outline every reader shows in its sidebar)
    // ------------------------------------------------------------------

    /** One entry in a document's outline. */
    public static final class Bookmark {
        public final String title;
        public final int page;    // 1-based
        public final int depth;   // 0 = top level

        public Bookmark(String title, int page) { this(title, page, 0); }

        public Bookmark(String title, int page, int depth) {
            this.title = title == null ? "" : title;
            this.page = page;
            this.depth = Math.max(0, depth);
        }
    }

    /** Read the outline. Empty when the document has none. */
    public static List<Bookmark> bookmarks(File src) throws Exception {
        List<Bookmark> out = new ArrayList<>();
        try (PDDocument d = open(src)) {
            PDDocumentOutline outline = d.getDocumentCatalog().getDocumentOutline();
            if (outline != null) collectOutline(outline.getFirstChild(), d, out, 0);
        }
        return out;
    }

    private static void collectOutline(PDOutlineItem first, PDDocument d,
                                       List<Bookmark> out, int depth) throws Exception {
        if (first == null || depth > 12) return;
        PDOutlineItem item = first;
        int guard = 0;
        while (item != null && guard++ < 5000) {
            int page = 1;
            try {
                PDPage dest = item.findDestinationPage(d);
                if (dest != null) page = d.getPages().indexOf(dest) + 1;
            } catch (Exception ignored) { }
            out.add(new Bookmark(item.getTitle(), page, depth));
            PDOutlineItem child = item.getFirstChild();
            if (child != null) collectOutline(child, d, out, depth + 1);
            item = item.getNextSibling();
        }
    }

    /** Replace the outline with exactly these entries, in this order. */
    public static void setBookmarks(File src, List<Bookmark> marks, File out) throws Exception {
        try (PDDocument d = open(src)) {
            PDDocumentOutline outline = new PDDocumentOutline();
            d.getDocumentCatalog().setDocumentOutline(outline);
            int n = d.getNumberOfPages();
            if (marks != null && !marks.isEmpty()) {
                PDOutlineItem lastTop = null;
                for (Bookmark b : marks) {
                    int page = Math.max(1, Math.min(b.page, n));
                    PDOutlineItem item = new PDOutlineItem();
                    item.setTitle(b.title.trim().isEmpty() ? ("Page " + page) : b.title.trim());
                    item.setDestination(d.getPage(page - 1));
                    if (b.depth <= 0 || lastTop == null) {
                        outline.addLast(item);
                        lastTop = item;
                    } else {
                        lastTop.addLast(item);   // one level of nesting is plenty here
                    }
                }
                outline.openNode();
            }
            d.save(out);
        }
    }

    // ------------------------------------------------------------------
    // Designed report (used by the activity-log export)
    // ------------------------------------------------------------------

    /** One column of a report table. */
    public static final class Column {
        public final String title;
        public final float weight;
        public Column(String title, float weight) { this.title = title; this.weight = weight; }
    }

    private static final float R_MARGIN = 42f;

    /**
     * A designed, printable report: a coloured header band, a facts card, a
     * striped table, and a footer. Everything is vector-drawn, so it stays crisp
     * at any zoom.
     */
    public static void report(File out, String brand, String title, String subtitle,
                              List<String[]> facts, List<Column> columns,
                              List<String[]> rows, String footer, int accentArgb)
            throws Exception {
        report(out, brand, title, subtitle, facts, columns, rows, footer, accentArgb, null);
    }

    /**
     * As above, plus a details section: long entries (a crash report) get their own
     * heading and wrapped body instead of being squeezed into a one-line table cell.
     */
    public static void report(File out, String brand, String title, String subtitle,
                              List<String[]> facts, List<Column> columns,
                              List<String[]> rows, String footer, int accentArgb,
                              List<String[]> details)
            throws Exception {
        final float pageW = PDRectangle.A4.getWidth(), pageH = PDRectangle.A4.getHeight();
        final float contentW = pageW - R_MARGIN * 2f;
        final float body = 10f, small = 8.5f, leading = 14f;
        float ar = ((accentArgb >> 16) & 0xFF) / 255f;
        float ag = ((accentArgb >> 8) & 0xFF) / 255f;
        float ab = (accentArgb & 0xFF) / 255f;

        try (PDDocument d = new PDDocument()) {
            PDFont font = PDType1Font.HELVETICA, bold = PDType1Font.HELVETICA_BOLD;
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            PDPageContentStream cs = new PDPageContentStream(d, page);

            // ---- header band ----
            float bandH = 96f;
            cs.setNonStrokingColor(ar, ag, ab);
            cs.addRect(0, pageH - bandH, pageW, bandH);
            cs.fill();
            textAt(cs, bold, 9f, R_MARGIN, pageH - 30f, brand, 1f, 1f, 1f);
            textAt(cs, bold, 21f, R_MARGIN, pageH - 56f, title, 1f, 1f, 1f);
            if (subtitle != null && !subtitle.isEmpty()) {
                textAt(cs, font, 10f, R_MARGIN, pageH - 76f, subtitle, 1f, 1f, 1f);
            }
            float y = pageH - bandH - 26f;

            // ---- facts card ----
            if (facts != null && !facts.isEmpty()) {
                float cardH = 16f + facts.size() * 17f;
                cs.setNonStrokingColor(0.965f, 0.968f, 0.976f);
                fillRounded(cs, R_MARGIN, y - cardH, contentW, cardH, 12f);
                float fy = y - 22f;
                for (String[] f : facts) {
                    textAt(cs, bold, small, R_MARGIN + 14f, fy, f[0], 0.13f, 0.15f, 0.19f);
                    textAt(cs, font, small, R_MARGIN + 120f, fy, f.length > 1 ? f[1] : "",
                            0.34f, 0.37f, 0.42f);
                    fy -= 17f;
                }
                y -= cardH + 22f;
            }

            // ---- table ----
            if (columns != null && !columns.isEmpty()) {
                float totalW = 0f;
                for (Column c : columns) totalW += c.weight;
                float[] colW = new float[columns.size()];
                for (int i = 0; i < columns.size(); i++) colW[i] = contentW * columns.get(i).weight / totalW;

                // header row
                cs.setNonStrokingColor(ar * 0.14f + 0.86f, ag * 0.14f + 0.86f, ab * 0.14f + 0.86f);
                fillRounded(cs, R_MARGIN, y - 22f, contentW, 22f, 8f);
                float hx = R_MARGIN + 10f;
                for (int i = 0; i < columns.size(); i++) {
                    textAt(cs, bold, small, hx, y - 15f, columns.get(i).title, 0.13f, 0.15f, 0.19f);
                    hx += colW[i];
                }
                y -= 30f;

                int n = rows == null ? 0 : rows.size();
                for (int r = 0; r < n; r++) {
                    if (y < R_MARGIN + 40f) {
                        cs.close();
                        page = new PDPage(PDRectangle.A4);
                        d.addPage(page);
                        cs = new PDPageContentStream(d, page);
                        y = pageH - R_MARGIN;
                    }
                    if (r % 2 == 1) {
                        cs.setNonStrokingColor(0.976f, 0.980f, 0.988f);
                        cs.addRect(R_MARGIN, y - 15f, contentW, 18f);
                        cs.fill();
                    }
                    String[] row = rows.get(r);
                    float rx = R_MARGIN + 10f;
                    for (int i = 0; i < columns.size() && i < row.length; i++) {
                        String cell = row[i] == null ? "" : row[i];
                        float size = small;
                        // status column: green for OK, red for FAIL
                        if ("OK".equals(cell)) textAt(cs, bold, size, rx, y - 10f, cell, 0.09f, 0.55f, 0.26f);
                        else if ("FAIL".equals(cell)) textAt(cs, bold, size, rx, y - 10f, cell, 0.78f, 0.16f, 0.16f);
                        else if (i == 0) textAt(cs, font, size, rx, y - 10f, cell, 0.44f, 0.47f, 0.52f);
                        else textAt(cs, font, size, rx, y - 10f, fit(cell, colW[i] - 12f, font, size),
                                     0.20f, 0.22f, 0.27f);
                        rx += colW[i];
                    }
                    y -= 18f;
                }
            }

            // ---- details: long entries in full ----
            if (details != null && !details.isEmpty()) {
                y -= 14f;
                for (String[] det : details) {
                    String detHead = det.length > 0 && det[0] != null ? det[0] : "";
                    String detBody = det.length > 1 && det[1] != null ? det[1] : "";
                    List<String> detLines = wrapAll(detBody, contentW - 24f, font, 8.5f);
                    float need = 20f + detLines.size() * 11f + 10f;
                    if (y - need < R_MARGIN + 40f) {
                        cs.close();
                        page = new PDPage(PDRectangle.A4);
                        d.addPage(page);
                        cs = new PDPageContentStream(d, page);
                        y = pageH - R_MARGIN;
                    }
                    textAt(cs, bold, 9f, R_MARGIN, y, fit(detHead, contentW, bold, 9f), 0.13f, 0.15f, 0.19f);
                    y -= 13f;
                    for (String ln : detLines) {
                        if (y < R_MARGIN + 30f) {
                            cs.close();
                            page = new PDPage(PDRectangle.A4);
                            d.addPage(page);
                            cs = new PDPageContentStream(d, page);
                            y = pageH - R_MARGIN;
                        }
                        textAt(cs, font, 8.5f, R_MARGIN + 12f, y, ln, 0.28f, 0.31f, 0.36f);
                        y -= 11f;
                    }
                    y -= 8f;
                }
            }

            // ---- footer ----
            if (footer != null && !footer.isEmpty()) {
                textAt(cs, font, 8f, R_MARGIN, R_MARGIN - 14f, footer, 0.55f, 0.58f, 0.63f);
            }
            cs.close();
            d.save(out);
        }
    }

    private static void fillRounded(PDPageContentStream cs, float x, float y, float w, float h, float r)
            throws Exception {
        // four corner arcs plus a cross - a simple, reliable rounded rectangle
        float k = r * 0.5523f;
        cs.moveTo(x + r, y);
        cs.lineTo(x + w - r, y);
        cs.curveTo(x + w - r + k, y, x + w, y + r - k, x + w, y + r);
        cs.lineTo(x + w, y + h - r);
        cs.curveTo(x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h);
        cs.lineTo(x + r, y + h);
        cs.curveTo(x + r - k, y + h, x, y + h - r + k, x, y + h - r);
        cs.lineTo(x, y + r);
        cs.curveTo(x, y + r - k, x + r - k, y, x + r, y);
        cs.closePath();
        cs.fill();
    }

    /** Break text into lines that fit a width, honouring existing newlines. */
    private static List<String> wrapAll(String text, float maxW, PDFont f, float size) throws Exception {
        List<String> out = new ArrayList<>();
        if (text == null || text.isEmpty()) return out;
        for (String para : text.split("\n", -1)) {
            String safe = winAnsi(para);
            if (safe.isEmpty()) { out.add(""); continue; }
            StringBuilder line = new StringBuilder();
            for (String word : safe.split(" ")) {
                String probe = line.length() == 0 ? word : line + " " + word;
                if (f.getStringWidth(probe) / 1000f * size <= maxW || line.length() == 0) {
                    line.setLength(0);
                    line.append(probe);
                } else {
                    out.add(line.toString());
                    line.setLength(0);
                    line.append(word);
                }
            }
            if (line.length() > 0) out.add(line.toString());
        }
        return out;
    }

    /** Shorten a cell so it cannot spill into the next column. */
    private static String fit(String s, float maxW, PDFont f, float size) throws Exception {
        String t = winAnsi(s);
        if (f.getStringWidth(t) / 1000f * size <= maxW) return t;
        while (t.length() > 1 && f.getStringWidth(t + "\u2026") / 1000f * size > maxW) {
            t = t.substring(0, t.length() - 1);
        }
        return t + "...";
    }

    // ------------------------------------------------------------------
    // Plain-text report (kept for simple exports)
    // ------------------------------------------------------------------

    /** Lay wrapped text out into a clean, multi-page A4 PDF. */
    public static void reportPdf(File out, String title, List<String> lines) throws Exception {
        final float margin = 56f, leading = 15f, body = 10.5f, head = 17f;
        try (PDDocument d = new PDDocument()) {
            PDFont font = PDType1Font.HELVETICA;
            PDFont bold = PDType1Font.HELVETICA_BOLD;
            float pageW = PDRectangle.A4.getWidth(), pageH = PDRectangle.A4.getHeight();
            float maxW = pageW - margin * 2f;
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            PDPageContentStream cs = new PDPageContentStream(d, page);
            float y = pageH - margin;
            for (String tl : wrapText(title == null ? "" : title, bold, head, maxW)) {
                textAt(cs, bold, head, margin, y, tl);
                y -= leading * 1.5f;
            }
            y -= 8f;
            List<String> all = lines == null ? new ArrayList<String>() : lines;
            for (String raw : all) {
                for (String l : wrapText(raw == null ? "" : raw, font, body, maxW)) {
                    if (y < margin) {
                        cs.close();
                        page = new PDPage(PDRectangle.A4);
                        d.addPage(page);
                        cs = new PDPageContentStream(d, page);
                        y = pageH - margin;
                    }
                    textAt(cs, font, body, margin, y, l);
                    y -= leading;
                }
            }
            cs.close();
            d.save(out);
        }
    }

    private static void textAt(PDPageContentStream cs, PDFont f, float size,
                               float x, float y, String s) throws Exception {
        cs.beginText();
        cs.setFont(f, size);
        cs.newLineAtOffset(x, y);
        cs.showText(winAnsi(s));
        cs.endText();
    }

    /** Text with an explicit colour. Filling a shape leaves the fill colour set,
     *  so anything drawn after a fill must say what colour it wants. */
    private static void textAt(PDPageContentStream cs, PDFont f, float size,
                               float x, float y, String s, float r, float g, float b) throws Exception {
        cs.setNonStrokingColor(r, g, b);
        textAt(cs, f, size, x, y, s);
    }

    private static List<String> wrapText(String s, PDFont f, float size, float maxW) throws Exception {
        List<String> out = new ArrayList<>();
        String safe = winAnsi(s);
        if (safe.isEmpty()) { out.add(""); return out; }
        for (String para : safe.split("\n", -1)) {
            StringBuilder line = new StringBuilder();
            for (String w : para.split(" ")) {
                String cand = line.length() == 0 ? w : line + " " + w;
                if (f.getStringWidth(cand) / 1000f * size > maxW && line.length() > 0) {
                    out.add(line.toString());
                    line = new StringBuilder(w);
                } else {
                    line = new StringBuilder(cand);
                }
            }
            out.add(line.toString());
        }
        return out;
    }

    // ------------------------------------------------------------------
    // Redaction
    // ------------------------------------------------------------------

    /**
     * Permanently remove what is under the given pages' images.
     *
     * A redaction that only paints a box is not a redaction - the text is still in
     * the file and can be copied or extracted. So each redacted page is REPLACED by
     * a flat image (the caller renders the page and paints the black boxes on it):
     * the original content stream, its resources and its annotations are all thrown
     * away, so nothing of the old text remains in the file.
     *
     * @param pageNos 1-based page numbers
     * @param images  the rendered, already-blackened page images, one per page
     */
    public static void redactPages(File src, int[] pageNos, android.graphics.Bitmap[] images,
                                   File out) throws Exception {
        if (pageNos == null || images == null || pageNos.length != images.length) {
            throw new IllegalArgumentException("Nothing to redact");
        }
        try (PDDocument d = open(src)) {
            int applied = 0;
            for (int i = 0; i < pageNos.length; i++) {
                int p = pageNos[i];
                android.graphics.Bitmap bmp = images[i];
                if (bmp == null || p < 1 || p > d.getNumberOfPages()) continue;
                PDPage page = d.getPage(p - 1);
                PDRectangle box = page.getCropBox();
                int r = ((page.getRotation() % 360) + 360) % 360;
                float dw = (r == 90 || r == 270) ? box.getHeight() : box.getWidth();
                float dh = (r == 90 || r == 270) ? box.getWidth() : box.getHeight();

                // drop everything the page used to hold
                page.setAnnotations(new ArrayList<com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotation>());
                page.setResources(new PDResources());
                // the image is already in the displayed orientation, so no extra /Rotate
                page.setRotation(0);
                PDRectangle nb = new PDRectangle(dw, dh);
                page.setMediaBox(nb);
                page.setCropBox(nb);

                PDImageXObject img = JPEGFactory.createFromImage(d, bmp, 0.9f);
                try (PDPageContentStream cs =
                             new PDPageContentStream(d, page, AppendMode.OVERWRITE, true, true)) {
                    cs.drawImage(img, 0, 0, dw, dh);
                }
                applied++;
            }
            if (applied == 0) throw new IllegalArgumentException("Nothing to redact");
            d.save(out);
        }
    }

    /** One page of a document built from scratch. */
    @SuppressWarnings("unused")
    public static final class PageSpec {
        public float width, height;
        public int bgColor = 0xFFFFFFFF;
        /** Transparent overlay (annotations/text) drawn on top of the background, or null. */
        public File raster;

        public PageSpec(float width, float height, int bgColor, File raster) {
            this.width = width; this.height = height; this.bgColor = bgColor; this.raster = raster;
        }
    }

    /** Build a PDF from a list of pages (background colour + optional transparent overlay). */
    public static void createPdf(List<PageSpec> pages, File out) throws Exception {
        if (pages == null || pages.isEmpty()) throw new IllegalArgumentException("Add at least one page");
        try (PDDocument d = new PDDocument()) {
            for (PageSpec p : pages) {
                PDPage page = new PDPage(new PDRectangle(p.width, p.height));
                d.addPage(page);
                try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                    cs.setNonStrokingColor((p.bgColor >> 16) & 0xFF, (p.bgColor >> 8) & 0xFF, p.bgColor & 0xFF);
                    cs.addRect(0, 0, p.width, p.height);
                    cs.fill();
                    if (p.raster != null && p.raster.exists()) {
                        PDImageXObject img = PDImageXObject.createFromFile(p.raster.getAbsolutePath(), d);
                        cs.drawImage(img, 0, 0, p.width, p.height);
                    }
                }
            }
            d.save(out);
        }
    }

    /** Refuse to decode an image the file claims is absurdly large. */
    private static boolean safeToDecode(PDImageXObject img) {
        try {
            long w = img.getWidth(), h = img.getHeight();
            return w > 0 && h > 0 && w * h <= MAX_IMAGE_PIXELS;
        } catch (Exception e) {
            return false;
        }
    }

    /** Decode an image the right way up - EXIF orientation applied. For previews. */
    public static Bitmap decodeUpright(File f, int maxDimension) {
        return decodeBounded(f, maxDimension);
    }

    private static Bitmap decodeBounded(File f, int maxDimension) {
        BitmapFactory.Options bounds = new BitmapFactory.Options();
        bounds.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(f.getAbsolutePath(), bounds);
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null;
        int sample = 1;
        if (maxDimension > 0) {
            while (Math.max(bounds.outWidth, bounds.outHeight) / (sample * 2) >= maxDimension) sample *= 2;
        }
        BitmapFactory.Options opts = new BitmapFactory.Options();
        opts.inSampleSize = sample;
        Bitmap bmp = BitmapFactory.decodeFile(f.getAbsolutePath(), opts);
        if (bmp == null) return null;
        return applyExifRotation(f, bmp);
    }

    /**
     * Camera JPEGs carry their true orientation in EXIF rather than in the pixels.
     * Ignoring it made every scanned page come out rotated, so it is applied here -
     * once, for every path that reads an image.
     */
    private static Bitmap applyExifRotation(File f, Bitmap bmp) {
        try {
            android.media.ExifInterface exif =
                    new android.media.ExifInterface(f.getAbsolutePath());
            int o = exif.getAttributeInt(
                    android.media.ExifInterface.TAG_ORIENTATION,
                    android.media.ExifInterface.ORIENTATION_NORMAL);
            android.graphics.Matrix m = new android.graphics.Matrix();
            switch (o) {
                case android.media.ExifInterface.ORIENTATION_ROTATE_90:  m.postRotate(90f);  break;
                case android.media.ExifInterface.ORIENTATION_ROTATE_180: m.postRotate(180f); break;
                case android.media.ExifInterface.ORIENTATION_ROTATE_270: m.postRotate(270f); break;
                case android.media.ExifInterface.ORIENTATION_FLIP_HORIZONTAL: m.postScale(-1f, 1f); break;
                case android.media.ExifInterface.ORIENTATION_FLIP_VERTICAL:   m.postScale(1f, -1f); break;
                case android.media.ExifInterface.ORIENTATION_TRANSPOSE: m.postRotate(90f);  m.postScale(-1f, 1f); break;
                case android.media.ExifInterface.ORIENTATION_TRANSVERSE: m.postRotate(270f); m.postScale(-1f, 1f); break;
                default: return bmp;
            }
            Bitmap fixed = Bitmap.createBitmap(bmp, 0, 0, bmp.getWidth(), bmp.getHeight(), m, true);
            if (fixed != bmp) bmp.recycle();
            return fixed;
        } catch (Throwable t) {
            return bmp;   // no EXIF, or unreadable: keep what we decoded
        }
    }

    public static List<File> extractImages(File src, File outDir) throws Exception {
        return extractImages(src, outDir, null);
    }

    /** Extract images, optionally limited to a set of 1-based pages (null = all pages). */
    public static List<File> extractImages(File src, File outDir, List<Integer> pages1based) throws Exception {
        List<File> written = new ArrayList<>();
        try (PDDocument d = open(src)) {
            IdentityHashMap<COSBase, Boolean> seen = new IdentityHashMap<>();
            int n = 0;
            int index = 0;
            Set<Integer> only = pages1based == null ? null : new HashSet<>(pages1based);
            for (PDPage page : d.getPages()) {
                index++;
                if (only != null && !only.contains(index)) continue;
                PDResources res = page.getResources();
                if (res == null) continue;
                for (COSName name : res.getXObjectNames()) {
                    PDXObject xo;
                    try { xo = res.getXObject(name); } catch (Exception e) { continue; }
                    if (!(xo instanceof PDImageXObject)) continue;
                    PDImageXObject img = (PDImageXObject) xo;
                    if (seen.put(img.getCOSObject(), Boolean.TRUE) != null) continue;
                    if (!safeToDecode(img)) continue;
                    Bitmap bmp;
                    try { bmp = img.getImage(); } catch (OutOfMemoryError | Exception e) { continue; }
                    if (bmp == null) continue;
                    boolean alpha = bmp.hasAlpha();
                    File dest = new File(outDir, "image_" + (++n) + (alpha ? ".png" : ".jpg"));
                    try (OutputStream os = new FileOutputStream(dest)) {
                        bmp.compress(alpha ? Bitmap.CompressFormat.PNG : Bitmap.CompressFormat.JPEG, 90, os);
                    }
                    bmp.recycle();
                    written.add(dest);
                }
            }
        }
        return written;
    }

    // ---------------------------------------------------------------------
    // helpers
    // ---------------------------------------------------------------------

    private static PDType1Font pickFont(String name, boolean bold, boolean italic) {
        String n = name == null ? "Helvetica" : name;
        if ("Times".equalsIgnoreCase(n)) {
            return bold && italic ? PDType1Font.TIMES_BOLD_ITALIC
                    : bold ? PDType1Font.TIMES_BOLD
                    : italic ? PDType1Font.TIMES_ITALIC
                    : PDType1Font.TIMES_ROMAN;
        }
        if ("Courier".equalsIgnoreCase(n)) {
            return bold && italic ? PDType1Font.COURIER_BOLD_OBLIQUE
                    : bold ? PDType1Font.COURIER_BOLD
                    : italic ? PDType1Font.COURIER_OBLIQUE
                    : PDType1Font.COURIER;
        }
        return bold && italic ? PDType1Font.HELVETICA_BOLD_OBLIQUE
                : bold ? PDType1Font.HELVETICA_BOLD
                : italic ? PDType1Font.HELVETICA_OBLIQUE
                : PDType1Font.HELVETICA;
    }

    /** Restrict a string to characters the standard-14 fonts can encode (WinAnsi-ish). */
    /**
     * Text for the invisible OCR layer, or "" when the font cannot represent it.
     * Latin-1 is kept (including accents), anything else is dropped rather than turned
     * into "?" so the search index never gains a word that was not on the page.
     */
    static String ocrEncodable(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\n' || c == '\r' || c == '\t') b.append(' ');
            else if (c >= 32 && c <= 126) b.append(c);
            else if (c >= 160 && c <= 255) b.append(c);
            // everything else is intentionally skipped
        }
        String out = b.toString().trim();
        // a run that lost all its letters (e.g. a Devanagari word) is not useful
        boolean hasLetter = false;
        for (int i = 0; i < out.length(); i++) {
            if (Character.isLetterOrDigit(out.charAt(i))) { hasLetter = true; break; }
        }
        return hasLetter ? out : "";
    }

    static String winAnsi(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\n' || c == '\r' || c == '\t') { b.append(' '); }
            else if (c >= 32 && c <= 126) { b.append(c); }
            else if (c >= 160 && c <= 255) { b.append(c); }
            else { b.append('?'); }
        }
        return b.toString();
    }

    private static String nullToEmpty(String s) { return s == null ? "" : s; }

    private static String emptyToNull(String s) { return (s == null || s.trim().isEmpty()) ? null : s; }
    /** "txt_p3_Address_1" -> "Address 1"; "chk_p1_New" -> "New". */
    private static String readableName(String key) {
        if (key == null) return "";
        String n = key.replaceAll("^(txt|chk|rb|dd|combo|list|sig)_p\\d+_", "");
        if (n.equals(key)) n = key.replaceAll("^(txt|chk|rb|dd|combo|list|sig)_", "");
        n = n.replace('_', ' ').trim();
        if (n.isEmpty()) return key;
        return Character.toUpperCase(n.charAt(0)) + n.substring(1);
    }

    /** "txt_p3_Address_1" -> 3; anything without a page marker -> 0. */
    private static int pageFromKey(String key) {
        if (key == null) return 0;
        java.util.regex.Matcher m = java.util.regex.Pattern.compile("_p(\\d+)_").matcher(key);
        if (m.find()) {
            try { return Integer.parseInt(m.group(1)); } catch (NumberFormatException ignore) { }
        }
        return 0;
    }

}
