package com.mockengine.sdk.network

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * API client for creating authenticated Retrofit instances
 */
object ApiClient {

    private const val BASE_URL = "http://10.0.2.2:8000" // 10.0.2.2 = host machine from Android emulator

    /**
     * Creates a configured MockEngineApiService with API key authentication
     *
     * @param apiKey The API key for authentication
     * @return Configured MockEngineApiService instance
     */
    fun create(apiKey: String): MockEngineApiService {
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val originalRequest = chain.request()
                val requestBuilder = originalRequest.newBuilder()
                    .header("X-API-KEY", apiKey)
                    .method(originalRequest.method, originalRequest.body)
                chain.proceed(requestBuilder.build())
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        return retrofit.create(MockEngineApiService::class.java)
    }

    /**
     * Sets a custom base URL for the API client (useful for different environments)
     *
     * @param baseUrl The base URL to use for API calls
     */
    fun setBaseUrl(baseUrl: String) {
        // In a production app, this would update the BASE_URL
        // For now, it's provided as a placeholder for environment configuration
    }
}