package com.kavopdf.app.util

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import com.kavopdf.app.R
import java.io.File
import java.io.FileOutputStream

/** Storage-Access-Framework helpers: everything is copied through the app cache,
 *  so no storage permission is ever required and files never leave the device. */
object Files {

    fun displayName(context: Context, uri: Uri): String {
        var name = "file"
        try {
            context.contentResolver.query(uri, null, null, null, null)?.use { c ->
                val idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (idx >= 0 && c.moveToFirst()) name = c.getString(idx) ?: name
            }
        } catch (_: Exception) { }
        return name
    }

    fun workDir(context: Context): File = File(context.cacheDir, "work").apply { mkdirs() }

    private val counter = java.util.concurrent.atomic.AtomicInteger(0)

    /** Unique cache file name — the counter guarantees no two copies collide even
     *  when several files are imported within the same millisecond. */
    fun newFile(context: Context, name: String): File =
        File(
            workDir(context),
            System.currentTimeMillis().toString() + "_" + counter.incrementAndGet() + "_" + sanitize(name)
        )

    fun sanitize(name: String): String = name.replace(Regex("[^A-Za-z0-9._-]"), "_")

    /** A PDF announces itself with "%PDF-" near the start (the spec allows leading junk). */
    fun looksLikePdf(f: File): Boolean = try {
        val head = ByteArray(1024)
        val n = java.io.FileInputStream(f).use { it.read(head) }
        n > 0 && String(head, 0, n, Charsets.ISO_8859_1).contains("%PDF-")
    } catch (_: Exception) {
        false
    }

    fun copyToCache(context: Context, uri: Uri): File {
        val name = displayName(context, uri)
        val out = newFile(context, name)
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(out).use { input.copyTo(it) }
        } ?: throw IllegalStateException("Could not read $name")
        return out
    }

    fun writeToUri(context: Context, file: File, uri: Uri) {
        context.contentResolver.openOutputStream(uri, "w")?.use { out ->
            file.inputStream().use { it.copyTo(out) }
        } ?: throw IllegalStateException("Could not write the output file")
    }

    private fun uriFor(context: Context, file: File): Uri =
        FileProvider.getUriForFile(context, context.packageName + ".fileprovider", file)

    /**
     * The type of a file this app writes. There are exactly three outputs and each has one
     * correct answer, so the answer comes from the file rather than from the caller.
     *
     * It used to be a default parameter - `mime: String = "application/pdf"` on showSuccess -
     * and every caller left it alone, so a .docx result was announced to Android as a PDF.
     * The chooser then offered every PDF viewer for a Word file and none of them could open
     * it, and a .txt result was offered PDF viewers too.
     */
    fun mimeOf(file: File): String = when (file.extension.lowercase(java.util.Locale.US)) {
        "pdf" -> "application/pdf"
        "docx" -> "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        "txt" -> "text/plain"
        else -> "application/octet-stream"
    }

    fun share(context: Context, file: File) {
        val i = Intent(Intent.ACTION_SEND).apply {
            type = mimeOf(file)
            putExtra(Intent.EXTRA_STREAM, uriFor(context, file))
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        try {
            context.startActivity(Intent.createChooser(i, null))
        } catch (_: Exception) {
            android.widget.Toast.makeText(
                context, context.getString(R.string.msg_no_app_share), android.widget.Toast.LENGTH_LONG
            ).show()
        }
    }

    /**
     * Set when this app launches its own share-choice screen from the "Open with" list.
     * The user has already answered the question that screen exists to ask.
     */
    const val EXTRA_INTERNAL_READ = "com.kavopdf.app.extra.INTERNAL_READ"

    private fun viewIntent(context: Context, file: File): Intent =
        Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uriFor(context, file), mimeOf(file))
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

    /**
     * The activities that can open this file. Empty means nothing on the phone declares the
     * type, which is the caller's cue to offer a store search instead.
     *
     * Flag 0 rather than MATCH_DEFAULT_ONLY: an app whose VIEW filter omits CATEGORY_DEFAULT
     * still opens the file when it is named explicitly, and filtering it out here would make
     * a phone that does have a viewer look as though it has none.
     *
     * Needs the <queries> entries in AndroidManifest.xml on Android 11 and later. Without
     * them every other app is invisible to this call and the answer is always empty.
     */
    fun openersFor(context: Context, file: File): List<android.content.pm.ResolveInfo> =
        context.packageManager.queryIntentActivities(viewIntent(context, file), 0)

    /**
     * Hand the file to the one app the user picked from that list.
     *
     * Explicit, by component, so the system never gets a second chance to choose - it would
     * resolve the same intent back to this list and the user would be asked twice.
     */
    fun openWith(context: Context, file: File, target: android.content.pm.ResolveInfo): Boolean {
        // This list can contain KavoPDF itself, because the app declares the VIEW filter.
        // When the user picks their own app from it they are saying "open this" from inside
        // the app they are already in - so the share-choice screen must not ask them again
        // whether they want to read it or work on it. It goes straight to the reader.
        val own = target.activityInfo.packageName == context.packageName
        val intent = viewIntent(context, file).setComponent(
            android.content.ComponentName(
                target.activityInfo.packageName, target.activityInfo.name
            )
        ).apply {
            if (own) putExtra(EXTRA_INTERNAL_READ, true)
        }
        return try {
            context.startActivity(intent)
            true
        } catch (_: Exception) {
            android.widget.Toast.makeText(
                context, context.getString(R.string.msg_no_app_open), android.widget.Toast.LENGTH_LONG
            ).show()
            false
        }
    }

    /** Strip the extension so we can suggest a clean output name. */
    fun baseName(name: String): String {
        val i = name.lastIndexOf('.')
        return if (i > 0) name.substring(0, i) else name
    }

    fun suggestName(source: String, suffix: String, ext: String = "pdf"): String =
        sanitize(baseName(source) + suffix + "." + ext)
}
