# deepfake_video.py (updated — returns per-frame data for frontend chart)

import cv2
from PIL import Image
import os
import random  # optional for variation if needed
from models_loader import video_model   # ← model import yahan

def analyze_video(filepath):
    filename = os.path.basename(filepath)
    
    try:
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise Exception("Could not open video file")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        duration_sec = total_frames / fps if fps > 0 else 0

        print(f"[INFO] Video: {filename} | Total frames: {total_frames} | FPS: {fps} | Duration: {duration_sec:.1f}s")

        fake_scores = []
        frame_data = []          # ← NEW: per-frame data for chart
        frames_analyzed = 0
        target_frames = min(40, max(5, int(duration_sec * 2)))  # 2 frames per second, max 40

        step = max(1, total_frames // target_frames)  # evenly spaced frames

        current_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame % step == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)

                result = video_model(pil_img)[0]
                label = result['label'].lower()
                score = result['score']

                # Model labels: "0": "fake", "1": "real" (from model card)
                if 'fake' in label or '0' in label:
                    fake_prob = score
                else:
                    fake_prob = 1 - score  # real score ko invert karo

                fake_scores.append(fake_prob)
                frames_analyzed += 1

                # ← NEW: timestamp in seconds for this frame
                timestamp_sec = round(current_frame / fps, 2) if fps > 0 else frames_analyzed

                frame_data.append({
                    "frame_num": frames_analyzed,
                    "timestamp_sec": timestamp_sec,
                    "fake_prob": round(fake_prob, 4),
                    "label": "fake" if fake_prob > 0.5 else "real"
                })

                print(f"[FRAME {frames_analyzed}] t={timestamp_sec:.1f}s | Label: {label} | Fake Prob: {fake_prob:.3f}")

            current_frame += 1

            if frames_analyzed >= target_frames:
                break

        cap.release()

        if not fake_scores:
            fake_score = 0.50
            summary = "Uncertain (no valid frames processed)"
        else:
            fake_score = round(sum(fake_scores) / len(fake_scores), 3)
            summary = "Likely Fake" if fake_score > 0.65 else "Likely Real" if fake_score < 0.35 else "Uncertain / Inconclusive"

        print(f"[FINAL RESULT] Fake Score: {fake_score} | Confidence: {fake_score*100:.1f}% | Frames: {frames_analyzed}/{current_frame}")

        return {
            "status": "success",
            "mode": "real_model",
            "fake_score": fake_score,
            "confidence_percent": round(fake_score * 100, 1),
            "summary": summary,
            "frames_analyzed": frames_analyzed,
            "model_used": "prithivMLmods/deepfake-detector-model-v1",
            "file": filename,
            "debug_frames": frames_analyzed,
            "frame_data": frame_data      # ← NEW: sent to frontend
        }

    except Exception as e:
        print(f"[ERROR] Analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fake_score": 0.0,
            "confidence_percent": 0.0,
            "summary": "Processing failed - try another video",
            "frames_analyzed": 0,
            "model_used": "error",
            "frame_data": []
        }