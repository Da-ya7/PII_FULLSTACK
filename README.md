# PII Workspace

This workspace now uses a single active project:

- App root: `D:\PII\PII`
- Frontend: Flutter web/mobile in `D:\PII\PII\lib`
- Backend: Flask API in `D:\PII\PII\app.py`
- AI modules: `D:\PII\PII\modules`

## Start the project

From `D:\PII\PII`:

```bash
# Backend
python app.py

# Frontend (web)
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:5000 --web-port=5080
```

## Guides

- `D:\PII\PII\RUNNING_GUIDE.md`
- `D:\PII\PII\TESTING_GUIDE.md`
