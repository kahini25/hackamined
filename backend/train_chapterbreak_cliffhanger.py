import os
import sys
import torch
import numpy as np
import warnings
from datasets import load_dataset
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.optim import AdamW
from transformers import get_scheduler

warnings.filterwarnings("ignore")

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BACKEND_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Use our existing heuristic for ground truth
sys.path.append(BACKEND_DIR)
from ai_engine.cliffhanger import _heuristic_score

class TextScoreDataset(Dataset):
    def __init__(self, texts, scores):
        self.texts = texts
        self.scores = scores
        # Truncate to the end of the text where the cliffhanger usually is
        tail_texts = [text[-512:] for text in self.texts]
        self.encodings = tokenizer(tail_texts, truncation=True, padding=True, max_length=128)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.scores[idx], dtype=torch.float)
        return item

    def __len__(self):
        return len(self.scores)

def main():
    print("Downloading ChapterBreak dataset via HuggingFace...")
    try:
        ds_dict = load_dataset("simsun131/chapterbreak")
        ds = ds_dict['train']
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    texts = []
    scores = []
    
    count = 0
    for example in ds:
        for domain_name, domain_data in example.items():
            if not isinstance(domain_data, dict):
                continue
            for doc_id, pages in domain_data.items():
                if not isinstance(pages, list):
                    continue
                for page in pages:
                    ctx = page.get('ctx', '')
                    if not ctx or len(ctx) < 50:
                        continue
                    
                    # Get heuristic score (0-100) on just the last 1500 chars to save time
                    short_ctx = ctx[-1500:]
                    score = _heuristic_score(short_ctx)
                    
                    texts.append(short_ctx)
                    scores.append(score / 100.0) # Normalize to 0-1 for regression

                    count += 1
                    if count >= 100:
                        break
                if count >= 100: break
            if count >= 100: break
        if count >= 100: break

    print(f"Loaded {len(texts)} texts.")
    
    # Split into train/val
    train_size = int(0.8 * len(texts))
    train_texts = texts[:train_size]
    train_scores = scores[:train_size]
    val_texts = texts[train_size:]
    val_scores = scores[train_size:]

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"Using device: {device}")
    
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=1)
    model.to(device)

    train_dataset = TextScoreDataset(train_texts, train_scores)
    val_dataset = TextScoreDataset(val_texts, val_scores)
    
    train_dataloader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=16)
    
    epochs = 2
    optimizer = AdamW(model.parameters(), lr=5e-5)
    num_training_steps = epochs * len(train_dataloader)
    lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

    print("Starting training on subset...")
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        for batch in train_dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} | Training Loss: {total_loss/len(train_dataloader):.4f}")

    # Evaluate
    model.eval()
    total_mae = 0
    with torch.no_grad():
        for batch in val_dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            preds = outputs.logits.squeeze(-1)
            # MAE on original 0-100 scale
            mae = torch.sum(torch.abs(preds - batch['labels']) * 100.0).item()
            total_mae += mae
            
    avg_mae = total_mae / len(val_dataset)
    # Estimate accuracy as 100 - MAE
    accuracy = max(0, 100.0 - avg_mae)
    
    print(f"\nEvaluation Complete:")
    print(f"Mean Absolute Error (0-100 scale): {avg_mae:.2f}")
    print(f"Estimated Accuracy (100 - MAE): {accuracy:.2f}%")
    
    model_save_path = os.path.join(MODEL_DIR, "chapterbreak_cliffhanger_transformer")
    print(f"Saving model to {model_save_path}...")
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)
    
    print("Done!")

if __name__ == "__main__":
    main()
