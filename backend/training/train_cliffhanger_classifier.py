"""
train_cliffhanger_classifier.py
────────────────────────────────
Trains a GradientBoostingRegressor on labeled screenplay endings.

Features extracted per sample:
  - vader_compound   : overall sentiment compound score (-1 to 1)
  - vader_neg        : negativity score (0-1)
  - vader_pos        : positivity score (0-1)
  - sentiment_shift  : abs difference between first and last sentence sentiment
  - question_count   : number of '?' in the last 4 sentences
  - stakes_score     : count of high-stakes keywords in last 200 chars
  - text_length      : total character length of the ending
  - excl_count       : number of '!' in the text
  - short_sentences  : count of sentences < 6 words (urgency signal)

Output:
  - Trained model saved to `backend/models/cliffhanger_model.pkl`

Run:
    python training/train_cliffhanger_classifier.py
"""

import csv
import os
import sys
import pickle

# ── resolve paths ──────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH   = os.path.join(BACKEND_DIR, 'training_data', 'cliffhanger_dataset.csv')
MODEL_DIR   = os.path.join(BACKEND_DIR, 'models')
MODEL_OUT   = os.path.join(MODEL_DIR, 'cliffhanger_model.pkl')
os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(DATA_PATH):
    print("[!] Training data not found. Run generate_training_data.py first.")
    sys.exit(1)

print("[1/5] Loading libraries...")
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

analyzer = SentimentIntensityAnalyzer()

STAKES_KEYWORDS = [
    'die', 'kill', 'secret', 'never', 'truth', 'trap', 'bomb', 'love',
    'run', 'escape', 'terrified', 'hunt', 'dead', 'murder', 'blood',
    'confess', 'betray', 'reveal', 'expose', 'destroy', 'gone', 'missing'
]

def extract_features(text: str) -> list:
    """Extract numeric features from a screenplay ending text."""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 2]

    # Sentiment on full text
    vs = analyzer.polarity_scores(text)
    vader_compound = vs['compound']
    vader_neg      = vs['neg']
    vader_pos      = vs['pos']

    # Sentiment shift: first sentence vs last sentence
    first_scores = analyzer.polarity_scores(sentences[0])['compound'] if sentences else 0.0
    last_scores  = analyzer.polarity_scores(sentences[-1])['compound'] if sentences else 0.0
    sentiment_shift = abs(last_scores - first_scores)

    # Questions in last 4 sentences
    last_sentences = sentences[-4:]
    question_count = sum(1 for s in last_sentences if '?' in s)

    # Stakes keyword score (last 200 chars)
    tail = text.lower()[-200:]
    stakes_score = sum(1 for kw in STAKES_KEYWORDS if kw in tail)

    # Text length
    text_length = len(text)

    # Exclamation marks
    excl_count = text.count('!')

    # Short sentences (< 6 words = urgency/fragments common in climax)
    short_sentences = sum(1 for s in sentences if len(s.split()) < 6)

    return [
        vader_compound, vader_neg, vader_pos,
        sentiment_shift,
        question_count, stakes_score,
        text_length, excl_count, short_sentences
    ]

# ── load dataset ───────────────────────────────────────────────────────────────
print("[2/5] Loading cliffhanger dataset...")
X, y = [], []
with open(DATA_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        features = extract_features(row['text'])
        X.append(features)
        y.append(float(row['score']))

X = np.array(X)
y = np.array(y)
print(f"      {len(y)} samples loaded")

# ── train ──────────────────────────────────────────────────────────────────────
print("[3/5] Training GradientBoostingRegressor...")
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('gbr', GradientBoostingRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        random_state=42,
    ))
])
pipeline.fit(X, y)

# ── cross-val score ────────────────────────────────────────────────────────────
print("[4/5] Cross-validating (3-fold)...")
cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring='neg_mean_absolute_error')
mae_mean = -cv_scores.mean()
print(f"      Mean Absolute Error (CV): {mae_mean:.1f} points out of 100")

# ── save model + feature extractor ────────────────────────────────────────────
print("[5/5] Saving model...")
payload = {
    'model': pipeline,
    'feature_names': [
        'vader_compound', 'vader_neg', 'vader_pos', 'sentiment_shift',
        'question_count', 'stakes_score', 'text_length', 'excl_count', 'short_sentences'
    ],
    'stakes_keywords': STAKES_KEYWORDS,
    'cv_mae': mae_mean,
}
with open(MODEL_OUT, 'wb') as f:
    pickle.dump(payload, f)

print(f"      ✅ Model saved → {MODEL_OUT}")
print(f"      CV MAE: {mae_mean:.1f} / 100 — model is ready for production use.")
