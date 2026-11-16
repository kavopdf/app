import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import com.tom_roush.pdfbox.text.TextPosition;
import java.io.File;
import java.util.List;

public class Probe {
    public static void main(String[] a) throws Exception {
        PDDocument d = PDDocument.load(new File(a[0]));
        PDFTextStripper s = new PDFTextStripper() {
            int n = 0;
            @Override protected void processTextPosition(TextPosition t) {
                if (n < 25) {
                    System.out.println(String.format(
                        "u=%-3s size=%.3f sizeInPt=%.3f x=%.1f y=%.1f font=%s",
                        t.getUnicode(), t.getFontSize(), t.getFontSizeInPt(),
                        t.getXDirAdj(), t.getYDirAdj(), t.getFont().getName()));
                    n++;
                }
                super.processTextPosition(t);
            }
        };
        s.setStartPage(1); s.setEndPage(1);
        s.getText(d);
        d.close();
    }
}
