# Who Is It For?

MockEngine is useful for any team that builds or tests Android apps that communicate with a backend. The interceptor sits transparently in the networking layer, so the same SDK integration serves multiple roles without any additional setup.

## Android Developers

You write the app. You add the interceptor once. From that point, MockEngine gets out of your way during normal development and activates only when a rule is enabled.

**Where it helps:**
- Reproduce a specific backend error during local development without waiting for the backend team to reproduce it
- Test edge cases — 401 unauthorized, 429 rate limited, 503 service unavailable — without coordinating with anyone
- Develop screens that depend on an endpoint that doesn't exist yet by mocking its response
- Verify your app's error-handling UI renders correctly for status codes that are hard to trigger in staging

## QA Engineers

You test the app. MockEngine lets you control the backend from the portal without modifying any app build or touching the backend.

**Where it helps:**
- Simulate server errors (4xx, 5xx) to verify the app handles them gracefully
- Test slow network conditions by adding artificial delays to specific endpoints
- Force a specific response payload to test how the UI renders edge-case data (empty lists, very long strings, missing optional fields)
- Reproduce a bug that only occurs under a specific server response, reliably and on demand
- Disable rules immediately after a test without rebuilding the app

## Backend Developers

You own the API. MockEngine lets you overview the entire backend http requests done in all connected devices.

**Where it helps:**
- See if any unexpected status code happened recently
- see if any endpoint is not called at all ( maybe can be deleted )
- see avg response time for each endpoint

## Teams Testing APIs

If your team runs integration tests, exploratory QA, or release verification cycles against an API, MockEngine gives you fine-grained per-endpoint control through the portal.

**Where it helps:**
- Control exactly which endpoints return what during a test session without touching the backend
- Run repeatable test scenarios using rules as fixtures — enable a set of rules for a test, disable them when done
- Monitor all API traffic from a connected device in real time via the analytics dashboard
- Understand endpoint usage patterns: which endpoints are called most, what the average response time is, where errors cluster
