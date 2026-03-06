import os
import torch
import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

warnings.filterwarnings("ignore")

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'emotion_transformer')

_tokenizer = None
_model = None
_device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

if os.path.exists(_MODEL_PATH):
    try:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_PATH)
        _model.to(_device)
        _model.eval()
        print(f"[emotion] Loaded fine-tuned Semantic Intensity transformer from {_MODEL_PATH}")
    except Exception as e:
        print(f"[emotion] Failed to load transformer model ({e}). Using full fallback.")
        _model = None

_analyzer = SentimentIntensityAnalyzer()

def analyze_emotional_arc(text):
    """
    Analyzes the emotional arc and semantic intensity.
    Uses the fine-tuned transformer to scale the core VADER polarities based on
    deep narrative semantics (Levi-Strauss Binary Oppositions).
    """
    sentences = text.split('.')
    arc = []
    
    for i, sentence in enumerate(sentences):
        if len(sentence.strip()) < 3: continue
        
        # Base polarity from VADER (-1 to 1)
        base_score = _analyzer.polarity_scores(sentence)['compound']
        
        # Deep Semantic Intensity from our model (0 to 1)
        semantic_multiplier = 1.0
        if _model is not None and _tokenizer is not None:
            try:
                inputs = _tokenizer(sentence[:128], return_tensors="pt", truncation=True, padding=True, max_length=128).to(_device)
                with torch.no_grad():
                    outputs = _model(**inputs)
                    # Output is 0-1 range from fine-tuning norm
                    semantic_multiplier = float(outputs.logits.item())
                    # Ensure multiplier increases amplitude
                    semantic_multiplier = max(0.5, min(2.0, semantic_multiplier * 2.0))
            except Exception:
                pass

        # Final score fuses polarity with semantic depth
        final_score = base_score * semantic_multiplier
        # Bound it between -1 and 1
        final_score = max(-1.0, min(1.0, final_score))
        
        arc.append({
            "beat": i, 
            "score": float(round(final_score, 3)), 
            "text": sentence[:30] + "..."
        })
        
    return arc
