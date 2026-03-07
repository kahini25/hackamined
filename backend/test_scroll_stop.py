import os
import sys

backend_dir = r"c:\Users\hetad\hackamined\backend"
sys.path.append(backend_dir)

from ai_engine.aggregator import NarrativeDNAAggregator

text = "Suddenly, the lights went out. A scream echoed through the hallway. Blood was nowhere to be seen, but the smell of copper hung heavy in the air. Who could have done this?"

aggregator = NarrativeDNAAggregator()
result = aggregator.analyze_story(text)

print("\n--- TEST RESULTS ---")
print(f"Scroll Stop Score: {result.get('scroll_stop_score')}")
print(f"Engagement Potential: {result.get('narrative_dna', {}).get('engagement_potential')}")
print("--------------------\n")

if result.get('scroll_stop_score') > 0:
    print("SUCCESS: Scroll Stop score was generated.")
else:
    print("FAILURE: Scroll Stop score is 0.0 or missing.")
