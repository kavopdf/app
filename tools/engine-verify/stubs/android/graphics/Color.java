package android.graphics;
public class Color {
  public static final int BLACK=0xFF000000,WHITE=0xFFFFFFFF,RED=0xFFFF0000,GREEN=0xFF00FF00,BLUE=0xFF0000FF,TRANSPARENT=0;
  public static int argb(int a,int r,int g,int b){return (a<<24)|(r<<16)|(g<<8)|b;}
  public static int rgb(int r,int g,int b){return argb(255,r,g,b);}
  public static int alpha(int c){return c>>>24;}
  public static int red(int c){return (c>>16)&0xFF;}
  public static int green(int c){return (c>>8)&0xFF;}
  public static int blue(int c){return c&0xFF;}
  public static float[] colorToHSV(int c,float[] h){ if(h==null)h=new float[3]; return h; }
}
