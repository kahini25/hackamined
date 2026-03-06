"""Windows-compatible verify script."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.aggregator import NarrativeDNAAggregator

agg = NarrativeDNAAggregator()

SAMPLES = [
    {
        "label": "HIGH INTENSITY - Action/Climax",
        "text": (
            "She pulled the trigger but the gun was empty. "
            "He lunged at her across the room, knife gleaming. "
            "Run! The building is on fire! She screamed but no one came. "
            "It was a trap - he had been the traitor all along. What had she missed?"
        )
    },
    {
        "label": "LOW INTENSITY - Reflective Scene",
        "text": (
            "She sat quietly by the window, watching the rain fall. "
            "He stirred his coffee and looked at the photograph. "
            "The morning sun crept through the curtains slowly. "
            "She thought about what her mother used to say. "
            "He folded the letter carefully and placed it in the drawer."
        )
    },
    {
        "label": "MID INTENSITY - Escalating Scene",
        "text": (
            "He didn't recognize the car parked outside. "
            "She heard footsteps on the stairs and froze. "
            "The door handle began to turn slowly. "
            "She grabbed her phone - no signal. "
            "He stepped into the room. Neither of them spoke."
        )
    },
]

print("=" * 65)
print("  NARRATIVE DNA ENGINE - TRANSFER LEARNING VALIDATION")
print("=" * 65)

for s in SAMPLES:
    result = agg.analyze_story(s["text"])
    print(f"\n>> {s['label']}")
    print(f"  Cliffhanger Score : {result['cliffhanger_score']:6.1f} / 100")
    print(f"  Scroll Stop Score : {result['scroll_stop_score']:6.1f} / 100")
    print(f"  Engagement Score  : {result['drop_off_risk'].get('engagement_score', 0):.2f} / 1.0")
    print(f"  Viral Moments     : {len(result['viral_moments'])} detected")
    pacing = result['pacing_curve']
    print(f"  Pacing Curve      : {[round(p, 2) for p in pacing]}")
    chars = result['tension_graph'].get('characters', [])
    if chars:
        print(f"  Characters Found  : {chars}")
    vm = result['viral_moments']
    if vm:
        top = vm[0]
        print(f"  Top Viral Moment  : [{top['reason']}] score={top['score']}")
        print(f"    Text: \"{top['text'][:70]}\"")
    ndna = result.get('narrative_dna', {})
    if ndna:
        print(f"  Narrative DNA     :")
        for k, v in ndna.items():
            print(f"    {k}: {v}")

print("\n" + "=" * 65)
print("Validation complete.")
print("=" * 65)
