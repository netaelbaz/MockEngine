package com.mockengine.sdk.engine

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for RuleMatcher
 */
class RuleMatcherTest {

    @Test
    fun testExactMatch() {
        // Test exact pattern matching
        assertTrue("Exact match should work", RuleMatcher.matches("/api/users", "/api/users"))
        assertFalse("Different paths should not match", RuleMatcher.matches("/api/users/123", "/api/users"))
        assertFalse("Case sensitivity should work", RuleMatcher.matches("/api/Users", "/api/users"))
    }

    @Test
    fun testWildcardMatch() {
        // Test wildcard pattern matching
        assertTrue("Wildcard should match subpaths", RuleMatcher.matches("/api/users/123", "/api/users/*"))
        assertTrue("Wildcard should match multiple levels", RuleMatcher.matches("/api/users/abc", "/api/users/*"))
        assertFalse("Wildcard should not match parent path", RuleMatcher.matches("/api/users", "/api/users/*"))
        assertTrue("Multiple wildcards should work", RuleMatcher.matches("/api/users/123/posts", "/api/users/*/posts"))
    }

    @Test
    fun testRegexMatch() {
        // Test regex pattern matching
        assertTrue("Regex should match numbers", RuleMatcher.matches("/api/users/123", "^/api/users/\\d+$"))
        assertFalse("Regex should not match letters", RuleMatcher.matches("/api/users/abc", "^/api/users/\\d+$"))
        assertTrue("Complex regex should work", RuleMatcher.matches("/api/v2/users", "^/api/v\\d+/.*"))
    }

    @Test
    fun testPathVariableExtraction() {
        // Test path variable extraction from wildcard patterns
        val variables = RuleMatcher.extractPathVariables("/api/users/123/posts", "/api/users/*/posts")
        assertTrue("Should extract path variables", variables.containsKey("param0"))
        assertEquals("Should extract correct value", "123", variables["param0"])
    }

    @Test
    fun testPatternTypeDetection() {
        // Test pattern type detection
        assertEquals("Regex pattern", "regex", RuleMatcher.getPatternType("^/api/users/\\d+$"))
        assertEquals("Wildcard pattern", "wildcard", RuleMatcher.getPatternType("/api/users/*"))
        assertEquals("Exact pattern", "exact", RuleMatcher.getPatternType("/api/users"))
    }

    @Test
    fun testPatternValidation() {
        // Test pattern validation
        assertTrue("Valid exact pattern", RuleMatcher.isValidPattern("/api/users"))
        assertTrue("Valid wildcard pattern", RuleMatcher.isValidPattern("/api/users/*"))
        assertTrue("Valid regex pattern", RuleMatcher.isValidPattern("^/api/users/\\d+$"))
        assertFalse("Invalid regex pattern", RuleMatcher.isValidPattern("^/api/users/[unclosed"))
    }

    @Test
    fun testComplexPatterns() {
        // Test complex real-world patterns
        assertTrue("API version pattern", RuleMatcher.matches("/api/v1/users", "^/api/v\\d+/.*"))
        assertTrue("UUID pattern", RuleMatcher.matches("/api/users/550e8400-e29b-41d4-a716-446655440000", "/api/users/*"))
        assertTrue("Slug pattern", RuleMatcher.matches("/api/posts/my-post-title", "/api/posts/*"))
    }

    @Test
    fun testEdgeCases() {
        // Test edge cases
        assertTrue("Root path", RuleMatcher.matches("/", "/"))
        assertFalse("Empty pattern should not match", RuleMatcher.matches("/api/users", ""))
        assertFalse("Trailing slash matters", RuleMatcher.matches("/api/users/", "/api/users"))
    }

    @Test
    fun testPerformanceWithLongPaths() {
        // Test performance with longer URL paths
        val longPath = "/api/v1/users/123/posts/456/comments/789"
        val pattern = "/api/v1/users/*/posts/*/comments/*"
        assertTrue("Long paths with multiple wildcards", RuleMatcher.matches(longPath, pattern))
    }
}