package com.mockengine.sdk.data.models

import android.os.Build

/**
 * Device registration data model for backend API
 */
data class DeviceRegistration(
    val deviceId: String,
    val appVersion: String,
    val androidVersion: String = Build.VERSION.RELEASE,
    val internetMode: String // "wifi", "cellular", "none"
)