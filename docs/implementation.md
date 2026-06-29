# How It Works

This page explains what happens internally after MockEngine is initialized and how requests are intercepted at runtime.

---

## SDK Initialization

When `MockEngine.init()` is called, the SDK performs the following sequence:

```text
Application starts
        │
        ▼
MockEngine.init()
        │
        ▼
Read API Key
        │
        ▼
Create authenticated HTTP client
        │
        ▼
Initialize local database
        │
        ▼
Register device
        │
        ▼
Download active rules
        │
        ▼
Cache rules locally
        │
        ▼
Start background polling
        │
        ▼
Return MockEngineInterceptor
```

Initialization happens only once during application startup.

---

## Request Interception

Every outgoing OkHttp request passes through the interceptor.

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

If no rule matches, the request proceeds normally.

If a rule matches, the configured behavior is applied before the response reaches your application.

---

## Rule Matching

Each request is evaluated against the active rules in order.

A rule matches when:

- The URL pattern matches the request URL.
- The HTTP method matches (or is set to `ANY`).
- The rule is enabled.

The first matching rule is applied.

---

## Rule Cache

Downloaded rules are stored locally using Room.

The cache allows interception to continue even if the MockEngine backend becomes temporarily unavailable.

---

## Background Synchronization

The SDK automatically synchronizes rules with the backend every **60 seconds**.

```text
Foreground
    │
    ▼
Poll every 60 seconds

Background
    │
    ▼
Polling paused

Foreground again
    │
    ▼
Immediate synchronization
```

No manual synchronization is required.

---

## Offline Behavior

If the SDK cannot reach the MockEngine backend:

- Cached rules continue to work.
- Requests are still intercepted.
- Analytics are retried when connectivity returns.

Once connectivity is restored, the SDK automatically downloads the latest rules.

---

## Analytics Logging

After each request completes, the SDK logs analytics asynchronously.

Two event types are recorded:

| Event | Description |
| --- | --- |
| Call Log | Recorded for every request. Includes endpoint, response time, HTTP status, and whether the request was intercepted. |
| Interception Log | Recorded only for intercepted requests. Includes the matched rule, request details, and generated response. |

Logging never blocks the request and does not affect application performance.

---

## Performance

The SDK is designed to have minimal runtime overhead.

- Rule lookup happens in memory.
- Database access is only used during synchronization.
- Analytics are sent asynchronously.
- Network polling runs in the background.
- No work is performed on the main UI thread.

In the common case where no rule matches, the interceptor simply forwards the request to OkHttp with minimal additional processing.