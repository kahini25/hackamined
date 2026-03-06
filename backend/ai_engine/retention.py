from . import emotion, cliffhanger, tension

def predict_drop_off(text):
    """
    Predict drop-off risk by dividing the script into 4 time segments.
    Uses emotion, cliffhanger, tension, and a hook analysis to generate deterministic scores.
    """
    # ---------------------------------------------------------
    # STEP 1: Compute Narrative Signals for the whole text first
    # ---------------------------------------------------------
    
    # 1. Emotion Intensity
    emotion_arc = emotion.analyze_emotional_arc(text)
    scores = [abs(x['score']) for x in emotion_arc] if emotion_arc else [0]
    avg_emotion_intensity = sum(scores) / len(scores) * 100  # Scale 0-100
    
    # 2. Cliffhanger Strength
    cliffhanger_strength = cliffhanger.calculate_score(text, emotion_arc)
    
    # 3. Conflict Density (using tension graph logic)
    tension_graph = tension.build_graph(text)
    # A proxy for conflict density is the number of character links relative to text length
    num_links = len(tension_graph.get('interaction_graph', {}).get('edges', []))
    conflict_density = min(num_links * 15, 100) # Arbitrary scaling, max 100
    
    # 4. Hook Strength (using scroll_stop logic as the baseline)
    hook_strength = predict_scroll_stop(text)
    
    # ---------------------------------------------------------
    # STEP 2 & 3: Divide Episode Timeline & Score Engagement
    # ---------------------------------------------------------
    
    # We break the text into 4 roughly equal segments to represent time.
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    total_sentences = max(len(sentences), 1)
    
    # Time ranges map to [0-15s, 15-30s, 30-60s, 60-90s]
    # We roughly map these to 1/6th, 1/6th, 2/6ths, and 2/6ths of the text.
    # For a simpler heuristic, let's just use 4 equal quadrants for the text segments.
    quad_size = max(total_sentences // 4, 1)
    
    segments_data = [
        {"time_range": "0-15s", "start": 0, "end": quad_size},
        {"time_range": "15-30s", "start": quad_size, "end": quad_size * 2},
        {"time_range": "30-60s", "start": quad_size * 2, "end": quad_size * 3},
        {"time_range": "60-90s", "start": quad_size * 3, "end": total_sentences}
    ]

    segments_output = []
    
    for seg in segments_data:
        # Extract the text for this segment
        segment_sentences = sentences[seg['start']:seg['end']]
        segment_text = ". ".join(segment_sentences) + "." if segment_sentences else ""
        
        # Calculate local signals for this segment
        local_emotion_arc = emotion.analyze_emotional_arc(segment_text)
        local_scores = [abs(x['score']) for x in local_emotion_arc] if local_emotion_arc else [0]
        local_emotion_intensity = (sum(local_scores) / len(local_scores) * 100) if local_scores else 0
        
        local_tension = tension.build_graph(segment_text)
        local_conflict_density = min(len(local_tension.get('interaction_graph', {}).get('edges', [])) * 20, 100)
        
        # Base engagement calculation
        engagement_score = (
            0.35 * local_emotion_intensity + 
            0.25 * cliffhanger_strength +     # Global cliffhanger affects overall retention positively
            0.20 * local_conflict_density + 
            0.20 * hook_strength              # Global hook strength anchors engagement
        )
        
        # Convert engagement score to drop-off risk (inverse relationship)
        # Range: 0 (high engagement) to 100 (low engagement)
        # Then map to a probability 0.00 to 1.00
        drop_off_percentage = max(0, min(100 - engagement_score, 100))
        drop_off_risk = round(drop_off_percentage / 100.0, 2)
        
        segments_output.append({
            "time_range": seg["time_range"],
            "drop_off_risk": drop_off_risk
        })

    # Overall Engagement Score (0-1)
    overall_engagement = (
        0.35 * avg_emotion_intensity +
        0.25 * cliffhanger_strength +
        0.20 * conflict_density +
        0.20 * hook_strength
    ) / 100.0
    
    return {
        "segments": segments_output,
        "engagement_score": round(min(overall_engagement, 1.0), 2)
    }

def predict_scroll_stop(text):
    """
    Original scroll stop logic preserved to act as hook strength.
    """
    hook = text[:150].lower()
    score = 50
    
    triggers = ['suddenly', '!', 'blood', 'kiss', 'money', 'secret', 'die', 'kill']
    for t in triggers:
        if t in hook:
            score += 15
            
    return min(score, 100)
