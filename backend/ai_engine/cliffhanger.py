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
import pickle

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# ── Try to load the trained model ──────────────────────────────────────────────
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'cliffhanger_model.pkl')

_clf_payload = None
if os.path.exists(_MODEL_PATH):
    try:
        with open(_MODEL_PATH, 'rb') as _f:
            _clf_payload = pickle.load(_f)
        print(f"[cliffhanger] Loaded trained model (CV MAE: {_clf_payload.get('cv_mae', '?'):.1f}/100)")
    except Exception as _e:
        print(f"[cliffhanger] Could not load trained model ({_e}). Using heuristic fallback.")
        _clf_payload = None
else:
    print("[cliffhanger] No trained model found. Using heuristic scoring.")
    print("              To train, run: python training/train_cliffhanger_classifier.py")


# ── Feature extractor (mirrors train_cliffhanger_classifier.py) ───────────────
def _extract_features(text: str, emotion_arc: list) -> list:
    """Extract numeric features from a screenplay ending for the trained model."""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 2]

    vs            = _analyzer.polarity_scores(text)
    vader_compound = vs['compound']
    vader_neg      = vs['neg']
    vader_pos      = vs['pos']

    first_sent = _analyzer.polarity_scores(sentences[0])['compound'] if sentences else 0.0
    last_sent  = _analyzer.polarity_scores(sentences[-1])['compound'] if sentences else 0.0
    sentiment_shift = abs(last_sent - first_sent)

    question_count = sum(1 for s in sentences[-4:] if '?' in s)

    stakes_keywords = _clf_payload['stakes_keywords'] if _clf_payload else [
        'die', 'kill', 'secret', 'never', 'truth', 'trap', 'bomb', 'love',
        'run', 'escape', 'terrified', 'hunt', 'dead', 'murder', 'blood',
        'confess', 'betray', 'reveal', 'expose', 'destroy', 'gone', 'missing'
    ]
    tail         = text.lower()[-200:]
    stakes_score = sum(1 for kw in stakes_keywords if kw in tail)

    text_length    = len(text)
    excl_count     = text.count('!')
    short_sentences = sum(1 for s in sentences if len(s.split()) < 6)

    return [[
        vader_compound, vader_neg, vader_pos,
        sentiment_shift,
        question_count, stakes_score,
        text_length, excl_count, short_sentences
    ]]


# ── Original heuristic (fallback) ─────────────────────────────────────────────
def _heuristic_score(text: str, emotion_arc: list) -> float:
    """Original rule-based cliffhanger scorer."""
    if not emotion_arc:
        return 0.0

    scores       = [x['score'] for x in emotion_arc]
    avg_sentiment = sum(scores) / len(scores)
    end_sentiment = sum(scores[-3:]) / 3 if len(scores) >= 3 else scores[-1]

    sentiment_shift = abs(end_sentiment - avg_sentiment) * 100

    last_sentences  = text.split('.')[-4:]
    questions       = sum(1 for s in last_sentences if '?' in s)
    info_gap_score  = min(questions * 25, 50)

    stakes_keywords = ['die', 'kill', 'secret', 'never', 'truth', 'trap', 'bomb',
                       'love', 'run', 'escape', 'terrified', 'hunt']
    stakes_score = sum(15 for w in stakes_keywords if w in text.lower()[-200:])

    total = (0.3 * sentiment_shift) + (0.4 * info_gap_score) + (0.3 * stakes_score)
    return min(round(total, 1), 100)


# ── Public API ────────────────────────────────────────────────────────────────
def calculate_score(text: str, emotion_arc: list) -> float:
    """
    Score a screenplay ending for cliffhanger potential (0–100).

    Uses the trained GradientBoostingRegressor if available,
    otherwise falls back to the original rule-based heuristic.
    """
    if _clf_payload is not None:
        try:
            features = _extract_features(text, emotion_arc)
            raw      = _clf_payload['model'].predict(features)[0]
            return float(min(max(round(raw, 1), 0.0), 100.0))
        except Exception as e:
            print(f"[cliffhanger] Model prediction failed ({e}). Using heuristic fallback.")

    return _heuristic_score(text, emotion_arc)

