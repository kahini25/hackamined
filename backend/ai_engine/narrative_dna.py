from sentence_transformers import SentenceTransformer, util
import numpy as np
import os

# ── Model loading: prefer fine-tuned screenplay model, fall back to base ──────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FINETUNED   = os.path.join(_BASE_DIR, 'models', 'narrative_model')
_BASE_MODEL  = 'all-MiniLM-L6-v2'

if os.path.isdir(_FINETUNED):
    print(f"[narrative_dna] Loading fine-tuned screenplay model from {_FINETUNED}")
    model = SentenceTransformer(_FINETUNED)
else:
    print(f"[narrative_dna] Fine-tuned model not found. Using base model: {_BASE_MODEL}")
    print(f"                To fine-tune, run: python training/finetune_sentence_transformer.py")
    model = SentenceTransformer(_BASE_MODEL)


def analyze_pacing(text: str) -> list:
    """
    Analyze pacing by computing sentence-level dissimilarity.
    Uses the fine-tuned screenplay model if available, otherwise falls
    back to the base all-MiniLM-L6-v2.

    Returns:
        List[float] — pacing speed per sentence transition (0=slow, 1=fast)
    """
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
    if len(sentences) < 2:
        return [0.5]

    embeddings = model.encode(sentences)
    pacing_curve = []

    for i in range(len(embeddings) - 1):
        sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
        # Low similarity → high pacing change (dramatic shift)
        speed = float(1.0 - sim)
        pacing_curve.append(round(speed, 4))

    return pacing_curve
