package com.mockengine.sdk.data.models

/**
 * API response models for backend communication
 */

data class DeviceResponse(
    val id: Int,
    val deviceId: String,
    val apiKey: String,
    val appVersion: String,
    val androidVersion: String,
    val internetMode: String,
    val firstSeen: String,
    val lastSeen: String
)

data class SuccessResponse(
    val success: Boolean,
    val message: String
)