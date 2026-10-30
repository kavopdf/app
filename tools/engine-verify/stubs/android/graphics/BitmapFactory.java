package android.graphics;
import java.io.*;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;

public class BitmapFactory {
  public static class Options {
    public boolean inJustDecodeBounds=false;
    public int inSampleSize=1;
    public Bitmap.Config inPreferredConfig;
    public int outWidth, outHeight;
  }
  private static Bitmap decode(InputStream is, Options o){
    try{
      BufferedImage img=ImageIO.read(is);
      if(img==null) return null;
      if(o!=null){o.outWidth=img.getWidth();o.outHeight=img.getHeight();}
      if(o!=null && o.inJustDecodeBounds) return null;
      if(o!=null && o.inSampleSize>1){
        int nw=Math.max(1,img.getWidth()/o.inSampleSize), nh=Math.max(1,img.getHeight()/o.inSampleSize);
        boolean al=img.getColorModel().hasAlpha();
        BufferedImage sm=new BufferedImage(nw,nh,al?BufferedImage.TYPE_INT_ARGB:BufferedImage.TYPE_INT_RGB);
        sm.createGraphics().drawImage(img.getScaledInstance(nw,nh,java.awt.Image.SCALE_SMOOTH),0,0,null);
        img=sm;
      }
      boolean alpha=img.getColorModel().hasAlpha();
      BufferedImage argb=new BufferedImage(img.getWidth(),img.getHeight(),alpha?BufferedImage.TYPE_INT_ARGB:BufferedImage.TYPE_INT_RGB);
      argb.createGraphics().drawImage(img,0,0,null);
      return new Bitmap(argb);
    }catch(Exception e){return null;}
  }
  public static Bitmap decodeFile(String p){ try{return decode(new FileInputStream(p),null);}catch(Exception e){return null;} }
  public static Bitmap decodeFile(String p,Options o){ try{return decode(new FileInputStream(p),o);}catch(Exception e){return null;} }
  public static Bitmap decodeStream(InputStream is){ return decode(is,null); }
  public static Bitmap decodeStream(InputStream is,Rect pad,Options o){ return decode(is,o); }
  public static Bitmap decodeByteArray(byte[] d,int off,int len){ return decode(new ByteArrayInputStream(d,off,len),null); }
  public static Bitmap decodeByteArray(byte[] d,int off,int len,Options o){ return decode(new ByteArrayInputStream(d,off,len),o); }
}
