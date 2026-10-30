package android.graphics;
import java.awt.image.BufferedImage;
import java.io.OutputStream;
import javax.imageio.ImageIO;

public class Bitmap {
  public enum Config { ALPHA_8, RGB_565, ARGB_4444, ARGB_8888 }
  public enum CompressFormat { JPEG, PNG, WEBP }
  private BufferedImage img;
  private boolean recycled=false;
  public Bitmap(BufferedImage i){this.img=i;}
  public BufferedImage _image(){return img;}
  public void copyPixelsFromBuffer(java.nio.Buffer buf){
    int w=img.getWidth(), h=img.getHeight(); int[] px=new int[w*h];
    if(buf instanceof java.nio.IntBuffer){ ((java.nio.IntBuffer)buf).get(px); }
    else if(buf instanceof java.nio.ByteBuffer){
      java.nio.ByteBuffer bb=((java.nio.ByteBuffer)buf).duplicate();
      for(int i=0;i<px.length && bb.remaining()>=4;i++){ int r=bb.get()&0xFF,g=bb.get()&0xFF,b=bb.get()&0xFF,al=bb.get()&0xFF; px[i]=(al<<24)|(r<<16)|(g<<8)|b; }
    }
    img.setRGB(0,0,w,h,px,0,w);
  }
  public void copyPixelsToBuffer(java.nio.Buffer buf){
    int w=img.getWidth(), h=img.getHeight(); int[] px=new int[w*h]; img.getRGB(0,0,w,h,px,0,w);
    if(buf instanceof java.nio.IntBuffer){ ((java.nio.IntBuffer)buf).put(px); }
  }
  public static Bitmap createBitmap(int[] colors,int w,int h,Config c){
    BufferedImage bi=new BufferedImage(w,h,BufferedImage.TYPE_INT_ARGB); bi.setRGB(0,0,w,h,colors,0,w); return new Bitmap(bi);
  }

  private Boolean alphaCache=null;
  public boolean hasAlpha(){
    if(alphaCache!=null) return alphaCache;
    boolean a=false;
    if(img.getColorModel().hasAlpha()){
      int w=img.getWidth(),h=img.getHeight(); int[] px=new int[w*h]; img.getRGB(0,0,w,h,px,0,w);
      for(int v:px){ if(((v>>>24)&0xFF)<255){ a=true; break; } }
    }
    alphaCache=a; return a;
  }
  public int getRowBytes(){ return img.getWidth()*4; }
  public int getDensity(){ return 160; }
  public void setDensity(int d){}
  public void eraseColor(int c){ java.awt.Graphics2D g=img.createGraphics(); g.setColor(new java.awt.Color(c,true)); g.fillRect(0,0,img.getWidth(),img.getHeight()); g.dispose(); }
  public Bitmap copy(Config c,boolean m){ return createBitmap(this); }
  public int describeContents(){ return 0; }

  public int getWidth(){return img.getWidth();}
  public int getHeight(){return img.getHeight();}
  public Config getConfig(){return Config.ARGB_8888;}
  public int getPixel(int x,int y){return img.getRGB(x,y);}
  public void getPixels(int[] px,int off,int stride,int x,int y,int w,int h){ img.getRGB(x,y,w,h,px,off,stride); }
  public int getByteCount(){return img.getWidth()*img.getHeight()*4;}
  public void recycle(){recycled=true;}
  public boolean isRecycled(){return recycled;}
  public boolean isMutable(){return true;}
  public void setHasAlpha(boolean b){}
  public void setPremultiplied(boolean b){}
  public boolean isPremultiplied(){return true;}
  public boolean compress(CompressFormat fmt,int quality,OutputStream out){
    try{
      if(fmt==CompressFormat.PNG) return ImageIO.write(img,"png",out);
      BufferedImage rgb=new BufferedImage(img.getWidth(),img.getHeight(),BufferedImage.TYPE_INT_RGB);
      rgb.createGraphics().drawImage(img,0,0,null);
      javax.imageio.ImageWriter w=ImageIO.getImageWritersByFormatName("jpg").next();
      javax.imageio.stream.ImageOutputStream ios=ImageIO.createImageOutputStream(out);
      w.setOutput(ios);
      javax.imageio.plugins.jpeg.JPEGImageWriteParam jp=new javax.imageio.plugins.jpeg.JPEGImageWriteParam(java.util.Locale.getDefault());
      jp.setCompressionMode(javax.imageio.ImageWriteParam.MODE_EXPLICIT);
      jp.setCompressionQuality(Math.max(0.05f,Math.min(1f,quality/100f)));
      w.write(null,new javax.imageio.IIOImage(rgb,null,null),jp);
      ios.close(); w.dispose();
      return true;
    }catch(Exception e){throw new RuntimeException(e);}
  }
  public static Bitmap createBitmap(int w,int h,Config c){ return new Bitmap(new BufferedImage(w,h,BufferedImage.TYPE_INT_ARGB)); }
  public static Bitmap createBitmap(Bitmap src){ return createBitmap(src,0,0,src.getWidth(),src.getHeight()); }
  public static Bitmap createBitmap(Bitmap src,int x,int y,int w,int h){
    BufferedImage copy=new BufferedImage(w,h,src.hasAlpha()?BufferedImage.TYPE_INT_ARGB:BufferedImage.TYPE_INT_RGB);
    copy.createGraphics().drawImage(src.img.getSubimage(x,y,w,h),0,0,null);
    return new Bitmap(copy);
  }
  /**
   * The matrix overload the engine uses for EXIF rotation. It applies the matrix for
   * real, so a harness check that rotates an image sees rotated pixels rather than a
   * silently unchanged copy.
   */
  public static Bitmap createBitmap(Bitmap src,int x,int y,int w,int h,Matrix m,boolean filter){
    BufferedImage copy=new BufferedImage(w,h,BufferedImage.TYPE_INT_ARGB);
    java.awt.Graphics2D g=copy.createGraphics();
    float[] mv=new float[9];
    if(m!=null) m.getValues(mv);
    // Android's Matrix values are [scaleX, skewX, transX, skewY, scaleY, transY, ...]
    g.setTransform(new java.awt.geom.AffineTransform(mv[0],mv[3],mv[1],mv[4],mv[2],mv[5]));
    g.drawImage(src.img.getSubimage(x,y,w,h),0,0,null);
    g.dispose();
    return new Bitmap(copy);
  }
  public static Bitmap createScaledBitmap(Bitmap src,int w,int h,boolean f){
    BufferedImage copy=new BufferedImage(w,h,src.hasAlpha()?BufferedImage.TYPE_INT_ARGB:BufferedImage.TYPE_INT_RGB);
    copy.createGraphics().drawImage(src.img.getScaledInstance(w,h,java.awt.Image.SCALE_SMOOTH),0,0,null);
    return new Bitmap(copy);
  }
}
