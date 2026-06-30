package com.mockengine.demo

import android.os.Bundle
import android.util.Log
import android.view.View
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

class MainActivity : AppCompatActivity() {

    private companion object {
        private const val TAG = "MockEngineDemo"
        private const val API_KEY = "572488a657b140609ad3f5ebba55089792ee3abfa63a99a15a9fd23d56046464"
        private const val DEMO_BASE_URL = "http://10.0.2.2:8000/demo"
    }

    private lateinit var btnRun1: Button
    private lateinit var btnRun2: Button
    private lateinit var btnRun3: Button
    private lateinit var tvLog1: TextView
    private lateinit var tvLog2: TextView
    private lateinit var tvLog3: TextView
    private lateinit var logSection1: View
    private lateinit var logSection2: View
    private lateinit var logSection3: View

    private lateinit var okHttpClient: OkHttpClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        btnRun1 = findViewById(R.id.btnRun1)
        btnRun2 = findViewById(R.id.btnRun2)
        btnRun3 = findViewById(R.id.btnRun3)
        tvLog1 = findViewById(R.id.tvLog1)
        tvLog2 = findViewById(R.id.tvLog2)
        tvLog3 = findViewById(R.id.tvLog3)
        logSection1 = findViewById(R.id.logSection1)
        logSection2 = findViewById(R.id.logSection2)
        logSection3 = findViewById(R.id.logSection3)

        val mockEngineInterceptor = MockEngine.init(this, API_KEY)

        okHttpClient = OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .addInterceptor(mockEngineInterceptor)
            .build()

        btnRun1.setOnClickListener { runCard(btnRun1, logSection1, tvLog1) { tv -> testGetUsers(tv) } }
        btnRun2.setOnClickListener { runCard(btnRun2, logSection2, tvLog2) { tv -> testGetUser(tv, "123") } }
        btnRun3.setOnClickListener { runCard(btnRun3, logSection3, tvLog3) { tv -> testCreateUser(tv) } }
    }

    private fun runCard(
        btn: Button,
        logSection: View,
        tv: TextView,
        block: suspend (TextView) -> Unit
    ) {
        logSection.visibility = View.VISIBLE
        tv.text = "Running..."
        btn.isEnabled = false
        lifecycleScope.launch(Dispatchers.IO) {
            block(tv)
            withContext(Dispatchers.Main) { btn.isEnabled = true }
        }
    }

    private fun addLog(tv: TextView, message: String) {
        val current = tv.text.toString()
        val next = if (current == "Running...") message else "$current\n$message"
        tv.text = next
        Log.d(TAG, message)
    }

    private suspend fun testGetUsers(tv: TextView) {
        withContext(Dispatchers.Main) { addLog(tv, "GET /demo/users") }
        try {
            val request = Request.Builder().url("$DEMO_BASE_URL/users").get().build()
            val response = okHttpClient.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog(tv, "Response: ${response.code} - ${response.message}")
                addLog(tv, "Body: ${body?.take(200)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog(tv, "Error: ${e.message}") }
        }
    }

    private suspend fun testGetUser(tv: TextView, userId: String) {
        withContext(Dispatchers.Main) { addLog(tv, "GET /demo/users/$userId") }
        try {
            val request = Request.Builder().url("$DEMO_BASE_URL/users/$userId").get().build()
            val response = okHttpClient.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog(tv, "Response: ${response.code} - ${response.message}")
                addLog(tv, "Body: ${body?.take(200)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog(tv, "Error: ${e.message}") }
        }
    }

    private suspend fun testCreateUser(tv: TextView) {
        withContext(Dispatchers.Main) { addLog(tv, "POST /demo/users") }
        try {
            val json = Gson().toJson(mapOf("name" to "Test User", "email" to "test@example.com"))
            val requestBody = json.toRequestBody("application/json".toMediaType())
            val request = Request.Builder().url("$DEMO_BASE_URL/users").post(requestBody).build()
            val response = okHttpClient.newCall(request).execute()
            val body = response.body?.string()
            withContext(Dispatchers.Main) {
                addLog(tv, "Response: ${response.code} - ${response.message}")
                addLog(tv, "Body: ${body?.take(200)}...")
            }
        } catch (e: IOException) {
            withContext(Dispatchers.Main) { addLog(tv, "Error: ${e.message}") }
        }
    }
}
