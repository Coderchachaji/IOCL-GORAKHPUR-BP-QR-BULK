from flask import Flask, render_template, send_from_directory, jsonify, request
import os
import json


app = Flask(__name__)

# Define base directories
BASE_DIR = os.path.join(os.getcwd(), "reports")
ENGLISH_DIR = os.path.join(BASE_DIR, "JRM_ENGLISH")
HINDI_GDRIVE_LINKS_FILE = os.path.join(BASE_DIR, "gdrive_links.json")
ENGLISH_GDRIVE_LINKS_FILE = os.path.join(BASE_DIR, "english_gdrive_links.json")

# Create directories if they don't exist
os.makedirs(ENGLISH_DIR, exist_ok=True)


def load_json_file(filepath):
    """Load JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Warning: {filepath} not found")
            return {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def load_gdrive_links():
    """Load Hindi Google Drive links from JSON file"""
    return load_json_file(HINDI_GDRIVE_LINKS_FILE)


def load_english_gdrive_links():
    """Load English Google Drive links from JSON file"""
    return load_json_file(ENGLISH_GDRIVE_LINKS_FILE)


@app.route("/")
def home():
    """Home page with file selection dropdown"""
    try:
        # Load English Google Drive links
        english_gdrive_links = load_english_gdrive_links()
        
        # Get files that have English links in the JSON
        files = []
        for filename, data in english_gdrive_links.items():
            if filename.endswith(".pdf") and data.get('exists', False):
                files.append(filename)
        
        files = sorted(files, key=str.lower)
        print(f"Found {len(files)} PDF files with English Google Drive links")
        
    except Exception as e:
        print(f"Error reading files: {e}")
        files = []
    
    return render_template("home.html", files=files)


@app.route("/view/<filename>")
def view(filename):
    """View page showing both Hindi and English PDFs"""
    # Load Google Drive links for both languages
    hindi_gdrive_links = load_gdrive_links()
    english_gdrive_links = load_english_gdrive_links()
    
    # Get Hindi data
    hindi_data = hindi_gdrive_links.get(filename, {})
    hindi_exists = hindi_data.get('exists', False)
    
    # Get English data
    english_data = english_gdrive_links.get(filename, {})
    english_exists = english_data.get('exists', False)
    
    if not hindi_exists and not english_exists:
        return f"Error: File {filename} not found", 404
    
    return render_template(
        "view.html",
        filename=filename,
        hindi_exists=hindi_exists,
        english_exists=english_exists,
        hindi_preview_url=hindi_data.get('preview_url', ''),
        hindi_download_url=hindi_data.get('download_url', ''),
        english_preview_url=english_data.get('preview_url', ''),
        english_download_url=english_data.get('download_url', '')
    )


@app.route("/pdf/english/<filename>")
def pdf_english(filename):
    """Serve English PDF file (fallback for local files)"""
    try:
        return send_from_directory(ENGLISH_DIR, filename)
    except Exception as e:
        return f"Error loading English PDF: {e}", 404


@app.route("/api/search")
def search_files():
    """API endpoint for searching files"""
    query = request.args.get('q', '').lower()
    
    try:
        english_gdrive_links = load_english_gdrive_links()
        
        # Get files that have English links
        all_files = []
        for filename, data in english_gdrive_links.items():
            if filename.endswith(".pdf") and data.get('exists', False):
                all_files.append(filename)
        
        if query:
            # Filter files based on search query
            filtered_files = [f for f in all_files if query in f.lower()]
        else:
            filtered_files = all_files
        
        return jsonify({
            'success': True,
            'files': sorted(filtered_files, key=str.lower)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'files': []
        })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
