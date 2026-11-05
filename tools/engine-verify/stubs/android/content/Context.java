package android.content;

import android.content.res.AssetManager;

/** JVM stub: the engine only needs getApplicationContext() and getAssets(). */
public class Context {
    private final AssetManager assets;

    public Context(AssetManager assets) {
        this.assets = assets;
    }

    public Context getApplicationContext() {
        return this;
    }

    public AssetManager getAssets() {
        return assets;
    }
}
