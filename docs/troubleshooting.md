# Troubleshooting

## Device Not Appearing in the Portal

After initializing the SDK and running the app, the device should appear in the Dashboard under **Device Health** within a few seconds.

**Check these first:**

1. **API key is correct** — copy the key from the portal (API Keys page) and compare it character-by-character with what's in your build. A single extra space or missing character will cause registration to fail silently.

2. **MockEngine.init() is called before any HTTP requests** — if you call `init()` after your OkHttp client is already built, the interceptor isn't added and the device is never registered. Move `init()` to `Application.onCreate()`.

3. **The interceptor is added to the OkHttp client** — `MockEngine.init()` returns an interceptor. You must pass it to `OkHttpClient.Builder().addInterceptor(...)`. If you discard the return value, nothing is registered.

4. **The app has network permission** — the SDK makes real network calls. Verify `INTERNET` permission is declared in `AndroidManifest.xml`:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```

5. **The device is online** — on a physical device, confirm it has a working internet connection. On an emulator, confirm the emulator has network access (check with a browser inside the emulator).

6. **A firewall or proxy is blocking outbound requests** — if you're on a corporate network or VPN, outbound HTTPS traffic to the MockEngine backend may be blocked.

---

## Rules Not Updating

You enabled or changed a rule in the portal but the device is still behaving as before.

**What to check:**

1. **Wait 60 seconds** — the SDK polls for rule updates every 60 seconds. Changes do not push to devices instantly.

2. **The app is in the foreground** — polling is paused when the app is in the background. Bring the app to the foreground, wait 60 seconds, and check again.

3. **The rule is enabled** — newly created rules are disabled by default. Confirm the toggle is on in the Rules list.

4. **The correct API key is in use** — rules belong to the account associated with the API key. If the device was registered with a different key, it won't see rules created under another key.

5. **Force a sync** — kill and restart the app. The SDK fetches rules immediately on init, so a fresh start bypasses the 60-second wait.

---

## Requests Are Not Being Intercepted

A rule is enabled and the device is synced, but requests to the target endpoint are going through to the real server.

**What to check:**

1. **URL pattern mismatch** — the most common cause. Compare the rule's URL pattern against the actual request URL logged in the Dashboard. The pattern must appear as a substring of the full URL. Examples:
   - Pattern `/api/users` matches `https://api.example.com/api/users/` ✓
   - Pattern `api/users` (no leading slash) matches `https://api.example.com/api/users` ✓
   - Pattern `/users` does **not** match `https://api.example.com/api/users/profile` ✗ (not present in the URL)
   - Pattern `/Api/Users` does **not** match `/api/users` ✗ (case-sensitive)

2. **Method mismatch** — if the rule's method is `POST` and your request is `GET`, it won't match. Use `ANY` to match all methods.

3. **The interceptor is not attached** — verify the OkHttp client used by your networking layer (Retrofit, etc.) is the same one built with `addInterceptor(mockInterceptor)`. If you create multiple OkHttp clients, only the one with the interceptor is covered.

4. **Rule is disabled** — double-check the enabled toggle in the portal.

5. **Check the Dashboard** — go to **Dashboard → Interception Mode** and look at the Recent Interceptions table. If the endpoint appears with 0 interceptions despite a matching rule, the rule's pattern is likely not matching.

---

## Network Errors After Adding the SDK

The app starts throwing `IOException` or `SocketTimeoutException` after adding MockEngine.

**What to check:**

1. **Delay is set too high** — if a rule has a `Delay (seconds)` value that exceeds your OkHttp `readTimeout`, every intercepted request will time out. Either increase the timeout or reduce the delay.

2. **Mock data is invalid JSON** — if the `mock_data` field in a rule is malformed JSON, the SDK may fail to build the mock response. Check the rule's Mock Data field in the portal and validate the JSON.

3. **use_mock_backend = false with an unreachable real server** — when a rule's Backend Mode is **Call Real Backend** and the actual server is down, the SDK catches the `IOException` and returns a 503. This is intentional, but if you see unexpected 503s, check if your backend is reachable.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling `MockEngine.init()` more than once | Call it exactly once in `Application.onCreate()`. Multiple calls create duplicate polling loops. |
| Not using the returned interceptor | `init()` returns the interceptor — you must add it to `OkHttpClient.Builder()`. If you ignore the return value, the SDK isn't active. |
| Hardcoding the API key in source | Use `BuildConfig` or a secrets manager. Never commit an API key to version control. |
| Creating a rule with method `GET` for a `POST` request | Set method to `ANY` when you want to intercept regardless of method. |
| Forgetting to enable the rule | Rules are disabled by default after creation. Toggle them on in the Rules list. |
| Testing with a broad rule and forgetting to disable it | A rule like URL pattern `/api/` + method `ANY` intercepts everything. Disable it immediately after your test session. |
| Using `addNetworkInterceptor()` instead of `addInterceptor()` | MockEngine must be added as an **application-level** interceptor (`addInterceptor()`). Network interceptors run after the connection is established — MockEngine needs to run before that to short-circuit the real request. |
