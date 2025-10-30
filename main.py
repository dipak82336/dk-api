# ====================================================================
# ફાઈલનું નામ: main.py
# આ નવો કોડ તમારી GitHub રિપોઝીટરીની main.py ફાઈલમાં પેસ્ટ કરો
# ====================================================================

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json

# Flask એપ્લિકેશન બનાવો
app = Flask(__name__)

# CORS (Cross-Origin Resource Sharing) ને સક્ષમ કરો
CORS(app)

# Markdown ફાઇલોને સ્ટોર કરવા માટે 'markdown_files' નામની ડિરેક્ટરી બનાવો
# Render.com પર આ કામચલાઉ સ્ટોરેજ હશે.
MARKDOWN_FOLDER = 'markdown_files'
if not os.path.exists(MARKDOWN_FOLDER):
    os.makedirs(MARKDOWN_FOLDER)

# --- મુખ્ય રૂટ ---
@app.route("/", methods=['GET'])
def index():
    """એપ્લિકેશન ચાલી રહી છે તે ચકાસવા માટેનો મુખ્ય રૂટ."""
    return "<h1>Markdown API Server is Running!</h1>"

# --- Render.com ને Active રાખવા માટેનો રૂટ ---
@app.route("/a", methods=['GET'])
def keep_alive():
    """cron-job.org દ્વારા ઉપયોગમાં લેવા માટેનો સિમ્પલ રૂટ."""
    return "1"

# --- Markdown ફાઇલો માટેના Routes ---

@app.route('/files', methods=['GET'])
def list_files():
    """'markdown_files' ફોલ્ડરમાં રહેલી બધી .md ફાઇલોની યાદી મોકલે છે."""
    try:
        files = [f for f in os.listdir(MARKDOWN_FOLDER) if f.endswith('.md')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(MARKDOWN_FOLDER, x)), reverse=True)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    """ચોક્કસ Markdown ફાઈલનો કન્ટેન્ટ મોકલે છે."""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(MARKDOWN_FOLDER, safe_filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"filename": safe_filename, "content": content})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files', methods=['POST'])
def save_file():
    """નવી Markdown ફાઈલ બનાવે છે અથવા હાલની ફાઈલને અપડેટ કરે છે."""
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({"error": "Invalid data. 'filename' and 'content' are required."}), 400

    try:
        filename = data['filename']
        # ખાતરી કરો કે ફાઈલનેમ .md માં સમાપ્ત થાય છે
        if not filename.endswith('.md'):
            filename += '.md'
            
        safe_filename = secure_filename(filename)
        if not safe_filename:
            return jsonify({"error": "Invalid filename."}), 400

        filepath = os.path.join(MARKDOWN_FOLDER, safe_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        
        return jsonify({"message": f"File '{safe_filename}' saved successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """ચોક્કસ Markdown ફાઈલને ડિલીટ કરે છે."""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(MARKDOWN_FOLDER, safe_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"message": f"File '{safe_filename}' deleted successfully."})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# આ ભાગને અંતમાં રાખો
if __name__ == "__main__":
    # Render.com માટે પોર્ટ અને હોસ્ટને 0.0.0.0 પર સેટ કરો
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
