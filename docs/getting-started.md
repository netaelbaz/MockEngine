# Getting Started

This guide walks you from zero to a working MockEngine integration in your Android application.

By the end of this guide, your application will be connected to the MockEngine platform and ready to receive rules from the web portal.

---

## Requirements

| Requirement | Minimum Version |
| --- | --- |
| Android | API 26 (Android 8.0 Oreo) |
| Kotlin | 1.6+ |
| OkHttp | 4.x |
| SDK API Key | Required |

MockEngine integrates using OkHttp's interceptor API. If your application already uses OkHttp or Retrofit, integration requires only one additional interceptor.

---

## Step 1 — Add the SDK Dependency

Add the SDK to your app module.

```groovy
dependencies {
    implementation("com.mockengine:sdk:1.0.0")
}
```

If you're using Kotlin DSL:

```kotlin
dependencies {
    implementation("com.mockengine:sdk:1.0.0")
}
```

---

## Step 2 — Create an API Key

1. Open the MockEngine Web Portal.
2. Navigate to **API Keys**.
3. Click **Create API Key**.
4. Give it a descriptive name.
5. Copy the generated key.

You'll use this key during SDK initialization.

---

## Step 3 — Initialize the SDK

Initialize MockEngine once from your `Application.onCreate()`.

```kotlin
val mockInterceptor = MockEngine.init(
    context = applicationContext,
    apiKey = BuildConfig.MOCK_ENGINE_API_KEY
)
```

---

## Step 4 — Add the Interceptor

Attach the interceptor to your existing `OkHttpClient`.

```kotlin
val client = OkHttpClient.Builder()
    .addInterceptor(mockInterceptor)
    .build()
```

If you use Retrofit, simply provide the same client.

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .client(client)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

---

## Step 5 — Verify the Connection

Run your application.

Open the MockEngine portal and navigate to **Dashboard**.

Within a few seconds your device should appear under **Connected Devices**.

Once the device appears, the SDK is ready to receive rules and intercept requests.

---

## Next Steps

Your SDK is now fully configured.

Continue with:

- **How to Use** — Learn how to create and manage rules.
- **Examples** — Explore common testing scenarios.
- **How It Works** — Understand the SDK internals.