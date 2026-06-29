package com.mockengine.sdk.interceptor

import android.util.Log
import com.google.gson.Gson
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

        val rule = matchingRules.firstOrNull()

        if (rule == null) {
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

        Log.d(TAG, "Applying rule ${rule.id} to ${request.url.encodedPath}, useMockBackend=${rule.useMockBackend}")

        if (!rule.useMockBackend) {
            val realResponse = try {
                chain.proceed(request)
            } catch (e: IOException) {
                Log.e(TAG, "Real server request failed for rule ${rule.id}", e)
                GlobalScope.launch(Dispatchers.IO) {
                    mockEngine.logCall(
                        endpoint = request.url.encodedPath,
                        method = request.method,
                        wasIntercepted = true,
                        responseTimeMs = null,
                        statusCode = 503
                    )
                }
                return Response.Builder()
                    .request(request)
                    .protocol(Protocol.HTTP_1_1)
                    .code(503)
                    .message("Real server unreachable")
                    .body("{}".toResponseBody("application/json".toMediaType()))
                    .build()
            }
            val start = System.currentTimeMillis()
            if (rule.delayS > 0) {
                try { Thread.sleep(rule.delayS * 1000L) } catch (e: InterruptedException) { Log.e(TAG, "Delay interrupted", e) }
            }
            val body = if (rule.mockData != null && rule.mockData.isNotEmpty())
                createJsonResponseBody(rule.mockData)
            else
                realResponse.body
            val effectiveStatusCode = rule.statusCode ?: realResponse.code
            val responseTimeMs = (System.currentTimeMillis() - start).toInt()
            GlobalScope.launch(Dispatchers.IO) {
                mockEngine.logCall(
                    endpoint = request.url.encodedPath,
                    method = request.method,
                    wasIntercepted = true,
                    interceptedByRuleId = rule.id,
                    responseTimeMs = responseTimeMs,
                    statusCode = effectiveStatusCode
                )
                mockEngine.logInterception(request, rule)
            }
            return realResponse.newBuilder()
                .code(effectiveStatusCode)
                .message("Mocked by MockEngine SDK")
                .body(body)
                .build()
        }

        val start = System.currentTimeMillis()
        val response = buildMockResponse(request, rule)
        val responseTimeMs = (System.currentTimeMillis() - start).toInt()

        GlobalScope.launch(Dispatchers.IO) {
            mockEngine.logCall(
                endpoint = request.url.encodedPath,
                method = request.method,
                wasIntercepted = true,
                interceptedByRuleId = rule.id,
                responseTimeMs = responseTimeMs,
                statusCode = rule.statusCode ?: 200
            )
            mockEngine.logInterception(request, rule)
        }

        return response
    }

    private fun buildMockResponse(
        request: Request,
        rule: com.mockengine.sdk.data.models.Rule
    ): Response {
        if (rule.delayS > 0) {
            Log.d(TAG, "Applying ${rule.delayS}s delay")
            try {
                Thread.sleep(rule.delayS * 1000L)
            } catch (e: InterruptedException) {
                Log.e(TAG, "Delay interrupted", e)
            }
        }

        val responseBody = if (rule.mockData != null && rule.mockData.isNotEmpty())
            createJsonResponseBody(rule.mockData)
        else
            "{}".toResponseBody("application/json".toMediaType())
        return Response.Builder()
            .request(request)
            .protocol(Protocol.HTTP_1_1)
            .code(rule.statusCode ?: 200)
            .message("Mocked by MockEngine SDK")
            .body(responseBody)
            .build()
    }

    private fun createJsonResponseBody(data: Map<String, Any>): ResponseBody {
        val json = Gson().toJson(data)
        return json.toResponseBody("application/json".toMediaType())
    }

}