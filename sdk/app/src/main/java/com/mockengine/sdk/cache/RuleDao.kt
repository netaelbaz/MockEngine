package com.mockengine.sdk.cache

import androidx.room.*
import com.mockengine.sdk.data.models.Rule

/**
 * Data Access Object for Rule entities
 */
@Dao
interface RuleDao {

    /**
     * Get all active (enabled) rules from the cache
     *
     * @return List of enabled rules
     */
    @Query("SELECT * FROM rules WHERE isEnabled = 1")
    suspend fun getActiveRules(): List<Rule>

    /**
     * Insert or replace rules in the cache
     *
     * @param rules List of rules to insert/replace
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRules(rules: List<Rule>)

    /**
     * Clear all rules from the cache
     */
    @Query("DELETE FROM rules")
    suspend fun clearAll()

    /**
     * Get a specific rule by ID
     *
     * @param ruleId The rule ID to search for
     * @return The rule if found, null otherwise
     */
    @Query("SELECT * FROM rules WHERE id = :ruleId")
    suspend fun getRuleById(ruleId: Int): Rule?

    /**
     * Update the enabled status of a specific rule
     *
     * @param ruleId The rule ID to update
     * @param enabled The new enabled status
     */
    @Query("UPDATE rules SET isEnabled = :enabled WHERE id = :ruleId")
    suspend fun updateRuleStatus(ruleId: Int, enabled: Boolean)
}