# models_loader.py
from transformers import pipeline
import torch

device = 0 if torch.cuda.is_available() else "cpu"
print(f"Using device: {'GPU' if device == 0 else 'CPU'}")

# Video Model (SigLIP based image classification)
video_model = pipeline(
    "image-classification",
    model="prithivMLmods/deepfake-detector-model-v1",
    device=device
)

# Audio Model (Wav2Vec2 fine-tuned for deepfake audio)
audio_model = pipeline(
    "audio-classification",
    model="Hemgg/Deepfake-audio-detection",
    device=device
)

print("Models loaded successfully!")