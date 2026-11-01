package com.kavopdf.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.animation.OvershootInterpolator
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.kavopdf.app.util.Busy
import com.kavopdf.app.util.AppLog
import com.kavopdf.app.util.Files
import com.kavopdf.app.util.ThemeUtil
import com.kavopdf.app.util.useHighestRefreshRate
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Shared base for every tool screen. It wires up the Storage Access Framework
 * launchers (pick PDF(s), pick images, pick a folder, create an output document)
 * and runs engine work off the main thread behind a progress dialog.
 */
abstract class PdfActivity : AppCompatActivity() {

    protected lateinit var busy: Busy
    private var pendingProducer: ((File) -> Unit)? = null

    /** Cache files this screen made, removed when it closes. */
    private val sessionFiles = ArrayList<File>()

    /** The one file the user shared or opened - another app may still be reading it. */
    private val keptFiles = HashSet<File>()
    /** The name the finished file is offered under; tool screens use it in their own receipt. */
    protected var pendingName: String = "output.pdf"

    /** True when the running task has already written its failure to the activity log. */
    private var failureLogged = false

    protected val openPdfLauncher =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri != null) { takePersist(uri); onPdfChosen(uri) }
        }

    protected val openPdfsLauncher =
        registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
            uris.forEach { takePersist(it) }
            if (uris.isNotEmpty()) onPdfsChosen(uris)
        }

    protected val openImagesLauncher =
        registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
            uris.forEach { takePersist(it) }
            if (uris.isNotEmpty()) onImagesChosen(uris)
        }

    protected val openTreeLauncher =
        registerForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
            if (uri != null) {
                try {
                    contentResolver.takePersistableUriPermission(
                        uri,
                        android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION or
                            android.content.Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    )
                } catch (_: Exception) {
                }
                onTreeChosen(uri)
            }
        }

    private val createDocLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument("application/pdf")) { uri ->
            finishSave(uri)
        }

    // The system file picker appends the extension for its own MIME type. Reusing the PDF
    // picker for a .docx wrote "report_word.docx.pdf" - the right file with the wrong name.
    private val createDocxLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument(DOCX_MIME)) { uri ->
            finishSave(uri)
        }

    private val createTxtLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument("text/plain")) { uri ->
            finishSave(uri)
        }

    /** Writes the produced file to the document the user picked. */
    private fun finishSave(uri: Uri?) {
        failureLogged = false
        val producer = pendingProducer
        pendingProducer = null
        if (uri == null || producer == null) return
        val out = trackCacheFile(Files.newFile(this, pendingName))
        val taskName = taskLabel()
        runTask(getString(R.string.msg_processing), onDone = saved@{ result ->
            if (result == null) return@saved
            showSuccess(getString(R.string.msg_saved_to, pendingName), result)
            onSaved(result)
        }) {
            try {
                producer(out)
                Files.writeToUri(this, out, uri)
                AppLog.record(this, taskName, pendingName, true)
                out
            } catch (t: Throwable) {
                com.kavopdf.app.util.CrashGuard.problem(this, taskName, t)
                failureLogged = true
                // The picker has already created an empty document. Leaving it behind means a
                // 0-byte file in the user's folder that looks like a result but is not one.
                runCatching { contentResolver.delete(uri, null, null) }
                if (t is com.kavopdf.app.util.UserFacing) {
                    runOnUiThread { toast(t.message ?: getString(R.string.msg_could_not_read)) }
                }
                throw t
            }
        }
    }

    /** True when the tool shows its own result dialog, so the generic one is skipped. */
    protected open fun showsOwnResult(): Boolean = false

    /** Save as a Word document or a text file rather than a PDF. */
    protected fun runAndSaveAs(name: String, kind: SaveKind, produce: (File) -> Unit) {
        pendingName = name
        pendingProducer = produce
        when (kind) {
            SaveKind.DOCX -> createDocxLauncher.launch(name)
            SaveKind.TXT -> createTxtLauncher.launch(name)
        }
    }

    /** The kind of document a tool produces, when it is not a PDF. */
    protected enum class SaveKind { DOCX, TXT }

    override fun onCreate(savedInstanceState: Bundle?) {
        ThemeUtil.apply(this)
        super.onCreate(savedInstanceState)
        // 120 Hz panels stay at 60 unless the window asks for more.
        useHighestRefreshRate()
        com.kavopdf.app.util.CrashGuard.step("Opened: " + javaClass.simpleName)
        busy = Busy(this)

        // A file handed over from the share sheet. Posted to the view rather than called here:
        // this runs before the tool's own onCreate, so its views do not exist yet.
        incomingUri?.let { uri ->
            window.decorView.post { onPdfChosen(uri) }
        }
    }

    /** The PDF this screen was opened with, when it came from another app. */
    protected val incomingUri: Uri?
        get() = intent?.getStringExtra(EXTRA_SOURCE_URI)?.let {
            runCatching { Uri.parse(it) }.getOrNull()
        }

    /**
     * Copy the picked PDF into the cache, asking for a password when the document is
     * protected. [onReady] always receives a file that can actually be opened.
     */
    protected fun openPdf(uri: Uri, onReady: (File) -> Unit) {
        runTask(getString(R.string.msg_processing), onDone = checked@{ res ->
            if (res == null) return@checked
            if (!res.second) { onReady(res.first); return@checked }
            askPassword(res.first, onReady)
        }) {
            val f = trackCacheFile(Files.copyToCache(this, uri))
            if (!Files.looksLikePdf(f)) error(getString(R.string.msg_not_a_pdf))
            pagesHint = runCatching { com.kavopdf.app.engine.PdfEngine.pageCount(f, "") }
                .getOrDefault(1).coerceAtLeast(1)
            sizeHint = runCatching { f.length() }.getOrDefault(0L)
            f to com.kavopdf.app.engine.PdfEngine.needsPassword(f)
        }
    }

    private fun askPassword(file: File, onReady: (File) -> Unit) {
        if (isFinishing || isDestroyed) return
        val v = layoutInflater.inflate(R.layout.dialog_password, null)
        val input = v.findViewById<android.widget.EditText>(R.id.pwInput)
        val dialog = AlertDialog.Builder(this)
            .setTitle(R.string.msg_password_required)
            .setView(v)
            .setPositiveButton(R.string.action_open, null)
            .setNegativeButton(R.string.action_cancel, null)
            .create()
        dialog.window?.setBackgroundDrawableResource(R.drawable.bg_dialog_rounded)
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val pw = input.text?.toString().orEmpty()
                if (pw.isEmpty()) {
                    toast(getString(R.string.msg_enter_password))
                    return@setOnClickListener
                }
                dialog.dismiss()
                runTask(getString(R.string.msg_processing), onDone = opened@{ out ->
                    if (out != null) {
                        toast(getString(R.string.msg_unlocked_note))
                        onReady(out)
                    }
                }) {
                    val dec = Files.newFile(this, "unlocked.pdf")
                    try {
                        com.kavopdf.app.engine.PdfEngine.decrypt(file, pw, dec)
                    } catch (e: Exception) {
                        error(getString(R.string.msg_wrong_password))
                    }
                    dec
                }
            }
        }
        dialog.show()
    }

    /** A friendly "all done" popup with Share and Open result. */
    protected fun showSuccess(message: String, file: File?, mime: String = "application/pdf") {
        if (isFinishing || isDestroyed) return
        val view = layoutInflater.inflate(R.layout.dialog_success, null)
        view.findViewById<TextView>(R.id.successMsg).text = message

        val icon = view.findViewById<View>(R.id.successIcon)
        icon.scaleX = 0.5f
        icon.scaleY = 0.5f
        icon.alpha = 0f
        icon.animate()
            .scaleX(1f).scaleY(1f).alpha(1f)
            .setDuration(260)
            .setInterpolator(OvershootInterpolator())
            .start()

        val dialog = AlertDialog.Builder(this).setView(view).setCancelable(true).create()
        dialog.window?.setBackgroundDrawableResource(R.drawable.bg_dialog_rounded)

        val open = view.findViewById<View>(R.id.successOpen)
        val share = view.findViewById<View>(R.id.successShare)
        open.isEnabled = file != null
        share.isEnabled = file != null
        open.setOnClickListener {
            file?.let {
                keptFiles.add(it)
                Files.openWith(this, it, mime)
            }
            dialog.dismiss()
        }
        share.setOnClickListener {
            file?.let {
                keptFiles.add(it)
                Files.share(this, it, mime)
            }
        }
        view.findViewById<View>(R.id.successClose).setOnClickListener { dialog.dismiss() }
        dialog.apply {
            // dead centre: no vertical offset, and the window itself is centred
            window?.setGravity(android.view.Gravity.CENTER)
            window?.attributes = window?.attributes?.apply { y = 0 }
        }.show()
    }

    // ---- overridable hooks -------------------------------------------------
    protected open fun onPdfChosen(uri: Uri) {}
    protected open fun onPdfsChosen(uris: List<Uri>) {}
    protected open fun onImagesChosen(uris: List<Uri>) {}
    protected open fun onTreeChosen(uri: Uri) {}
    protected open fun onSaved(file: File) {}

    // ---- launchers ---------------------------------------------------------
    protected fun pickPdf() = openPdfLauncher.launch(arrayOf("application/pdf"))
    protected fun pickPdfs() = openPdfsLauncher.launch(arrayOf("application/pdf"))
    protected fun pickImages() = openImagesLauncher.launch(arrayOf("image/*"))
    protected fun pickTree() = openTreeLauncher.launch(null)

    /**
     * Remember a cache file so this screen can remove it when it closes.
     *
     * Nothing is deleted while the screen is alive: the success dialog offers Open and
     * Share, which hand the same file to another app, and the reader keeps its copy open
     * for as long as it is showing. Closing the screen is the first moment it is certain
     * that this screen is done with the file.
     */
    protected fun trackCacheFile(f: File): File {
        sessionFiles.add(f)
        return f
    }

    override fun onDestroy() {
        super.onDestroy()
        val removable = sessionFiles.filter { it !in keptFiles }
        com.kavopdf.app.util.CacheSweep.deleteNow(removable)
        sessionFiles.clear()
        keptFiles.clear()
        // Whatever this screen did not make - other screens' leftovers - ages out here too,
        // so the cache does not wait for the next cold start to be tidied.
        com.kavopdf.app.util.CacheSweep.sweep(this)
    }

    /** Ask the user where to save, then run [produce] to build the output file. */
    protected fun runAndSave(name: String, produce: (File) -> Unit) {
        pendingName = name
        pendingProducer = produce
        createDocLauncher.launch(name)
    }

    /** Run [block] on a background thread with a progress dialog; [onDone] gets null on failure. */
    /**
     * The name a tool is recorded under. Screens override [toolName] so that ten
     * different tools inside one activity never share a single norm.
     */
    protected open fun toolName(): String? = null

    /** How many pages the file being worked on has; set when it is opened. */
    protected var pagesHint: Int = 1
    /** Size of the open file, so the detector can compare like with like. */
    protected var sizeHint: Long = 0L

    companion object {
        /** A PDF handed over by another app, so the tool screen opens with it already chosen. */
        const val EXTRA_SOURCE_URI = "com.kavopdf.app.extra.SOURCE_URI"

        const val DOCX_MIME =
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    /**
     * The name a run is measured under: the tool plus the operation.
     *
     * It used to be the screen alone, so opening a document and exporting thirty pages
     * shared one history. The export was then compared against the open's 176 ms norm
     * and every export was reported as slow, while nothing was wrong at all.
     */
    private fun taskKey(status: String): String {
        val tool = toolName() ?: javaClass.simpleName
        val op = status.trim().replace(Regex("[^A-Za-z0-9]+"), "_").trim('_').take(24)
        return if (op.isEmpty()) tool else tool + ":" + op
    }

    protected fun <T> runTask(status: String, pages: Int = 1, onDone: (T?) -> Unit, block: () -> T) {
        com.kavopdf.app.util.CrashGuard.step(javaClass.simpleName + ": " + status)
        // A blank status means "do not show the card at all" - used where the work
        // finishes in a fraction of a second and the card would only flash.
        val showCard = status.isNotBlank()
        if (showCard) busy.show(status)
        lifecycleScope.launch {
            val result: T? = try {
                withContext(Dispatchers.IO) {
                    com.kavopdf.app.util.CrashGuard.timed(
                        this@PdfActivity, taskKey(status), maxOf(pages, pagesHint),
                        sizeHint
                    ) { block() }
                }
            } catch (t: Throwable) {
                // The producer already recorded this failure with its breadcrumbs. Recording it
                // again under a second name put the same crash in the log twice.
                if (!failureLogged) AppLog.problem(applicationContext, "Failed", t)
                toast(getString(R.string.msg_could_not_read))
                null
            }
            if (showCard) busy.dismiss()
            onDone(result)
        }
    }

    /**
     * What this task is called in the activity log - the feature's own name, so the
     * log reads "Merge PDFs" instead of "ToolsActivity".
     */
    private fun taskLabel(): String {
        supportActionBar?.title?.toString()?.takeIf {
            it.isNotBlank() && it != getString(R.string.app_name)
        }?.let { return it }
        return runCatching {
            packageManager.getActivityInfo(componentName, 0).loadLabel(packageManager).toString()
        }.getOrNull()?.takeIf { it.isNotBlank() } ?: javaClass.simpleName
    }

    protected fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_LONG).show()

    /**
     * Open a picker only once this screen has finished sliding in. Launching it
     * while the activity is still animating makes the two transitions fight, and
     * the whole thing visibly stutters.
     */
    protected fun pickAfterEnter(block: () -> Unit) {
        // Open straight away - a delay here just makes the screen feel slow. The
        // stutter came from this screen sliding in while the picker opened, so we
        // drop this screen's own animation instead of postponing the picker.
        window.setWindowAnimations(R.style.Animation_KavoPDF_None)
        block()
    }

    private fun takePersist(uri: Uri) {
        try {
            contentResolver.takePersistableUriPermission(
                uri, Intent.FLAG_GRANT_READ_URI_PERMISSION
            )
        } catch (_: Exception) { }
    }
}
