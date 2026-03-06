import spacy
from collections import defaultdict
import itertools

# Try to load the model. If it's missing in a real environment, 
# it needs to be downloaded via `python -m spacy download en_core_web_sm`
try:
    nlp = spacy.load("en_core_web_sm")
except ImportError:
    # Graceful fallback if spacy isn't installed
    nlp = None
except OSError:
    # Graceful fallback if model isn't downloaded
    nlp = None

def _normalize_name(name):
    """Normalize names to handle variations like 'Alice' vs 'Alice Morgan'."""
    # Basic normalization: lowercase and remove leading/trailing whitespace
    name = name.strip()
    
    # We could do more complex resolution here (e.g. keeping the longest name 
    # that contains the shorter string), but for heuristic purposes, 
    # we'll use the first token as the base identifier to group 'Alice Morgan' and 'Alice'.
    # This is a simple approximation.
    parts = name.split()
    if not parts:
        return ""
        
    return parts[0].capitalize()

def build_graph(text):
    """
    Extract characters, build an interaction graph based on sentence co-occurrence,
    and compute a narrative tension score.
    """
    if nlp is None:
        return {
            "characters": [],
            "interaction_graph": {"nodes": [], "edges": []},
            "tension_score": 0.0,
            "error": "spaCy model 'en_core_web_sm' not installed/loaded."
        }

    doc = nlp(text)
    
    # Extract entities (PERSON and ORG as actors)
    raw_characters = set()
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            raw_characters.add(ent.text)

    # Normalize Characters
    normalized_mapping = {}
    for rc in raw_characters:
        norm_name = _normalize_name(rc)
        if norm_name:
            normalized_mapping[rc] = norm_name
    
    unique_characters = list(set(normalized_mapping.values()))
    
    # Build Interaction Graph (Sentence Co-occurrence)
    interaction_counts = defaultdict(int)
    
    for sent in doc.sents:
        # Find all normalized characters in this sentence
        chars_in_sent = set()
        for ent in sent.ents:
            if ent.label_ in ["PERSON", "ORG"] and ent.text in normalized_mapping:
                chars_in_sent.add(normalized_mapping[ent.text])
                
        chars_in_sent = list(chars_in_sent)
        
        # If multiple characters are in the same sentence, they interact
        if len(chars_in_sent) > 1:
            # Create pairs, sort them so (A, B) is same as (B, A)
            for pair in itertools.combinations(sorted(chars_in_sent), 2):
                interaction_counts[pair] += 1
                
    # Format the graph
    nodes = [{"id": c, "group": 1} for c in unique_characters]
    edges = [{"source": pair[0], "target": pair[1], "weight": weight} 
             for pair, weight in interaction_counts.items()]
             
             
    # Compute Conflict Density & Tension Score
    tension_score = 0.0
    
    if unique_characters:
        # 1. Interaction Frequency
        total_interactions = sum(interaction_counts.values())
        interaction_factor = min(total_interactions / max(len(unique_characters), 1) * 0.1, 0.4)
        
        # 2. Conflict Keywords
        conflict_keywords = {'betray', 'attack', 'accuse', 'threaten', 'kill', 'fight', 'hate', 'lie', 'steal', 'argue'}
        conflict_count = sum(1 for token in doc if token.lemma_.lower() in conflict_keywords)
        conflict_factor = min(conflict_count * 0.05, 0.4)
        
        # 3. Overall Density (Characters per sentence)
        num_sentences = len(list(doc.sents))
        density_factor = min((len(unique_characters) / max(num_sentences, 1)) * 0.5, 0.2)
        
        tension_score = interaction_factor + conflict_factor + density_factor
        
    return {
        "characters": unique_characters,
        "interaction_graph": {
            "nodes": nodes,
            "edges": edges
        },
        "tension_score": round(min(tension_score, 1.0), 2)
    }
