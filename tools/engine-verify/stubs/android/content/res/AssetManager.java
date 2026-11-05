package android.content.res;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

/** JVM stub: assets are read from a directory on disk instead of the APK. */
public class AssetManager {
    private final File root;

    public AssetManager(File root) {
        this.root = root;
    }

    public InputStream open(String path) throws IOException {
        return new FileInputStream(new File(root, path));
    }
}
