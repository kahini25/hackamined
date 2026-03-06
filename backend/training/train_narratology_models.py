"""
train_narratology_models.py
─────────────────────────
Fine-tunes lightweight Transformer models (DistilBERT) on our Narratology datasets.
- Cliffhanger (Hermeneutic code)
- Emotion Intensity & Binary Opposites (Semantic / Symbolic code)
- Retention Risk (Proairetic code)

We will use simple HuggingFace regression pipelines to replace the heuristics.
Since the dataset is small (from the 5 stories), we train lightweight models 
that will serve as the foundation of the updated VBOX AI engine.
"""

import os
import sys
import csv
import torch
from torch.utils.data import Dataset, DataLoader
import warnings
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import get_scheduler
from tqdm.auto import tqdm

# Suppress HuggingFace warnings for cleaner output
warnings.filterwarnings("ignore")

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BACKEND_DIR, 'training_data')
MODEL_DIR = os.path.join(BACKEND_DIR, 'models')

os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class TextScoreDataset(Dataset):
    def __init__(self, texts, scores):
        self.texts = texts
        self.scores = scores
        self.encodings = tokenizer(self.texts, truncation=True, padding=True, max_length=128)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.scores[idx], dtype=torch.float)
        return item

    def __len__(self):
        return len(self.scores)

def load_data(csv_path, text_col, score_col):
    texts, scores = [], []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        t_idx = header.index(text_col)
        s_idx = header.index(score_col)
        
        for row in reader:
            if not row: continue
            texts.append(row[t_idx])
            scores.append(float(row[s_idx]))
            
    return texts, scores

def train_regression_model(texts, scores, model_save_path, epochs=8, lr=5e-5):
    print(f"--> Training model with {len(texts)} samples (Regression)")
    dataset = TextScoreDataset(texts, scores)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"--> Using device: {device}")
    
    # Num labels = 1 for Regression
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=1)
    model.to(device)
    
    optimizer = AdamW(model.parameters(), lr=lr)
    num_training_steps = epochs * len(dataloader)
    lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            
            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()
            total_loss += loss.item()
            
        print(f"      Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(dataloader):.4f}")
        
    print(f"--> Saving model to {model_save_path}")
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)
    print("DONE.\n")

def main():
    print("==================================================")
    print("VBOX Narratology Model Fine-Tuning")
    print("==================================================")
    
    # 1. Cliffhanger Model (Hermeneutic)
    print("\n[1] Training Cliffhanger / Hermeneutic Model (0-100 score)")
    c_texts, c_scores = load_data(os.path.join(DATA_DIR, "dataset_cliffhangers.csv"), 'text', 'score')
    # Normalize scores 0-1 for easier training
    c_scores_norm = [s/100.0 for s in c_scores]
    train_regression_model(c_texts, c_scores_norm, os.path.join(MODEL_DIR, "cliffhanger_transformer"))
    
    # 2. Emotion Intensity Model (Semantic)
    print("\n[2] Training Emotion Intensity Model (0-100 score)")
    e_texts, e_scores = load_data(os.path.join(DATA_DIR, "dataset_emotion.csv"), 'text', 'intensity_score')
    e_scores_norm = [s/100.0 for s in e_scores]
    train_regression_model(e_texts, e_scores_norm, os.path.join(MODEL_DIR, "emotion_transformer"))
    
    # 3. Retention Risk Model (Proairetic)
    print("\n[3] Training Retention Risk Model (0-100 risk score)")
    r_texts, r_scores = load_data(os.path.join(DATA_DIR, "dataset_retention.csv"), 'text', 'risk_score')
    r_scores_norm = [s/100.0 for s in r_scores]
    train_regression_model(r_texts, r_scores_norm, os.path.join(MODEL_DIR, "retention_transformer"))

    print("All models successfully fine-tuned and saved!")

if __name__ == "__main__":
    main()
