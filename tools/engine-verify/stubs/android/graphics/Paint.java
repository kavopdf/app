package android.graphics;
public class Paint {
  public enum Cap { BUTT, ROUND, SQUARE }
  public enum Join { MITER, ROUND, BEVEL }
  public enum Style { FILL, STROKE, FILL_AND_STROKE }
  public enum Align { LEFT, CENTER, RIGHT }
  private int color=0xFF000000, alpha=255, style=0, cap=0, join=0;
  private float strokeWidth=1f, strokeMiter=4f, textSize=12f;
  private PathEffect pathEffect; private Object shader, colorFilter, xfermode, typeface;
  public Paint(){}
  public Paint(int flags){}
  public Paint(Paint p){ set(p); }
  public void set(Paint p){ if(p==null)return; color=p.color; alpha=p.alpha; style=p.style; cap=p.cap; join=p.join; strokeWidth=p.strokeWidth; strokeMiter=p.strokeMiter; textSize=p.textSize; pathEffect=p.pathEffect; shader=p.shader; colorFilter=p.colorFilter; xfermode=p.xfermode; typeface=p.typeface; }
  public void reset(){ color=0xFF000000; alpha=255; style=0; cap=0; join=0; strokeWidth=1f; strokeMiter=4f; textSize=12f; pathEffect=null; shader=null; colorFilter=null; xfermode=null; typeface=null; }
  public int getFlags(){ return 0; } public void setFlags(int f){}
  public void setColor(int c){ color=c; }
  public int getColor(){ return color; }
  public void setAlpha(int a){ alpha=a; }
  public int getAlpha(){ return alpha; }
  public void setStyle(Style s){ style=s.ordinal(); }
  public Style getStyle(){ return Style.values()[style]; }
  public void setStrokeCap(Cap c){ cap=c.ordinal(); }
  public Cap getStrokeCap(){ return Cap.values()[cap]; }
  public void setStrokeJoin(Join j){ join=j.ordinal(); }
  public Join getStrokeJoin(){ return Join.values()[join]; }
  public void setStrokeWidth(float w){ strokeWidth=w; }
  public float getStrokeWidth(){ return strokeWidth; }
  public void setStrokeMiter(float m){ strokeMiter=m; }
  public float getStrokeMiter(){ return strokeMiter; }
  public void setTextSize(float s){ textSize=s; }
  public float getTextSize(){ return textSize; }
  public PathEffect setPathEffect(PathEffect e){ PathEffect o=pathEffect; pathEffect=e; return o; }
  public PathEffect getPathEffect(){ return pathEffect; }
  public Object setShader(Object s){ Object o=shader; shader=s; return o; }
  public Object getShader(){ return shader; }
  public Object setColorFilter(Object f){ Object o=colorFilter; colorFilter=f; return o; }
  public Object getColorFilter(){ return colorFilter; }
  public Object setXfermode(Object x){ Object o=xfermode; xfermode=x; return o; }
  public Object getXfermode(){ return xfermode; }
  public Object setTypeface(Object t){ Object o=typeface; typeface=t; return o; }
  public Object getTypeface(){ return typeface; }
  public void setAntiAlias(boolean b){} public boolean isAntiAlias(){ return true; }
  public void setDither(boolean b){} public void setFilterBitmap(boolean b){}
  public void setSubpixelText(boolean b){} public void setLinearText(boolean b){}
  public void setFakeBoldText(boolean b){} public void setUnderlineText(boolean b){}
  public void setStrikeThruText(boolean b){}
  public float measureText(String s){ return s==null?0:s.length()*textSize*0.5f; }
  public float measureText(char[] c,int i,int n){ return n*textSize*0.5f; }
  public float getFontSpacing(){ return textSize; }
  public float ascent(){ return -textSize*0.8f; } public float descent(){ return textSize*0.2f; }
  public void getTextBounds(String s,int a,int b,Rect r){ if(r!=null) r.set(0,0,(int)measureText(s),(int)textSize); }
}
