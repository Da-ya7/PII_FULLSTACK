# Running Guide

This project has two parts:
- Flutter frontend in `D:\PII\PII`
- Flask backend in `D:\PII\PII`

## Prerequisites

- Python 3.10+
- Flutter SDK
- MySQL Server running locally
- Tesseract OCR installed on Windows

## Backend Setup

1. Open terminal 1.
2. Run:

```bash
cd /d D:\PII\PII
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Make sure database credentials in `.env` are correct.  
   (Fixed: this is `.env`, not `PII\.env`)
4. Start backend:

```bash
python app.py
```

Backend URL:
- `http://127.0.0.1:5000`

Health check:
- `http://127.0.0.1:5000/api/health`

## Frontend Setup (Web)

1. Open terminal 2.
2. Run:

```bash
cd /d D:\PII\PII
flutter clean
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:5000 --web-port=5080
```

Frontend URL:
- `http://localhost:5080`

## Recommended Run Order

1. Start MySQL.
2. Start backend and confirm `/api/health` is success.
3. Start Flutter frontend.
4. Open `http://localhost:5080`.

## Browser Notes / White Screen Fix

- Hard refresh: `Ctrl + Shift + R`
- If still blank:
  1. Stop Flutter (`Ctrl + C`)
  2. Run `flutter clean`
  3. Run frontend command again
  4. Open a fresh tab at `http://localhost:5080`
- On web, fingerprint login is disabled (mobile-only plugin).
- On web, upload/download uses browser-safe byte handling.
