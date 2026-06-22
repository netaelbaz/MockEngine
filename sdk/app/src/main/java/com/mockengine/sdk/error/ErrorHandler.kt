package com.mockengine.sdk.error

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Centralized error handler for MockEngine SDK
 *
 * Provides safe API call execution with error handling and fallback strategies
 */
object ErrorHandler {

    private const val TAG = "MockEngineErrorHandler"

    /**
     * Execute an API call safely with error handling
     *
     * @param onSuccess Callback for successful result
     * @param onError Callback for error handling
     * @param apiCall The suspend function to execute
     */
    fun <T> safeApiCall(
        onSuccess: (T) -> Unit,
        onError: (Throwable) -> Unit,
        apiCall: suspend () -> T
    ) {
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val result = apiCall()
                withContext(Dispatchers.Main) {
                    onSuccess(result)
                }
            } catch (e: Exception) {
                Log.e(TAG, "API call failed", e)
                withContext(Dispatchers.Main) {
                    onError(e)
                }
            }
        }
    }

    /**
     * Determine if an error should trigger fallback to original response
     *
     * @param error The exception that occurred
     * @return true if fallback should occur, false otherwise
     */
    fun shouldFallbackToOriginal(error: Throwable): Boolean {
        return when (error) {
            is UnknownHostException -> {
                Log.w(TAG, "Network unreachable - using fallback")
                true
            }
            is SocketTimeoutException -> {
                Log.w(TAG, "Connection timeout - using fallback")
                true
            }
            is java.net.ConnectException -> {
                Log.w(TAG, "Connection refused - using fallback")
                true
            }
            else -> {
                Log.e(TAG, "Unexpected error: ${error.javaClass.simpleName}")
                false
            }
        }
    }

    /**
     * Get user-friendly error message
     *
     * @param error The exception that occurred
     * @return Human-readable error message
     */
    fun getErrorMessage(error: Throwable): String {
        return when (error) {
            is UnknownHostException -> "Network unreachable. Please check your connection."
            is SocketTimeoutException -> "Connection timeout. Please try again."
            is java.net.ConnectException -> "Unable to reach server."
            is SecurityException -> "Permission denied."
            else -> error.message ?: "An unexpected error occurred."
        }
    }

    /**
     * Log error with context
     *
     * @param context Description of what was happening
     * @param error The exception that occurred
     */
    fun logError(context: String, error: Throwable) {
        Log.e(TAG, "Error in $context: ${error.javaClass.simpleName} - ${error.message}")
    }

    /**
     * Check if error is network-related
     */
    fun isNetworkError(error: Throwable): Boolean {
        return error is UnknownHostException ||
               error is SocketTimeoutException ||
               error is java.net.ConnectException ||
               error is java.io.IOException
    }

    /**
     * Check if error is authentication-related
     */
    fun isAuthError(error: Throwable): Boolean {
        val message = error.message?.lowercase() ?: return false
        return message.contains("401") ||
               message.contains("403") ||
               message.contains("unauthorized") ||
               message.contains("forbidden")
    }

    /**
     * Check if error is server-related (5xx errors)
     */
    fun isServerError(error: Throwable): Boolean {
        val message = error.message?.lowercase() ?: return false
        return message.contains("500") ||
               message.contains("502") ||
               message.contains("503") ||
               message.contains("504")
    }
}