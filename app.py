"""
Secure PII File Redaction System - Flask Web Application
Main application with routes for:
- User authentication (register, login, logout)
- Document upload and processing
- PII detection and redaction pipeline
- Audit log viewing
- Result comparison (original vs redacted)
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file, jsonify
)
from werkzeug.utils import secure_filename
import pymysql
import bcrypt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.ocr_engine import get_full_text_and_boxes
from modules.hybrid_engine import detect_pii_hybrid
from modules.rag_decision_engine import decide_redaction, get_rag_engine
from modules.redaction_engine import process_redaction

# ============================================================
# APP INITIALIZATION
# ============================================================

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Create directories
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.REDACTED_FOLDER, exist_ok=True)


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_db():
    """Get MySQL database connection."""
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    """Initialize database tables if they don't exist."""
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        cursor.execute(f"USE {Config.DB_NAME}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_path VARCHAR(500),
                redacted_path VARCHAR(500),
                document_type VARCHAR(50),
                pii_found TEXT,
                pii_count INT DEFAULT 0,
                action_taken VARCHAR(50) DEFAULT 'REDACTED',
                processing_time FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Make sure MySQL is running and credentials are correct in config.py")


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/')
def index():
    """Landing page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
            if cursor.fetchone():
                flash('Username or email already exists.', 'error')
                conn.close()
                return render_template('register.html')
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter username and password.', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


# ============================================================
# MAIN APPLICATION ROUTES
# ============================================================

@app.route('/dashboard')
def dashboard():
    """Main dashboard with upload form and history."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get recent processing history
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM audit_logs WHERE user_id=%s ORDER BY created_at DESC LIMIT 10",
            (session['user_id'],)
        )
        history = cursor.fetchall()
        conn.close()
    except Exception:
        history = []
    
    # Get RAG engine status
    try:
        rag_status = get_rag_engine().get_engine_status()
    except Exception:
        rag_status = {'rag_enabled': False}
    
    return render_template('dashboard.html', history=history, rag_status=rag_status)


@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and run full AI pipeline."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('dashboard'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed: JPG, JPEG, PNG, WEBP, BMP, TIFF', 'error')
        return redirect(url_for('dashboard'))
    
    doc_type = request.form.get('doc_type', 'unknown')
    
    try:
        start_time = time.time()
        
        # Save uploaded file
        unique_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(upload_path)
        
        # ============================
        # AI PIPELINE EXECUTION
        # ============================
        
        # Step 1: OCR - Extract text and bounding boxes
        ocr_result = get_full_text_and_boxes(upload_path)
        extracted_text = ocr_result['text']
        ocr_words = ocr_result['words']
        original_image = ocr_result['original_image']
        
        # Step 2 & 3: Hybrid Detection (Regex + NER)
        hybrid_result = detect_pii_hybrid(extracted_text)
        detections = hybrid_result['detections']
        stats = hybrid_result['stats']
        
        # Step 4: RAG Decision Engine
        enriched_detections = decide_redaction(detections)
        
        # Step 5: Redaction Engine
        redacted_name = f"redacted_{unique_name}"
        # Ensure output is jpg (in case input was webp)
        redacted_name = os.path.splitext(redacted_name)[0] + '.jpg'
        redacted_path = os.path.join(Config.REDACTED_FOLDER, redacted_name)
        
        redaction_result = process_redaction(
            extracted_text, original_image, ocr_words,
            enriched_detections, redacted_path
        )
        
        processing_time = round(time.time() - start_time, 2)
        
        # ============================
        # SAVE AUDIT LOG
        # ============================
        
        pii_summary = json.dumps([{
            'type': d['type'],
            'value': d['value'][:20] + '...' if len(d['value']) > 20 else d['value'],
            'decision': d.get('decision', 'REDACTED'),
            'confidence': d.get('confidence', 0),
            'source': d.get('source', 'UNKNOWN')
        } for d in enriched_detections])
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_logs 
               (user_id, filename, original_path, redacted_path, document_type, 
                pii_found, pii_count, action_taken, processing_time)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (session['user_id'], file.filename, unique_name, redacted_name,
             doc_type, pii_summary, len(enriched_detections), 'REDACTED', processing_time)
        )
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Store result in session for display
        session['last_result'] = {
            'log_id': log_id,
            'filename': file.filename,
            'doc_type': doc_type,
            'original_name': unique_name,
            'redacted_name': redacted_name,
            'extracted_text': extracted_text[:2000],
            'redacted_text': redaction_result['redacted_text'][:2000],
            'detections': [{
                'type': d['type'],
                'value': d['value'],
                'decision': d.get('decision', 'REDACTED'),
                'confidence': d.get('confidence', 0),
                'source': d.get('source', 'UNKNOWN'),
                'severity': d.get('severity', 'UNKNOWN'),
                'regulation': d.get('regulation', 'Unknown')
            } for d in enriched_detections],
            'stats': stats,
            'summary': redaction_result['summary'],
            'processing_time': processing_time
        }
        
        return redirect(url_for('result'))
    
    except Exception as e:
        flash(f'Processing error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('dashboard'))


@app.route('/result')
def result():
    """Display processing results."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    result_data = session.get('last_result')
    if not result_data:
        flash('No results to display.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('result.html', result=result_data)


@app.route('/download/<filename>')
def download(filename):
    """Download redacted file."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file_path = os.path.join(Config.REDACTED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    
    flash('File not found.', 'error')
    return redirect(url_for('dashboard'))


@app.route('/audit-logs')
def audit_logs():
    """View all audit logs."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT al.*, u.username 
               FROM audit_logs al 
               JOIN users u ON al.user_id = u.id 
               WHERE al.user_id = %s
               ORDER BY al.created_at DESC""",
            (session['user_id'],)
        )
        logs = cursor.fetchall()
        conn.close()
        
        # Parse PII JSON for display
        for log in logs:
            try:
                log['pii_list'] = json.loads(log['pii_found']) if log['pii_found'] else []
            except (json.JSONDecodeError, TypeError):
                log['pii_list'] = []
    except Exception:
        logs = []
    
    return render_template('audit_logs.html', logs=logs)


# ============================================================
# API ENDPOINT (Optional - for programmatic access)
# ============================================================

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for processing files programmatically."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    # Process same as upload but return JSON
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        start_time = time.time()
        
        unique_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(upload_path)
        
        ocr_result = get_full_text_and_boxes(upload_path)
        hybrid_result = detect_pii_hybrid(ocr_result['text'])
        enriched = decide_redaction(hybrid_result['detections'])
        
        redacted_name = f"redacted_{os.path.splitext(unique_name)[0]}.jpg"
        redacted_path = os.path.join(Config.REDACTED_FOLDER, redacted_name)
        
        redaction_result = process_redaction(
            ocr_result['text'], ocr_result['original_image'],
            ocr_result['words'], enriched, redacted_path
        )
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'pii_count': len(enriched),
            'detections': [{
                'type': d['type'], 'value': d['value'],
                'decision': d.get('decision'), 'confidence': d.get('confidence')
            } for d in enriched],
            'stats': hybrid_result['stats'],
            'redacted_file': redacted_name,
            'processing_time': processing_time
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  SECURE PII FILE REDACTION SYSTEM")
    print("  AI-Powered Document Privacy Protection")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Initialize RAG engine (preload)
    print("\nInitializing AI engines...")
    try:
        rag = get_rag_engine()
        print(f"RAG Engine: {'FAISS + Embeddings' if rag.use_rag else 'Fallback Mode'}")
    except Exception as e:
        print(f"RAG Engine: Fallback Mode ({e})")
    
    print(f"\nServer starting at http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
