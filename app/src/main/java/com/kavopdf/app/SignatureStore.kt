package com.kavopdf.app

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import java.io.File
import java.io.FileOutputStream

/**
 * Keeps the last signature the user drew, so the next document does not need it
 * drawn again. Stored as a PNG in the app's private files - nothing leaves the
 * device, and the app has no INTERNET permission.
 */
object SignatureStore {

    private fun file(ctx: Context) = File(ctx.filesDir, "signature.png")

    fun has(ctx: Context): Boolean {
        val f = file(ctx)
        return f.exists() && f.length() > 0
    }

    fun save(ctx: Context, bmp: Bitmap): Boolean = try {
        FileOutputStream(file(ctx)).use { out ->
            bmp.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
        true
    } catch (t: Throwable) {
        false
    }

    fun load(ctx: Context): Bitmap? = try {
        val f = file(ctx)
        if (!f.exists() || f.length() == 0L) null else BitmapFactory.decodeFile(f.absolutePath)
    } catch (t: Throwable) {
        null
    }

    fun clear(ctx: Context) {
        try { file(ctx).delete() } catch (_: Throwable) { }
    }
}
