"""
cliffhanger.py
─────────────────────────────────────────────────────────────────────────────
Scores a screenplay ending for its cliffhanger / tension potential (0–100).

Priority order:
  1. Trained GradientBoostingRegressor from `models/cliffhanger_model.pkl`
     (created by running `training/train_cliffhanger_classifier.py`)
  2. Original rule-based heuristic (used if the model hasn't been trained yet)
"""

import os
import torch
import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification

warnings.filterwarnings("ignore")

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'cliffhanger_transformer')

_tokenizer = None
_model = None
_device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

if os.path.exists(_MODEL_PATH):
    try:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_PATH)
        _model.to(_device)
        _model.eval()
        print(f"[cliffhanger] Loaded fine-tuned Hermeneutic transformer model from {_MODEL_PATH}")
    except Exception as e:
        print(f"[cliffhanger] Failed to load transformer model ({e}). Using fallback.")
        _model = None
else:
    print("[cliffhanger] No transformer model found. Using heuristic fallback.")


def _heuristic_score(text: str) -> float:
    """Fallback heuristic if model is missing."""
    text = text.lower()
    stakes = ['die', 'kill', 'secret', 'never', 'truth', 'trap', 'bomb', 'reveal', 'shock']
    score = 20.0
    if '?' in text[-100:]: score += 30
    score += sum(15 for w in stakes if w in text[-200:])
    return min(score, 100.0)


def calculate_score(text: str, emotion_arc: list = None) -> float:
    """
    Score a screenplay ending for cliffhanger/Hermeneutic mystery potential (0-100).
    """
    if _model is not None and _tokenizer is not None and len(text.strip()) > 5:
        try:
            # We take the last chunk of text for cliffhanger evaluation
            tail_text = text[-500:]
            inputs = _tokenizer(tail_text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(_device)
            with torch.no_grad():
                outputs = _model(**inputs)
                # Output represents score in 0-1 range scaled to 100
                score = outputs.logits.item() * 100.0
                return float(min(max(round(score, 1), 0.0), 100.0))
        except Exception as e:
            print(f"[cliffhanger] Model prediction failed: {e}. Using fallback.")
            
    return _heuristic_score(text)

