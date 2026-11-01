package com.kavopdf.app.util

/**
 * A failure whose message is meant for the person using the app.
 *
 * The shared save path shows one generic line for any failure, which is right for a bug but
 * wrong when the tool already knows exactly what went wrong - "no text could be read from this
 * PDF" tells the user what to do; "that file could not be read" does not.
 */
class UserFacing(message: String) : Exception(message)
