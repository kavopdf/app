package android.graphics;
public class Canvas {
  public Canvas(){}
  public Canvas(Bitmap b){}
  public int getWidth(){ return 0; } public int getHeight(){ return 0; }
  public void drawColor(int c){} public void drawPath(Path p,Paint pt){}
  public void drawBitmap(Bitmap b,float x,float y,Paint p){} public void drawText(String s,float x,float y,Paint p){}
  public void save(){} public void restore(){} public int saveLayer(RectF r,Paint p,int f){return 0;}
  public void translate(float x,float y){} public void scale(float x,float y){}
  public void clipPath(Path p){} public void clipRect(float a,float b,float c,float d){}
  public void drawRect(float a,float b,float c,float d,Paint p){}
}
