# deepfake_audio.py
USING_DUMMY = False

from models_loader import audio_model   # ← model import yahan
import os

def analyze_audio(filepath):
    filename = os.path.basename(filepath)
    
    try:
        result = audio_model(filepath)[0]   # top prediction
        
        # Model usually returns "fake" or "real"
        fake_score = result['score'] if result['label'].lower() in ['fake', 'spoof'] else 1 - result['score']
        fake_score = round(fake_score, 3)
        
        summary = "Likely Fake" if fake_score > 0.60 else "Likely Real" if fake_score < 0.35 else "Uncertain / Inconclusive"
        
        return {
            "status": "success",
            "mode": "real_model",
            "warning": None,
            "fake_score": fake_score,
            "confidence_percent": round(fake_score * 100, 1),
            "summary": summary,
            "scores_by_time": [],           # optional
            "emotion_drift": [],
            "model_used": "Hemgg/Deepfake-audio-detection",
            "file": filename
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}