import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.aggregator import NarrativeDNAAggregator

story_1_text = """
A college student accidentally sends a private voice note to her entire class group — exposing secrets she never meant to share.

Episode 1: The Send 
It was a quiet Tuesday. Mia hits “send” on a voice note complaining about her professor and a secret relationship  with a classmate. Immediately, her heart drops—it’s the main class group. The message delivers. She panics, tries to delete it, but the app crashes. She sees the “seen by” count rising fast. Her phone starts buzzing with incoming messages. 
"""

def main():
    print("Testing ML narratology pipeline via AI Engine Aggregator on Sample Story 1:")
    print("---------------------------------------------------------------------------------")
    
    aggregator = NarrativeDNAAggregator()
    result = aggregator.analyze_story(story_1_text)
    
    print(json.dumps(result, indent=2))
    print("---------------------------------------------------------------------------------")
    print("Test Complete.")
    
if __name__ == "__main__":
    main()
