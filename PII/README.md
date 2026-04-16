# PII Redaction — Flutter Mobile App

Mobile client for the **Secure PII Redaction System** Flask backend.

## Project structure

```
lib/
├── main.dart                    # App entry point
├── theme/
│   └── app_theme.dart           # Material 3 theme
├── services/
│   └── api_service.dart         # All HTTP calls to Flask backend
├── providers/
│   ├── auth_provider.dart       # Login/register state
│   └── document_provider.dart  # Upload & result state
├── models/
│   ├── detection_result.dart    # PiiDetection, ProcessingStats
│   └── audit_log.dart           # AuditLog
└── screens/
    ├── splash_screen.dart
    ├── login_screen.dart
    ├── register_screen.dart
    ├── dashboard_screen.dart    # Upload & select doc type
    ├── result_screen.dart       # PII detections + stats
    └── audit_logs_screen.dart   # Processing history
```

## Setup

### 1. Install Flutter
https://docs.flutter.dev/get-started/install

### 2. Install dependencies
```bash
flutter pub get
```

For backend (Flask + AI), from `D:\PII\PII`:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

AI module loading priority in backend:
- `AI_MODULES_DIR` (if set)
- local modules at `D:\PII\PII\modules`
- shared workspace fallback at `D:\PII\modules`

### 3. Point to your Flask server
Open `lib/services/api_service.dart` and change:
```dart
static const String baseUrl = 'http://127.0.0.1:5000';
```

- **Android emulator**: use `http://10.0.2.2:5000`
- **Physical device**: use your machine's local IP, e.g. `http://192.168.1.100:5000`
- **Production**: use your deployed domain

### 4. Android network permissions
Add to `android/app/src/main/AndroidManifest.xml` inside `<manifest>`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
```

For HTTP (non-HTTPS) on Android, also add inside `<application>`:
```xml
android:usesCleartextTraffic="true"
```

### 5. iOS permissions
Add to `ios/Runner/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>Required to photograph identity documents</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Required to select document images</string>
```

### 6. Run
```bash
flutter run
```

Run backend separately:
```bash
python app.py
```

Quick integration check:
- Open `/api/health` and verify `ai.loaded = true`
- Verify `ai.source` points to the intended modules path

## Guides

- [Running Guide](RUNNING_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)

## Notes

- The app calls `/api/process` (JSON endpoint) for document processing.
- Session cookies are captured after login and sent with all subsequent requests.
- The audit logs screen requires the Flask server to return JSON from `/audit-logs`
  (you may need to add `Accept: application/json` handling or a separate `/api/audit-logs` endpoint).
