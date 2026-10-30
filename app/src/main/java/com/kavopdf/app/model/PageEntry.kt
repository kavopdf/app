package com.kavopdf.app.model

/** One page in the "Organize pages" screen: original 1-based index plus edits. */
data class PageEntry(
    val original: Int,
    var rotation: Int = 0,
    var selected: Boolean = false
)
