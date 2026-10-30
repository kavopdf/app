package android.graphics;
public class Region {
  public enum Op { DIFFERENCE, INTERSECT, UNION, XOR, REVERSE_DIFFERENCE, REPLACE }
  public Region(){}
  public Region(int l,int t,int r,int b){}
  public boolean setPath(Path p,Region c){ return true; }
  public void setEmpty(){}
  public boolean isEmpty(){ return false; }
  public boolean set(Region r){ return true; }
}
