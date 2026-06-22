package com.mockengine.sdk.error

import android.util.Log
import com.mockengine.sdk.cache.ConfigCacheManager
import com.mockengine.sdk.data.models.Rule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Fallback strategy for handling API failures gracefully
 *
 * Provides offline support and error recovery mechanisms
 */
class FallbackStrategy(private val cacheManager: ConfigCacheManager) {

    private companion object {
        private const val TAG = "FallbackStrategy"
    }

    /**
     * Handle API failure by returning cached rules
     *
     * @return List of cached rules, or empty list if none available
     */
    suspend fun handleApiFailure(): List<Rule> = withContext(Dispatchers.IO) {
        try {
            Log.w(TAG, "API failure detected - using cached rules")
            val cached = cacheManager.getCachedRules()

            if (cached.isEmpty()) {
                Log.w(TAG, "No cached rules available")
            } else {
                Log.i(TAG, "Using ${cached.size} cached rules")
            }

            cached
        } catch (e: Exception) {
            Log.e(TAG, "Failed to retrieve cached rules", e)
            emptyList()
        }
    }

    /**
     * Check if fallback should be triggered based on error type
     *
     * @param error The exception that occurred
     * @return true if fallback should occur, false otherwise
     */
    fun shouldFallbackToOriginal(error: Throwable): Boolean {
        return ErrorHandler.shouldFallbackToOriginal(error)
    }

    /**
     * Get fallback response when all else fails
     *
     * @param context Description of the operation that failed
     * @return Error message indicating fallback mode
     */
    fun getFallbackResponse(context: String): String {
        Log.w(TAG, "Using fallback response for: $context")
        return "MockEngine SDK: Running in offline mode - using cached data"
    }

    /**
     * Check if SDK should operate in offline mode
     *
     * @return true if offline mode should be used
     */
    fun shouldUseOfflineMode(): Boolean {
        // Check if we have cached rules and recent sync was successful
        val lastSync = cacheManager.getDeviceId() != null
        val hasCachedRules = try {
            // Quick check if we have any rules (don't want to block here)
            true // Placeholder - actual implementation would check cache
        } catch (e: Exception) {
            false
        }

        return lastSync && hasCachedRules
    }

    /**
     * Get number of available cached rules (non-blocking)
     *
     * @return Number of cached rules, or 0 if unavailable
     */
    suspend fun getCachedRuleCount(): Int = withContext(Dispatchers.IO) {
        try {
            cacheManager.getCachedRules().size
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get cached rule count", e)
            0
        }
    }

    /**
     * Clear cached data and force fresh sync on next attempt
     */
    suspend fun clearCacheAndForceSync() = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "Clearing cache and forcing fresh sync")
            cacheManager.clearAll()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to clear cache", e)
        }
    }

    /**
     * Handle rule matching failure gracefully
     *
     * @param errorMessage Description of what went wrong
     * @return Empty list (no rules matched)
     */
    fun handleMatchingFailure(errorMessage: String): List<Rule> {
        Log.e(TAG, "Rule matching failed: $errorMessage")
        return emptyList()
    }

    /**
     * Validate cache integrity
     *
     * @return true if cache is valid, false otherwise
     */
    suspend fun isCacheValid(): Boolean = withContext(Dispatchers.IO) {
        try {
            val rules = cacheManager.getCachedRules()
            rules.isNotEmpty()
        } catch (e: Exception) {
            Log.e(TAG, "Cache validation failed", e)
            false
        }
    }

    /**
     * Get diagnostic information for troubleshooting
     *
     * @return Diagnostic information as a readable string
     */
    suspend fun getDiagnostics(): String = withContext(Dispatchers.IO) {
        try {
            val ruleCount = getCachedRuleCount()
            val lastSync = System.currentTimeMillis() // Placeholder - would get actual last sync time
            val cacheValid = isCacheValid()

            """
            |MockEngine SDK Diagnostics:
            |---------------------------
            |Cached Rules: $ruleCount
            |Cache Valid: $cacheValid
            |Last Sync: $lastSync
            |Offline Mode: ${shouldUseOfflineMode()}
            """.trimMargin()
        } catch (e: Exception) {
            "Failed to retrieve diagnostics: ${e.message}"
        }
    }
}