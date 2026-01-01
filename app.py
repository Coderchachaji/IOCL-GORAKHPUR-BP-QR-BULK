from flask import Flask, render_template, send_from_directory, jsonify, request
import os
import json


app = Flask(__name__)

# Define base directories
BASE_DIR = os.path.join(os.getcwd(), "reports")
ENGLISH_DIR = os.path.join(BASE_DIR, "JRM_ENGLISH")
GDRIVE_LINKS_FILE = os.path.join(BASE_DIR, "gdrive_links.json")

# Create directories if they don't exist
os.makedirs(ENGLISH_DIR, exist_ok=True)


def load_gdrive_links():
    """Load Google Drive links from JSON file"""
    try:
        if os.path.exists(GDRIVE_LINKS_FILE):
            with open(GDRIVE_LINKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Warning: {GDRIVE_LINKS_FILE} not found")
            return {}
    except Exception as e:
        print(f"Error loading Google Drive links: {e}")
        return {}


@app.route("/")
def home():
    """Home page with file selection dropdown"""
    try:
        # Get all PDF files from English directory
        if os.path.exists(ENGLISH_DIR):
            all_files = os.listdir(ENGLISH_DIR)
            pdf_files = [f for f in all_files if f.endswith(".pdf")]
            files = sorted(pdf_files, key=str.lower)
        else:
            files = []
            print(f"Warning: Directory {ENGLISH_DIR} does not exist")
        
        print(f"Found {len(files)} PDF files in {ENGLISH_DIR}")
        
    except Exception as e:
        print(f"Error reading directory: {e}")
        files = []
    
    return render_template("home.html", files=files)


@app.route("/view/<filename>")
def view(filename):
    """View page showing both Hindi and English PDFs"""
    # Check if English file exists
    english_path = os.path.join(ENGLISH_DIR, filename)
    english_exists = os.path.exists(english_path)
    
    # Check if Hindi file exists in Google Drive links
    gdrive_links = load_gdrive_links()
    hindi_data = gdrive_links.get(filename, {})
    hindi_exists = hindi_data.get('exists', False)
    
    if not hindi_exists and not english_exists:
        return f"Error: File {filename} not found", 404
    
    return render_template(
        "view.html",
        filename=filename,
        hindi_exists=hindi_exists,
        english_exists=english_exists,
        hindi_preview_url=hindi_data.get('preview_url', ''),
        hindi_download_url=hindi_data.get('download_url', '')
    )


@app.route("/pdf/english/<filename>")
def pdf_english(filename):
    """Serve English PDF file"""
    try:
        return send_from_directory(ENGLISH_DIR, filename)
    except Exception as e:
        return f"Error loading English PDF: {e}", 404


@app.route("/api/search")
def search_files():
    """API endpoint for searching files"""
    query = request.args.get('q', '').lower()
    
    try:
        if os.path.exists(ENGLISH_DIR):
            all_files = os.listdir(ENGLISH_DIR)
            pdf_files = [f for f in all_files if f.endswith(".pdf")]
            
            if query:
                # Filter files based on search query
                filtered_files = [f for f in pdf_files if query in f.lower()]
            else:
                filtered_files = pdf_files
            
            return jsonify({
                'success': True,
                'files': sorted(filtered_files, key=str.lower)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Directory not found',
                'files': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'files': []
        })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)