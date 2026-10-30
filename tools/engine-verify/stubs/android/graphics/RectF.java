package android.graphics;
public class RectF {
  public float left,top,right,bottom;
  public RectF(){}
  public RectF(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}
  public void set(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}
  public void set(RectF o){left=o.left;top=o.top;right=o.right;bottom=o.bottom;}
  public void setEmpty(){left=top=right=bottom=0;}
  public float width(){return right-left;} public float height(){return bottom-top;}
  public boolean isEmpty(){return left>=right||top>=bottom;}
}
