"""
story_decomposer.py
─────────────────────────
Implements:
1. Todorov's Equilibrium Theory (5 stages pathing)
2. Propp's Character Archetypes
"""

import re

def analyze_todorov_stage(text: str) -> dict:
    """
    Rule-based heuristic to map a story segment to Todorov's 5 stages.
    """
    text_lower = text.lower()
    
    # 1. Equilibrium 
    # 2. Disruption
    # 3. Recognition
    # 4. Repair
    # 5. New Equilibrium
    
    stages_score = {
        "Equilibrium": 0,
        "Disruption": 0,
        "Recognition": 0,
        "Repair": 0,
        "New Equilibrium": 0
    }
    
    # Simple keyword mapping
    if any(w in text_lower for w in ['normal', 'peace', 'routine', 'calm', 'quiet']):
        stages_score["Equilibrium"] += 1
        
    if any(w in text_lower for w in ['suddenly', 'explosion', 'attack', 'break', 'discover', 'leak']):
        stages_score["Disruption"] += 2
        
    if any(w in text_lower for w in ['realize', 'understand', 'knew', 'saw', 'revealed']):
        stages_score["Recognition"] += 2
        
    if any(w in text_lower for w in ['fight', 'fix', 'argue', 'confront', 'escape']):
        stages_score["Repair"] += 2
        
    if any(w in text_lower for w in ['finally', 'settle', 'after', 'new normal', 'changed']):
        stages_score["New Equilibrium"] += 2
        
    most_likely = max(stages_score, key=stages_score.get)
    if stages_score[most_likely] == 0:
        most_likely = "Unknown/Transition"
        
    return {
        "stage": most_likely,
        "confidence": min(stages_score[most_likely] * 20, 100)
    }

def extract_propp_characters(text: str, characters: list) -> dict:
    """
    Identify Propp's character archetypes for the given cast.
    """
    text_lower = text.lower()
    mapping = {}
    
    # Propp's 7 character types
    archetypes = {
        "Hero": ['brave', 'save', 'fight', 'lead', 'protect', 'main'],
        "Villain": ['evil', 'attack', 'destroy', 'enemy', 'kill', 'leak'],
        "Donor": ['give', 'help', 'magic', 'tool', 'weapon'],
        "Helper": ['assist', 'friend', 'support', 'sidekick'],
        "Princess/Prize": ['save', 'rescue', 'goal', 'kidnap'],
        "Dispatcher": ['send', 'mission', 'tell', 'warn'],
        "False Hero": ['betray', 'lie', 'trick', 'fake']
    }
    
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
    except:
        doc = None

    for char in characters:
        char_lower = char.lower()
        role_scores = {k: 0 for k in archetypes}
        
        # If Spacy is available, look at sentences where character is mentioned
        if doc:
            for sent in doc.sents:
                if char_lower in sent.text.lower():
                    for role, keywords in archetypes.items():
                        if any(kw in sent.text.lower() for kw in keywords):
                            role_scores[role] += 1
        else:
            # Fallback string matching window around character name
            for match in re.finditer(char_lower, text_lower):
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                window = text_lower[start:end]
                for role, keywords in archetypes.items():
                    if any(kw in window for kw in keywords):
                        role_scores[role] += 1
                        
        best_role = max(role_scores, key=role_scores.get)
        if role_scores[best_role] > 0:
             mapping[char] = best_role
        else:
             mapping[char] = "Unassigned"
             
    return mapping
