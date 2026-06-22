package com.mockengine.sdk.cache

import android.content.Context
import android.content.SharedPreferences
import com.mockengine.sdk.data.models.Rule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Manages local caching using hybrid storage approach:
 * - SharedPreferences: Simple config values (device ID, sync timestamps)
 * - Room Database: Complex data structures (rules, analytics)
 */
class ConfigCacheManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val database: CacheDatabase = CacheDatabase.getInstance(context)

    companion object {
        private const val PREFS_NAME = "mock_engine_cache"
        private const val KEY_LAST_SYNC = "last_sync"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_API_KEY = "api_key"

        // Sync interval: 10 minutes
        private const val SYNC_INTERVAL_MS = 10 * 60 * 1000L
    }

    /**
     * Save rules to local cache and update sync timestamp
     *
     * @param rules List of rules to cache
     */
    suspend fun saveRules(rules: List<Rule>) = withContext(Dispatchers.IO) {
        database.ruleDao().clearAll()
        database.ruleDao().insertRules(rules)
        updateLastSync()
    }

    /**
     * Get all cached active rules
     *
     * @return List of enabled rules from cache
     */
    suspend fun getCachedRules(): List<Rule> = withContext(Dispatchers.IO) {
        database.ruleDao().getActiveRules()
    }

    /**
     * Check if it's time to sync with backend
     *
     * @return true if sync is needed, false otherwise
     */
    fun shouldSync(): Boolean {
        val lastSync = prefs.getLong(KEY_LAST_SYNC, 0)
        return System.currentTimeMillis() - lastSync > SYNC_INTERVAL_MS
    }

    /**
     * Get the device ID from SharedPreferences
     *
     * @return Device ID if exists, null otherwise
     */
    fun getDeviceId(): String? {
        return prefs.getString(KEY_DEVICE_ID, null)
    }

    /**
     * Save the device ID to SharedPreferences
     *
     * @param deviceId The device ID to save
     */
    fun saveDeviceId(deviceId: String) {
        prefs.edit().putString(KEY_DEVICE_ID, deviceId).apply()
    }

    /**
     * Get the API key from SharedPreferences
     *
     * @return API key if exists, null otherwise
     */
    fun getApiKey(): String? {
        return prefs.getString(KEY_API_KEY, null)
    }

    /**
     * Save the API key to SharedPreferences
     *
     * @param apiKey The API key to save
     */
    fun saveApiKey(apiKey: String) {
        prefs.edit().putString(KEY_API_KEY, apiKey).apply()
    }

    /**
     * Clear all cached data (both SharedPreferences and Room)
     */
    suspend fun clearAll() = withContext(Dispatchers.IO) {
        database.ruleDao().clearAll()
        prefs.edit().clear().apply()
    }

    /**
     * Update the last sync timestamp to current time
     */
    private fun updateLastSync() {
        prefs.edit().putLong(KEY_LAST_SYNC, System.currentTimeMillis()).apply()
    }

    /**
     * Force sync on next check (reset last sync time)
     */
    fun forceSyncNext() {
        prefs.edit().putLong(KEY_LAST_SYNC, 0).apply()
    }
}