import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.font.*;
import com.tom_roush.pdfbox.text.*;
import com.tom_roush.fontbox.ttf.*;
import java.io.File;
import java.util.*;

public class GlyphProbe2 {
    public static void main(String[] a) throws Exception {
        PDDocument d = PDDocument.load(new File(a[0]));
        final Set<String> seen = new HashSet<>();
        PDFTextStripper s = new PDFTextStripper() {
            @Override protected void processTextPosition(TextPosition t) {
                String u = t.getUnicode();
                if (u != null && u.indexOf('\uFFFD') >= 0 && t.getFont() instanceof PDType0Font) {
                    PDType0Font f = (PDType0Font) t.getFont();
                    PDCIDFont desc = f.getDescendantFont();
                    if (!(desc instanceof PDCIDFontType2)) return;
                    PDCIDFontType2 c2 = (PDCIDFontType2) desc;
                    for (int c : t.getCharacterCodes()) {
                        if (!seen.add(f.getName() + "#" + c)) continue;
                        String out = "font=" + f.getName() + " code=0x" + Integer.toHexString(c);
                        try {
                            int gid = c2.codeToGID(c);
                            out += " gid=" + gid;
                            TrueTypeFont ttf = c2.getTrueTypeFont();
                            if (ttf == null) { out += " ttf=null"; }
                            else {
                                try {
                                    PostScriptTable ps = ttf.getPostScript();
                                    out += " postFormat=" + (ps == null ? "null" : ps.getFormatType())
                                         + " name=" + (ps == null ? "null" : ps.getName(gid));
                                } catch (Throwable e) { out += " postEX=" + e; }
                                try {
                                    CmapSubtable cm = ttf.getUnicodeCmap();
                                    if (cm == null) out += " cmap=null";
                                    else {
                                        StringBuilder hits = new StringBuilder();
                                        int[] cand = new int[]{0xFB00,0xFB01,0xFB02,0xFB03,0xFB04,0xFB05,0xFB06};
                                        for (int cp : cand) if (cm.getGlyphId(cp) == gid) hits.append(String.format("U+%04X ", cp));
                                        for (int cp = 0x20; cp < 0x7F; cp++) if (cm.getGlyphId(cp) == gid) hits.append(String.format("U+%04X ", cp));
                                        out += " cmapHits=[" + hits.toString().trim() + "]";
                                    }
                                } catch (Throwable e) { out += " cmapEX=" + e; }
                            }
                        } catch (Throwable e) { out += " EX=" + e; }
                        System.out.println(out);
                    }
                }
                super.processTextPosition(t);
            }
        };
        s.getText(d);
        d.close();
    }
}
