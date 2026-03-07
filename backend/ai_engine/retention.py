import os
import torch
import pickle
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

_scroll_model_path = os.path.join(_BASE_DIR, 'models', 'scroll_stop_model.pkl')
_scroll_model = None

if os.path.exists(_scroll_model_path):
    try:
        with open(_scroll_model_path, 'rb') as f:
            _scroll_payload = pickle.load(f)
            _scroll_model = _scroll_payload['model']
        print(f"[scroll_stop] Loaded trained GradientBoosting model from {_scroll_model_path}")
    except Exception as e:
        print(f"[scroll_stop] Failed to load model ({e}). Using heuristic fallback.")
else:
    print("[scroll_stop] No model found. Using heuristic fallback.")

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

def predict_scroll_stop(text, retention_data=None):
    """
    Predict scroll stop probability.
    If retention_data (heatmap) is provided and model is loaded, uses the trained ML model.
    Otherwise, falls back to the original text-based heuristic.
    """
    hook = text[:150].lower()
    hook_exclamation = 1.0 if '!' in hook else 0.0

    # Try ML model first
    if _scroll_model is not None and retention_data is not None:
        try:
            segments = retention_data.get("segments", [])
            if len(segments) == 4:
                risk_0_15 = segments[0].get("drop_off_risk", 0.5)
                risk_15_30 = segments[1].get("drop_off_risk", 0.5)
                risk_30_60 = segments[2].get("drop_off_risk", 0.5)
                risk_60_90 = segments[3].get("drop_off_risk", 0.5)
                engagement_score = retention_data.get("engagement_score", 0.5)
                word_count = len(text.split())
                
                features = [[
                    risk_0_15, risk_15_30, risk_30_60, risk_60_90,
                    engagement_score, word_count, hook_exclamation
                ]]
                
                pred = _scroll_model.predict(features)[0]
                return round(float(max(0.0, min(100.0, pred))), 2)
        except Exception as e:
            print(f"[scroll_stop] ML prediction failed: {e}. Falling back to heuristic.")
            
    # Fallback to heuristic
    score = 50
    triggers = ['suddenly', '!', 'blood', 'kiss', 'money', 'secret', 'die', 'kill']
    for t in triggers:
        if t in hook:
            score += 15
            
    return round(min(score, 100),2)
