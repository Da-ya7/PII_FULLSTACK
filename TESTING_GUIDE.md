# How to Test the PII Redaction System - Complete Guide

## Prerequisites Check

Before testing, make sure these are running:

1. **MySQL Server** → Should be running (check: Services → MySQL80)
2. **Tesseract OCR** → Installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Python packages** → All installed via `pip install -r requirements.txt`
4. **SpaCy model** → Downloaded via `python -m spacy download en_core_web_sm`

---

## Step 1: Start the App

```bash
cd D:\PII
python app.py
```

You should see:
```
SECURE PII FILE REDACTION SYSTEM
Database initialized successfully.
RAG Engine: FAISS + Embeddings
Server starting at http://127.0.0.1:5000
```

Open browser → **http://127.0.0.1:5000**

---

## Step 2: Test User Registration

1. Click **"Register here"** link
2. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `test123`
3. Click **Register**
4. You should see: **"Registration successful! Please login."**

### Edge Cases to Test:
- Try registering with same username → Should show "already exists" error
- Try empty fields → Should show validation error
- Try password less than 6 chars → Should show error

---

## Step 3: Test Login

1. Enter: `testuser` / `test123`
2. Click **Login**
3. You should land on the **Dashboard** page
4. You should see:
   - 4 AI status cards (OCR, Regex, NER, RAG)
   - Upload form
   - Empty processing history
   - AI Pipeline Architecture diagram

### Edge Cases:
- Wrong password → Should show "Invalid username or password"
- Empty fields → Should show error

---

## Step 4: Test Document Upload & PII Detection

### Test 4.1: Aadhaar Card
1. Select Document Type: **Aadhaar Card**
2. Click "Choose File" → Select `PII-DATASET/PII - dataset/aadhar card/aadhar1.jpg`
3. You should see image preview
4. Click **"Process & Redact PII"**
5. Wait for processing (5-15 seconds)
6. **Result page should show:**
   - Original vs Redacted image side-by-side
   - Extracted OCR text vs Redacted text
   - Table of detected PII with type, confidence, source, decision
   - Stats: Regex hits, NER hits, Hybrid confirmed

### Test 4.2: PAN Card
1. Go back to Dashboard
2. Select Document Type: **PAN Card**
3. Upload `PII-DATASET/PII - dataset/pan card/pan1.webp`
4. Check if PAN number (format: ABCDE1234F) is detected and redacted

### Test 4.3: Driving License
1. Upload `PII-DATASET/PII - dataset/driving license/dl2.jpg`
2. Select type: **Driving License**
3. Check if DL number, name, DOB are detected

### Test 4.4: Voter ID
1. Upload `PII-DATASET/PII - dataset/voter ID/voter1.jpg`
2. Select type: **Voter ID**
3. Check if Voter ID number (format: ABC1234567) is detected

---

## Step 5: Test Result Page Features

After processing any document, on the Result page:

1. **Image comparison** → Original (left) vs Redacted (right)
   - Redacted image should have black boxes over PII
2. **Text comparison** → Original OCR text vs Redacted text
   - Names should be masked: `Rajesh` → `R*****`
   - Aadhaar/PAN should be fully redacted: `████████████`
   - Phone should be partially masked: `XXXXXX3210`
   - Email should show domain only: `****@gmail.com`
3. **PII Detail Table columns:**
   - PII Type (AADHAAR, PAN, PERSON_NAME, etc.)
   - Detected Value
   - Source (REGEX / NER / HYBRID)
   - Confidence bar (percentage)
   - Decision (REDACT / MASK / KEEP)
   - Severity (CRITICAL / HIGH / MEDIUM / LOW)
   - Regulation (Aadhaar Act, DPDP Act, etc.)
4. **Download button** → Should download the redacted image

---

## Step 6: Test Download

1. On the Result page, click **"Download Redacted"**
2. A `.jpg` file should download
3. Open it — PII regions should be blacked out
4. Also test download from Dashboard history table (small download icon)

---

## Step 7: Test Audit Logs

1. Click **"Audit Logs"** in the navbar
2. You should see a table with:
   - Timestamp
   - Filename
   - Document Type
   - PII Count
   - PII Details (detected types & decisions)
   - Processing Time
   - Download button
3. Summary cards at the bottom:
   - Total Documents Processed
   - Total PII Detected
   - Documents Secured

---

## Step 8: Test Logout

1. Click **Logout** in navbar
2. Should redirect to Login page
3. Try accessing `http://127.0.0.1:5000/dashboard` → Should redirect to Login

---

## Step 9: Test All 25 Dataset Images

Upload each image and note results:

| # | File | Type | PII Found? | Redacted? | Notes |
|---|------|------|-----------|-----------|-------|
| 1 | aadhar1.jpg | Aadhaar | | | |
| 2 | aadhar2.jpg | Aadhaar | | | |
| 3 | aadhar3.jpeg | Aadhaar | | | |
| 4 | aadhar4.jpg | Aadhaar | | | |
| 5 | aadhar5.jpg | Aadhaar | | | |
| 6 | aadhar6.jpg | Aadhaar | | | |
| 7 | aadhar7.webp | Aadhaar | | | |
| 8 | dl1.webp | DL | | | |
| 9 | dl2.jpg | DL | | | |
| 10 | dl3.jpg | DL | | | |
| 11 | dl4.jpg | DL | | | |
| 12 | dl5.jpg | DL | | | |
| 13 | dl6.jpg | DL | | | |
| 14 | pan1.webp | PAN | | | |
| 15 | pan2.jpg | PAN | | | |
| 16 | pan3.jpg | PAN | | | |
| 17 | pan4.webp | PAN | | | |
| 18 | pan5.jpg | PAN | | | |
| 19 | pan6.jpg | PAN | | | |
| 20 | voter1.jpg | Voter | | | |
| 21 | voter2.webp | Voter | | | |
| 22 | voter3.jpg | Voter | | | |
| 23 | voter4.jpg | Voter | | | |
| 24 | voter5.png | Voter | | | |
| 25 | voter6.webp | Voter | | | |

---

## Step 10: Test Individual AI Modules (Terminal)

### Test OCR Engine Only
```bash
cd D:\PII
python -c "from modules.ocr_engine import extract_text; print(extract_text(r'PII-DATASET/PII - dataset/aadhar card/aadhar1.jpg'))"
```

### Test Regex Detector Only
```bash
python -c "
from modules.regex_detector import detect_pii_regex
text = 'Aadhaar: 4832 7612 9045, PAN: ABCPK1234F, Phone: 9876543210'
for d in detect_pii_regex(text):
    print(f'{d[\"type\"]}: {d[\"value\"]}')
"
```

### Test NER Detector Only
```bash
python -c "
from modules.ner_detector import detect_pii_ner
text = 'Rajesh Kumar lives in Chennai and works at TCS'
for d in detect_pii_ner(text):
    print(f'{d[\"type\"]}: {d[\"value\"]}')
"
```

### Test Hybrid Engine
```bash
python -c "
from modules.hybrid_engine import detect_pii_hybrid
text = 'Name: Rajesh Kumar, Aadhaar: 4832 7612 9045, Phone: 9876543210, Chennai'
result = detect_pii_hybrid(text)
for d in result['detections']:
    print(f'{d[\"type\"]}: {d[\"value\"]} (source={d[\"source\"]})')
print(f'Stats: {result[\"stats\"]}')
"
```

### Test RAG Decision Engine
```bash
python -c "
from modules.rag_decision_engine import get_rag_engine
engine = get_rag_engine()
print(engine.get_engine_status())
decision = engine.get_decision({'type': 'AADHAAR', 'value': '4832 7612 9045'})
print(f'Aadhaar decision: {decision[\"action\"]} ({decision[\"regulation\"]})')
"
```

### Test Full Pipeline
```bash
python test_pipeline.py
```

---

## Step 11: Test Error Handling

1. **Upload non-image file** (e.g., .txt, .pdf) → Should show "Invalid file type" error
2. **Upload very large file** (>16MB) → Should be rejected
3. **Access pages without login** → Should redirect to login
4. **Upload with no file selected** → Should show error

---

## Step 12: Verify MySQL Database

```bash
# Open MySQL and check data
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p"iambatman@12" -e "USE pii_redaction_db; SELECT * FROM users; SELECT id, filename, document_type, pii_count, processing_time, created_at FROM audit_logs;"
```

You should see:
- Your registered user in `users` table
- All processed documents in `audit_logs` table

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Tesseract not found" | Check path in `config.py` → `TESSERACT_CMD` |
| "MySQL connection refused" | Make sure MySQL80 service is running |
| "SpaCy model not found" | Run: `python -m spacy download en_core_web_sm` |
| "No PII detected" | Image quality may be low; OCR couldn't read it clearly |
| "Module not found" | Run: `pip install -r requirements.txt` |
| WebP images not loading | Pillow handles this; make sure Pillow is installed |
| Black image output | OCR bounding box coordinates may not match; expected for some images |

---

## What to Show in Viva Demo

1. **Start app** → Show the dashboard with AI status cards
2. **Upload an Aadhaar card** → Show real-time processing
3. **Show Result page** → Original vs Redacted comparison
4. **Show PII detection table** → Types, sources, confidence, decisions
5. **Show Audit Logs** → All processed documents logged
6. **Explain AI pipeline** → OCR → Regex → NER → Hybrid → RAG → Redaction
7. **Show RAG engine** → FAISS vector DB with 13 privacy policies
8. **Download redacted document** → PII blacked out
