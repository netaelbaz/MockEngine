# MockEngine

SDK for Android applications — mock HTTP responses during development and testing without changing a single line of app code.

---

## What is MockEngine?

MockEngine is a developer tool that lets you intercept HTTP calls made by your Android app and return controlled responses — mock data, error codes, delays — all configured from a web dashboard, with no app redeployment required.

It consists of three parts:
- **Android SDK** — sits inside your app and intercepts matching HTTP calls
- **Backend** — FastAPI server that stores rules and serves them to the SDK
- **Dashboard** — React web app for creating and managing interception rules

---

## Features

- **Interception Rules** — match requests by URL pattern and HTTP method, then return a custom status code, JSON body, and optional delay
- **Mock or Real Backend** — per-rule toggle: either return a full mock response or let the real server reply while the rule still applies
- **AI-Generated Mock Data** — describe the data you need in plain English and get a ready-to-use JSON response body instantly
- **Upload JSON** — paste or upload a `.json` file as the response body
- **Enable / Disable Rules** — toggle rules on or off without deleting them
- **Analytics Dashboard** — track SDK activity, interception counts, device health, error distribution, and traffic over time
- **API Key Management** — generate scoped API keys for each SDK integration
- **Device Registration** — track which devices are running the SDK

---

## Installation

Add the SDK to your `build.gradle`:

```kotlin
dependencies {
    implementation("com.github.netaelbaz:MockEngine:<version>")
}
```

Initialize it in your `Application` class (or `MainActivity`) with the API key from the dashboard:

```kotlin
val interceptor = MockEngine.init(
    context = this,
    apiKey = "YOUR_API_KEY"
)
```

Then add the returned interceptor to your OkHttp client:

```kotlin
val client = OkHttpClient.Builder()
    .addInterceptor(interceptor)
    .build()
```

---

## Quick Start (30 seconds)

1. Open the MockEngine dashboard → **API Keys** → generate a new key
2. Add the SDK dependency and call `MockEngine.init(...)` with that key
3. Go to **Rules** → **New Rule**
4. Set an endpoint pattern (e.g. `/api/orders/*`), a status code (e.g. `200`), and a JSON response body
5. Run your app — matching requests now return your mock response

---

## Simple Flow Diagram

```
Android App
    │
    │  HTTP request  (e.g. GET /api/orders/123)
    ▼
MockEngine SDK
    │
    ├── fetches active rules from Backend on startup
    │
    ├── rule matches?
    │       YES → return mock response (status, JSON body, delay)
    │       NO  → pass request to real server as normal
    │
    └── logs interception event to Backend
    
Backend (FastAPI)          Dashboard (React)
    │                           │
    ├── stores rules ◄──────────┤  developer creates / edits rules
    ├── issues API keys         │
    └── serves analytics ──────►┘  developer views SDK activity
```

---

## Documentation

Full documentation, guides, and API reference:
**[https://netaelbaz.github.io/MockEngine/](https://netaelbaz.github.io/MockEngine/)**
