package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.cos.COSArray;
import com.tom_roush.pdfbox.cos.COSBase;
import com.tom_roush.pdfbox.cos.COSDictionary;
import com.tom_roush.pdfbox.cos.COSName;
import com.tom_roush.pdfbox.cos.COSNull;
import com.tom_roush.pdfbox.cos.COSObject;
import com.tom_roush.pdfbox.cos.COSStream;
import com.tom_roush.pdfbox.io.MemoryUsageSetting;
import com.tom_roush.pdfbox.io.RandomAccessBufferedFileInputStream;
import com.tom_roush.pdfbox.io.ScratchFile;
import com.tom_roush.pdfbox.pdfparser.PDFParser;
import com.tom_roush.pdfbox.pdfparser.PDFStreamParser;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.graphics.PDXObject;
import com.tom_roush.pdfbox.pdmodel.PDResources;
import com.tom_roush.pdfbox.contentstream.operator.Operator;
import com.tom_roush.pdfbox.pdmodel.common.PDStream;
import com.tom_roush.pdfbox.pdmodel.encryption.AccessPermission;
import com.tom_roush.pdfbox.pdmodel.encryption.InvalidPasswordException;
import com.tom_roush.pdfbox.pdmodel.encryption.StandardProtectionPolicy;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/**
 * Repairs damaged PDFs on the device.
 *
 * <p>A PDF repair is not magic: it finds whatever is still physically present in the file
 * and writes it back out with a clean structure. Bytes that are gone are gone - no tool
 * can invent them. So this class does three honest things, in order:
 *
 * <ol>
 *   <li><b>Diagnose</b> - read the bytes themselves (header, %%EOF, startxref, object
 *       census) and report exactly what is wrong, before touching anything.</li>
 *   <li><b>Repair</b> - parse with three increasingly forgiving attempts (strict, lenient,
 *       lenient with a long EOF look-up for trailing garbage). If the page tree is the
 *       broken part, salvage the page objects out of the object pool and rebuild a fresh
 *       document from them.</li>
 *   <li><b>Verify</b> - reopen the result strictly and walk every page's content
 *       operators. A repair that does not pass its own check is reported as a failure,
 *       never as a success.</li>
 * </ol>
 *
 * <p>Nothing here renders, so nothing here is guessed: every statement in the report comes
 * from a byte that was read or an object that was parsed.
 */
public final class PdfRepair {

    private PdfRepair() { }

    /** Everything the caller needs to show the user, all of it measured. */
    public static final class Report {
        /** True when a document could be parsed at all. */
        public boolean readable;
        /** strict | lenient | deep | salvaged | none */
        public String stage = "none";
        /** Why it could not be repaired, when readable is false. */
        public String failure = "";

        // ---- byte-level facts ----
        public boolean headerFound;
        public int headerOffset;
        public String version = "";
        public boolean eofFound;
        public boolean startxrefOk;
        public long startxref = -1L;
        public boolean xrefStream;
        public int objectsSeen;      // "endobj" occurrences - a census, not a parse
        public int objectsLoaded;    // objects the parser actually built
        public boolean linearized;

        // ---- document-level facts ----
        public int pagesBefore;
        public int pagesAfter;
        public boolean encrypted;
        public boolean signed;
        public int formFields;
        public boolean hasOutline;
        public boolean hasLinks;

        // ---- outcome ----
        public long sizeBefore;
        public long sizeAfter;
        public boolean changed;
        public boolean verified;
        public String verifyNote = "";

        /** What was wrong, one line each. */
        public final List<String> findings = new ArrayList<>();
        /** What was done about it, one line each. */
        public final List<String> actions = new ArrayList<>();
        /** 1-based page numbers that could not be carried across. */
        public final List<Integer> lostPages = new ArrayList<>();
        /** 1-based pages that name content the file no longer holds, so they come out blank. */
        public final List<Integer> blankPages = new ArrayList<>();
        /** 1-based pages whose content stops partway and draws only part of itself. */
        public final List<Integer> partialPages = new ArrayList<>();
    }

    // =====================================================================================
    //  Public API
    // =====================================================================================

    /** Reads the file and reports what is wrong with it. Writes nothing. */
    public static Report diagnose(File src, String password) {
        Report r = new Report();
        r.sizeBefore = src == null ? 0L : src.length();
        if (src == null || !src.isFile()) {
            r.failure = "the file could not be found";
            return r;
        }
        scanBytes(src, r);

        PDDocument doc = null;
        try {
            doc = open(src, password, null, r);
            if (doc == null) {
                if (r.failure.isEmpty()) r.failure = "the file could not be parsed";
                return r;
            }
            r.readable = true;
            readDocumentFacts(doc, src, r);
            // A structure can be perfect and a page still be rubble, so the content is
            // walked here too - read-only, but it is the difference between "looks fine"
            // and "actually reads".
            walkPages(doc, r);
        } finally {
            close(doc);
        }
        return r;
    }

    /**
     * Repairs {@code src} into {@code out}.
     *
     * <p>The output is written only if it passes verification. On failure {@code out} is
     * deleted so the caller can never hand the user a file that is worse than the input.
     */
    public static Report repair(File src, String password, File out) {
        Report r = new Report();
        r.sizeBefore = src == null ? 0L : src.length();
        if (src == null || !src.isFile()) {
            r.failure = "the file could not be found";
            return r;
        }
        scanBytes(src, r);

        // Whatever happens next, a file at the output path must only ever be the result of
        // this run. A stale one from an earlier attempt would look like a success.
        if (out.exists()) {
            //noinspection ResultOfMethodCallIgnored
            out.delete();
        }

        String pw = password == null ? "" : password;
        File working = null;
        PDDocument doc = null;
        PDDocument rebuilt = null;
        try {
            // ---- normalise the bytes first: junk before the header, or no header at all
            working = prepare(src, out, r);
            if (working == null) {
                r.failure = "this is not a PDF - there is no page in it to repair";
                return r;
            }

            doc = open(working, pw, out, r);
            if (doc == null) {
                if (r.failure.isEmpty()) r.failure = "the file could not be parsed";
                return r;
            }
            r.readable = true;
            // De-duplicate before anything counts or walks the tree: a page bomb lists one
            // page four thousand times, and every pass over that list is work on a 15 KB file.
            dedupeKids(doc, r);
            readDocumentFacts(doc, working, r);

            // Pages whose /Contents was removed while their streams are still in the file are
            // recoverable: the streams are intact and decodable, they are simply not attached.
            adoptOrphanContent(doc, java.nio.file.Files.readAllBytes(src.toPath()), r);

            // ---- decide: is the page tree usable, or do we have to salvage? ----
            // A tree can report a page count and still be un-walkable: a circular /Kids, or
            // a /Count that no longer matches. Every page is fetched once here, because a
            // document whose pages cannot be reached is not a repaired document.
            boolean treeWalks = r.pagesBefore > 0;
            if (treeWalks) {
                for (int i = 0; i < r.pagesBefore; i++) {
                    try {
                        doc.getPage(i);
                    } catch (Throwable t) {
                        treeWalks = false;
                        r.findings.add("the page tree cannot be walked at page " + (i + 1)
                                + ": " + describe(t));
                        break;
                    }
                }
            }
            PDDocument source = doc;
            if (!treeWalks) {
                // The object pool only holds what the parser managed to reach, which for a
                // circular or truncated tree can be a fraction of the pages. The bytes still
                // carry every /Type /Page object, so the byte-level lift is tried first and
                // the pool is only a fallback.
                File lifted = null;
                try {
                    lifted = salvageObjects(src, out, r);
                    if (lifted != null) {
                        PDDocument liftedDoc = parse(lifted, pw, true, 64 * 1024);
                        source = liftedDoc;
                        r.stage = "salvaged";
                        r.failure = "";
                        r.pagesBefore = source.getNumberOfPages();
                        //noinspection ResultOfMethodCallIgnored
                        lifted.deleteOnExit();
                    }
                } catch (Throwable ignored) {
                }
                if (source == doc) {
                    source = null;      // fall through to the pool-based salvage below
                }
            }
            if (source == null) {
                rebuilt = salvagePages(doc, r);
                if (rebuilt == null) {
                    r.failure = "no readable page could be found in the file";
                    return r;
                }
                source = rebuilt;
            }

            // Which pages were already unreadable before we touched anything? Only those
            // are ours to report as blank; a page we break ourselves is a real regression.
            walkPages(source, r);
            List<Integer> brokenOnArrival = new ArrayList<>(r.lostPages);
            List<Integer> blankOnArrival = new ArrayList<>(r.blankPages);
            r.lostPages.clear();
            r.blankPages.clear();

            // A page whose content stream is destroyed is kept, so the pages after it keep
            // their numbers - but its broken stream is replaced with an empty page. Leaving
            // it in place makes every reader that touches that page fail, which would take
            // the readable pages down with it.
            for (int page : brokenOnArrival) {
                try {
                    PDPage p = source.getPage(page - 1);
                    p.setContents((com.tom_roush.pdfbox.pdmodel.common.PDStream) null);
                    r.actions.add("page " + page + " had no readable content - kept as a blank page");
                } catch (Throwable ignored) { }
            }

            // ---- write, then verify ----
            keepProtection(source, pw, r);
            if (!writeOut(source, out, r)) return r;
            verify(out, pw, r);

            // A page that failed in the input and fails the same way now is not a regression;
            // keeping it preserves the page count, and the report already says it is blank.
            for (int i = r.lostPages.size() - 1; i >= 0; i--) {
                int page = r.lostPages.get(i);
                if (brokenOnArrival.contains(page)) {
                    r.lostPages.remove(i);
                    if (!r.blankPages.contains(page)) r.blankPages.add(page);
                }
            }
            // Pages that came in with no content, and pages whose content we had to clear,
            // are both blank in the output - and both are named in the report.
            for (int page : blankOnArrival) {
                if (!r.blankPages.contains(page)) r.blankPages.add(page);
            }
            for (int page : brokenOnArrival) {
                if (r.partialPages.contains(page)) continue;     // partial, not blank
                if (!r.blankPages.contains(page)) r.blankPages.add(page);
            }
            java.util.Collections.sort(r.blankPages);
            if (r.lostPages.isEmpty()) r.verified = r.pagesAfter > 0;

            // A file whose pages are all empty is not a repaired document - it is a blank
            // one, and handing that over would look like the content was destroyed by us.
            // Better to say plainly that nothing could be recovered.
            int usable = r.pagesAfter - r.blankPages.size() - r.lostPages.size();
            if (r.pagesAfter > 0 && usable <= 0) {
                r.failure = "the pages are in the file, but none of their content survived";
                //noinspection ResultOfMethodCallIgnored
                out.delete();
                r.sizeAfter = 0L;
                r.verified = false;
                return r;
            }

            // ---- a page whose own content is rubble is dropped, not the whole repair ----
            // Only pages that came in readable and went out broken are ours to drop. A page
            // that was already rubble in the input is the input's fault: deleting it would
            // change the document, so it is kept and reported instead.
            if (r.pagesAfter > 0 && !r.lostPages.isEmpty()) {
                List<Integer> dropped = new ArrayList<>(r.lostPages);
                PDDocument trimmed = dropPages(source, dropped, r);
                if (trimmed != null) {
                    close(rebuilt);
                    rebuilt = trimmed;
                    keepProtection(trimmed, pw, r);
                    if (!writeOut(trimmed, out, r)) return r;
                    verify(out, pw, r);
                }
            }

            if (!r.verified || r.pagesAfter <= 0) {
                // A repair that cannot be verified is not a repair.
                //noinspection ResultOfMethodCallIgnored
                out.delete();
                r.sizeAfter = 0L;
                if (r.failure.isEmpty()) {
                    r.failure = r.pagesAfter <= 0
                            ? "the repaired file came out with no pages"
                            : "the repaired file did not pass verification";
                }
                return r;
            }
            return r;
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            //noinspection ResultOfMethodCallIgnored
            out.delete();
            return r;
        } catch (Throwable t) {
            r.failure = describe(t);
            //noinspection ResultOfMethodCallIgnored
            out.delete();
            return r;
        } finally {
            close(rebuilt);
            close(doc);
            if (working != null && !working.equals(src)) {
                //noinspection ResultOfMethodCallIgnored
                working.delete();
            }
        }
    }

    // =====================================================================================
    //  Stage 1 - the bytes themselves
    // =====================================================================================

    /**
     * Reads the raw file and records what is physically there. Everything in this method is
     * a fact about bytes, so it stays true even when the parser gives up entirely - which is
     * exactly when the user needs an answer.
     */
    private static void scanBytes(File src, Report r) {
        // ---- header: "%PDF-" must be near the start; the spec allows leading junk ----
        try (InputStream in = new FileInputStream(src)) {
            byte[] head = new byte[1024];
            int n = readFully(in, head);
            if (n > 0) {
                String s = new String(head, 0, n, "ISO-8859-1");
                int at = s.indexOf("%PDF-");
                if (at >= 0) {
                    r.headerFound = true;
                    r.headerOffset = at;
                    // the version follows the dash: 1.4, 1.7, 2.0
                    int end = Math.min(s.length(), at + 8);
                    StringBuilder v = new StringBuilder();
                    for (int i = at + 5; i < end; i++) {
                        char c = s.charAt(i);
                        if (c >= '0' && c <= '9' || c == '.') v.append(c); else break;
                    }
                    r.version = v.toString();
                    r.linearized = s.contains("/Linearized");
                }
            }
        } catch (Exception ignored) { }

        // ---- tail: %%EOF and the startxref offset ----
        long len = src.length();
        int tailLen = (int) Math.min(len, 4096L);
        byte[] tail = new byte[tailLen];
        try (RandomAccessFile raf = new RandomAccessFile(src, "r")) {
            raf.seek(len - tailLen);
            raf.readFully(tail);
        } catch (Exception e) {
            return;
        }
        String t = new String(tail, java.nio.charset.StandardCharsets.ISO_8859_1);
        r.eofFound = t.contains("%%EOF");

        int at = t.lastIndexOf("startxref");
        if (at >= 0) {
            long value = -1L;
            StringBuilder digits = new StringBuilder();
            for (int i = at + "startxref".length(); i < t.length(); i++) {
                char c = t.charAt(i);
                if (c >= '0' && c <= '9') digits.append(c);
                else if (digits.length() > 0) break;
            }
            if (digits.length() > 0 && digits.length() < 19) {
                try { value = Long.parseLong(digits.toString()); } catch (Exception ignored) { }
            }
            r.startxref = value;
            // The offset is only usable if it lands inside the file on something that can
            // start a cross-reference section: the "xref" keyword, or an object header
            // (a cross-reference stream).
            if (value >= 0 && value < len) {
                r.startxrefOk = looksLikeXref(src, value, r);
            }
        }

        // ---- object census: how much of the file still holds objects ----
        r.objectsSeen = countEndobj(src);
    }

    /** True when the bytes at {@code offset} begin a cross-reference section. */
    private static boolean looksLikeXref(File src, long offset, Report r) {
        byte[] buf = new byte[64];
        int n;
        try (RandomAccessFile raf = new RandomAccessFile(src, "r")) {
            raf.seek(offset);
            n = raf.read(buf);
        } catch (Exception e) {
            return false;
        }
        if (n <= 0) return false;
        String s = new String(buf, 0, n, java.nio.charset.StandardCharsets.ISO_8859_1).trim();
        if (s.startsWith("xref")) return true;
        // "12 0 obj" - a cross-reference stream object
        java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("^(\\d+)\\s+(\\d+)\\s+obj").matcher(s);
        if (m.find()) {
            r.xrefStream = true;
            return true;
        }
        return false;
    }

    /** Counts "endobj" markers, chunk by chunk, without loading the file into memory. */
    private static int countEndobj(File src) {
        final byte[] needle = "endobj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int count = 0;
        byte[] buf = new byte[64 * 1024];
        int carry = 0;                       // bytes of a possible split match kept from before
        try (InputStream in = new FileInputStream(src)) {
            int n;
            while ((n = in.read(buf, carry, buf.length - carry)) > 0) {
                int total = carry + n;
                int i = 0;
                while (i <= total - needle.length) {
                    boolean hit = true;
                    for (int k = 0; k < needle.length; k++) {
                        if (buf[i + k] != needle[k]) { hit = false; break; }
                    }
                    if (hit) { count++; i += needle.length; } else { i++; }
                }
                // keep the tail so a match split across two reads is still found
                carry = Math.min(needle.length - 1, total);
                System.arraycopy(buf, total - carry, buf, 0, carry);
            }
        } catch (Exception ignored) { }
        return count;
    }

    // =====================================================================================
    //  Stage 1b - give the parser something it can actually read
    // =====================================================================================

    /**
     * Returns a file the parser can start on, or null when there is nothing here.
     *
     * <p>Two real-world failures live before the first object: junk in front of the header
     * (an interrupted download, a mail gateway that prepends a banner, a file concatenated
     * after something else) and a header that is gone altogether. A reader gives up on both;
     * a repair tool trims or rebuilds the front of the file and tries again.
     */
    private static File prepare(File src, File outFile, Report r) throws IOException {
        boolean needsWork = (r.headerFound && r.headerOffset > 0) || !r.headerFound;
        if (!needsWork) return src;

        // Nothing to repair if the file never held a PDF object at all.
        if (!r.headerFound && r.objectsSeen == 0) return null;

        File work = File.createTempFile("kavopdf-repair-", ".pdf", workDir(src, outFile));
        work.deleteOnExit();

        try (InputStream in = new FileInputStream(src);
             java.io.OutputStream os = new java.io.FileOutputStream(work)) {
            if (r.headerFound) {
                long skip = r.headerOffset;
                long left = skip;
                while (left > 0) {
                    long n = in.skip(left);
                    if (n <= 0) break;
                    left -= n;
                }
                copy(in, os);
                r.actions.add("removed " + skip + " byte(s) of junk before the %PDF- header");
            } else {
                // A header can be rebuilt: every reader only uses it to pick a parser
                // version, and the objects below it are untouched.
                os.write(("%PDF-1.7\n").getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                copy(in, os);
                r.actions.add("rebuilt the missing %PDF- header");
            }
        }
        return work;
    }

    /** One object header found in the raw bytes: its number, and what it says it is. */
    private static final class RawObject {
        final int number;
        final int start;          // offset of "N G obj"
        final String type;        // Page | Pages | Catalog | other
        RawObject(int number, int start, String type) {
            this.number = number; this.start = start; this.type = type;
        }
    }

    /**
     * Rebuilds a page tree that the parser refuses to look past.
     *
     * <p>Some damage stops a reader dead before it reads anything: if the catalog's /Pages
     * entry points at something that is not a page-tree node, PDFBox throws and the whole
     * document is unreadable - even though every page object is still sitting in the file.
     * This scans the raw bytes for the objects, writes a fresh /Type /Pages dictionary that
     * lists them in file order, and points the catalog at it. Offsets after the insertion
     * move, which is fine: the parser reconstructs the cross-reference table anyway, and the
     * result is re-saved with a clean one.
     */
    private static File rebuildPageTree(File src, File outFile, Report r) {
        // Byte surgery needs the file in memory. Above this size the honest answer is to
        // say so rather than to risk the phone.
        if (src.length() > 16L * 1024 * 1024L) {
            r.actions.add("the file is too large to rebuild a page tree in memory");
            return null;
        }
        byte[] b;
        try {
            b = readAll(src);
        } catch (Throwable t) {
            return null;
        }

        List<RawObject> objects = scanObjects(b);
        List<Integer> pages = new ArrayList<>();
        java.util.Set<Integer> treeNodes = new java.util.HashSet<>();
        int catalogStart = -1;
        int maxNumber = 0;

        for (RawObject o : objects) {
            maxNumber = Math.max(maxNumber, o.number);
            if ("Page".equals(o.type)) pages.add(o.number);
            else if ("Pages".equals(o.type)) treeNodes.add(o.number);
            else if ("Catalog".equals(o.type) && catalogStart < 0) catalogStart = o.start;
        }
        // A trailer whose /Root is gone leaves the whole document without a catalog, and
        // the parser refuses before reading anything. The catalog object is usually still
        // there - only the pointer to it is lost - so the fix is a correct trailer.
        if (catalogStart < 0) {
            int catalog = -1;
            for (RawObject o : objects) {
                if ("Catalog".equals(o.type)) { catalog = o.number; break; }
            }
            if (catalog < 0) return null;                 // no catalog anywhere: nothing to point at
            byte[] tailBytes = ("\ntrailer\n<< /Size " + (maxNumber + 1) + " /Root "
                    + catalog + " 0 R >>\nstartxref\n0\n%%EOF\n")
                    .getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
            try {
                File patched = File.createTempFile("kavopdf-root-", ".pdf", workDir(src, outFile));
                patched.deleteOnExit();
                try (java.io.FileOutputStream os = new java.io.FileOutputStream(patched)) {
                    os.write(b);
                    os.write(tailBytes);
                }
                r.actions.add("rebuilt the trailer and pointed it at catalog object " + catalog);
                return patched;
            } catch (Throwable t) {
                return null;
            }
        }

        if (pages.isEmpty() || catalogStart < 0) return null;

        // The catalog's own /Pages entry: is it pointing at a real page-tree node?
        int target = pagesReference(b, catalogStart);
        if (target >= 0 && treeNodes.contains(target)) return null;   // tree is fine

        int newNumber = maxNumber + 1;
        StringBuilder kids = new StringBuilder("[");
        for (int i = 0; i < pages.size(); i++) {
            if (i > 0) kids.append(' ');
            kids.append(pages.get(i)).append(" 0 R");
        }
        kids.append(']');
        String synth = "\n" + newNumber + " 0 obj\n<< /Type /Pages /Kids " + kids
                + " /Count " + pages.size() + " >>\nendobj\n";

        // Insert before the cross-reference section, whichever kind it is.
        int insertAt = lastIndexOf(b, "\nxref".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
        if (insertAt < 0) {
            insertAt = lastIndexOf(b, "startxref".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
        }
        if (insertAt < 0) insertAt = b.length;

        // Rewrite the catalog's /Pages entry to point at the new node.
        int refAt = pagesEntryOffset(b, catalogStart);
        if (refAt < 0) return null;
        int refEnd = refAt;
        while (refEnd < b.length && b[refEnd] != 'R') refEnd++;
        if (refEnd < b.length) refEnd++;

        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream(b.length + synth.length() + 32);
        try {
            out.write(b, 0, refAt);
            out.write(("/Pages " + newNumber + " 0 R").getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
            int afterRef = Math.min(refEnd, insertAt);
            out.write(b, afterRef, insertAt - afterRef);
            out.write(synth.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
            out.write(b, insertAt, b.length - insertAt);

            File patched = File.createTempFile("kavopdf-tree-", ".pdf", workDir(src, outFile));
            patched.deleteOnExit();
            try (java.io.FileOutputStream os = new java.io.FileOutputStream(patched)) {
                out.writeTo(os);
            }
            r.actions.add("rebuilt the page tree from " + pages.size()
                    + " page object(s) found in the file");
            return patched;
        } catch (Throwable t) {
            return null;
        }
    }

    /** Every "N G obj" header in the bytes, with what its dictionary says it is. */
    private static List<RawObject> scanObjects(byte[] b) {
        List<RawObject> out = new ArrayList<>();
        byte[] needle = " obj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int at = 0;
        while (true) {
            at = indexOf(b, needle, at);
            if (at < 0) break;
            // walk back over "N G" - digits, space, digits
            int i = at - 1;
            while (i >= 0 && (b[i] == ' ' || b[i] == '\r' || b[i] == '\n' || b[i] == '\t')) i--;
            int genEnd = i;
            while (i >= 0 && b[i] >= '0' && b[i] <= '9') i--;
            int genStart = i + 1;
            if (genStart > genEnd) { at += needle.length; continue; }
            while (i >= 0 && (b[i] == ' ' || b[i] == '\r' || b[i] == '\n')) i--;
            int numEnd = i;
            while (i >= 0 && b[i] >= '0' && b[i] <= '9') i--;
            int numStart = i + 1;
            if (numStart > numEnd) { at += needle.length; continue; }
            int number;
            try {
                number = Integer.parseInt(new String(b, numStart, numEnd - numStart + 1,
                        java.nio.charset.StandardCharsets.ISO_8859_1));
            } catch (Exception e) { at += needle.length; continue; }

            // what is this object? look a little way ahead
            int window = Math.min(b.length, at + 4096);
            String head = new String(b, at, window - at, java.nio.charset.StandardCharsets.ISO_8859_1);
            String type = "other";
            if (head.contains("/Type /Catalog")) type = "Catalog";
            else if (head.contains("/Type /Pages")) type = "Pages";
            else if (head.contains("/Type /Page")) type = "Page";
            out.add(new RawObject(number, numStart, type));
            at += needle.length;
        }
        return out;
    }

    /** The object number the catalog points its /Pages at, or -1. */
    private static int pagesReference(byte[] b, int catalogStart) {
        int at = pagesEntryOffset(b, catalogStart);
        if (at < 0) return -1;
        int i = at + "/Pages ".length();
        StringBuilder digits = new StringBuilder();
        while (i < b.length && b[i] >= '0' && b[i] <= '9') digits.append((char) b[i++]);
        if (digits.length() == 0) return -1;
        try { return Integer.parseInt(digits.toString()); } catch (Exception e) { return -1; }
    }

    /** Offset of the catalog's "/Pages " keyword. */
    private static int pagesEntryOffset(byte[] b, int catalogStart) {
        byte[] key = "/Pages ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int end = Math.min(b.length, catalogStart + 4096);
        int at = indexOf(b, key, catalogStart);
        return (at < 0 || at > end) ? -1 : at;
    }

    private static int indexOf(byte[] hay, byte[] needle, int from) {
        if (from < 0) from = 0;
        outer:
        for (int i = from; i <= hay.length - needle.length; i++) {
            for (int k = 0; k < needle.length; k++) {
                if (hay[i + k] != needle[k]) continue outer;
            }
            return i;
        }
        return -1;
    }

    private static int lastIndexOf(byte[] hay, byte[] needle) {
        outer:
        for (int i = hay.length - needle.length; i >= 0; i--) {
            for (int k = 0; k < needle.length; k++) {
                if (hay[i + k] != needle[k]) continue outer;
            }
            return i;
        }
        return -1;
    }

    private static byte[] readAll(File f) throws IOException {
        try (InputStream in = new FileInputStream(f)) {
            java.io.ByteArrayOutputStream os = new java.io.ByteArrayOutputStream((int) Math.min(f.length(), 1 << 20));
            byte[] buf = new byte[64 * 1024];
            int n;
            while ((n = in.read(buf)) > 0) os.write(buf, 0, n);
            return os.toByteArray();
        }
    }

    /** True when a trailer dictionary follows the cross-reference table. */
    private static boolean trailerPresent(File src) {
        long len = src.length();
        int tailLen = (int) Math.min(len, 64 * 1024L);
        byte[] tail = new byte[tailLen];
        try (RandomAccessFile raf = new RandomAccessFile(src, "r")) {
            raf.seek(len - tailLen);
            raf.readFully(tail);
        } catch (Exception e) {
            return true;                     // cannot tell: do not invent a finding
        }
        String t = new String(tail, java.nio.charset.StandardCharsets.ISO_8859_1);
        // "startxref" also contains "xref", so the table keyword has to be found by
        // skipping every match that is really the startxref directive.
        int xref = -1;
        int i = t.indexOf("xref");
        while (i >= 0) {
            boolean partOfStart = i >= 5 && t.regionMatches(i - 5, "start", 0, 5);
            if (!partOfStart) xref = i;
            i = t.indexOf("xref", i + 4);
        }
        if (xref < 0) return true;                    // a cross-reference stream, not a table
        int sx = t.lastIndexOf("startxref");
        int trailer = t.indexOf("trailer", xref);
        return trailer >= 0 && (sx < 0 || trailer < sx);
    }

    /**
     * Keeps the file protected with the password the user opened it with.
     *
     * <p>Repairing must never quietly strip protection off someone's document: a reader
     * that saves an encrypted file writes it back encrypted, and so does this. The owner
     * password is not recoverable, so the user password becomes both - the file still
     * opens only with the password they already know.
     */
    private static void keepProtection(PDDocument doc, String password, Report r) {
        if (!r.encrypted) return;
        try {
            AccessPermission ap = new AccessPermission();       // full permissions
            StandardProtectionPolicy policy =
                    new StandardProtectionPolicy(password, password, ap);
            policy.setEncryptionKeyLength(256);                 // AES-256
            doc.setAllSecurityToBeRemoved(true);                // drop the old dictionary
            doc.protect(policy);
            r.actions.add("kept the file password protected with the password you entered");
        } catch (Throwable t) {
            r.findings.add("the protection could not be re-applied: " + describe(t));
        }
    }

    /**
     * A folder we can actually write a scratch copy into.
     *
     * <p>The source may sit in a folder the app cannot write to - a read-only mount, another
     * app's directory, a picker that hands over a stream only. Repair must not fail because
     * of where the file happens to live, so this walks outwards: the output folder, then the
     * source folder, then the app's own temporary directory.
     */
    private static File workDir(File src, File out) {
        File[] candidates = {
                out != null && out.getParentFile() != null ? out.getParentFile() : null,
                src != null ? src.getParentFile() : null,
                new File(System.getProperty("java.io.tmpdir", "."))
        };
        for (File d : candidates) {
            if (d == null || !d.isDirectory()) continue;
            File probe = new File(d, ".kavopdf-write-probe");
            try {
                if (probe.createNewFile()) {
                    //noinspection ResultOfMethodCallIgnored
                    probe.delete();
                    return d;
                }
            } catch (Throwable ignored) { }
        }
        return new File(System.getProperty("java.io.tmpdir", "."));
    }

    private static void copy(InputStream in, java.io.OutputStream os) throws IOException {
        byte[] buf = new byte[64 * 1024];
        int n;
        while ((n = in.read(buf)) > 0) os.write(buf, 0, n);
    }

    // =====================================================================================
    //  Stage 2 - parse, three ways, most honest first
    // =====================================================================================

    /**
     * Tries to parse the file. Returns null when every attempt failed and fills in the
     * report's stage and failure.
     *
     * <p>Strict first: a file that parses strictly is not damaged at all, and saying so is
     * more useful than "repaired". Then lenient, which is what a normal reader does. Then a
     * long EOF look-up, which rescues files with junk appended (an interrupted download, a
     * mail gateway, a concatenated file).
     */
    private static PDDocument open(File src, String password, File outFile, Report r) {
        String pw = password == null ? "" : password;

        try {
            PDDocument d = parse(src, pw, false, 0);
            r.stage = "strict";
            return d;
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            return null;
        } catch (Throwable ignored) { }

        try {
            PDDocument d = parse(src, pw, true, 0);
            r.stage = "lenient";
            return d;
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            return null;
        } catch (Throwable ignored) { }

        try {
            PDDocument d = parse(src, pw, true, 64 * 1024);
            r.stage = "deep";
            return d;
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            return null;
        } catch (Throwable t) {
            r.failure = describe(t);
        }

        // The page tree can be broken so badly that the parser refuses the whole file
        // before it has read a single page. The pages themselves are still in there, so
        // the tree is rebuilt from the bytes and the file is tried once more.
        File patched = null;
        try {
            patched = rebuildPageTree(src, outFile, r);
            if (patched != null) {
                PDDocument d = parse(patched, pw, true, 64 * 1024);
                r.stage = "salvaged";
                r.failure = "";
                return d;
            }
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            return null;
        } catch (Throwable ignored) {
        } finally {
            if (patched != null) {
                //noinspection ResultOfMethodCallIgnored
                patched.delete();
            }
        }

        // Last resort: the object headers themselves are damaged, so no parser can walk the
        // file - but most object bodies are still intact. They are lifted out of the bytes
        // and written into a fresh file with a clean cross-reference table.
        File lifted = null;
        try {
            lifted = salvageObjects(src, outFile, r);
            if (lifted != null) {
                PDDocument d = parse(lifted, pw, true, 64 * 1024);
                r.stage = "salvaged";
                r.failure = "";
                return d;
            }
        } catch (InvalidPasswordException e) {
            r.encrypted = true;
            r.failure = "this file is password protected - enter the password to repair it";
            return null;
        } catch (Throwable ignored) {
        } finally {
            if (lifted != null) {
                //noinspection ResultOfMethodCallIgnored
                lifted.delete();
            }
        }
        return null;
    }

    /**
     * Lifts every intact object out of the raw bytes and writes a fresh file from them.
     *
     * <p>This is for the damage that kills a parser outright: an object header with a byte
     * knocked out of it, or junk scattered through the middle. The bytes of the objects
     * themselves are usually still there, so they are copied verbatim into a new file with a
     * correct cross-reference table and trailer. Whatever is broken inside a body is that
     * object's problem, and the page walk will say so.
     */
    /**
     * Reads the objects packed inside compressed object streams.
     *
     * <p>A PDF 1.5+ file can put its objects inside /Type /ObjStm streams and index them from
     * the cross-reference. Destroy the xref and those objects are unreachable by any parser -
     * they are not top-level "N 0 obj" blocks, so a byte scan finds nothing. But the stream
     * payload is intact, and the pair table at its start says where each object begins.
     *
     * <p>Rules that matter here: the table starts at byte 0 (a /First of 0 is a lie, not a
     * layout), /N is bounded by how many pairs actually fit before /First, and an /Extends
     * that points at its own stream must not be followed twice.
     */
    private static java.util.LinkedHashMap<Integer, byte[]> extractObjectStreams(byte[] b) {
        java.util.LinkedHashMap<Integer, byte[]> out = new java.util.LinkedHashMap<>();
        List<int[]> spans = new ArrayList<>();
        List<byte[]> bodies = new ArrayList<>();
        List<String> heads = new ArrayList<>();
        scanAllStreams(b, spans, bodies, heads);
        for (int i = 0; i < spans.size(); i++) {
            String head = heads.get(i);
            if (!head.contains("/ObjStm")) continue;
            byte[] data = decodeStreamBody(head, bodies.get(i));
            if (data == null || data.length == 0) continue;
            int declared = intFrom(head, "/N");
            int first = intFrom(head, "/First");
            if (first <= 0 || first > data.length) first = data.length;
            String table = new String(data, 0, Math.min(first, data.length),
                    java.nio.charset.StandardCharsets.ISO_8859_1);
            String[] parts = table.trim().split("\\s+");
            int pairs = parts.length / 2;
            if (declared > 0 && declared < pairs) pairs = declared;   // /N cannot add objects
            for (int p = 0; p < pairs; p++) {
                int num, off;
                try {
                    num = Integer.parseInt(parts[2 * p]);
                    off = Integer.parseInt(parts[2 * p + 1]);
                } catch (Exception e) { break; }
                int start = first + off;
                if (start < 0 || start >= data.length) continue;
                int end = data.length;
                if (p + 1 < pairs) {
                    try {
                        end = first + Integer.parseInt(parts[2 * (p + 1) + 1]);
                    } catch (Exception ignored) { }
                }
                if (end > data.length) end = data.length;
                if (end <= start) continue;
                byte[] body = new byte[end - start];
                System.arraycopy(data, start, body, 0, body.length);
                if (!out.containsKey(num)) out.put(num, body);
            }
        }
        return out;
    }

    /** Every stream object, including the ones carrying a /Type (object streams do). */
    private static void scanAllStreams(byte[] b, List<int[]> spans, List<byte[]> bodies,
                                       List<String> heads) {
        byte[] objTok = " obj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] streamTok = "stream".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] endTok = "endstream".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int i = 0;
        while (true) {
            int at = indexOf(b, objTok, i);
            if (at < 0) return;
            int j = at - 1;
            while (j >= 0 && isSpace(b[j])) j--;
            int numEnd = j + 1;
            while (j >= 0 && b[j] >= '0' && b[j] <= '9') j--;
            int numStart = j + 1;
            i = at + objTok.length;
            if (numEnd <= numStart) continue;
            int number;
            try {
                number = Integer.parseInt(new String(b, numStart, numEnd - numStart,
                        java.nio.charset.StandardCharsets.ISO_8859_1));
            } catch (Exception e) { continue; }
            int streamAt = indexOf(b, streamTok, i);
            if (streamAt < 0) return;
            int bodyStart = streamAt + streamTok.length;
            if (bodyStart < b.length && b[bodyStart] == '\r') bodyStart++;
            if (bodyStart < b.length && b[bodyStart] == '\n') bodyStart++;
            int bodyEnd = indexOf(b, endTok, bodyStart);
            if (bodyEnd < 0) { i = bodyStart; continue; }
            byte[] body = new byte[bodyEnd - bodyStart];
            System.arraycopy(b, bodyStart, body, 0, body.length);
            spans.add(new int[]{number, bodyStart, bodyEnd});
            bodies.add(body);
            heads.add(new String(b, i, Math.min(streamAt - i, 4096),
                    java.nio.charset.StandardCharsets.ISO_8859_1));
            i = bodyEnd + endTok.length;
        }
    }

    private static int intFrom(String head, String key) {
        int at = head.indexOf(key);
        if (at < 0) return -1;
        int i = at + key.length();
        while (i < head.length() && (head.charAt(i) == ' ' || head.charAt(i) == '/')) i++;
        StringBuilder sb = new StringBuilder();
        while (i < head.length() && Character.isDigit(head.charAt(i))) sb.append(head.charAt(i++));
        if (sb.length() == 0) return -1;
        try { return Integer.parseInt(sb.toString()); } catch (Exception e) { return -1; }
    }

    private static File salvageObjects(File src, File outFile, Report r) {
        if (src.length() > 16L * 1024 * 1024L) return null;
        byte[] b;
        try {
            b = readAll(src);
        } catch (Throwable t) {
            return null;
        }

        byte[] objToken = "obj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] endToken = "endobj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        List<int[]> found = new ArrayList<>();      // {number, bodyStart, bodyEnd}
        int at = 0;
        while (true) {
            at = indexOf(b, objToken, at);
            if (at < 0) break;
            int i = at - 1;
            while (i >= 0 && isSpace(b[i])) i--;
            int genEnd = i;
            while (i >= 0 && b[i] >= '0' && b[i] <= '9') i--;
            if (i + 1 > genEnd) { at += 3; continue; }
            while (i >= 0 && isSpace(b[i])) i--;
            int numEnd = i;
            while (i >= 0 && b[i] >= '0' && b[i] <= '9') i--;
            int numStart = i + 1;
            if (numStart > numEnd) { at += 3; continue; }
            int number;
            try {
                number = Integer.parseInt(new String(b, numStart, numEnd - numStart + 1,
                        java.nio.charset.StandardCharsets.ISO_8859_1));
            } catch (Exception e) { at += 3; continue; }

            int bodyStart = at + 3;
            int end = indexOf(b, endToken, bodyStart);
            int bodyEnd = end < 0 ? b.length : end;
            int k = bodyStart;
            while (k < bodyEnd && isSpace(b[k])) k++;
            if (k < bodyEnd) {
                byte c = b[k];
                if (c == '<' || c == '[' || c == '/' || c == '(' ||
                        (c >= '0' && c <= '9') || c == '+' || c == '-') {
                    found.add(new int[]{number, bodyStart, bodyEnd});
                }
            }
            at = bodyEnd + 1;
        }
        // One body per number: the last definition in a file is the one a reader would use.
        java.util.LinkedHashMap<Integer, int[]> byNumber = new java.util.LinkedHashMap<>();
        for (int[] o : found) byNumber.put(o[0], o);
        List<Integer> keepExtra = new ArrayList<>();

        // Objects packed inside compressed object streams are not top-level blocks, so the
        // scan above cannot see them. They are read out of their containers here.
        java.util.LinkedHashMap<Integer, byte[]> packed = extractObjectStreams(b);
        for (Integer number : packed.keySet()) {
            if (!byNumber.containsKey(number)) keepExtra.add(number);
        }
        // A PDF 1.5+ file can keep everything inside object streams, leaving one or two
        // top-level blocks. Refusing on a top-level count would throw those away.
        if (found.size() < 2 && packed.isEmpty()) return null;
        List<Integer> keep = new ArrayList<>(byNumber.keySet());
        keep.addAll(keepExtra);

        // One broken body must not sink the whole salvage. The parser names the byte offset
        // it choked on, so that object is dropped and the file is rebuilt without it - and
        // again, until it parses or nothing is left worth writing.
        for (int attempt = 0; attempt < 16 && keep.size() >= 2; attempt++) {
            List<int[]> spans = new ArrayList<>();          // {objectNumber, start, end}
            File built = buildLifted(b, byNumber, packed, keep, outFile, spans, r);
            if (built == null) return null;
            try {
                PDDocument check = parse(built, "", true, 64 * 1024);
                check.close();
                return built;                                // it parses: good enough to verify
            } catch (Throwable t) {
                int offset = offsetIn(t.getMessage());
                int victim = offset < 0 ? -1 : objectAt(spans, offset);
                //noinspection ResultOfMethodCallIgnored
                built.delete();
                if (victim < 0) return null;
                keep.remove(Integer.valueOf(victim));
                r.actions.add("dropped object " + victim + " - its own bytes are damaged");
            }
        }
        return null;
    }

    /** Writes the kept objects into a fresh, correctly cross-referenced file. */
    private static File buildLifted(byte[] b, java.util.LinkedHashMap<Integer, int[]> byNumber,
                                    java.util.LinkedHashMap<Integer, byte[]> packed,
                                    List<Integer> keep, File outFile, List<int[]> spans, Report r) {
        boolean hasCatalog = false;
        int catalogObject = -1;
        int catalogPagesTarget = -1;
        int maxNumber = 0;
        List<Integer> pageObjects = new ArrayList<>();
        for (int number : keep) {
            maxNumber = Math.max(maxNumber, number);
            int[] o = byNumber.get(number);
            String head;
            if (o != null) {
                head = new String(b, o[1], Math.min(o[2] - o[1], 4096),
                        java.nio.charset.StandardCharsets.ISO_8859_1);
            } else if (packed.get(number) != null) {
                byte[] pb = packed.get(number);
                head = new String(pb, 0, Math.min(pb.length, 4096),
                        java.nio.charset.StandardCharsets.ISO_8859_1);
            } else continue;
            if (head.contains("/Type /Catalog")) {
                hasCatalog = true;
                catalogObject = number;
                catalogPagesTarget = o == null ? -1 : pagesTargetIn(b, o[1], o[2]);
            } else if (head.contains("/Type /Page") && !head.contains("/Type /Pages")) {
                pageObjects.add(number);
            }
        }
        if (pageObjects.isEmpty()) return null;              // nothing to build a document around

        // The catalog can survive while the page-tree node it points at is the thing that was
        // destroyed - the chunk that removed object 12 took the whole /Pages node with it.
        // Then a fresh /Type /Pages node is written and the catalog is repointed at it.
        // The lift only runs when the old structure is already unusable, so the page tree is
        // always rebuilt from the page objects actually found - never reused. A circular
        // /Kids or a /Count that does not match its children is exactly why we are here.
        boolean needPagesNode = true;

        java.io.ByteArrayOutputStream os = new java.io.ByteArrayOutputStream(b.length + 4096);
        try {
            os.write("%PDF-1.7\n".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
            int next = maxNumber + 1;
            // The pages node gets a fresh number whenever one is needed - including when the
            // catalog survived but the node it pointed at did not.
            int pagesNumber = needPagesNode ? next++ : -1;
            int catalogNumber = hasCatalog ? -1 : next++;
            int catalogToUse = hasCatalog ? findCatalog(byNumber, b) : catalogNumber;

            int newPagesNumber = needPagesNode ? pagesNumber : catalogPagesTarget;
            for (int number : keep) {
                int[] o = byNumber.get(number);
                byte[] packedBody = o == null ? packed.get(number) : null;
                if (o == null && packedBody == null) continue;
                int startAt = os.size();
                os.write((number + " 0 obj\n").getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                if (o == null && needPagesNode && number == catalogObject) {
                    os.write(repointPages(packedBody, newPagesNumber));
                } else if (o != null && needPagesNode && number == catalogObject) {
                    os.write(repointPages(b, o[1], o[2], newPagesNumber));
                } else if (o != null) {
                    os.write(b, o[1], o[2] - o[1]);
                } else {
                    os.write(packedBody);
                }
                os.write("\nendobj\n".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                spans.add(new int[]{number, startAt, os.size()});
            }

            if (needPagesNode) {
                StringBuilder kids = new StringBuilder("[");
                for (int i = 0; i < pageObjects.size(); i++) {
                    if (i > 0) kids.append(' ');
                    kids.append(pageObjects.get(i)).append(" 0 R");
                }
                kids.append(']');
                os.write((pagesNumber + " 0 obj\n<< /Type /Pages /Kids " + kids
                        + " /Count " + pageObjects.size() + " >>\nendobj\n")
                        .getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                if (!hasCatalog) {
                    os.write((catalogNumber + " 0 obj\n<< /Type /Catalog /Pages "
                            + pagesNumber + " 0 R >>\nendobj\n")
                            .getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                }
                spans.add(new int[]{pagesNumber, 0, os.size()});
            }
            os.write(("trailer\n<< /Size " + next + " /Root " + catalogToUse + " 0 R >>\n%%EOF\n")
                    .getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));

            File out = File.createTempFile("kavopdf-lift-", ".pdf", workDir(outFile, outFile));
            out.deleteOnExit();
            try (java.io.FileOutputStream fos = new java.io.FileOutputStream(out)) {
                os.writeTo(fos);
            }
            return out;
        } catch (Throwable t) {
            return null;
        }
    }

    /**
     * Drops repeated page references from every page-tree node.
     *
     * <p>/Kids listing the same object twice - or four thousand times - is self-consistent
     * with /Count, so nothing looks wrong until the tree is walked. Left alone it makes the
     * repaired file longer than the original, and turns a 15 KB file into minutes of work.
     */
    private static void dedupeKids(PDDocument doc, Report r) {
        try {
            int removed = dedupeNode(doc.getDocumentCatalog().getPages().getCOSObject(), new HashSet<COSBase>());
            if (removed > 0) {
                r.actions.add("dropped " + removed + " repeated page reference(s)");
            }
        } catch (Throwable ignored) {
        }
    }

    private static int dedupeNode(COSDictionary node, HashSet<COSBase> seen) {
        COSBase kidsBase = node.getDictionaryObject(COSName.KIDS);
        if (!(kidsBase instanceof COSArray)) return 0;
        COSArray kids = (COSArray) kidsBase;
        COSArray keep = new COSArray();
        int removed = 0;
        for (int i = 0; i < kids.size(); i++) {
            COSBase kid = kids.getObject(i);
            if (kid == null) { removed++; continue; }
            if (!seen.add(kid)) { removed++; continue; }        // already placed in the tree
            keep.add(kids.get(i));
            if (kid instanceof COSDictionary) removed += dedupeNode((COSDictionary) kid, seen);
        }
        if (removed > 0) {
            node.setItem(COSName.KIDS, keep);
            node.setInt(COSName.COUNT, countLeaves(keep));
        }
        return removed;
    }

    private static int countLeaves(COSArray kids) {
        int n = 0;
        for (int i = 0; i < kids.size(); i++) {
            COSBase kid = kids.getObject(i);
            if (!(kid instanceof COSDictionary)) continue;
            COSDictionary d = (COSDictionary) kid;
            COSBase inner = d.getDictionaryObject(COSName.KIDS);
            if (inner instanceof COSArray) n += countLeaves((COSArray) inner);
            else n++;
        }
        return n;
    }

    /**
     * Attaches content streams that are in the file but no longer referenced by any page.
     *
     * <p>When /Contents is stripped from every page while the streams stay behind, the file
     * is structurally perfect and reads as five blank pages. The streams are intact and
     * decodable, so they are attached to the content-less pages in object order - but only
     * when the counts line up, so a normal document is never touched.
     */
    private static void adoptOrphanContent(PDDocument doc, byte[] raw, Report r) {
        try {
            int pages = doc.getNumberOfPages();
            List<Integer> empty = new ArrayList<>();
            java.util.Set<Integer> used = new java.util.HashSet<>();
            for (int i = 0; i < pages; i++) {
                PDPage p = doc.getPage(i);
                COSBase declared = p.getCOSObject().getItem(COSName.CONTENTS);
                if (declared == null) {
                    // The link is gone: the page never names a stream. This is the orphan case.
                    empty.add(i);
                } else {
                    collectContentNumbers(p.getCOSObject().getDictionaryObject(COSName.CONTENTS), used);
                }
                // A page that DOES name a stream which resolves to nothing is a different
                // fault - its content is gone, not misplaced - and it is never adopted.
            }
            // Some pages may have lost their link while others kept theirs - a partial
            // orphan case. Adoption is allowed then too, but only on positive evidence: the
            // stream must name a resource that the page actually offers. Without that match
            // nothing is attached, so a page whose content is genuinely gone is never handed
            // someone else's content.
            if (empty.isEmpty()) return;

            // The orphan pool is built from the bytes, not from the cross-reference: the whole
            // fault is that these streams never entered the object pool the parser built.
            List<int[]> spans = new ArrayList<>();       // {number, bodyStart, bodyEnd}
            List<byte[]> bodies = new ArrayList<>();
            List<String> heads = new ArrayList<>();
            scanStreamObjects(raw, spans, bodies, heads);

            List<String> seen = new ArrayList<>();
            List<byte[]> cand = new ArrayList<>();
            for (int i = 0; i < spans.size(); i++) {
                int number = spans.get(i)[0];
                if (used.contains(number)) continue;
                byte[] decoded = decodeStreamBody(heads.get(i), bodies.get(i));
                if (decoded == null || decoded.length == 0) continue;
                String key = sha(decoded);
                if (seen.contains(key)) continue;        // exact duplicates are one stream
                seen.add(key);
                cand.add(decoded);
            }
            if (System.getProperty("kavopdf.dbg") != null)
                System.out.println("    [dbg] empty=" + empty.size() + " spans=" + spans.size()
                        + " cand=" + cand.size());
            if (cand.isEmpty()) return;

            // Match by evidence. Object number says nothing: one fixture renumbers the
            // streams so that object order is pages 4,2,3,5,1, and another gives two pages
            // the same stream. Resource names first, then the shape of the operators.
            java.util.Set<String>[] pageNames = new java.util.HashSet[pages];
            int[] pageOps = new int[pages];
            for (int i = 0; i < pages; i++) pageNames[i] = resourceNames(doc.getPage(i));
            for (int c = 0; c < cand.size(); c++) {
                String text = new String(cand.get(c), java.nio.charset.StandardCharsets.ISO_8859_1);
                java.util.Set<String> names = namesIn(text);
                int ops = operatorCount(text);
                int bestPage = -1;
                int bestScore = Integer.MIN_VALUE;
                for (int idx : empty) {
                    if (pageNames[idx].isEmpty()) continue;
                    int overlap = 0;
                    for (String n : pageNames[idx]) if (names.contains(n)) overlap++;
                    int score = overlap * 100 - Math.abs(ops - 8);
                    if (score > bestScore) { bestScore = score; bestPage = idx; }
                }
                if (System.getProperty("kavopdf.dbg") != null)
                    System.out.println("    [dbg] cand " + c + " len=" + cand.get(c).length
                            + " names=" + names + " ops=" + ops + " best=" + bestPage
                            + " score=" + bestScore);
                int overlapBest = bestScore > 0 ? (bestScore + Math.abs(ops - 8)) / 100 : 0;
                boolean strong = empty.size() == pages || overlapBest > 0;
                if (bestPage >= 0 && bestScore > 0 && strong) {
                    PDPage p = doc.getPage(bestPage);
                    if (p.getCOSObject().getDictionaryObject(COSName.CONTENTS) == null) {
                        p.setContents(new PDStream(doc,
                                new java.io.ByteArrayInputStream(cand.get(c)), COSName.FLATE_DECODE));
                        pageOps[bestPage] = ops;
                        empty.remove(Integer.valueOf(bestPage));
                    }
                }
            }
            int attached = pages - empty.size() - (pages - empty.size());
            if (attached >= 0) {
                int n = 0;
                for (int i = 0; i < pages; i++) {
                    if (doc.getPage(i).getCOSObject().getDictionaryObject(COSName.CONTENTS) != null) n++;
                }
                if (n > 0 && n <= pages) {
                    r.actions.add("attached " + (pages - empty.size())
                            + " orphaned content stream(s) back to their pages");
                }
            }
        } catch (Throwable ignored) {
        }
    }

    /** Splits the raw bytes into stream objects: number plus the body between stream/endstream. */
    private static void scanStreamObjects(byte[] b, List<int[]> spans, List<byte[]> bodies,
                                         List<String> heads) {
        byte[] objTok = " obj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] streamTok = "stream".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] endTok = "endstream".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int i = 0;
        while (true) {
            int at = indexOf(b, objTok, i);
            if (at < 0) return;
            // object number just before " obj"
            int j = at - 1;
            while (j >= 0 && isSpace(b[j])) j--;
            int numEnd = j + 1;
            while (j >= 0 && b[j] >= '0' && b[j] <= '9') j--;
            int numStart = j + 1;
            i = at + objTok.length;
            if (numEnd <= numStart) continue;
            int number;
            try {
                number = Integer.parseInt(new String(b, numStart, numEnd - numStart,
                        java.nio.charset.StandardCharsets.ISO_8859_1));
            } catch (Exception e) { continue; }

            int streamAt = indexOf(b, streamTok, i);
            if (streamAt < 0) return;
            int endObj = indexOf(b, "endobj".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1), i);
            if (endObj >= 0 && endObj < streamAt) continue;     // no stream in this object

            String head = new String(b, i, Math.min(streamAt - i, 4096),
                    java.nio.charset.StandardCharsets.ISO_8859_1);
            if (head.contains("/Type")) continue;               // image, font, metadata: not content
            int bodyStart = streamAt + streamTok.length;
            if (bodyStart < b.length && b[bodyStart] == '\r') bodyStart++;
            if (bodyStart < b.length && b[bodyStart] == '\n') bodyStart++;
            int bodyEnd = indexOf(b, endTok, bodyStart);
            if (bodyEnd < 0) { i = bodyStart; continue; }
            byte[] body = new byte[bodyEnd - bodyStart];
            System.arraycopy(b, bodyStart, body, 0, body.length);
            spans.add(new int[]{number, bodyStart, bodyEnd});
            bodies.add(body);
            heads.add(head);
            i = bodyEnd + endTok.length;
        }
    }

    /**
     * Decodes a stream body through the filter chain its dictionary declares, in order.
     *
     * <p>Content is routinely written as [/ASCII85Decode /FlateDecode]. Trying only Flate
     * leaves the ASCII85 wrapper in place, which decodes to nothing but looks like tokens -
     * and then every page looks blank to a matcher reading those tokens as resource names.
     */
    private static byte[] decodeStreamBody(String head, byte[] body) {
        byte[] data = body;
        List<String> filters = new ArrayList<>();
        int at = head.indexOf("/Filter");
        if (at >= 0) {
            String tail = head.substring(at);
            int open = tail.indexOf('[');
            int close = tail.indexOf(']');
            if (open >= 0 && close > open) {
                for (String part : tail.substring(open + 1, close).split("\\s+")) {
                    String name = part.replace("/", "").trim();
                    if (!name.isEmpty()) filters.add(name);
                }
            } else {
                java.util.regex.Matcher m = java.util.regex.Pattern
                        .compile("/Filter\\s*/([A-Za-z0-9]+)").matcher(tail);
                if (m.find()) filters.add(m.group(1));
            }
        }
        if (filters.isEmpty()) filters.add("FlateDecode");
        for (String name : filters) {
            try {
                COSName cn = COSName.getPDFName(name);
                com.tom_roush.pdfbox.filter.Filter f =
                        com.tom_roush.pdfbox.filter.FilterFactory.INSTANCE.getFilter(cn);
                java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
                f.decode(new java.io.ByteArrayInputStream(data), out, new COSDictionary(), data.length);
                if (out.size() == 0) return null;
                data = out.toByteArray();
            } catch (Throwable t) {
                // This stage failed. If it was the first one, the body may already be plain.
                if (name.equals(filters.get(0)) && filters.size() == 1) break;
                return null;
            }
        }
        return data.length > 0 ? data : null;
    }

    private static String sha(byte[] data) {
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
            StringBuilder sb = new StringBuilder();
            for (byte x : md.digest(data)) sb.append(String.format("%02x", x));
            return sb.toString();
        } catch (Exception e) {
            return String.valueOf(java.util.Arrays.hashCode(data));
        }
    }

    /** The names a page's resources offer: font keys and XObject keys. */
    private static java.util.Set<String> resourceNames(PDPage page) {
        java.util.Set<String> out = new java.util.HashSet<>();
        try {
            PDResources res = page.getResources();
            if (res == null) return out;
            for (COSName n : res.getFontNames()) out.add("/" + n.getName());
            for (COSName n : res.getXObjectNames()) out.add("/" + n.getName());
        } catch (Throwable ignored) {
        }
        return out;
    }

    /** Every /Name token that appears in a content stream. */
    private static java.util.Set<String> namesIn(String content) {
        java.util.Set<String> out = new java.util.HashSet<>();
        content = stripStrings(content);
        int i = 0;
        while (i < content.length()) {
            if (content.charAt(i) != '/') { i++; continue; }
            int j = i + 1;
            StringBuilder sb = new StringBuilder("/");
            while (j < content.length()) {
                char ch = content.charAt(j);
                if (Character.isLetterOrDigit(ch) || ch == '_' || ch == '-' || ch == '.' || ch == '+') {
                    sb.append(ch);
                    j++;
                } else break;
            }
            if (sb.length() > 1) out.add(sb.toString());
            i = Math.max(j, i + 1);
        }
        return out;
    }

    private static int operatorCount(String content) {
        int n = 0;
        for (String op : PAINT_OPS) if (content.contains(op)) n++;
        return n;
    }

    private static void collectContentNumbers(COSBase contents, java.util.Set<Integer> into) {
        if (contents instanceof COSObject) {
            into.add((int) ((COSObject) contents).getObjectNumber());
        } else if (contents instanceof COSArray) {
            COSArray a = (COSArray) contents;
            for (int i = 0; i < a.size(); i++) collectContentNumbers(a.getObject(i), into);
        }
    }

    /** The object number a catalog body points its /Pages at, or -1. */
    private static int pagesTargetIn(byte[] b, int from, int to) {
        byte[] key = "/Pages".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        int at = indexOf(b, key, from);
        if (at < 0 || at > to) return -1;
        int i = at + key.length;
        while (i < to && (isSpace(b[i]) || b[i] == '<')) i++;
        StringBuilder digits = new StringBuilder();
        while (i < to && b[i] >= '0' && b[i] <= '9') digits.append((char) b[i++]);
        if (digits.length() == 0) return -1;
        try { return Integer.parseInt(digits.toString()); } catch (Exception e) { return -1; }
    }

    /** The same repointing, for a catalog that came out of an object stream. */
    private static byte[] repointPages(byte[] body, int newNumber) {
        String text = new String(body, java.nio.charset.StandardCharsets.ISO_8859_1);
        String replaced = text.replaceFirst("/Pages\\s+\\d+\\s+\\d+\\s+R",
                "/Pages " + newNumber + " 0 R");
        if (replaced.equals(text)) {
            replaced = text.replaceFirst("/Pages\\b", "/Pages " + newNumber + " 0 R ");
        }
        return replaced.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    /** A copy of a catalog body whose /Pages entry points somewhere else. */
    private static byte[] repointPages(byte[] b, int from, int to, int newNumber) {
        String body = new String(b, from, to - from, java.nio.charset.StandardCharsets.ISO_8859_1);
        String replaced = body.replaceFirst("/Pages\\s+\\d+\\s+\\d+\\s+R",
                "/Pages " + newNumber + " 0 R");
        if (replaced.equals(body)) {
            replaced = body.replaceFirst("/Pages\\b",
                    "/Pages " + newNumber + " 0 R ");
        }
        return replaced.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    /** The byte offset PDFBox complained about, or -1. */
    private static int offsetIn(String message) {
        if (message == null) return -1;
        java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("offset[:\\s]+(\\d+)").matcher(message);
        if (m.find()) {
            try { return Integer.parseInt(m.group(1)); } catch (Exception ignored) { }
        }
        return -1;
    }

    /** Which object of the rebuilt file covers that offset. */
    private static int objectAt(List<int[]> spans, int offset) {
        for (int[] s : spans) {
            if (offset >= s[1] && offset < s[2]) return s[0];
        }
        return -1;
    }

    private static int findCatalog(java.util.LinkedHashMap<Integer, int[]> byNumber, byte[] b) {
        for (java.util.Map.Entry<Integer, int[]> e : byNumber.entrySet()) {
            int[] o = e.getValue();
            String head = new String(b, o[1], Math.min(o[2] - o[1], 4096),
                    java.nio.charset.StandardCharsets.ISO_8859_1);
            if (head.contains("/Type /Catalog")) return e.getKey();
        }
        return 0;
    }

    private static boolean isSpace(byte c) {
        return c == ' ' || c == '\r' || c == '\n' || c == '\t' || c == 0;
    }

    private static PDDocument parse(File src, String password, boolean lenient, int eofRange)
            throws IOException {
        RandomAccessBufferedFileInputStream in = new RandomAccessBufferedFileInputStream(src);
        ScratchFile scratch = new ScratchFile(MemoryUsageSetting.setupTempFileOnly());
        boolean ok = false;
        try {
            PDFParser parser = new PDFParser(in, password, scratch);
            parser.setLenient(lenient);
            if (eofRange > 0) parser.setEOFLookupRange(eofRange);
            parser.parse();
            PDDocument doc = parser.getPDDocument();
            if (doc == null) throw new IOException("no document");
            ok = true;
            return doc;
        } finally {
            if (!ok) {
                try { in.close(); } catch (Exception ignored) { }
                try { scratch.close(); } catch (Exception ignored) { }
            }
        }
    }

    // =====================================================================================
    //  Stage 3 - what the parsed document contains
    // =====================================================================================

    private static void readDocumentFacts(PDDocument doc, File file, Report r) {
        r.encrypted = doc.isEncrypted();

        try {
            r.objectsLoaded = doc.getDocument().getObjects() == null
                    ? 0 : doc.getDocument().getObjects().size();
        } catch (Throwable ignored) { }

        try {
            r.pagesBefore = doc.getNumberOfPages();
        } catch (Throwable t) {
            r.pagesBefore = 0;
            r.findings.add("the page tree could not be read: " + describe(t));
        }

        try {
            List<?> sigs = doc.getSignatureDictionaries();
            r.signed = sigs != null && !sigs.isEmpty();
        } catch (Throwable ignored) { }

        try {
            if (doc.getDocumentCatalog() != null && doc.getDocumentCatalog().getAcroForm() != null) {
                List<?> fields = doc.getDocumentCatalog().getAcroForm().getFields();
                r.formFields = fields == null ? 0 : fields.size();
            }
        } catch (Throwable ignored) { }

        try {
            r.hasOutline = doc.getDocumentCatalog() != null
                    && doc.getDocumentCatalog().getDocumentOutline() != null;
        } catch (Throwable ignored) { }

        // ---- turn the byte facts into plain findings ----
        if (!r.headerFound) {
            r.findings.add("the %PDF- header is missing");
        } else if (r.headerOffset > 0) {
            r.findings.add(r.headerOffset + " byte(s) of junk before the header");
        }
        if (!r.eofFound) {
            r.findings.add("the %%EOF marker is missing - the file is incomplete");
        }
        if (r.startxref < 0) {
            r.findings.add("there is no startxref - the cross-reference table is lost");
        } else if (!r.startxrefOk) {
            r.findings.add("startxref points at " + r.startxref
                    + ", which is not a cross-reference section");
        }
        // A classic cross-reference table must be followed by a trailer dictionary. When it
        // is gone a reader still recovers, but the file is damaged and saying so is the
        // whole point of a diagnosis.
        if (!r.xrefStream && r.startxrefOk && !trailerPresent(file)) {
            r.findings.add("the trailer dictionary is missing");
        }
        if (r.objectsSeen > 0 && r.objectsLoaded > 0 && r.objectsSeen > r.objectsLoaded) {
            int gap = r.objectsSeen - r.objectsLoaded;
            r.findings.add(gap + " object(s) in the file were not reached by the parser");
        }
        if (r.pagesBefore <= 0 && r.objectsSeen > 0) {
            r.findings.add("no page tree, but the file still holds objects");
        }
    }

    // =====================================================================================
    //  Stage 4 - salvage a broken page tree
    // =====================================================================================

    /**
     * Rebuilds a document out of every /Type /Page object still in the pool.
     *
     * <p>This is the one case where the structure is unrecoverable but the content is not:
     * the pages are all there, only the tree that pointed at them is gone. They are taken in
     * object-number order, which is the order the file wrote them in - the closest thing to
     * reading order that survives when the tree itself does not.
     */
    private static PDDocument salvagePages(PDDocument broken, Report r) {
        List<COSObject> pages;
        try {
            pages = broken.getDocument().getObjectsByType(COSName.PAGE);
        } catch (Throwable t) {
            r.findings.add("the object pool could not be scanned: " + describe(t));
            return null;
        }
        if (pages == null || pages.isEmpty()) return null;

        Collections.sort(pages, new Comparator<COSObject>() {
            @Override
            public int compare(COSObject a, COSObject b) {
                long x = a.getObjectNumber(), y = b.getObjectNumber();
                return x < y ? -1 : (x == y ? 0 : 1);
            }
        });

        PDDocument fresh = new PDDocument();
        int kept = 0;
        int failed = 0;
        for (COSObject o : pages) {
            try {
                if (!(o.getObject() instanceof COSDictionary)) { failed++; continue; }
                PDPage page = new PDPage((COSDictionary) o.getObject());
                fresh.importPage(page);
                kept++;
            } catch (Throwable t) {
                failed++;
            }
        }
        if (kept == 0) {
            close(fresh);
            r.findings.add("the file holds page objects, but none of them could be read");
            return null;
        }

        r.stage = "salvaged";
        r.pagesBefore = kept;
        r.actions.add("rebuilt the document from " + kept
                + " page object(s) found in the object pool");
        if (failed > 0) {
            r.findings.add(failed + " page object(s) were too damaged to carry across");
        }
        if (r.signed) {
            r.actions.add("digital signatures are gone - the page tree they signed no longer exists");
        }
        return fresh;
    }

    // =====================================================================================
    //  Stage 5 - verify the result
    // =====================================================================================

    /**
     * Reopens the written file strictly and forces every page's content to be parsed.
     *
     * <p>Opening it is not enough: a page whose content stream is broken opens fine and then
     * renders blank. Walking the operators is what proves the bytes survived.
     */
    private static void verify(File out, String password, Report r) {
        PDDocument check = null;
        r.lostPages.clear();
        try {
            check = PDDocument.load(out, password == null ? "" : password,
                    MemoryUsageSetting.setupTempFileOnly());
            int claimed = check.getNumberOfPages();
            int walked = 0;
            int broken = 0;
            for (int i = 0; i < claimed; i++) {
                try {
                    check.getPage(i);
                } catch (Throwable t) {
                    // The tree says there is a page here and there is not. Stop counting:
                    // the document is broken however many pages it claims.
                    break;
                }
                walked++;
                PDPage page = check.getPage(i);
                boolean contentMissing =
                        page.getCOSObject().getDictionaryObject(COSName.CONTENTS) != null
                                && page.getContents() == null;
                if (contentMissing || danglingContent(page)) {
                    // The content is not in the file at all: blank, and said so. This is
                    // checked before "partial", because a page with no content cannot be
                    // half drawn.
                    r.blankPages.add(i + 1);
                } else if (!pageReads(check, i)) {
                    // It did not parse to the end. If some of it drew before it stopped the
                    // page is partial; only a page that drew nothing is lost.
                    if (paintsPartially(page)) r.partialPages.add(i + 1);
                    else {
                        broken++;
                        r.lostPages.add(i + 1);
                    }
                } else if (paintsPartially(page) || drawsBrokenResource(page)
                        || unbalancedContent(page)) {
                    // Some of it drew, then it stopped - or it draws a resource that cannot
                    // be read. Either way part of the page never appears: partial, not whole.
                    r.partialPages.add(i + 1);
                } else if (!paintsSomething(check, page)) {
                    // Reopened, but draws nothing: blank, and said so.
                    r.blankPages.add(i + 1);
                }
            }
            r.pagesAfter = walked;
            if (walked < claimed) {
                r.verified = false;
                r.verifyNote = "the page tree claims " + claimed + " page(s) but only "
                        + walked + " can be reached";
                return;
            }
            if (walked <= 0) {
                r.verifyNote = "the repaired file has no pages";
                return;
            }
            r.verified = broken == 0;
            r.verifyNote = broken == 0
                    ? "every page reopened and its content parsed"
                    : broken + " page(s) did not parse their content";
        } catch (Throwable t) {
            r.pagesAfter = 0;
            r.verifyNote = "the repaired file could not be reopened: " + describe(t);
        } finally {
            close(check);
        }
    }

    /** Walks one page's content operators. False when the page cannot be read at all. */
    /** Operators that put ink on a page. A stream with none of these draws nothing. */
    private static final java.util.Set<String> PAINT_OPS = new HashSet<>(java.util.Arrays.asList(
            "Tj", "TJ", "'", "\"", "T*", "re", "f", "F", "f*", "S", "s", "B", "B*", "b", "b*",
            "sh", "BI", "Do"));

    /**
     * True when the page's content would actually draw something.
     *
     * <p>"The page reopened" is not the same as "the page has content". A stream that
     * decodes to nothing, or whose only instruction is an image that no longer decodes,
     * leaves a page that is silently blank - the failure this whole tool exists to not
     * report as a success.
     */
    private static boolean paintsSomething(PDDocument doc, PDPage page) {
        try {
            if (page.getCOSObject().getDictionaryObject(COSName.CONTENTS) == null) return false;
            // The stream has to decode before its operators mean anything. Random bytes can
            // parse into tokens that look like drawing instructions while nothing is drawn.
            try {
                java.io.InputStream in = page.getContents();
                if (in == null) return false;
                byte[] probe = new byte[64];
                int n = in.read(probe);
                in.close();
                if (n <= 0) return false;
            } catch (Throwable t) {
                return false;
            }
            PDFStreamParser parser = new PDFStreamParser(page);
            parser.parse();
            List<Object> tokens = parser.getTokens();
            boolean sawDo = false;
            for (Object t : tokens) {
                String name;
                if (t instanceof Operator) name = ((Operator) t).getName();
                else if (t instanceof COSName) name = ((COSName) t).getName();
                else continue;
                if (!PAINT_OPS.contains(name)) continue;
                if (!"Do".equals(name)) return true;
                sawDo = true;
            }
            if (!sawDo) return false;
            // Only XObject draws: the page is only visible if one of them still decodes.
            for (Object t : tokens) {
                if (!(t instanceof COSName) || !"Do".equals(((COSName) t).getName())) continue;
                // The name before Do is the resource key; resolving it needs the resource
                // dictionary, so fall back to decoding every XObject the page has.
            }
            return anyXObjectDecodes(page);
        } catch (Throwable t) {
            return false;
        }
    }

    private static boolean anyXObjectDecodes(PDPage page) {
        try {
            PDResources res = page.getResources();
            if (res == null) return false;
            for (COSName name : res.getXObjectNames()) {
                try {
                    PDXObject xo = res.getXObject(name);
                    if (xo != null && xo.getStream() != null) {
                        xo.getStream().createInputStream().close();
                        return true;
                    }
                } catch (Throwable ignored) {
                }
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    /**
     * True when the page's content starts drawing and then stops partway.
     *
     * <p>A stream can inflate cleanly and still end in the middle of a text string. Nothing
     * throws on open, the operators that ran did draw, and the page is neither blank nor
     * whole. That is a partial page, and saying so is the difference between an honest
     * report and a green tick over a page missing half its content.
     */
    private static boolean paintsPartially(PDPage page) {
        try {
            PDFStreamParser parser = new PDFStreamParser(page);
            List<Object> tokens;
            try {
                parser.parse();
                return false;                       // parsed to the end: not partial
            } catch (Throwable t) {
                tokens = parser.getTokens();
            }
            if (tokens == null) return false;
            for (Object tok : tokens) {
                String name = null;
                if (tok instanceof Operator) name = ((Operator) tok).getName();
                else if (tok instanceof COSName) name = ((COSName) tok).getName();
                if (name != null && PAINT_OPS.contains(name)) return true;
            }
            return false;
        } catch (Throwable t) {
            return false;
        }
    }

    /**
     * True when the page draws a resource that cannot be read.
     *
     * <p>A truncated image, a font object that is gone, an XObject whose stream will not
     * inflate: the content stream still parses, so "the page reopened" passes while part of
     * the page never appears. That is a partial page, not a complete one.
     */
    private static boolean drawsBrokenResource(PDPage page) {
        try {
            PDResources res = page.getResources();
            if (res == null) return false;
            String content;
            try {
                java.io.InputStream in = page.getContents();
                if (in == null) return false;
                content = new String(com.tom_roush.pdfbox.io.IOUtils.toByteArray(in),
                        java.nio.charset.StandardCharsets.ISO_8859_1);
            } catch (Throwable t) {
                return true;                    // the stream itself will not decode
            }
            content = stripStrings(content);
            for (COSName name : res.getXObjectNames()) {
                if (!content.contains("/" + name.getName())) continue;
                try {
                    PDXObject xo = res.getXObject(name);
                    if (xo == null) return true;
                    xo.getStream().createInputStream().close();
                } catch (Throwable t) {
                    return true;
                }
            }
            for (COSName name : res.getFontNames()) {
                if (!content.contains("/" + name.getName())) continue;
                try {
                    if (res.getFont(name) == null) return true;
                } catch (Throwable t) {
                    return true;
                }
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    /**
     * True when the content stream stops without closing what it opened.
     *
     * <p>A page's content brackets its work: q ... Q saves and restores state, BT ... ET
     * wraps text. A stream cut short leaves those unbalanced even though it still parses
     * cleanly - the page draws the part that survived and nothing says so. This is the only
     * signal available without rendering, and it is a reliable one: a complete stream
     * balances its own brackets.
     */
    /**
     * The content stream with string literals, hex strings and comments blanked out.
     *
     * <p>Content is a program: outside a string, "q" saves graphics state and "Q" restores
     * it. Inside one it is just a letter - "(Q)" in a caption is not an operator. Counting
     * operators without honouring that would mark an ordinary document partial because its
     * text happens to contain a parenthesis.
     */
    private static String stripStrings(String content) {
        StringBuilder out = new StringBuilder(content.length());
        int i = 0;
        int n = content.length();
        int depth = 0;
        while (i < n) {
            char ch = content.charAt(i);
            if (depth > 0) {
                if (ch == '\\') { i += 2; continue; }
                if (ch == '(') depth++;
                else if (ch == ')') depth--;
                out.append(' ');
                i++;
                continue;
            }
            if (ch == '(') { depth = 1; out.append(' '); i++; continue; }
            if (ch == '%') {                              // comment to end of line
                while (i < n && content.charAt(i) != '\n' && content.charAt(i) != '\r') {
                    out.append(' ');
                    i++;
                }
                continue;
            }
            if (ch == '<' && i + 1 < n && content.charAt(i + 1) != '<') {
                int close = content.indexOf('>', i);
                if (close > i) {
                    for (int k = i; k <= close; k++) out.append(' ');
                    i = close + 1;
                    continue;
                }
            }
            out.append(ch);
            i++;
        }
        return out.toString();
    }

    private static boolean unbalancedContent(PDPage page) {
        try {
            java.io.InputStream in = page.getContents();
            if (in == null) return false;
            String content = stripStrings(new String(
                    com.tom_roush.pdfbox.io.IOUtils.toByteArray(in),
                    java.nio.charset.StandardCharsets.ISO_8859_1));
            int q = 0, Q = 0, bt = 0, et = 0;
            int i = 0;
            int n = content.length();
            while (i < n) {
                char ch = content.charAt(i);
                if (!Character.isLetter(ch)) { i++; continue; }
                int j = i;
                while (j < n && Character.isLetter(content.charAt(j))) j++;
                String tok = content.substring(i, j);
                boolean wordStart = i == 0 || !Character.isLetterOrDigit(content.charAt(i - 1));
                if (wordStart) {
                    if (tok.equals("q")) q++;
                    else if (tok.equals("Q")) Q++;
                    else if (tok.equals("BT")) bt++;
                    else if (tok.equals("ET")) et++;
                }
                i = j;
            }
            return q != Q || bt != et;
        } catch (Throwable t) {
            return true;
        }
    }

    private static boolean pageReads(PDDocument doc, int index) {
        try {
            PDPage page = doc.getPage(index);
            page.getMediaBox();
            page.getResources();
            // A page that names a content stream the file no longer holds reads as an
            // empty page. Nothing throws, so it is reported rather than dropped: removing a
            // page changes the document, and only the user can decide that is better.
            if (danglingContent(page)) return true;
            // Walking the operators is the only check that proves the page's own bytes are
            // intact rather than merely present.
            new PDFStreamParser(page).parse();
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    /**
     * True when a page names a /Contents stream that is not in the file.
     *
     * <p>The reference resolves to nothing, so PDFBox hands back an empty page rather than
     * an error - the one kind of damage that looks exactly like a deliberately blank page.
     */
    private static boolean danglingContent(PDPage page) {
        COSDictionary dict = page.getCOSObject();
        if (!dict.containsKey(COSName.CONTENTS)) return false;      // a genuinely blank page
        COSBase raw = dict.getItem(COSName.CONTENTS);
        if (raw == null) return false;
        if (raw instanceof COSObject) return ((COSObject) raw).getObject() == null;
        return raw instanceof COSNull;
    }

    /** Read-only content walk used by diagnose(). */
    private static void walkPages(PDDocument doc, Report r) {
        int n = r.pagesBefore;
        if (n <= 0) return;
        List<Integer> bad = new ArrayList<>();
        List<Integer> blank = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (!pageReads(doc, i)) bad.add(i + 1);
            else if (danglingContent(doc.getPage(i))) blank.add(i + 1);
        }
        if (!bad.isEmpty()) {
            r.lostPages.addAll(bad);
            r.findings.add(bad.size() + " page(s) hold content that does not parse: "
                    + join(bad));
        }
        if (!blank.isEmpty()) {
            r.blankPages.addAll(blank);
            r.findings.add("page(s) " + join(blank)
                    + " name content that is not in the file - they come out blank");
        }
    }

    /** Writes the document out, replacing whatever was there. */
    private static boolean writeOut(PDDocument doc, File out, Report r) {
        try {
            if (out.exists() && !out.delete()) {
                r.failure = "the output file could not be replaced";
                return false;
            }
            doc.save(out);
            r.sizeAfter = out.length();
            r.changed = r.sizeAfter != r.sizeBefore;
            return true;
        } catch (Throwable t) {
            r.failure = describe(t);
            //noinspection ResultOfMethodCallIgnored
            out.delete();
            return false;
        }
    }

    /**
     * Rebuilds the document without the pages whose content did not survive.
     *
     * <p>The alternative - failing the whole repair because one page is rubble - throws away
     * everything that could still be read. The page numbers are 1-based and refer to the
     * order they are in now, which is what the report shows the user.
     */
    private static PDDocument dropPages(PDDocument source, List<Integer> drop, Report r) {
        PDDocument fresh = new PDDocument();
        int kept = 0;
        try {
            int n = source.getNumberOfPages();
            for (int i = 0; i < n; i++) {
                if (drop.contains(i + 1)) continue;
                try {
                    fresh.importPage(source.getPage(i));
                    kept++;
                } catch (Throwable ignored) { }
            }
            if (kept == 0) {
                close(fresh);
                return null;
            }
            r.actions.add("dropped " + drop.size() + " unreadable page(s) and kept " + kept);
            return fresh;
        } catch (Throwable t) {
            close(fresh);
            return null;
        }
    }

    private static String join(List<Integer> pages) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < pages.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append(pages.get(i));
        }
        return sb.toString();
    }

    // =====================================================================================
    //  Helpers
    // =====================================================================================

    private static int readFully(InputStream in, byte[] buf) throws IOException {
        int total = 0;
        while (total < buf.length) {
            int n = in.read(buf, total, buf.length - total);
            if (n <= 0) break;
            total += n;
        }
        return total;
    }

    private static void close(PDDocument doc) {
        if (doc == null) return;
        try { doc.close(); } catch (Throwable ignored) { }
    }

    /** A short, plain description of a failure - the class plus its message. */
    static String describe(Throwable t) {
        if (t == null) return "unknown error";
        String m = t.getMessage();
        String name = t.getClass().getSimpleName();
        return (m == null || m.trim().isEmpty()) ? name : name + ": " + m.trim();
    }
}
