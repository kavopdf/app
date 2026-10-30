package android.media;

import java.io.File;
import java.io.InputStream;

/**
 * JVM stub of android.media.ExifInterface, only as far as the PDF engine touches it.
 *
 * The harness never needs real EXIF parsing: the engine's uprightBitmap() reads the
 * orientation tag and rotates, and the checks that matter are the ones that pass an
 * orientation in. This stub therefore always reports ORIENTATION_NORMAL, which is the
 * same thing the real class does for an image with no EXIF block - so the engine takes
 * the "already upright" path, exactly as it would for a plain PNG.
 */
public class ExifInterface {

  public static final String TAG_ORIENTATION = "Orientation";

  public static final int ORIENTATION_UNDEFINED = 0;
  public static final int ORIENTATION_NORMAL = 1;
  public static final int ORIENTATION_FLIP_HORIZONTAL = 2;
  public static final int ORIENTATION_ROTATE_180 = 3;
  public static final int ORIENTATION_FLIP_VERTICAL = 4;
  public static final int ORIENTATION_TRANSPOSE = 5;
  public static final int ORIENTATION_ROTATE_90 = 6;
  public static final int ORIENTATION_TRANSVERSE = 7;
  public static final int ORIENTATION_ROTATE_270 = 8;

  public ExifInterface(String filename) { }
  public ExifInterface(File file) { }
  public ExifInterface(InputStream in) { }

  /** Always NORMAL - see the class comment. */
  public int getAttributeInt(String tag, int defaultValue) {
    return ORIENTATION_NORMAL;
  }

  public String getAttribute(String tag) { return null; }
}
