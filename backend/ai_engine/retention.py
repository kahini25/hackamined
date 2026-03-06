import os
import torch
import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from . import emotion, cliffhanger, tension

warnings.filterwarnings("ignore")

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'retention_transformer')

_tokenizer = None
_model = None
_device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

if os.path.exists(_MODEL_PATH):
    try:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_PATH)
        _model.to(_device)
        _model.eval()
        print(f"[retention] Loaded fine-tuned Proairetic transformer model from {_MODEL_PATH}")
    except Exception as e:
        print(f"[retention] Failed to load transformer model ({e}). Using heuristic fallback.")
        _model = None
else:
    print("[retention] No transformer model found. Using heuristic fallback.")

def predict_drop_off(text):
    """
    Predict drop-off risk by dividing the script into segments.
    Uses Proairetic code (sequence/tension) from the transformer if available,
    otherwise falls back to heuristics based on emotion and tension.
    """
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    total_sentences = max(len(sentences), 1)
    
    quad_size = max(total_sentences // 4, 1)
    
    segments_data = [
        {"time_range": "0-15s", "start": 0, "end": quad_size},
        {"time_range": "15-30s", "start": quad_size, "end": quad_size * 2},
        {"time_range": "30-60s", "start": quad_size * 2, "end": quad_size * 3},
        {"time_range": "60-90s", "start": quad_size * 3, "end": total_sentences}
    ]

    segments_output = []
    
    overall_risk = 0.0
    valid_segments = 0

    for seg in segments_data:
        segment_sentences = sentences[seg['start']:seg['end']]
        segment_text = ". ".join(segment_sentences) + "." if segment_sentences else ""
        
        if len(segment_text.strip()) < 10:
            segments_output.append({
                "time_range": seg["time_range"],
                "drop_off_risk": 0.50
            })
            continue

        local_emotion_arc = emotion.analyze_emotional_arc(segment_text)
        local_tension = tension.build_graph(segment_text)
        
        drop_off_risk = 0.50

        # Use AI model if available for true Proairetic analysis
        if _model is not None and _tokenizer is not None:
            try:
                inputs = _tokenizer(segment_text[:512], return_tensors="pt", truncation=True, padding=True, max_length=512).to(_device)
                with torch.no_grad():
                    outputs = _model(**inputs)
                    # output is 0-1 scale normalized to 0-100 risk
                    raw_risk = float(outputs.logits.item())
                    drop_off_risk = max(0.0, min(1.0, raw_risk))
            except Exception as e:
                # Fallback to heuristic
                drop_off_risk = _heuristic_risk(segment_text, local_emotion_arc, local_tension)
        else:
            drop_off_risk = _heuristic_risk(segment_text, local_emotion_arc, local_tension)
            
        overall_risk += drop_off_risk
        valid_segments += 1
            
        segments_output.append({
            "time_range": seg["time_range"],
            "drop_off_risk": float(round(drop_off_risk, 2))
        })

    avg_overall_risk = float(overall_risk / valid_segments) if valid_segments > 0 else 0.50

    return {
        "segments": segments_output,
        "engagement_score": float(round(max(0.0, min(1.0, 1.0 - avg_overall_risk)), 2))
    }

def _heuristic_risk(segment_text, local_emotion_arc, local_tension):
    """Fallback heuristic for retention risk calculation."""
    hook_strength = predict_scroll_stop(segment_text) / 100.0
    
    local_scores = [abs(x['score']) for x in local_emotion_arc] if local_emotion_arc else [0]
    local_emotion_intensity = (sum(local_scores) / len(local_scores)) if local_scores else 0

    local_conflict_density = min(len(local_tension.get('interaction_graph', {}).get('edges', [])) * 0.20, 1.0)
    
    engagement_score = (
        0.4 * local_emotion_intensity +
        0.3 * local_conflict_density +
        0.3 * hook_strength
    )
    
    return max(0.0, min(1.0, 1.0 - engagement_score))

def predict_scroll_stop(text):
    """
    Original scroll stop logic preserved to act as hook strength.
    """
    hook = text[:150].lower()
    score = 50
    
    triggers = ['suddenly', '!', 'blood', 'kiss', 'money', 'secret', 'die', 'kill']
    for t in triggers:
        if t in hook:
            score += 15
            
    return min(score, 100)
