# FAQ

## General

<details>
<summary><strong>What is MockEngine?</strong></summary>


MockEngine is an Android SDK that intercepts HTTP requests from your app and returns configurable mock responses. Rules are managed through a web portal and sync to connected devices in real time. No app code changes are needed after the initial setup.

---


</details>
<details>
<summary><strong>Is MockEngine free?</strong></summary>


Please check the [MockEngine website](https://mockengine.app) for current pricing and plan details.

---


</details>
<details>
<summary><strong>Does MockEngine work in production builds?</strong></summary>


The SDK can be included in any build variant. Most teams add it only to debug or QA builds using Gradle product flavors or build types, and use a no-op stub (or simply omit the interceptor) in release builds. There is nothing that technically prevents it from running in production, but enabling mock rules in a production app is generally not recommended.

---


</details>
<details>
<summary><strong>Can I use MockEngine without OkHttp?</strong></summary>


The current Android SDK is an OkHttp interceptor. If your app uses a different HTTP client (e.g., Volley, Ktor), the SDK does not support it directly. OkHttp is used by Retrofit, which covers most Android projects.

---

</details>


## Rules

<details>
<summary><strong>How quickly do rule changes take effect on a device?</strong></summary>


The SDK polls for rule updates every 60 seconds while the app is in the foreground. A rule change takes effect within one polling cycle. To apply a change immediately, restart the app — the SDK fetches rules fresh on every `init()` call.

---


</details>
<details>
<summary><strong>Can I have multiple rules for the same endpoint?</strong></summary>


Yes, we are not blocking you. But please note that only the first rule will take effect. Disable the higher-priority rule to allow the next one to take effect.

---


</details>
<details>
<summary><strong>Can a rule match all endpoints at once?</strong></summary>


Yes. Set the URL pattern to a common prefix (e.g., `/api/*`) and the method to `ANY`. This matches every request to that path prefix. Use this carefully — it blocks or overrides all matched endpoints simultaneously.

---


</details>
<details>
<summary><strong>What URL patterns are supported?</strong></summary>


The SDK performs a substring match: the rule's `url_pattern` must appear somewhere in the full request URL. Regex is supported as well.

Examples:
- `/api/users` matches `https://api.example.com/api/users` and `https://api.example.com/api/users/42`
- `/users/42` matches `https://api.example.com/api/users/42` but not `https://api.example.com/api/users/99`

---


</details>
<details>
<summary><strong>Can I mock HTTPS endpoints?</strong></summary>


Yes. The interceptor runs at the OkHttp application layer, before TLS. It intercepts both HTTP and HTTPS requests transparently.

---


</details>
<details>
<summary><strong>What is the difference between Mock Backend and Call Real Backend?</strong></summary>


| | Mock Backend | Call Real Backend |
|---|---|---|
| Real server called? | No | Yes |
| Response body | From mock data in the rule | From mock data in the rule |
| Response status code | From the rule | From the rule |
| Use when | Endpoint doesn't exist, or you need full control | Server side effects needed, or you only want to override part of the response |

---


</details>
<details>
<summary><strong>Can I leave Mock Data empty?</strong></summary>


Yes. If Mock Data is empty, the response body will be an empty string, unless real server is called too and then response will be the server response. The status code from the rule still applies. This is useful when testing endpoints where the app only checks the status code and ignores the body.

---


</details>
<details>
<summary><strong>Can delay_s be a decimal (e.g., 1.5 seconds)?</strong></summary>


No

---


</details>


## Analytics

<details>
<summary><strong>What data does MockEngine collect?</strong></summary>


The SDK logs:
- Every HTTP request: device ID, endpoint, HTTP method, status code, response time (ms), and whether it was intercepted
- Every interception event: device ID, rule ID, endpoint, method, request data, and mock response data

No personal user data from your app's requests (request bodies, auth tokens, PII) is included in logs.

---


</details>
<details>
<summary><strong>How long is analytics data retained?</strong></summary>


Please refer to the MockEngine portal or contact support for the current data retention policy.

---


</details>
<details>
<summary><strong>Can I see which device triggered which interception?</strong></summary>


Yes. The Dashboard's **Interception Mode** shows recent interceptions. Each interception is associated with a device ID (a UUID generated on first install and stored on-device).

---


</details>

## SDK Behavior

<details>
<summary><strong>Does MockEngine affect app performance?</strong></summary>


The rule-matching logic runs synchronously on the thread making the HTTP call (same as any OkHttp interceptor). For most apps with fewer than a few hundred rules, the overhead is negligible (microseconds). Analytics logging is done asynchronously and does not block the response.

---


</details>
<details>
<summary><strong>What happens if the MockEngine backend is unreachable?</strong></summary>


The SDK falls back to the locally cached rules and continues intercepting as normal. New rule changes from the portal will not reach the device until connectivity is restored. All analytics events are dropped if the backend is unreachable (they are not queued for retry).

---


</details>
<details>
<summary><strong>What happens when the app goes to the background?</strong></summary>


Background polling is paused automatically. The SDK resumes polling (and performs an immediate sync) when the app comes back to the foreground.

---


</details>
<details>
<summary><strong>Is the device ID persistent across app reinstalls?</strong></summary>


No. The device ID is a UUID generated on the first SDK initialization and stored in the app's local data. Uninstalling and reinstalling the app generates a new device ID.

---


</details>
<details>
<summary><strong>Can I use multiple API keys in the same app?</strong></summary>


No. `MockEngine.init()` is a singleton — calling it a second time with a different key does not create a second instance. Configure the key once at startup.

---


</details>
<details>
<summary><strong>Does MockEngine require any Android permissions?</strong></summary>


Only the standard `INTERNET` permission, which is required for any app that makes network calls. MockEngine does not request location, camera, contacts, or any other sensitive permissions.

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

</details>