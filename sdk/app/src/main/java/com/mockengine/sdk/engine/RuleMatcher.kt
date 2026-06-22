package com.mockengine.sdk.engine

import android.util.Log
import java.util.regex.PatternSyntaxException

/**
 * Rule matching engine for URL pattern matching
 *
 * Supports three pattern types:
 * 1. Exact match: "/api/users" matches only "/api/users"
 * 2. Wildcard match: "/api/users/ *" matches "/api/users/123", "/api/users/abc"
 * 3. Regex match: "^/api/users/\\d+$" matches "/api/users/123" (not "/api/users/abc")
 */
object RuleMatcher {

    private const val TAG = "RuleMatcher"

    /**
     * Check if a request URL matches a rule pattern
     *
     * @param requestUrl The URL path from the HTTP request
     * @param pattern The pattern from the rule
     * @return true if the pattern matches, false otherwise
     */
    fun matches(requestUrl: String, pattern: String, requestMethod: String = "GET", ruleMethod: String = "ANY"): Boolean {
        val methodMatches = ruleMethod == "ANY" || ruleMethod.equals(requestMethod, ignoreCase = true)
        if (!methodMatches) return false
        return try {
            when {
                // Regex pattern (starts with ^)
                pattern.startsWith("^") -> {
                    matchRegex(requestUrl, pattern)
                }
                // Wildcard pattern (contains *)
                pattern.contains("*") -> {
                    matchWildcard(requestUrl, pattern)
                }
                // Exact match
                else -> {
                    matchExact(requestUrl, pattern)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Pattern matching failed for pattern: $pattern", e)
            false
        }
    }

    /**
     * Match using regex pattern
     */
    private fun matchRegex(requestUrl: String, pattern: String): Boolean {
        return try {
            val regex = Regex(pattern)
            regex.matches(requestUrl)
        } catch (e: PatternSyntaxException) {
            Log.e(TAG, "Invalid regex pattern: $pattern", e)
            false
        }
    }

    /**
     * Match using wildcard pattern
     * Converts wildcard to regex and matches
     */
    private fun matchWildcard(requestUrl: String, pattern: String): Boolean {
        return try {
            // Convert wildcard pattern to regex
            val regexPattern = pattern
                .replace(".", "\\.") // Escape dots
                .replace("*", ".*")   // Convert * to .*
                .replace("?", ".")    // Convert ? to .

            val regex = Regex("^$regexPattern$")
            regex.matches(requestUrl)
        } catch (e: PatternSyntaxException) {
            Log.e(TAG, "Invalid wildcard pattern: $pattern", e)
            false
        }
    }

    /**
     * Match using exact string comparison
     */
    private fun matchExact(requestUrl: String, pattern: String): Boolean {
        return requestUrl == pattern
    }

    /**
     * Extract variables from a wildcard pattern match
     * For example, from "/api/users/ *" and "/api/users/123", extract "123"
     *
     * @param requestUrl The URL path from the HTTP request
     * @param pattern The pattern from the rule
     * @return Map of extracted variable names and values
     */
    fun extractPathVariables(requestUrl: String, pattern: String): Map<String, String> {
        val variables = mutableMapOf<String, String>()

        try {
            when {
                pattern.contains("*") -> {
                    val regexPattern = pattern
                        .replace(".", "\\.") // Escape dots
                        .replace("*", "(.*)")   // Convert * to capture group

                    val regex = Regex("^$regexPattern$")
                    val matchResult = regex.find(requestUrl)

                    if (matchResult != null) {
                        val groups = matchResult.destructured.toList()
                        groups.forEachIndexed { index, value ->
                            variables["param$index"] = value
                        }
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to extract path variables", e)
        }

        return variables
    }

    /**
     * Get pattern type for logging/debugging
     */
    fun getPatternType(pattern: String): String {
        return when {
            pattern.startsWith("^") -> "regex"
            pattern.contains("*") -> "wildcard"
            else -> "exact"
        }
    }

    /**
     * Validate if a pattern is syntactically correct
     */
    fun isValidPattern(pattern: String): Boolean {
        return try {
            when {
                pattern.startsWith("^") -> {
                    Regex(pattern)
                    true
                }
                pattern.contains("*") -> {
                    val regexPattern = pattern.replace(".", "\\.").replace("*", ".*")
                    Regex("^$regexPattern$")
                    true
                }
                else -> true // Exact match is always valid
            }
        } catch (e: PatternSyntaxException) {
            false
        }
    }
}
