import spacy

# Load spaCy model for character confrontation detection.
# Use graceful fallback if model is missing to ensure system remains stable.
try:
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    nlp = None

def detect_viral_moments(text, emotion_arc):
    """
    Detects top viral moments in the text using narrative signals:
    - Emotion Spikes
    - Conflict Triggers
    - Information Reveals
    - Character Confrontations
    """
    if not text:
        return []

    # Map emotion arc by approximate sentence index if possible
    emotion_scores = {}
    if emotion_arc:
        for beat in emotion_arc:
            # Assuming beat['beat'] roughly correlates to sentence index
            emotion_scores[beat.get('beat', 0)] = abs(beat.get('score', 0.0))

    # Segment Story Into Narrative Beats (Sentences)
    # If spaCy is available, use it for better sentence boundary detection
    if nlp is not None:
        doc = nlp(text)
        sentences = list(doc.sents)
        sentence_texts = [sent.text for sent in sentences]
    else:
        # Fallback to basic string splitting
        sentences = []
        sentence_texts = [s.strip() for s in text.split('.') if len(s.strip()) > 5]

    viral_candidates = []

    # Keyword lists
    conflict_words = {'betray', 'attack', 'reveal', 'expose', 'confess', 'threaten', 'destroy', 'confront'}
    reveal_phrases = ["turns out", "the truth is", "secret", "revealed", "suddenly realized"]

    for i, seq_text in enumerate(sentence_texts):
        if len(seq_text.strip()) < 5:
            continue
            
        seq_text_lower = seq_text.lower()
        
        # 1. Emotion Spike (Scale 0 to 1)
        emotion_spike = emotion_scores.get(i, 0.0)
        
        # 2. Conflict Trigger
        # Check words in sentence against conflict_words
        words = set(seq_text_lower.replace(',', '').replace('.', '').replace('!', '').replace('?', '').split())
        has_conflict = bool(words.intersection(conflict_words))
        conflict_trigger = 1.0 if has_conflict else 0.0
        
        # 3. Information Reveal
        has_reveal = any(phrase in seq_text_lower for phrase in reveal_phrases)
        information_reveal = 1.0 if has_reveal else 0.0
        
        # 4. Character Confrontation
        character_confrontation = 0.0
        if has_conflict and nlp is not None:
            # Count distinct characters in this sentence
            sent_doc = sentences[i]
            chars = set(ent.text for ent in sent_doc.ents if ent.label_ in ["PERSON", "ORG"])
            if len(chars) >= 2:
                character_confrontation = 1.0
                
        # Calculate Viral Score
        viral_score = (
            0.35 * emotion_spike +
            0.30 * conflict_trigger +
            0.20 * information_reveal +
            0.15 * character_confrontation
        )
        
        if viral_score > 0:
            # Determine primary reason for UI display
            reason = "emotional spike"
            if information_reveal > 0:
                reason = "major reveal"
            elif character_confrontation > 0:
                reason = "character confrontation"
            elif conflict_trigger > 0:
                reason = "high conflict"
                
            viral_candidates.append({
                "text": seq_text.strip() + ("." if not seq_text.strip().endswith(('.','!','?')) else ""),
                "score": round(min(viral_score, 1.0), 2),
                "reason": reason
            })
            
    # Sort candidates by score descending
    viral_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 3 moments
    return viral_candidates[:3]
