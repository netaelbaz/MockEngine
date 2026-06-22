package com.mockengine.sdk.data.models

data class CallLog(
    val deviceId: String,
    val endpoint: String,
    val method: String,
    val wasIntercepted: Boolean,
    val interceptedByRuleId: Int?,
    val responseTimeMs: Int?,
    val statusCode: Int?
)
