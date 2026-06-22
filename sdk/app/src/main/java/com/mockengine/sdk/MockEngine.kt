package com.mockengine.sdk

import android.content.Context
import android.util.Log
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ProcessLifecycleOwner
import com.mockengine.sdk.cache.ConfigCacheManager
import com.mockengine.sdk.data.models.DeviceRegistration
import com.mockengine.sdk.engine.RuleMatcher
import com.mockengine.sdk.interceptor.MockEngineInterceptor
import com.mockengine.sdk.network.ApiClient
import kotlinx.coroutines.*
import okhttp3.Request
import java.util.*

/**
 * MockEngine SDK - Main singleton for HTTP response interception
 *
 * This SDK allows developers to modify HTTP responses without changing backend code.
 * Use cases include QA testing, demo presentations, and development debugging.
 */
object MockEngine : DefaultLifecycleObserver {

    private const val TAG = "MockEngine"

    private lateinit var context: Context
    private lateinit var apiKey: String
    private lateinit var apiService: com.mockengine.sdk.network.MockEngineApiService
    private lateinit var cacheManager: ConfigCacheManager

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var syncJob: Job? = null

    /**
     * Initialize the MockEngine SDK
     *
     * @param context Application context
     * @param apiKey API key for authentication
     * @return Configured MockEngineInterceptor for OkHttp
     */
    fun init(context: Context, apiKey: String): MockEngineInterceptor {
        this.context = context.applicationContext
        this.apiKey = apiKey
        this.apiService = ApiClient.create(apiKey)
        this.cacheManager = ConfigCacheManager(context)

        // Save API key to cache
        cacheManager.saveApiKey(apiKey)

        // Register device on first init
        scope.launch {
            try {
                registerDevice()
            } catch (e: Exception) {
                Log.e(TAG, "Device registration failed", e)
            }
        }

        // Start periodic config sync
        startPeriodicSync()

        // Hook into app lifecycle
        ProcessLifecycleOwner.get().lifecycle.addObserver(this)

        Log.d(TAG, "MockEngine SDK initialized successfully")
        return MockEngineInterceptor(this)
    }

    /**
     * Called when app comes to foreground
     */
    override fun onStart(owner: LifecycleOwner) {
        super.onStart(owner)
        Log.d(TAG, "App came to foreground - starting sync")
        startPeriodicSync()
    }

    /**
     * Called when app goes to background
     */
    override fun onStop(owner: LifecycleOwner) {
        super.onStop(owner)
        Log.d(TAG, "App went to background - stopping sync")
        stopPeriodicSync()
    }

    /**
     * Start periodic configuration sync with backend
     */
    private fun startPeriodicSync() {
        if (syncJob?.isActive == true) {
            Log.d(TAG, "Sync already running")
            return
        }

        syncJob = scope.launch {
            Log.d(TAG, "Starting periodic config sync")
            syncConfig() // Fetch rules immediately on startup
            while (isActive) {
                delay(60 * 1000) // Then re-check every minute
                if (cacheManager.shouldSync()) {
                    syncConfig()
                }
            }
        }
    }

    /**
     * Stop periodic configuration sync
     */
    private fun stopPeriodicSync() {
        syncJob?.cancel()
        Log.d(TAG, "Periodic sync stopped")
    }

    /**
     * Synchronize configuration with backend
     */
    private suspend fun syncConfig() {
        try {
            Log.d(TAG, "Syncing config with backend...")
            val response = apiService.fetchConfig()
            if (response.isSuccessful && response.body() != null) {
                cacheManager.saveRules(response.body()!!)
                Log.d(TAG, "Config synced successfully - ${response.body()!!.size} rules cached")
            } else {
                Log.w(TAG, "Config sync failed - HTTP ${response.code()}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Config sync failed, using cache", e)
        }
    }

    /**
     * Get matching rules for a specific HTTP request
     *
     * @param request HTTP request to match against rules
     * @return List of matching rules
     */
    suspend fun getMatchingRules(request: Request): List<com.mockengine.sdk.data.models.Rule> {
        val allRules = cacheManager.getCachedRules()
        val matchingRules = allRules.filter { rule ->
            RuleMatcher.matches(request.url.encodedPath, rule.urlPattern, request.method, rule.method)
        }

        if (matchingRules.isNotEmpty()) {
            Log.d(TAG, "Found ${matchingRules.size} matching rules for ${request.url.encodedPath}")
        }

        return matchingRules
    }

    /**
     * Register device with backend
     */
    private suspend fun registerDevice() {
        val deviceId = getOrCreateDeviceId()
        val appVersion = getAppVersion()
        val androidVersion = android.os.Build.VERSION.RELEASE
        val internetMode = getInternetMode()

        val registration = DeviceRegistration(
            deviceId = deviceId,
            appVersion = appVersion,
            androidVersion = androidVersion,
            internetMode = internetMode
        )

        Log.d(TAG, "Registering device: $deviceId")
        val response = apiService.registerDevice(registration)
        if (response.isSuccessful) {
            Log.d(TAG, "Device registered successfully")
        } else {
            Log.w(TAG, "Device registration failed - HTTP ${response.code()}")
        }
    }

    /**
     * Get existing device ID or create new one
     */
    private fun getOrCreateDeviceId(): String {
        val existingId = cacheManager.getDeviceId()
        if (existingId != null) {
            return existingId
        }

        // Generate new UUID
        val newId = UUID.randomUUID().toString()
        cacheManager.saveDeviceId(newId)
        Log.d(TAG, "Generated new device ID: $newId")
        return newId
    }

    /**
     * Get app version from package info
     */
    private fun getAppVersion(): String {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            packageInfo.versionName ?: "unknown"
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get app version", e)
            "unknown"
        }
    }

    /**
     * Detect current internet mode
     */
    private fun getInternetMode(): String {
        // Simple implementation - can be enhanced with proper network detection
        return "wifi" // Placeholder
    }

    /**
     * Clean up resources when SDK is destroyed
     */
    fun destroy() {
        Log.d(TAG, "Destroying MockEngine SDK")
        stopPeriodicSync()
        ProcessLifecycleOwner.get().lifecycle.removeObserver(this)
        scope.cancel()
    }
}