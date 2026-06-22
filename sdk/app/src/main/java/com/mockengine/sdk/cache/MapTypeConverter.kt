package com.mockengine.sdk.cache

import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class MapTypeConverter {
    private val gson = Gson()

    @TypeConverter
    fun fromMap(map: Map<String, Any>?): String? =
        map?.let { gson.toJson(it) }

    @TypeConverter
    fun toMap(json: String?): Map<String, Any>? =
        json?.let {
            val type = object : TypeToken<Map<String, Any>>() {}.type
            gson.fromJson(it, type)
        }
}
