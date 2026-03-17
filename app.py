# app.py (backend only – pure API, no render_template)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile

from deepfake_video import analyze_video
from deepfake_audio import analyze_audio
from utils import allowed_video, allowed_audio, format_filepath

app = Flask(__name__)

# Allow CORS from everywhere for now (change to specific domains in production)
CORS(app, resources={r"/*": {"origins": "*"}})

USING_DUMMY = False

# app.py ke top pe (CORS ke baad)
print("Loading real deepfake models... (first time slow)")
from models_loader import video_model, audio_model   # ← sirf yeh do
print("Models loaded successfully!")

# Use temporary directory → safe for Hugging Face / ephemeral filesystems
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix="realeyes_uploads_")

@app.route('/analyze/video', methods=['POST'])
def analyze_video_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_video(file.filename):
        return jsonify({"error": "Invalid video file type. Allowed: .mp4, .mov, .avi"}), 400

    filepath = format_filepath(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        result = analyze_video(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        # Always cleanup uploaded file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass  # silent fail – don't block response


@app.route('/analyze/audio', methods=['POST'])
def analyze_audio_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_audio(file.filename):
        return jsonify({"error": "Invalid audio file type. Allowed: .mp3, .wav"}), 400

    filepath = format_filepath(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        result = analyze_audio(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        # Always cleanup uploaded file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass  # silent fail


@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "version": "1.0",
        "mode": "dummy" if USING_DUMMY else "production"
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860, debug=True)