# Examples

Practical, copy-paste-ready examples for common testing scenarios. Each example shows what to configure in the portal and what the app will receive.

---

## Mock a Login Endpoint

**Scenario:** The login endpoint isn't ready yet, or you want to test the app's behavior after a successful login without needing real credentials.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `Mock Login - Success` |
| URL Pattern | `/api/auth/login` |
| Method | `POST` |
| Status Code | `200` |
| Backend Mode | Mock Backend |
| Mock Data | See below |

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User"
  },
  "expiresIn": 86400
}
```

**Expected result:** Any POST to `/api/auth/login` returns HTTP 200 with this payload. The app logs in and navigates to the main screen as if authentication succeeded.

---

## Return 404

**Scenario:** Test how the app handles a missing resource — an item that was deleted, a profile that doesn't exist, a URL that's mistyped.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `404 - User Not Found` |
| URL Pattern | `/api/users/` |
| Method | `GET` |
| Status Code | `404` |
| Backend Mode | Mock Backend |
| Mock Data | See below |

```json
{
  "error": "not_found",
  "message": "The requested user does not exist."
}
```

**Expected result:** Any GET to a `/api/users/*` path returns HTTP 404 with this error body. Verify the app shows an appropriate empty state or error screen rather than crashing or showing stale data.

---

## Return 500

**Scenario:** Simulate an unhandled server error to verify the app displays a meaningful error message instead of a blank screen or crash.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `500 - Internal Server Error` |
| URL Pattern | `/api/` |
| Method | `ANY` |
| Status Code | `500` |
| Backend Mode | Mock Backend |
| Mock Data | See below |

```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred. Please try again later."
}
```

**Expected result:** All API requests return HTTP 500. The app should display a user-friendly error state with a retry option. This rule is broad (`/api/` + `ANY`) — disable it immediately after testing to avoid blocking other scenarios.

---

## Delay a Response

**Scenario:** Test loading spinners, skeleton screens, timeout handling, and cancellation behavior by slowing down a specific endpoint.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `Slow Feed - 4s delay` |
| URL Pattern | `/api/feed` |
| Method | `GET` |
| Status Code | `200` |
| Delay (seconds) | `4` |
| Backend Mode | Call Real Backend |
| Mock Data | *(leave empty — returns real response after the delay)* |

**Expected result:** The feed endpoint responds after a 4-second delay. The app should show a loading indicator for the duration. If your OkHttp `readTimeout` is less than 4 seconds, the request times out — useful for testing timeout handling.

> **Testing timeout specifically:** set the delay to exceed your `readTimeout` value. The SDK sleeps for the full delay, then the response is returned. OkHttp's timeout fires before it arrives, so the app sees a `SocketTimeoutException`.

---

## Replace a User's Name

**Scenario:** You want the real authentication and user data to be fetched, but you need to override a specific field in the response — for example, to test how the UI renders a very long name or a name with special characters.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `Override User Name` |
| URL Pattern | `/api/users/me` |
| Method | `GET` |
| Status Code | `200` |
| Backend Mode | Call Real Backend |
| Mock Data | See below |

```json
{
  "id": 1,
  "firstName": "Bartholomew-Hieronymus",
  "lastName": "Von Großschmidt-Weisskopf",
  "email": "real@example.com"
}
```

**Expected result:** The real `/api/users/me` request is made (auth headers are sent, session is valid). The response body is replaced with the mock payload. The app renders the overridden name, letting you verify the UI doesn't break with unusually long or special-character names.

---

## Simulate a Rate Limit

**Scenario:** Test that the app handles 429 Too Many Requests gracefully — showing a message, backing off, or blocking further requests.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `429 - Rate Limited` |
| URL Pattern | `/api/` |
| Method | `ANY` |
| Status Code | `429` |
| Backend Mode | Mock Backend |
| Mock Data | See below |

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please slow down.",
  "retryAfter": 60
}
```

**Expected result:** All API calls return 429. The app should surface a user-readable message and respect the `retryAfter` value if implemented.

---

## Simulate a Complete Server Outage

**Scenario:** Test offline/degraded state — the backend is completely unreachable. Verify the app shows a connection error screen and that cached data (if any) is still visible.

**Portal configuration:**

| Field | Value |
|---|---|
| Name | `Server Down` |
| URL Pattern | `/api/` |
| Method | `ANY` |
| Status Code | `503` |
| Backend Mode | Mock Backend |
| Mock Data | See below |

```json
{
  "error": "service_unavailable",
  "message": "The server is temporarily unavailable. Please try again later."
}
```

**Expected result:** Every API call returns 503 immediately, without reaching the real server. The app should fall back to cached content where available and display a connection error for live data. Remember to disable this rule when you're done — it affects all endpoints.
