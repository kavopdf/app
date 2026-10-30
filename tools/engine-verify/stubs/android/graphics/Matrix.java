package android.graphics;
public class Matrix {
  private final float[] v=new float[]{1,0,0,0,1,0,0,0,1};
  public Matrix(){}
  public void reset(){ v[0]=1;v[1]=0;v[2]=0;v[3]=0;v[4]=1;v[5]=0;v[6]=0;v[7]=0;v[8]=1; }
  public void set(Matrix m){ System.arraycopy(m.v,0,v,0,9); }
  public void getValues(float[] a){ System.arraycopy(v,0,a,0,9); }
  public void setValues(float[] a){ System.arraycopy(a,0,v,0,9); }
  public void postTranslate(float dx,float dy){ concat(1,0,dx, 0,1,dy); }
  public void preTranslate(float dx,float dy){ concat(1,0,dx, 0,1,dy); }
  public void postScale(float sx,float sy){ concat(sx,0,0, 0,sy,0); }
  public void preScale(float sx,float sy){ concat(sx,0,0, 0,sy,0); }
  public void postRotate(float d){ float r=(float)Math.toRadians(d), c=(float)Math.cos(r), n=(float)Math.sin(r); concat(c,-n,0, n,c,0); }
  public void preRotate(float d){ postRotate(d); }
  /** this = this * [a c e; b d f] */
  private void concat(float a,float b,float c,float d,float e,float f){
    float m0=v[0],m1=v[1],m2=v[2],m3=v[3],m4=v[4],m5=v[5];
    v[0]=m0*a+m1*b; v[1]=m0*c+m1*d; v[2]=m0*e+m1*f+m2;
    v[3]=m3*a+m4*b; v[4]=m3*c+m4*d; v[5]=m3*e+m4*f+m5;
  }
  public void postConcat(Matrix m){} public void preConcat(Matrix m){}
  public void setConcat(Matrix a,Matrix b){}
  public void mapPoints(float[] p){} public void mapPoints(float[] p,float[] d){ if(d!=null&&p!=null) System.arraycopy(p,0,d,0,Math.min(p.length,d.length)); }
  public boolean mapRect(RectF r){ return true; }
  public boolean mapRect(RectF d,RectF s){ if(d!=null&&s!=null) d.set(s.left,s.top,s.right,s.bottom); return true; }
  public boolean invert(Matrix inv){ return true; }
}
