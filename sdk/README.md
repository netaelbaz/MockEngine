# MockEngine Android SDK

## 🚀 Quick Start

This is a fresh Android Studio project with the MockEngine SDK fully integrated!

### Prerequisites
- Android Studio Hedgehog | 2024.1.1+
- Android SDK API 24+
- Backend running on `http://localhost:8000`

### Running the App

1. **Open in Android Studio**
   - File → Open → Select this directory
   - Wait for Gradle sync

2. **Run the App**
   - Click green ▶️ button
   - Select emulator or device
   - App will install and launch

### 🔑 API Configuration

The demo app is pre-configured with:
- **API Key**: `4715e71512b537a515be00694473aa34dab5b45f41a7672126f3d03cc9832aa9`
- **Backend URL**: `http://localhost:8000` (configured in network layer)

## 📱 App Features

The demo app showcases:
- ✅ SDK initialization with device registration
- ✅ Real-time request/response logging
- ✅ Test API calls demonstrating interception
- ✅ Integration with existing OkHttp/Retrofit setup

## 🏗️ Project Structure

```
com.mockengine.sdk/
├── MockEngine.kt              # Main SDK singleton
├── data/models/               # Data models (Rule, DeviceRegistration, etc.)
├── network/                   # API service and client
├── cache/                     # Room database + SharedPreferences
├── engine/                    # Pattern matching engine
├── interceptor/               # HTTP response interceptor
└── error/                     # Error handling & fallback

com.mockengine.demo/
└── MainActivity.kt            # Demo application
```

## 🔧 Dependencies Included

- OkHttp3 4.12.0
- Retrofit2 2.9.0
- Room Database 2.6.1
- Coroutines 1.7.3
- Gson 2.10.1
- AndroidX Lifecycle 2.6.2

## 🧪 Testing

Run unit tests:
```bash
./gradlew test
```

Run instrumented tests:
```bash
./gradlew connectedAndroidTest
```

## 📚 Available Rules (from Backend)

The SDK is configured to use these existing rules:

1. `/api/test1` → Returns `{"message": "test"}`
2. `/api/test2` → Returns `{"message": "test"}`
3. `/api/users` → Returns `{}`

## 🎯 Next Steps

1. **Create more rules** via backend web portal
2. **Test SDK** with your own API endpoints
3. **Customize demo** for your specific use cases
4. **Build release APK** for distribution

## 🐛 Troubleshooting

### Build Issues
- **Sync Gradle**: File → Sync Project with Gradle Files
- **Clean Build**: Build → Clean Project → Rebuild Project

### Runtime Issues
- **Check Backend**: Ensure backend is running on localhost:8000
- **API Key**: Verify the API key is valid in backend portal
- **Permissions**: Check INTERNET permission in AndroidManifest.xml

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using MockEngine SDK**
