"""
train_scroll_stop_model.py
────────────────────────
Trains a GradientBoostingRegressor to predict "Scroll Stop" scores.

Instead of hardcoded labels, since we don't have explicit scroll-stop targets 
in the raw data, we will generate a synthetic target combining the old 
heuristic (which looked for strong hook keywords) and the inverse of the 
drop-off risk from the first 15 seconds.

Features extracted per sample from `parsed_stories.json`:
  - risk_0_15          : Drop-off risk for the 0-15s segment
  - risk_15_30         : Drop-off risk for the 15-30s segment
  - risk_30_60         : Drop-off risk for the 30-60s segment
  - risk_60_90         : Drop-off risk for the 60-90s segment
  - engagement_score   : Overall predicted engagement capacity
  - word_count         : Text length
  - hook_exclamation   : Presence of exclamations in first 150 chars

Output:
  - Trained model saved to `backend/models/scroll_stop_model.pkl`

Run:
    python training/train_scroll_stop_model.py
"""

import os
import sys
import json
import pickle
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ── setup paths ──────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH   = os.path.join(BACKEND_DIR, 'training_data', 'parsed_stories.json')
MODEL_DIR   = os.path.join(BACKEND_DIR, 'models')
MODEL_OUT   = os.path.join(MODEL_DIR, 'scroll_stop_model.pkl')

sys.path.append(BACKEND_DIR)
from ai_engine import retention

if not os.path.exists(DATA_PATH):
    print("[!] parsed_stories.json not found. Run prepare_narratology_data.py first.")
    sys.exit(1)

print("[1/5] Loading story texts and generating features...")

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    stories = json.load(f)

X = []
y = []

# Triggers from old heuristic to generate synthethic targets
triggers = ['suddenly', '!', 'blood', 'kiss', 'money', 'secret', 'die', 'kill']

valid_samples = 0
for s in stories:
    for ep in s.get("episodes", []):
        text = ep.get("summary", "")
        if len(text.strip()) < 20: 
            continue
            
        # 1. Generate retention heatmap features
        try:
            drop_off_data = retention.predict_drop_off(text)
        except Exception as e:
            print(f"Skipping segment due to retention error: {e}")
            continue
            
        segments = drop_off_data.get("segments", [])
        if len(segments) != 4:
            continue
            
        risk_0_15 = segments[0].get("drop_off_risk", 0.5)
        risk_15_30 = segments[1].get("drop_off_risk", 0.5)
        risk_30_60 = segments[2].get("drop_off_risk", 0.5)
        risk_60_90 = segments[3].get("drop_off_risk", 0.5)
        engagement_score = drop_off_data.get("engagement_score", 0.5)
        
        # Additional text features
        word_count = len(text.split())
        hook_text = text[:150].lower()
        hook_exclamation = 1.0 if '!' in hook_text else 0.0
        
        features = [
            risk_0_15, risk_15_30, risk_30_60, risk_60_90,
            engagement_score, word_count, hook_exclamation
        ]
        
        # 2. Generate Synthetic Target
        # Base score 50. Add points for strong structural first 15s (low risk).
        # Add points for old heuristic triggers to preserve hook strength detection.
        synthetic_target = 50.0
        
        # Lower risk in first 15s -> higher scroll stop
        synthetic_target += (1.0 - risk_0_15) * 30.0 
        
        for t in triggers:
            if t in hook_text:
                synthetic_target += 10.0
                
        synthetic_target = min(100.0, max(0.0, synthetic_target))
        
        X.append(features)
        y.append(synthetic_target)
        valid_samples += 1

X = np.array(X)
y = np.array(y)

print(f"      {valid_samples} samples generated based on retention heatmaps.")

if valid_samples == 0:
    print("[!] No valid samples found. Exiting.")
    sys.exit(1)

# ── train ──────────────────────────────────────────────────────────────────────
print("[2/5] Training GradientBoostingRegressor...")
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('gbr', GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    ))
])
pipeline.fit(X, y)

# ── cross val ──────────────────────────────────────────────────────────────────
print("[3/5] Cross-validating (3-fold)...")
try:
    cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring='neg_mean_absolute_error')
    mae_mean = -cv_scores.mean()
    print(f"      Mean Absolute Error (CV): {mae_mean:.1f} points out of 100")
except ValueError:
    print("      Not enough samples for 3-fold CV. Skipping CV.")
    mae_mean = 0.0

# ── save model ─────────────────────────────────────────────────────────────────
print("[4/5] Saving model...")
payload = {
    'model': pipeline,
    'feature_names': [
        'risk_0_15', 'risk_15_30', 'risk_30_60', 'risk_60_90',
        'engagement_score', 'word_count', 'hook_exclamation'
    ],
    'cv_mae': mae_mean,
}

os.makedirs(MODEL_DIR, exist_ok=True)
with open(MODEL_OUT, 'wb') as f:
    pickle.dump(payload, f)

print(f"[5/5] Model saved -> {MODEL_OUT}")
print(f"      Scroll Stop model based on Retention Heatmap is ready for production use.")
