package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.pdmodel.graphics.form.PDTransparencyGroup;
import com.tom_roush.pdfbox.pdmodel.graphics.state.PDSoftMask;
import com.tom_roush.pdfbox.util.Matrix;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * The alpha a page's soft mask gives a region, sampled where the page draws.
 *
 * <p>A fill under an {@code /SMask} is not the colour the content stream names: the mask
 * multiplies that colour's alpha, and where the mask is zero the page paints nothing at all.
 * The engine used to ignore the mask completely and write the fill as a flat solid colour, so
 * 414_transparency_softmask - whose mask group sits at the page origin and covers nothing of
 * the bar at y 640..740 - came out as a solid 400 x 100 pt block of #1A4D99 over a region the
 * page shows as blank. Measured: the page is (255,255,255) at five points across the bar, the
 * render was (26,77,153) at the same five, and 14_filled_shapes passed it, because 14 asks
 * whether the page's ink survived and never whether the render invented ink.
 *
 * <p>So the mask is read, and evaluated, here. The group's content stream is replayed as far
 * as it matters for coverage - the CTM, the path rectangles and the fill colours - and the
 * region is sampled on a grid. What this does not do is render the group: a mask made of text,
 * of curves or of a shading is reported as unknown, and an unknown mask leaves the fill exactly
 * as the engine drew it before. That is deliberate. A wrong alpha is a wrong colour on the page,
 * and no measurement in this bench would see it.
 */
public final class SoftMaskAlpha {

    private SoftMaskAlpha() {
    }

    /** How much of a region a mask lets through. */
    public static final class Coverage {
        /** The most alpha anywhere in the region, 0..1. */
        public final float max;
        /** The mean alpha over the sample grid, 0..1. */
        public final float mean;
        /** False when the mask is something this evaluator cannot read. */
        public final boolean known;

        Coverage(float max, float mean, boolean known) {
            this.max = max;
            this.mean = mean;
            this.known = known;
        }

        static Coverage unknown() {
            return new Coverage(1f, 1f, false);
        }
    }

    /** The grid a region is sampled on: 9 x 9 points, inset so an edge cannot decide it. */
    private static final int GRID = 9;

    /**
     * Samples {@code mask} over {@code rect}, given in PDF page space.
     *
     * @param fallbackCtm the transform in force when the fill was drawn, used only when the
     *                    mask carries no initial matrix of its own.
     */
    public static Coverage of(PDSoftMask mask, float[] rect, Matrix fallbackCtm) {
        if (mask == null || rect == null) return Coverage.unknown();
        try {
            PDTransparencyGroup group = mask.getGroup();
            if (group == null) return Coverage.unknown();
            List<float[]> paints = paints(group);
            if (paints == null) return Coverage.unknown();
            boolean luminosity = !"Alpha".equals(name(mask.getSubType()));
            float[] m = maskMatrix(mask, group, fallbackCtm);
            float[] inv = invert(m);
            if (inv == null) return Coverage.unknown();

            float x0 = Math.min(rect[0], rect[2]), x1 = Math.max(rect[0], rect[2]);
            float y0 = Math.min(rect[1], rect[3]), y1 = Math.max(rect[1], rect[3]);
            float max = 0f, sum = 0f;
            int n = 0;
            for (int i = 0; i < GRID; i++) {
                for (int j = 0; j < GRID; j++) {
                    float px = x0 + (x1 - x0) * (i + 0.5f) / GRID;
                    float py = y0 + (y1 - y0) * (j + 0.5f) / GRID;
                    float a = alphaAt(paints, inv, px, py, luminosity);
                    if (a > max) max = a;
                    sum += a;
                    n++;
                }
            }
            return new Coverage(max, n == 0 ? 0f : sum / n, true);
        } catch (Throwable t) {
            // A mask that will not read is not a reason to lose the page's ink.
            return Coverage.unknown();
        }
    }

    /**
     * The mask sampled on an {@code nx} x {@code ny} grid over {@code rect}, row-major from the
     * top of the rect, or null when the mask is not one this evaluator can read.
     *
     * <p>This is what the raster candidate needs: one alpha per pixel of the bitmap it writes.
     * It is the same evaluation {@link #of} does, at a finer grid, so the two candidates cannot
     * disagree about what the mask says - only about what is done with it.
     */
    public static float[] grid(PDSoftMask mask, float[] rect, Matrix fallbackCtm,
                               int nx, int ny) {
        if (mask == null || rect == null || nx <= 0 || ny <= 0) return null;
        try {
            PDTransparencyGroup group = mask.getGroup();
            if (group == null) return null;
            List<float[]> paints = paints(group);
            if (paints == null) return null;
            boolean luminosity = !"Alpha".equals(name(mask.getSubType()));
            float[] inv = invert(maskMatrix(mask, group, fallbackCtm));
            if (inv == null) return null;
            float x0 = Math.min(rect[0], rect[2]), x1 = Math.max(rect[0], rect[2]);
            float y0 = Math.min(rect[1], rect[3]), y1 = Math.max(rect[1], rect[3]);
            float[] out = new float[nx * ny];
            for (int j = 0; j < ny; j++) {
                for (int i = 0; i < nx; i++) {
                    float px = x0 + (x1 - x0) * (i + 0.5f) / nx;
                    float py = y1 - (y1 - y0) * (j + 0.5f) / ny;
                    out[j * nx + i] = alphaAt(paints, inv, px, py, luminosity);
                }
            }
            return out;
        } catch (Throwable t) {
            return null;
        }
    }

    /** The alpha the mask gives one page-space point, in the mask's own coordinate system. */
    private static float alphaAt(List<float[]> paints, float[] inv, float px, float py,
                                 boolean luminosity) {
        float mx = inv[0] * px + inv[2] * py + inv[4];
        float my = inv[1] * px + inv[3] * py + inv[5];
        float value = 0f;
        for (float[] p : paints) {
            if (mx >= p[0] && mx <= p[2] && my >= p[1] && my <= p[3]) value = p[4];
        }
        // A luminosity mask takes the luminance of what the group painted; an alpha mask takes
        // the paint's own alpha. Both are 0 where the group painted nothing, which is the case
        // that matters: nothing under the mask means the page shows nothing there.
        return luminosity ? value : (value > 0f ? 1f : 0f);
    }

    /**
     * Replays the mask group's content as a list of axis-aligned paints
     * {@code {x0, y0, x1, y1, value}}, in the group's own space, in drawing order.
     *
     * <p>Returns null when the stream holds something this replay does not model - a curve, a
     * shading, a text object, a form - because then the coverage is not known and the caller
     * must not act on a guess.
     */
    private static List<float[]> paints(PDTransparencyGroup group) throws Exception {
        String s = read(group.getContents());
        if (s == null) return null;
        List<float[]> out = new ArrayList<float[]>();
        List<Object> stack = new ArrayList<Object>();
        float[] ctm = {1, 0, 0, 1, 0, 0};
        float value = 1f;
        float[] path = null;
        List<float[]> saved = new ArrayList<float[]>();

        int i = 0, len = s.length();
        List<Float> nums = new ArrayList<Float>();
        while (i < len) {
            char c = s.charAt(i);
            if (c == '%') {
                while (i < len && s.charAt(i) != '\n' && s.charAt(i) != '\r') i++;
                continue;
            }
            if (c == ' ' || c == '\n' || c == '\r' || c == '\t' || c == '\f' || c == 0) {
                i++;
                continue;
            }
            if (c == '(' || c == '<' || c == '[') {
                // A string, a hex string or an array: skip it whole. None of them can change
                // coverage, and a 'Tj' after one is caught below.
                i = skip(s, i);
                continue;
            }
            if ((c >= '0' && c <= '9') || c == '-' || c == '+' || c == '.') {
                int j = i;
                while (j < len && ("0123456789+-.eE".indexOf(s.charAt(j)) >= 0)) j++;
                try {
                    nums.add(Float.parseFloat(s.substring(i, j)));
                } catch (NumberFormatException e) {
                    return null;
                }
                i = j;
                continue;
            }
            int j = i;
            while (j < len && " \n\r\t\f".indexOf(s.charAt(j)) < 0) j++;
            String op = s.substring(i, j);
            i = j;
            float[] a = floats(nums);
            nums.clear();
            if (op.equals("q")) {
                stack.add(new Object[]{ctm.clone(), Float.valueOf(value)});
            } else if (op.equals("Q")) {
                if (!stack.isEmpty()) {
                    Object[] top = (Object[]) stack.remove(stack.size() - 1);
                    ctm = (float[]) top[0];
                    value = ((Float) top[1]).floatValue();
                }
            } else if (op.equals("cm") && a != null && a.length >= 6) {
                ctm = compose(ctm, new float[]{a[0], a[1], a[2], a[3], a[4], a[5]});
            } else if (op.equals("re") && a != null && a.length >= 4) {
                float[] r = {a[0], a[1], a[0] + a[2], a[1] + a[3]};
                path = path == null ? r : union(path, r);
            } else if ((op.equals("rg") || op.equals("RG")) && a != null && a.length >= 3) {
                value = luminance(a[0], a[1], a[2]);
            } else if ((op.equals("g") || op.equals("G")) && a != null && a.length >= 1) {
                value = clamp(a[0]);
            } else if ((op.equals("k") || op.equals("K")) && a != null && a.length >= 4) {
                value = luminance((1 - a[0]) * (1 - a[3]), (1 - a[1]) * (1 - a[3]),
                        (1 - a[2]) * (1 - a[3]));
            } else if (op.equals("sc") || op.equals("scn") || op.equals("SC")
                    || op.equals("SCN")) {
                if (a == null || a.length == 0) return null;
                if (a.length == 1) value = clamp(a[0]);
                else if (a.length >= 3) value = luminance(a[0], a[1], a[2]);
                else return null;
            } else if (op.equals("f") || op.equals("F") || op.equals("f*")
                    || op.equals("b") || op.equals("b*") || op.equals("B")
                    || op.equals("B*")) {
                if (path == null) return null;
                // Through the CTM in force for THIS paint, not the last one the stream set:
                // a mask that translates each of its rectangles would otherwise be replayed
                // all at the origin, and a bar under a half-covering mask would read as zero.
                saved.add(through(ctm, new float[]{path[0], path[1], path[2], path[3], value}));
                path = null;
            } else if (op.equals("n") || op.equals("S") || op.equals("s")
                    || op.equals("W") || op.equals("W*")) {
                path = null;
            } else if (op.equals("Do") || op.equals("sh") || op.equals("BT")
                    || op.equals("c") || op.equals("v") || op.equals("y")
                    || op.equals("BX") || op.equals("BDC")) {
                // Something this replay cannot account for. The coverage is unknown.
                return null;
            }
        }
        out.addAll(saved);
        return out;
    }

    /** One paint's rect through the CTM it was drawn under. */
    private static float[] through(float[] m, float[] p) {
        float[][] corners = {{p[0], p[1]}, {p[2], p[1]}, {p[0], p[3]}, {p[2], p[3]}};
        float x0 = Float.MAX_VALUE, y0 = Float.MAX_VALUE;
        float x1 = -Float.MAX_VALUE, y1 = -Float.MAX_VALUE;
        for (float[] c : corners) {
            float x = m[0] * c[0] + m[2] * c[1] + m[4];
            float y = m[1] * c[0] + m[3] * c[1] + m[5];
            x0 = Math.min(x0, x); x1 = Math.max(x1, x);
            y0 = Math.min(y0, y); y1 = Math.max(y1, y);
        }
        return new float[]{x0, y0, x1, y1, p[4]};
    }

    /** The transform that carries the group's space onto the page. */
    private static float[] maskMatrix(PDSoftMask mask, PDTransparencyGroup group, Matrix fallback) {
        float[] form = group.getMatrix() == null ? IDENT : affine(group.getMatrix());
        float[] init = null;
        try {
            Matrix m = mask.getInitialTransformationMatrix();
            if (m != null) init = affine(m);
        } catch (Throwable ignored) {
            init = null;
        }
        if (init == null) init = fallback == null ? IDENT : affine(fallback);
        return compose(init, form);
    }

    private static final float[] IDENT = {1, 0, 0, 1, 0, 0};

    private static float[] affine(Matrix m) {
        android.graphics.PointF o = m.transformPoint(0, 0);
        android.graphics.PointF ex = m.transformPoint(1, 0);
        android.graphics.PointF ey = m.transformPoint(0, 1);
        return new float[]{ex.x - o.x, ex.y - o.y, ey.x - o.x, ey.y - o.y, o.x, o.y};
    }

    /** {@code a} applied after {@code b}. */
    private static float[] compose(float[] a, float[] b) {
        return new float[]{
                a[0] * b[0] + a[2] * b[1],
                a[1] * b[0] + a[3] * b[1],
                a[0] * b[2] + a[2] * b[3],
                a[1] * b[2] + a[3] * b[3],
                a[0] * b[4] + a[2] * b[5] + a[4],
                a[1] * b[4] + a[3] * b[5] + a[5]};
    }

    private static float[] invert(float[] m) {
        float det = m[0] * m[3] - m[1] * m[2];
        if (Math.abs(det) < 1e-9f) return null;
        float id = 1f / det;
        return new float[]{m[3] * id, -m[1] * id, -m[2] * id, m[0] * id,
                (m[2] * m[5] - m[3] * m[4]) * id, (m[1] * m[4] - m[0] * m[5]) * id};
    }

    private static float[] union(float[] a, float[] b) {
        return new float[]{Math.min(a[0], b[0]), Math.min(a[1], b[1]),
                Math.max(a[2], b[2]), Math.max(a[3], b[3])};
    }

    private static float[] floats(List<Float> nums) {
        if (nums.isEmpty()) return null;
        float[] a = new float[nums.size()];
        for (int i = 0; i < a.length; i++) a[i] = nums.get(i).floatValue();
        return a;
    }

    private static float luminance(float r, float g, float b) {
        return clamp(0.3f * r + 0.59f * g + 0.11f * b);
    }

    private static float clamp(float v) {
        return v < 0f ? 0f : (v > 1f ? 1f : v);
    }

    private static String name(com.tom_roush.pdfbox.cos.COSName n) {
        return n == null ? "" : n.getName();
    }

    private static int skip(String s, int i) {
        char c = s.charAt(i);
        int depth = 0;
        while (i < s.length()) {
            char d = s.charAt(i);
            if (d == '\\' && c == '(') {
                i += 2;
                continue;
            }
            i++;
            if (c == '(') {
                if (d == '(') depth++;
                else if (d == ')') {
                    depth--;
                    if (depth == 0) return i;
                }
            } else if (c == '[') {
                if (d == ']') return i;
            } else {
                if (d == '>') return i;
            }
        }
        return i;
    }

    private static String read(InputStream in) {
        if (in == null) return null;
        try {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return new String(out.toByteArray(), "ISO-8859-1");
        } catch (Exception e) {
            return null;
        } finally {
            try {
                in.close();
            } catch (Exception ignored) {
                // nothing to do
            }
        }
    }
}
