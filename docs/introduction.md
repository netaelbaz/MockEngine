# Introduction

## What Is MockEngine SDK?

MockEngine is an Android SDK that intercepts HTTP requests made by your app and returns configurable mock responses, without having to create a mock server or edit your existing server.

You define rules in a web-based portal. The SDK downloads them automatically, caches them on-device, and applies them at runtime through an OkHttp interceptor. When a request matches a rule, MockEngine returns whatever response you configured: a custom status code, a JSON body, an artificial delay, or any combination of these.

## Why Use MockEngine?

Testing network-dependent Android apps is difficult. You need to reproduce error states, specific API payloads, slow responses, and server downtime — but the backend may not support this, and modifying app code for every test scenario is impractical and error-prone.

MockEngine solves this by moving control to a dashboard:

- **No app code changes required** — add the interceptor once during setup; control everything from the portal after that
- **Works on any build** — debug, staging, or dedicated QA builds
- **Team-friendly** — QA engineers and backend developers can create or modify rules without touching Android code
- **Real-time** — rule changes propagate to all connected devices within 60 seconds
- **Observable** — every call is logged so you can verify rules are firing and measure endpoint behavior

## Key Features

| Feature | Description |
|---|---|
| Rule-based interception | Match requests by URL pattern and HTTP method |
| Dual backend modes | Skip the real server (full mock) or call it and override the response |
| Configurable mock responses | Set status code, JSON response body, and artificial delay |
| Offline-first cache | Rules cached locally using Room — mocking works without network |
| Real-time sync | Rules refresh every 60 seconds via background polling |
| Device tracking | See which devices are connected and their app versions |
| Analytics | Full call log: interception rates, response times, error distribution |
| AI mock generation | Generate realistic JSON from a plain English description |

## How It Works

```text
Application Request
        │
        ▼
MockEngine Interceptor
        │
        ▼
Find Matching Rule
        │
   ┌────┴────┐
   │         │
No Match   Match
   │         │
   ▼         ▼
Real     Backend Mode
Server        │
         ┌────┴────┐
         │         │
        Mock      Real
        Mode      Backend
        │           │
        ▼           ▼
        Apply     Call Real Server
        Mock          │
        Rules         ▼
                Apply Mock Rules
```

1. **Initialize** — your app calls `MockEngine.init()` once on startup, passing the app context and your API key
2. **Register** — the SDK registers the device with the MockEngine backend
3. **Sync** — active rules are fetched and cached locally; the SDK re-syncs every 60 seconds
4. **Intercept** — every HTTP request is checked against active rules
5. **Respond** — matching requests receive the configured mock response; unmatched requests reach the real server normally
6. **Log** — all calls and interception events are sent to the backend for analytics
