package com.mockengine.sdk.data.models

/**
 * Interception log data model for backend API analytics
 */
data class InterceptionLog(
    val deviceId: String,
    val ruleId: Int,
    val endpoint: String,
    val method: String,
    val requestData: Map<String, Any>,
    val responseMockData: Map<String, Any>
)