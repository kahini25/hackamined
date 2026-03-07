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

def divide_into_episodes(text: str, max_episodes: int = 7, max_words_per_ep: int = 225) -> dict:
    """
    Splits the script into up to max_episodes parts.
    Each part is constrained to roughly max_words_per_ep (~90 seconds of V/O).
    It splits at the highest cliffhanger score within that window limits.
    """
    from . import cliffhanger, emotion
    import re

    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if len(b.strip()) > 10]
    
    if not blocks:
        return {"episodes": [], "is_truncated": False}
        
    episodes = []
    current_block_idx = 0
    total_blocks = len(blocks)
    
    while current_block_idx < total_blocks and len(episodes) < max_episodes - 1:
        window_blocks = []
        window_words = 0
        potential_breaks = []
        
        for i in range(current_block_idx, total_blocks):
            blk = blocks[i]
            blk_words = len(blk.split())
            
            # If adding this block exceeds the limit (and we already have at least one block)
            if window_words + blk_words > max_words_per_ep and len(window_blocks) > 0:
                break
                
            window_blocks.append(blk)
            window_words += blk_words
            
            # Evaluate cliffhanger score if we cut here
            segment_so_far = " ".join(blocks[current_block_idx : i + 1])
            try:
               seg_emotion = emotion.analyze_emotional_arc(segment_so_far)
               score = cliffhanger.calculate_score(segment_so_far, seg_emotion)
            except Exception:
               score = cliffhanger.calculate_score(segment_so_far, None)
               
            potential_breaks.append({
                "split_after_index": i,
                "score": score
            })
            
        if not potential_breaks:
            break
            
        # If we reached the end of the text, let the final episode logic handle it
        if potential_breaks[-1]["split_after_index"] == total_blocks - 1:
             break 
            
        # Find the best break in this window
        best_break = max(potential_breaks, key=lambda x: x["score"])
        
        # Construct the episode
        ep_blocks = blocks[current_block_idx : best_break["split_after_index"] + 1]
        ep_text = "\n\n".join(ep_blocks)
        
        episodes.append({
            "episode_number": len(episodes) + 1,
            "text": ep_text,
            "cliffhanger_score_at_end": round(float(best_break["score"]), 2),
            "duration_seconds": int(len(ep_text.split()) / 2.5)
        })
        
        current_block_idx = best_break["split_after_index"] + 1

    # Final episode construction
    remaining_blocks = blocks[current_block_idx:]
    if remaining_blocks:
        final_blocks = []
        final_words = 0
        for blk in remaining_blocks:
            blk_words = len(blk.split())
            if final_words + blk_words > max_words_per_ep and len(final_blocks) > 0:
                break
            final_blocks.append(blk)
            final_words += blk_words
            
        final_text = "\n\n".join(final_blocks)
        episodes.append({
            "episode_number": len(episodes) + 1,
            "text": final_text,
            "cliffhanger_score_at_end": 0.0,
            "duration_seconds": int(len(final_text.split()) / 2.5)
        })
        
        current_block_idx += len(final_blocks)

    is_truncated = current_block_idx < total_blocks

    return {
        "episodes": episodes,
        "is_truncated": is_truncated
    }
