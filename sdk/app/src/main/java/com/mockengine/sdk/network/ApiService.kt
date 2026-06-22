package com.mockengine.sdk.network

import com.mockengine.sdk.data.models.*
import retrofit2.Response
import retrofit2.http.*

/**
 * MockEngine API service for backend communication
 */
interface MockEngineApiService {

    @GET("/api/sdk/config")
    suspend fun fetchConfig(): Response<List<Rule>>

    @POST("/api/sdk/register")
    suspend fun registerDevice(@Body registration: DeviceRegistration): Response<DeviceResponse>

    @POST("/api/sdk/log-intercept")
    suspend fun logInterception(@Body log: InterceptionLog): Response<SuccessResponse>

    @POST("/api/sdk/log-call")
    suspend fun logCall(@Body log: CallLog): Response<SuccessResponse>
}