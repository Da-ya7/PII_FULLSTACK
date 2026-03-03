<h1 align="center">Secure PII Redaction System</h1>

<p align="center">
  <b>AI-Powered Document Privacy Protection for Indian Identity Documents</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.1-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Tesseract-OCR-green?logo=google" alt="Tesseract">
  <img src="https://img.shields.io/badge/SpaCy-NER-09a3d5?logo=spacy" alt="SpaCy">
  <img src="https://img.shields.io/badge/FAISS-Vector%20DB-yellow" alt="FAISS">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen" alt="License">
</p>

---

## Overview

A full-stack web application that automatically detects and redacts **Personally Identifiable Information (PII)** from scanned Indian identity documents (Aadhaar, PAN, Driving License, Voter ID) using a multi-stage AI pipeline.

### Key Features

- **OCR Engine** — Tesseract-based text extraction with OpenCV image preprocessing  
- **Regex Detector** — Rule-based pattern matching for structured PII (Aadhaar, PAN, phone, email, etc.)  
- **NER Detector** — SpaCy NLP model for contextual entity recognition (names, locations, dates)  
- **Hybrid Engine** — Intelligent fusion of Regex + NER results with confidence boosting  
- **RAG Decision Engine** — Retrieval-Augmented Generation with FAISS vector search over privacy policies  
- **Redaction Engine** — Full redaction, partial masking, and visual redaction on images  
- **Audit Logging** — Complete processing history with per-user tracking  
- **User Authentication** — Secure registration/login with bcrypt password hashing  

---

## Architecture

```
┌──────────────┐
│  Upload UI   │  Flask Web Interface
└──────┬───────┘
       ▼
┌──────────────┐
│  OCR Engine  │  Tesseract + OpenCV preprocessing
└──────┬───────┘
       ▼
┌──────────────────────────────────┐
│       Hybrid Detection Engine    │
│  ┌────────────┐  ┌────────────┐ │
│  │   Regex    │  │  SpaCy NER │ │
│  │  Detector  │  │  Detector  │ │
│  └─────┬──────┘  └──────┬─────┘ │
│        └───────┬────────┘       │
│          Merge & Deduplicate     │
└──────────────┬───────────────────┘
               ▼
┌──────────────────────────┐
│   RAG Decision Engine    │
│  FAISS + SentenceTransf. │
│  Policy-Aware Decisions  │
└──────────────┬───────────┘
               ▼
┌──────────────────────────┐
│    Redaction Engine      │
│  Text + Image Redaction  │
└──────────────┬───────────┘
               ▼
┌──────────────────────────┐
│  Result View + Audit Log │
└──────────────────────────┘
```

---

## Tech Stack

| Layer          | Technology                                  |
|----------------|---------------------------------------------|
| Backend        | Python 3.10+, Flask                         |
| OCR            | Tesseract OCR, OpenCV, Pillow               |
| NLP / NER      | SpaCy (`en_core_web_sm`)                    |
| Embeddings     | Sentence-Transformers (`all-MiniLM-L6-v2`)  |
| Vector Search  | FAISS (Facebook AI Similarity Search)       |
| Database       | MySQL 8.0                                   |
| Auth           | bcrypt                                      |
| Frontend       | Jinja2, HTML/CSS                            |

---

## Prerequisites

| Requirement     | Version   | Link                                                |
|-----------------|-----------|-----------------------------------------------------|
| Python          | 3.10+     | https://www.python.org/downloads/                   |
| MySQL Server    | 8.0+      | https://dev.mysql.com/downloads/mysql/              |
| Tesseract OCR   | 5.x       | https://github.com/tesseract-ocr/tesseract          |

> **Windows:** Install Tesseract to `C:\Program Files\Tesseract-OCR\` (default path in config).

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/pii-redaction-system.git
cd pii-redaction-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your MySQL credentials and Tesseract path
```

### 5. Start MySQL and run the app

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000** — the database tables are created automatically on first run.

---

## Project Structure

```
pii-redaction-system/
├── app.py                    # Flask application & routes
├── config.py                 # Configuration (env-based)
├── requirements.txt          # Pinned Python dependencies
├── .env.example              # Environment variable template
│
├── modules/
│   ├── ocr_engine.py         # Tesseract OCR + OpenCV preprocessing
│   ├── regex_detector.py     # Rule-based PII pattern matching
│   ├── ner_detector.py       # SpaCy NER entity detection
│   ├── hybrid_engine.py      # Regex + NER fusion engine
│   ├── rag_decision_engine.py# RAG policy engine (FAISS + embeddings)
│   └── redaction_engine.py   # Text & image redaction
│
├── database/
│   └── schema.sql            # MySQL schema (auto-created by app)
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── result.html
│   └── audit_logs.html
│
├── static/
│   ├── css/style.css
│   ├── uploads/              # Uploaded documents (git-ignored)
│   └── redacted/             # Redacted output (git-ignored)
│
├── test_pipeline.py          # End-to-end pipeline test
├── TESTING_GUIDE.md          # Detailed manual testing guide
├── CONTRIBUTING.md           # Contribution guidelines
└── LICENSE                   # MIT License
```

---

## Supported Document Types

| Document          | PII Detected                                       |
|-------------------|-----------------------------------------------------|
| Aadhaar Card      | Aadhaar number, name, DOB, address, photo           |
| PAN Card          | PAN number, name, DOB, father's name                |
| Driving License   | DL number, name, DOB, address, validity dates       |
| Voter ID          | EPIC number, name, address, father's/husband's name |

---

## API Reference

### `POST /api/process`

Programmatic file processing endpoint (requires authenticated session).

**Request:** `multipart/form-data` with `file` field  
**Response:**

```json
{
  "status": "success",
  "filename": "aadhaar1.jpg",
  "pii_count": 5,
  "detections": [
    {
      "type": "AADHAAR",
      "value": "1234 5678 9012",
      "decision": "FULL_REDACT",
      "confidence": 1.0
    }
  ],
  "stats": {
    "regex_count": 3,
    "ner_count": 4,
    "hybrid_confirmed": 2
  },
  "redacted_file": "redacted_abc123.jpg",
  "processing_time": 4.52
}
```

---

## Testing

```bash
# Run the end-to-end pipeline test
python test_pipeline.py

# For detailed manual testing steps, see:
# TESTING_GUIDE.md
```

---

## Environment Variables

| Variable         | Description                        | Default                                        |
|------------------|------------------------------------|------------------------------------------------|
| `SECRET_KEY`     | Flask session secret               | *(random — set in production)*                 |
| `DB_HOST`        | MySQL host                         | `localhost`                                    |
| `DB_USER`        | MySQL username                     | `root`                                         |
| `DB_PASSWORD`    | MySQL password                     | *(required)*                                   |
| `DB_NAME`        | MySQL database name                | `pii_redaction_db`                             |
| `TESSERACT_CMD`  | Path to Tesseract binary           | `C:\Program Files\Tesseract-OCR\tesseract.exe` |

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with Python, Flask, Tesseract, SpaCy, FAISS &amp; Sentence-Transformers
</p>
