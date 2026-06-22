package com.mockengine.sdk.cache

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.mockengine.sdk.data.models.Rule

/**
 * Room database for caching MockEngine rules locally
 */
@Database(entities = [Rule::class], version = 2)
@TypeConverters(MapTypeConverter::class)
abstract class CacheDatabase : RoomDatabase() {

    abstract fun ruleDao(): RuleDao

    companion object {
        @Volatile
        private var INSTANCE: CacheDatabase? = null

        /**
         * Gets the singleton instance of the cache database
         *
         * @param context Application context
         * @return Singleton CacheDatabase instance
         */
        fun getInstance(context: Context): CacheDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CacheDatabase::class.java,
                    "mock_engine_cache"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}