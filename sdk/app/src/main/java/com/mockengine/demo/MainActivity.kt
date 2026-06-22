package com.mockengine.demo

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.gson.Gson
import com.mockengine.sdk.MockEngine
import com.mockengine.sdk.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import java.io.IOException

/**
 * Demo Activity showing MockEngine SDK integration
 */
class MainActivity : AppCompatActivity() {

    private companion object {
        private const val TAG = "MockEngineDemo"
        private const val API_KEY = "572488a657b140609ad3f5ebba55089792ee3abfa63a99a15a9fd23d56046464"
        private const val DEMO_BASE_URL = "http://10.0.2.2:8000/demo"
    }

    private lateinit var tvLog: TextView
    private val logMessages = mutableListOf<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI components
        tvLog = findViewById<TextView>(R.id.tvLog)
        val btnTest = findViewById<Button>(R.id.btnTest)

        // Add initial log message
        addLog("MockEngine SDK Demo")
        addLog("-------------------")
        addLog("Initializing SDK...")

        // Initialize MockEngine SDK
        val mockEngineInterceptor = MockEngine.init(this, API_KEY)

        // Setup OkHttp with logging and MockEngine interceptor
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor(mockEngineInterceptor)
            .build()

        addLog("SDK initialized successfully!")
        addLog("Ready to test API calls")

        // Set up test button
        btnTest.setOnClickListener {
            addLog("Starting test API calls...")
            testApiCalls(okHttpClient)
        }
    }

    /**
     * Test various API calls to demonstrate SDK functionality
     */
    private fun testApiCalls(client: OkHttpClient) {
        lifecycleScope.launch(Dispatchers.IO) {
            testGetUsers(client)
            testGetUser(client, "123")
            testCreateUser(client)
            withContext(Dispatchers.Main) { addLog("All test calls completed!") }
        }
    }

    private suspend fun testGetUsers(client: OkHttpClient) {
        withContext(Dispatchers.Main) { addLog("Test 1: GET /demo/users") }
        try {
            val request = Request.Builder()
                .url("$DEMO_BASE_URL/users")
                .get()
                .build()
            val response = client.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog("Response: ${response.code} - ${response.message}")
                addLog("Body: ${body?.take(100)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog("Error: ${e.message}") }
        }
    }

    private suspend fun testGetUser(client: OkHttpClient, userId: String) {
        withContext(Dispatchers.Main) { addLog("Test 2: GET /demo/users/$userId") }
        try {
            val request = Request.Builder()
                .url("$DEMO_BASE_URL/users/$userId")
                .get()
                .build()
            val response = client.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog("Response: ${response.code} - ${response.message}")
                addLog("Body: ${body?.take(100)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog("Error: ${e.message}") }
        }
    }

    private suspend fun testCreateUser(client: OkHttpClient) {
        withContext(Dispatchers.Main) { addLog("Test 3: POST /demo/users") }
        try {
            val json = Gson().toJson(mapOf(
                "name" to "Test User",
                "email" to "test@example.com"
            ))
            val requestBody = json.toRequestBody("application/json".toMediaType())
            val request = Request.Builder()
                .url("$DEMO_BASE_URL/users")
                .post(requestBody)
                .build()
            val response = client.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog("Response: ${response.code} - ${response.message}")
                addLog("Body: ${body?.take(100)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog("Error: ${e.message}") }
        }
    }

    private fun addLog(message: String) {
        logMessages.add("${System.currentTimeMillis()}: $message")
        updateLogDisplay()
        Log.d(TAG, message)
    }

    private fun updateLogDisplay() {
        val displayText = logMessages.joinToString("\n")
        tvLog.text = displayText
    }
}