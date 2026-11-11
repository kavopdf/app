package com.kavopdf.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.animation.OvershootInterpolator
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
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

    /**
     * Cache files this screen made, removed when it closes.
     *
     * Synchronised because a copy made inside a background task is registered from that
     * task's thread, while [onDestroy] reads and clears the list on the main thread.
     */
    private val sessionFiles = java.util.Collections.synchronizedList(ArrayList<File>())

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
        if (uri == null) return
        // producer is null when the activity was recreated while the save dialog was open -
        // a dark-mode switch or a split-screen resize rebuilds it and the lambda is gone.
        // Returning silently meant the user picked a location and nothing happened: no file,
        // no message. Say so instead, so a second tap fixes it.
        if (producer == null) {
            toast(getString(R.string.msg_failed, pendingName))
            return
        }
        val out = trackCacheFile(Files.newFile(this, pendingName))
        val taskName = taskLabel()
        runTask(getString(R.string.msg_processing), onDone = saved@{ result ->
            if (result == null) return@saved
            // A tool that shows its own result dialog must get the screen first. Showing the
            // generic "Done" sheet here and then the tool's own dialog put one on top of the
            // other - the repair receipt appeared over the Done sheet instead of before it.
            if (showsOwnResult()) {
                onSaved(result)
            } else {
                showSuccess(getString(R.string.msg_saved_to, pendingName), result)
                onSaved(result)
            }
        }) {
            try {
                producer(out)
                Files.writeToUri(this, out, uri)
                AppLog.record(this, taskName, pendingName, true)
                out
            } catch (t: Throwable) {
                // A UserFacing failure is the tool telling the user something they can act
                // on. Recording it as a problem made ordinary mistakes - opening a Word file
                // in the PDF picker, say - look like crashes in the activity log.
                if (t !is com.kavopdf.app.util.UserFacing) {
                    com.kavopdf.app.util.CrashGuard.problem(this, taskName, t)
                }
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
        // FLAG_SECURE used to be set here, to keep the page out of the recents thumbnail.
        // It also made every screenshot and every screen recording of the app fail, which
        // is not a trade the user agreed to: they photograph their own documents, and a
        // document viewer that refuses to be photographed is a viewer they cannot use.
        // Android offers no flag that hides a screen from recents without also blocking
        // capture, so the recents thumbnail is the cost of a usable app.
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
     * A file another app shared straight into this screen, however the sender put it there.
     *
     * The two image screens are share targets in their own right, and a sender may leave the
     * file in the intent data, in EXTRA_STREAM or in clipData. Every in-app launch sets none
     * of the three, so this is null everywhere else.
     */
    protected val sharedStreamUri: Uri?
        get() {
            val i = intent ?: return null
            i.data?.let { return it }
            val extra: Uri? = if (android.os.Build.VERSION.SDK_INT >= 33) {
                i.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
            } else {
                @Suppress("DEPRECATION")
                i.getParcelableExtra(Intent.EXTRA_STREAM)
            }
            if (extra != null) return extra
            val clip = i.clipData
            if (clip != null && clip.itemCount > 0) return clip.getItemAt(0).uri
            return null
        }

    /**
     * Copy the picked PDF into the cache, asking for a password when the document is
     * protected. [onReady] always receives a file that can actually be opened.
     */
    protected fun openPdf(uri: Uri, onReady: (File) -> Unit) {
        // The size has to be known BEFORE the timed block runs, or the reading step is judged
        // against runs of completely different files: a 45 MB scan and one text page were both
        // "1 page, ? size", and the scan was reported as a 26x stall.
        runCatching {
            contentResolver.openAssetFileDescriptor(uri, "r")?.use { afd ->
                if (afd.length > 0) sizeHint = afd.length
            }
        }
        runTask(getString(R.string.msg_processing), onDone = checked@{ res ->
            if (res == null) return@checked
            if (!res.second) { onReady(res.first); return@checked }
            askPassword(res.first, onReady)
        }) {
            val f = trackCacheFile(Files.copyToCache(this, uri))
            // Picking the wrong file is a user mistake, not an app failure: it is said plainly
            // and never logged as a problem, or the log fills with failures that are not bugs.
            if (!Files.looksLikePdf(f)) throw com.kavopdf.app.util.UserFacing(
                getString(R.string.msg_not_a_pdf)
            )
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
    protected fun showSuccess(message: String, file: File?) {
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
            val chosen = file ?: return@setOnClickListener
            keptFiles.add(chosen)
            // The sheet goes first so the "no app" dialog below is the only one on screen:
            // two stacked dialogs is the bug that put the repair receipt over this sheet.
            dialog.dismiss()
            val openers = Files.openersFor(this, chosen)
            if (openers.isEmpty()) findAnApp(chosen) else chooseApp(chosen, openers)
        }
        share.setOnClickListener {
            file?.let {
                keptFiles.add(it)
                Files.share(this, it)
            }
        }
        view.findViewById<View>(R.id.successClose).setOnClickListener { dialog.dismiss() }
        dialog.apply {
            // dead centre: no vertical offset, and the window itself is centred
            window?.setGravity(android.view.Gravity.CENTER)
            window?.attributes = window?.attributes?.apply { y = 0 }
        }.show()
    }

    /**
     * The apps that can open the result, as a list of our own.
     *
     * Not Intent.createChooser. When exactly one app matches, the system's resolver finishes
     * itself and forwards straight to that app, so the list never appears - a phone with a
     * single Word viewer skipped the list entirely and put the file into it. No flag and no
     * extra makes a chooser show a single entry, so the list is ours.
     */
    private fun chooseApp(file: File, openers: List<android.content.pm.ResolveInfo>) {
        if (isFinishing || isDestroyed) return
        val pm = packageManager
        // A plain view rather than the stock dialog's adapter, so the Cancel is an outlined
        // pill like every other confirmation in this app instead of a bare text button that
        // reads as one more row of the list.
        val view = layoutInflater.inflate(R.layout.dialog_open_with, null)
        val list = view.findViewById<android.widget.LinearLayout>(R.id.openWithList)
        val dialog = AlertDialog.Builder(this).setView(view).setCancelable(true).create()
        dialog.window?.setBackgroundDrawableResource(R.drawable.bg_dialog_rounded)
        for (info in openers) {
            val row = layoutInflater.inflate(R.layout.row_app_choice, list, false)
            row.findViewById<android.widget.ImageView>(R.id.appIcon)
                .setImageDrawable(info.loadIcon(pm))
            row.findViewById<TextView>(R.id.appName).text = info.loadLabel(pm)
            row.setOnClickListener {
                dialog.dismiss()
                Files.openWith(this, file, info)
            }
            list.addView(row)
        }
        view.findViewById<android.widget.Button>(R.id.openWithCancel)
            .setOnClickListener { dialog.dismiss() }
        dialog.show()
    }

    /**
     * Nothing on this phone can open the file, so offer the one thing that can change that.
     *
     * Deliberately the same shape as the dialog that asks "read it or work on it" when a PDF
     * is shared in - a title and two rows - because this app already asks that question that
     * way, and a second dialog style would be one more thing to learn.
     */
    private fun findAnApp(file: File) {
        if (isFinishing || isDestroyed) return
        com.google.android.material.dialog.MaterialAlertDialogBuilder(this)
            .setTitle(R.string.no_app_title)
            .setItems(
                arrayOf(getString(R.string.no_app_find), getString(R.string.action_cancel))
            ) { _, which ->
                if (which == 0) searchStore(file)
            }
            .show()
    }

    /**
     * The store's own search for this format. Play Store first; if it is not on the phone,
     * the same search on the web - handed to whatever browser the user has made their
     * default, which is why no browser is named here. Neither step needs the INTERNET
     * permission: this app opens no connection, it hands a URL to an app that already has one.
     */
    private fun searchStore(file: File) {
        val q = Uri.encode(file.extension.lowercase(java.util.Locale.US))
        if (openStoreLink("market://search?q=" + q)) return
        if (!openStoreLink("https://play.google.com/store/search?q=" + q + "&c=apps")) {
            toast(getString(R.string.msg_no_store))
        }
    }

    /**
     * Open one of the two store links, and only those.
     *
     * Both strings here are literals this app builds, but the scheme is checked anyway:
     * this is the same rule the reader applies to a link inside a PDF, and it means this
     * function cannot become a way to launch intent://, file:// or content:// if it is ever
     * handed a string from somewhere else.
     */
    private fun openStoreLink(url: String): Boolean {
        val uri = Uri.parse(url)
        if (uri.scheme?.lowercase(java.util.Locale.US) !in STORE_SCHEMES) return false
        return try {
            startActivity(Intent(Intent.ACTION_VIEW, uri))
            true
        } catch (_: Exception) {
            false
        }
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

    /**
     * Hand a tracked cache file to the screen being opened, instead of deleting it here.
     *
     * [onDestroy] removes every tracked file that was not kept. When this screen opens
     * another screen on the same file and finishes - Fill forms handing its PDF to Annotate -
     * that deletion would take the file out from under the screen that just received it.
     * The receiving screen tracks it in turn, so it is still removed when the last one closes.
     */
    protected fun keepCacheFile(f: File): File {
        keptFiles.add(f)
        return f
    }

    override fun onDestroy() {
        super.onDestroy()
        val removable = synchronized(sessionFiles) {
            val taken = sessionFiles.filter { it !in keptFiles }
            sessionFiles.clear()
            taken
        }
        com.kavopdf.app.util.CacheSweep.deleteNow(removable)
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

        /** The only schemes the "find an app" row will hand to the system. */
        private val STORE_SCHEMES = setOf("market", "https")

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
                // The task name, not the literal word "Failed" - every failure used to be
                // filed under "Failed", so the log could not say which tool broke.
                if (!failureLogged) AppLog.problem(applicationContext, taskKey(status), t)
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
     * What to do when the camera permission was refused.
     *
     * A toast on its own leaves the camera screens with a black preview, a button that
     * does nothing and no way forward: after the second refusal the system stops showing
     * the dialog at all, so asking again from [onCreate] asks nothing. This says why the
     * permission is needed and offers the one action that can still fix it - another
     * request while the system is still willing to show it, and the app's settings page
     * once it is not.
     *
     * @param ask launches this screen's own permission request
     */
    protected fun cameraDenied(ask: () -> Unit) {
        if (isFinishing || isDestroyed) return
        val canAsk = shouldShowRequestPermissionRationale(Manifest.permission.CAMERA)
        AlertDialog.Builder(this)
            .setTitle(R.string.msg_camera_needed)
            .setMessage(R.string.msg_camera_needed_body)
            .setPositiveButton(
                if (canAsk) R.string.action_allow_camera else R.string.action_open_settings
            ) { _, _ -> if (canAsk) ask() else openAppSettings() }
            .setNegativeButton(R.string.action_cancel, null)
            .create()
            .show()
    }

    /** This app's own page in system Settings, where a refused permission can be granted. */
    protected fun openAppSettings() {
        val i = Intent(
            android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
            Uri.fromParts("package", packageName, null)
        )
        runCatching { startActivity(i) }
            .onFailure { toast(getString(R.string.msg_camera_needed)) }
    }

    /** True when the camera permission is held right now. */
    protected fun hasCamera(): Boolean =
        ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) ==
            PackageManager.PERMISSION_GRANTED

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
