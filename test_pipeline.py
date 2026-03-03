"""Quick test of the full AI pipeline"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.ocr_engine import extract_text
from modules.hybrid_engine import detect_pii_hybrid
from modules.rag_decision_engine import decide_redaction
from modules.redaction_engine import redact_text

# Step 1: OCR
print("=" * 50)
print("STEP 1: OCR Text Extraction")
print("=" * 50)
text = extract_text(r'PII-DATASET/PII - dataset/aadhar card/aadhar1.jpg')
print(text[:500])

# Step 2: Hybrid Detection (Regex + NER)
print("\n" + "=" * 50)
print("STEP 2: Hybrid PII Detection (Regex + NER)")
print("=" * 50)
result = detect_pii_hybrid(text)
for d in result['detections']:
    print(f"  [{d['type']}] '{d['value']}' (src={d['source']}, conf={d['confidence']})")
print(f"\nStats: {result['stats']}")

# Step 3: RAG Decision
print("\n" + "=" * 50)
print("STEP 3: RAG Policy Decision Engine")
print("=" * 50)
enriched = decide_redaction(result['detections'])
for d in enriched:
    print(f"  [{d['type']}] '{d['value']}' -> {d.get('decision', '?')} (severity={d.get('severity', '?')})")

# Step 4: Text Redaction
print("\n" + "=" * 50)
print("STEP 4: Redacted Text Output")
print("=" * 50)
redacted = redact_text(text, enriched)
print(redacted[:500])

print("\n\nFULL PIPELINE TEST COMPLETE!")
