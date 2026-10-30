package android.graphics;
import java.util.ArrayList;
public class Path {
  public enum FillType { WINDING, EVEN_ODD, INVERSE_WINDING, INVERSE_EVEN_ODD }
  public enum Op { DIFFERENCE, INTERSECT, UNION, XOR, REVERSE_DIFFERENCE }
  private FillType ft=FillType.WINDING;
  public Path(){}
  public Path(Path src){}
  public void reset(){} public void rewind(){}
  public void setFillType(FillType f){ ft=f; }
  public FillType getFillType(){ return ft; }
  public void moveTo(float x,float y){} public void lineTo(float x,float y){}
  public void quadTo(float a,float b,float c,float d){} public void cubicTo(float a,float b,float c,float d,float e,float f){}
  public void close(){} public void rMoveTo(float x,float y){} public void rLineTo(float x,float y){}
  public void addRect(float l,float t,float r,float b,Object dir){}
  public void addRoundRect(float l,float t,float r,float b,float rx,float ry,Object dir){}
  public void addOval(float l,float t,float r,float b,Object dir){}
  public void addCircle(float x,float y,float rad,Object dir){}
  public void addPath(Path p){} public void addPath(Path p,Matrix m){}
  public boolean isEmpty(){ return false; }
  public void set(Path p){} public void transform(Matrix m){}
  public void computeBounds(RectF b,boolean exact){ if(b!=null) b.set(0,0,0,0); }
  public boolean op(Path a,Path b,Op o){ return true; }
  public void offset(float dx,float dy){}
}
