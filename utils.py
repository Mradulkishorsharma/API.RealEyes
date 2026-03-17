# ─── UTILITY FUNCTIONS ───
import os

def allowed_video(filename):
    """Check if file is a supported video format (case insensitive)"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in {".mp4", ".mov", ".avi"}

def allowed_audio(filename):
    """Check if file is a supported audio format (case insensitive)"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in {".mp3", ".wav"}

def format_filepath(upload_folder, filename):
    """Securely join upload folder with filename"""
    from werkzeug.utils import secure_filename
    return os.path.join(upload_folder, secure_filename(filename))