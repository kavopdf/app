package android.graphics;
public class PointF {
  public float x,y;
  public PointF(){}
  public PointF(float x,float y){this.x=x;this.y=y;}
  public void set(float x,float y){this.x=x;this.y=y;}
  public final void offset(float dx,float dy){x+=dx;y+=dy;}
}
