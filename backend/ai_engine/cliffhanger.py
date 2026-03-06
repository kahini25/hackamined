"""
cliffhanger.py
─────────────────────────────────────────────────────────────────────────────
Scores a screenplay ending for its cliffhanger / tension potential (0–100).

Priority order:
  1. Trained GradientBoostingRegressor from `models/cliffhanger_model.pkl`
     (created by running `training/train_cliffhanger_classifier.py`)
  2. Enhanced rule-based heuristic (used if the model hasn't been trained yet)
"""

import os
import pickle
import warnings

warnings.filterwarnings("ignore")

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'cliffhanger_model.pkl')

_pipeline = None

if os.path.exists(_MODEL_PATH):
    try:
        with open(_MODEL_PATH, 'rb') as f:
            payload = pickle.load(f)
        _pipeline = payload['model']
        print(f"[cliffhanger] Loaded trained GradientBoosting model from {_MODEL_PATH}")
        print(f"[cliffhanger] Model CV MAE: {payload.get('cv_mae', 'N/A'):.1f} / 100")
    except Exception as e:
        print(f"[cliffhanger] Failed to load model ({e}). Using heuristic fallback.")
        _pipeline = None
else:
    print("[cliffhanger] No trained model found. Using heuristic fallback.")
    print("[cliffhanger] Run: python training/train_cliffhanger_classifier.py")


# ── Feature extractor (must match the one used during training) ───────────────
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as _VADER
    _vader = _VADER()
except ImportError:
    _vader = None

_STAKES_KEYWORDS = [
    'die', 'kill', 'secret', 'never', 'truth', 'trap', 'bomb', 'love',
    'run', 'escape', 'terrified', 'hunt', 'dead', 'murder', 'blood',
    'confess', 'betray', 'reveal', 'expose', 'destroy', 'gone', 'missing'
]

def _extract_features(text: str) -> list:
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 2]

    if _vader:
        vs             = _vader.polarity_scores(text)
        vader_compound = vs['compound']
        vader_neg      = vs['neg']
        vader_pos      = vs['pos']
        first_score    = _vader.polarity_scores(sentences[0])['compound'] if sentences else 0.0
        last_score     = _vader.polarity_scores(sentences[-1])['compound'] if sentences else 0.0
    else:
        vader_compound = vader_neg = vader_pos = first_score = last_score = 0.0

    sentiment_shift = abs(last_score - first_score)
    last_sents      = sentences[-4:]
    question_count  = sum(1 for s in last_sents if '?' in s)
    tail            = text.lower()[-200:]
    stakes_score    = sum(1 for kw in _STAKES_KEYWORDS if kw in tail)
    text_length     = len(text)
    excl_count      = text.count('!')
    short_sentences = sum(1 for s in sentences if len(s.split()) < 6)

    return [
        vader_compound, vader_neg, vader_pos,
        sentiment_shift,
        question_count, stakes_score,
        text_length, excl_count, short_sentences
    ]


def _heuristic_score(text: str) -> float:
    """
    Stronger heuristic fallback when the trained model is unavailable.
    Uses VADER sentiment + a richer keyword set.
    """
    import re
    lower  = text.lower()
    tail   = lower[-300:]
    score  = 10.0  # base

    # Sentiment shift (big swing from calm→intense = high cliffhanger)
    if _vader:
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 2]
        if len(sentences) >= 2:
            first = _vader.polarity_scores(sentences[0])['compound']
            last  = _vader.polarity_scores(sentences[-1])['compound']
            shift = abs(last - first)
            score += shift * 35          # up to +35

        neg = _vader.polarity_scores(tail)['neg']
        score += neg * 30               # up to +30 for highly negative tail

    # Questions in last part (unresolved mystery)
    q_count = tail.count('?')
    score += min(q_count * 12, 24)      # up to +24

    # High-stakes keywords in tail
    stakes = [
        'die', 'dead', 'kill', 'murder', 'blood', 'bomb', 'trap',
        'secret', 'reveal', 'truth', 'betray', 'confess', 'expose',
        'run', 'escape', 'never', 'always', 'missing', 'gone', 'hunt',
        'terrified', 'danger', 'destroy', 'lies', 'lied', 'shock'
    ]
    hit = sum(1 for w in stakes if re.search(r'\b' + w + r'\b', tail))
    score += min(hit * 8, 32)           # up to +32

    # Short, punchy sentences at the end = urgency
    tail_sents = [s.strip() for s in tail.split('.') if s.strip()]
    short = sum(1 for s in tail_sents if 0 < len(s.split()) < 6)
    score += min(short * 4, 12)         # up to +12

    # Exclamation marks
    score += min(text.count('!') * 3, 9)

    return float(min(round(score, 1), 100.0))


def calculate_score(text: str, emotion_arc: list = None) -> float:
    """
    Score a screenplay ending for cliffhanger/Hermeneutic mystery potential (0–100).
    Uses the trained GradientBoosting model if available, otherwise the heuristic.
    """
    if not text or len(text.strip()) < 5:
        return 0.0

    # Use the last 500 chars so short episodes aren't penalized by preamble
    tail_text = text[-500:]

    if _pipeline is not None:
        try:
            import numpy as np
            features = _extract_features(tail_text)
            score = _pipeline.predict([features])[0]
            return float(min(max(round(score, 1), 0.0), 100.0))
        except Exception as e:
            print(f"[cliffhanger] Model prediction failed: {e}. Using heuristic.")

    return _heuristic_score(tail_text)
