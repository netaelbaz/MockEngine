package com.mockengine.sdk.data.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName

/**
 * Represents an interception rule that can modify HTTP responses
 */
@Entity(tableName = "rules")
data class Rule(
    @PrimaryKey
    val id: Int,
    @SerializedName("url_pattern")
    val urlPattern: String,
    val method: String = "GET",
    @SerializedName("status_code")
    val statusCode: Int,
    @SerializedName("delay_s")
    val delayS: Int,
    @SerializedName("mock_data")
    val mockData: Map<String, Any>?,
    @SerializedName("is_enabled")
    val isEnabled: Boolean
)