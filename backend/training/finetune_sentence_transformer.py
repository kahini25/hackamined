"""
finetune_sentence_transformer.py
──────────────────────────────────
Fine-tunes `all-MiniLM-L6-v2` on screenplay-domain sentence pairs using
a raw PyTorch training loop — no `datasets` library required.

Uses the underlying transformer backbone directly so gradients flow correctly
through the loss (sentence_transformers v5 .encode() is inference-only and
detaches tensors from the computation graph).

Output:
  - Fine-tuned model saved to `backend/models/narrative_model/`

Run:
    python training/finetune_sentence_transformer.py
"""

import csv
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH   = os.path.join(BACKEND_DIR, 'training_data', 'pacing_pairs.csv')
MODEL_OUT   = os.path.join(BACKEND_DIR, 'models', 'narrative_model')
os.makedirs(MODEL_OUT, exist_ok=True)

if not os.path.exists(DATA_PATH):
    print("[!] Training data not found. Run generate_training_data.py first.")
    sys.exit(1)

print("[1/6] Loading libraries...")
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from sentence_transformers import SentenceTransformer

print("[2/6] Loading base model: all-MiniLM-L6-v2 ...")
st_model    = SentenceTransformer('all-MiniLM-L6-v2')
tokenizer   = st_model.tokenizer
transformer = st_model[0].auto_model   # the underlying HuggingFace BERT model

print("[3/6] Loading pacing pairs dataset...")
s1_list, s2_list, labels = [], [], []
with open(DATA_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        s1_list.append(row['sentence1'])
        s2_list.append(row['sentence2'])
        labels.append(float(row['label']))

labels_tensor = torch.tensor(labels, dtype=torch.float32)
print(f"      {len(labels)} training pairs loaded")


def mean_pooling(model_output, attention_mask):
    """Average token embeddings weighted by the attention mask."""
    token_emb = model_output.last_hidden_state
    mask_exp  = attention_mask.unsqueeze(-1).expand(token_emb.size()).float()
    return torch.sum(token_emb * mask_exp, 1) / torch.clamp(mask_exp.sum(1), min=1e-9)


def encode_with_grad(sentences):
    """Tokenize + forward-pass the transformer, returning L2-normed embeddings with gradients."""
    enc    = tokenizer(sentences, padding=True, truncation=True, max_length=128, return_tensors='pt')
    out    = transformer(**enc)
    pooled = mean_pooling(out, enc['attention_mask'])
    return F.normalize(pooled, p=2, dim=1)


EPOCHS     = 4
BATCH_SIZE = 16
LR         = 2e-5

cos_emb_loss = nn.CosineEmbeddingLoss(margin=0.1)
optimizer    = AdamW(transformer.parameters(), lr=LR)

print(f"[4/6] Fine-tuning for {EPOCHS} epochs (batch_size={BATCH_SIZE}) ...")
transformer.train()

n = len(s1_list)
for epoch in range(EPOCHS):
    total_loss  = 0.0
    num_batches = 0
    perm        = torch.randperm(n).tolist()

    for i in range(0, n, BATCH_SIZE):
        idx      = perm[i: i + BATCH_SIZE]
        b_s1     = [s1_list[j] for j in idx]
        b_s2     = [s2_list[j] for j in idx]
        b_labels = labels_tensor[idx]

        emb1    = encode_with_grad(b_s1)
        emb2    = encode_with_grad(b_s2)
        targets = torch.where(b_labels >= 0.5,
                              torch.ones_like(b_labels),
                              -torch.ones_like(b_labels))

        optimizer.zero_grad()
        loss = cos_emb_loss(emb1, emb2, targets)
        loss.backward()
        optimizer.step()

        total_loss  += loss.item()
        num_batches += 1

    print(f"      Epoch {epoch + 1}/{EPOCHS}  |  avg_loss = {total_loss / max(num_batches, 1):.4f}")

transformer.eval()

print(f"[5/6] Saving fine-tuned model → {MODEL_OUT} ...")
st_model.save(MODEL_OUT)

print("[6/6] Sanity check (cosine similarities after fine-tuning)...")
with torch.no_grad():
    e_h1 = encode_with_grad(["She pulled the trigger but the gun was empty — it was a trap!"])
    e_h2 = encode_with_grad(["He screamed and lunged at her, knife gleaming in the dark."])
    e_l1 = encode_with_grad(["She sat quietly by the window watching the rain fall."])
    e_l2 = encode_with_grad(["He stirred his coffee and thought about last summer."])

print(f"      HIGH↔HIGH : {F.cosine_similarity(e_h1, e_h2).item():.3f}  (expect: high)")
print(f"      LOW↔LOW   : {F.cosine_similarity(e_l1, e_l2).item():.3f}  (expect: high)")
print(f"      HIGH↔LOW  : {F.cosine_similarity(e_h1, e_l1).item():.3f}  (expect: low)")
print()
print("✅ Fine-tuned model saved. Backend will auto-load it on next startup.")
