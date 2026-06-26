package com.mockengine.sdk.interceptor

import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.mockengine.sdk.MockEngine
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import java.io.IOException

class MockEngineInterceptor(private val mockEngine: MockEngine) : Interceptor {

    private companion object {
        private const val TAG = "MockEngineInterceptor"
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Check rules BEFORE making the real request so we can skip the real call
        // when mockData is provided (fixes delay accuracy and allows mocking 404 endpoints)
        val matchingRules = try {
            kotlinx.coroutines.runBlocking(kotlinx.coroutines.Dispatchers.IO) {
                mockEngine.getMatchingRules(request)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get matching rules", e)
            emptyList()
        }

        if (matchingRules.isEmpty()) {
            Log.d(TAG, "No matching rules for ${request.url.encodedPath}")
            val start = System.currentTimeMillis()
            val response = chain.proceed(request)
            val responseTimeMs = (System.currentTimeMillis() - start).toInt()
            GlobalScope.launch(Dispatchers.IO) {
                mockEngine.logCall(
                    endpoint = request.url.encodedPath,
                    method = request.method,
                    wasIntercepted = false,
                    responseTimeMs = responseTimeMs,
                    statusCode = response.code
                )
            }
            return response
        }

        val rule = matchingRules.first()
        Log.d(TAG, "Applying rule ${rule.id} to ${request.url.encodedPath}")

        val start = System.currentTimeMillis()
        val response = buildMockResponse(chain, request, rule)
        val responseTimeMs = (System.currentTimeMillis() - start).toInt()

        GlobalScope.launch(Dispatchers.IO) {
            mockEngine.logInterception(request, rule)
        }

        return response
    }

    private fun buildMockResponse(
        chain: Interceptor.Chain,
        request: Request,
        rule: com.mockengine.sdk.data.models.Rule
    ): Response {
        // Apply delay before returning the response so it reflects the configured latency
        if (rule.delayS > 0) {
            Log.d(TAG, "Applying ${rule.delayS}s delay")
            try {
                Thread.sleep(rule.delayS * 1000L)
            } catch (e: InterruptedException) {
                Log.e(TAG, "Delay interrupted", e)
            }
        }

        return if (rule.mockData != null && rule.mockData.isNotEmpty()) {
            // User-provided mock data — skip the real network call entirely.
            // This means the real endpoint's status code (e.g. 404) is irrelevant.
            Log.d(TAG, "Using user-provided mock data")
            val responseBody = createJsonResponseBody(rule.mockData)
            Response.Builder()
                .request(request)
                .protocol(Protocol.HTTP_1_1)
                .code(rule.statusCode)
                .message("Mocked by MockEngine SDK")
                .body(responseBody)
                .build()
        } else {
            // Ghost mode — need the real response to clone, so make the actual call
            Log.d(TAG, "Using ghost mode auto-generation")
            val originalResponse = try {
                chain.proceed(request)
            } catch (e: IOException) {
                Log.e(TAG, "Network request failed in ghost mode", e)
                return Response.Builder()
                    .request(request)
                    .protocol(Protocol.HTTP_1_1)
                    .code(503)
                    .message("Ghost mode unavailable: real server unreachable")
                    .body("{}".toResponseBody("application/json".toMediaType()))
                    .build()
            }
            val responseBody = createGhostModeResponse(originalResponse)
            originalResponse.newBuilder()
                .code(rule.statusCode)
                .message("Mocked by MockEngine SDK")
                .body(responseBody)
                .build()
        }
    }

    /**
     * Create JSON response body from data map
     */
    private fun createJsonResponseBody(data: Map<String, Any>): ResponseBody {
        val json = Gson().toJson(data)
        return json.toResponseBody("application/json".toMediaType())
    }

    /**
     * Create Ghost Mode response - auto-generated mock data
     * Clones original response with "MOCK_" prefix on string values
     */
    private fun createGhostModeResponse(originalResponse: Response): ResponseBody {
        val originalBody = originalResponse.body
        val originalJson = try {
            val bodyString = originalBody?.string() ?: "{}"
            Gson().fromJson(bodyString, object : TypeToken<Map<String, Any>>() {}.type) as? Map<String, Any> ?: emptyMap()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse original response", e)
            emptyMap()
        }

        // Clone with "MOCK_" prefix on string values
        val mockedJson = originalJson.mapValues { (_, value) ->
            when (value) {
                is String -> "MOCK_$value"
                is Number -> value
                is Boolean -> value
                else -> value
            }
        }

        return createJsonResponseBody(mockedJson)
    }

}