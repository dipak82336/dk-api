from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

# Flask એપ્લિકેશન બનાવો
app = Flask(__name__)
CORS(app) # કોઈપણ ઓરિજિનથી આવતી રિક્વેસ્ટને મંજૂરી આપો

# અપલોડ થયેલી ઈમેજોને સ્ટોર કરવા માટે 'uploads' નામની ડિરેક્ટરી બનાવો
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ટેક્સ્ટ ડેટાને સ્ટોર કરવા માટે એક વેરિયેબલ
shared_text = "Hello from a server running on Render.com!"

# --- ટેક્સ્ટ માટેના Routes ---
@app.route('/get_text', methods=['GET'])
def get_text():
    """ક્લાયન્ટને હાલનો ટેક્સ્ટ JSON ફોર્મેટમાં મોકલે છે."""
    return jsonify({"text": shared_text})

@app.route('/send_text', methods=['POST'])
def send_text():
    """ક્લાયન્ટ પાસેથી નવો ટેક્સ્ટ મેળવીને તેને અપડેટ કરે છે."""
    global shared_text
    data = request.get_json()
    if data and 'text' in data:
        shared_text = data['text']
        return jsonify({"message": "Text updated successfully!", "new_text": shared_text}), 200
    return jsonify({"error": "Invalid data."}), 400

# --- ઈમેજ માટેના Routes ---
@app.route('/upload_image', methods=['POST'])
def upload_image():
    """ક્લાયન્ટ પાસેથી ઈમેજ ફાઈલ અપલોડ કરાવે છે."""
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file selected"}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({"message": "Image uploaded successfully!", "filename": filename}), 200

@app.route('/get_image/<filename>')
def get_image(filename):
    """સર્વર પરથી ચોક્કસ ઈમેજ ક્લાયન્ટને મોકલે છે."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ગેલેરી માટેનો Route ---
@app.route('/list_images', methods=['GET'])
def list_images():
    """'uploads' ફોલ્ડરમાં રહેલી બધી ઈમેજોની યાદી મોકલે છે."""
    try:
        image_files = os.listdir(app.config['UPLOAD_FOLDER'])
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        images = [f for f in image_files if os.path.splitext(f)[1].lower() in allowed_extensions]
        # નવી અપલોડ થયેલી ઈમેજ પહેલા દેખાય તે માટે ફેરફારના સમય મુજબ સોર્ટ કરો
        images.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": f"Could not list images: {e}"}), 500

# --- મુખ્ય (Index) Route ---
@app.route("/")
def index():
    """એપ્લિકેશન ચાલી રહી છે તે ચકાસવા માટેનો મુખ્ય રૂટ."""
    return "<h1>Your Flask server is running on Render.com! (Gallery Edition)</h1>"
