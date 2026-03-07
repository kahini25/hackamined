import os
import sys

backend_dir = r"c:\Users\hetad\hackamined\backend"
sys.path.append(backend_dir)

from ai_engine.aggregator import NarrativeDNAAggregator

text = """
This is block 1. A lot of things happen here. It is just an introduction to the characters and the world. We see John walking down the street.

This is block 2. Suddenly, an explosion goes off! People scream and run. John looks around, terrified. A man with a gun approaches him.

This is block 3. The man points the gun at John. "Where is the money?" he asks. John has no idea what he is talking about. He tries to escape.

This is block 4. John runs into an alleyway. It's a dead end. The man corners him. "You can't run," he says.

This is block 5. Just as the man pulls the trigger, a mysterious woman jumps down from a fire escape and kicks the gun out of his hand!

This is block 6. The woman grabs John's hand. "Come if you want to live!" she yells. They run.

This is block 7. They reach a safehouse. "Who are you?" John asks. She turns around. "I'm your sister," she reveals.
""" * 5

aggregator = NarrativeDNAAggregator()
result = aggregator.analyze_story(text)

print("\n--- TEST RESULTS ---")
episodes = result.get('episodes', [])
print(f"Total Episodes found: {len(episodes)}")
for ep in episodes:
    print(f"Episode {ep['episode_number']} (Cliffhanger Score: {ep['cliffhanger_score_at_end']}):")
    print(f"Text Snippet: {ep['text'][:60]}...\n")

if len(episodes) > 1:
    print("SUCCESS: Script was successfully broken down into multiple episodes.")
else:
    print("FAILURE: Script was not broken down.")
