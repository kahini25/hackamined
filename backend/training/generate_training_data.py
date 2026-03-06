"""
generate_training_data.py
─────────────────────────
Generates two screenplay-domain training datasets:

1. pacing_pairs.csv
   - Columns: sentence1, sentence2, label
   - label: 0.0 = same tempo/tone (low pacing change)
             1.0 = very different tempo/tone (high pacing change)
   - Used to fine-tune SentenceTransformer with CosineSimilarityLoss

2. cliffhanger_dataset.csv
   - Columns: text, score
   - score: 0-100 (hand-labeled cliffhanger intensity)
   - Used to train a regression model replacing the heuristic scorer

Run:
    python training/generate_training_data.py
"""

import csv
import os
import random

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'training_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Screenplay Sentence Bank
# ─────────────────────────────────────────────────────────────────────────────
HIGH_INTENSITY = [
    "She pulled the trigger but the gun was empty.",
    "He slammed the door and screamed into the darkness.",
    "The bomb exploded, tearing through the corridor.",
    "Marcus lunged at Alice with the knife gleaming.",
    "She gasped — the killer was standing right behind her.",
    "Run! The building is on fire!",
    "Blood dripped from the wound as he staggered forward.",
    "The car crashed through the barrier at full speed.",
    "He grabbed her by the throat, eyes wild with rage.",
    "The secret is out — everyone knows what you did.",
    "They shot him in the back as he ran.",
    "She screamed, but no one could hear her.",
    "The villain revealed himself — it was her father.",
    "The hostage was pushed to the edge of the roof.",
    "An explosion ripped through the server room.",
    "He confessed — he had been the traitor all along.",
    "The door burst open and soldiers flooded the room.",
    "She stabbed him and ran into the rain.",
    "The virus spread before anyone could stop it.",
    "They both reached for the gun at the same time.",
    "He fell from the bridge into the icy water below.",
    "Flames engulfed the warehouse in seconds.",
    "She couldn't breathe. The water was rising fast.",
    "He discovered the body hidden under the floorboards.",
    "The traitor had been in the room with them all along.",
    "The countdown reached zero and the city went dark.",
    "She is the one who killed your brother!",
    "He detonated the charge and the tunnel caved in.",
    "No one gets out of here alive.",
    "The truth will destroy everything you love.",
]

LOW_INTENSITY = [
    "She sat quietly by the window, watching the rain fall.",
    "He stirred his coffee slowly and looked at the photograph.",
    "The library was empty except for the old librarian.",
    "She thought about what her mother used to say.",
    "He folded the letter carefully and placed it in the drawer.",
    "The morning sun crept through the curtains.",
    "She hummed softly to herself while cooking.",
    "He remembered the summer they spent at the lake.",
    "The clock on the wall ticked steadily.",
    "She looked down at the map spread across the table.",
    "He watched the birds outside the kitchen window.",
    "The old house creaked gently in the wind.",
    "She walked slowly through the empty hallway.",
    "He poured two glasses of wine and sat down.",
    "The garden was overgrown but still beautiful.",
    "She brushed her hair and looked in the mirror.",
    "He read the last line of the letter twice.",
    "The street was quiet in the early morning light.",
    "She smiled at the photo on the mantle.",
    "He thought about whether he had made the right choice.",
    "The kettle whistled from the kitchen.",
    "She packed her bags methodically, room by room.",
    "He sat on the porch and stared at the horizon.",
    "They had dinner together in comfortable silence.",
    "She traced the outline of the map with her finger.",
    "He watered the plant on the windowsill.",
    "The children played in the street outside.",
    "She wrote a few lines in her journal before sleeping.",
    "He leaned back in the chair and closed his eyes.",
    "The train moved through the countryside at a gentle pace.",
]

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Generate Pacing Pairs
# ─────────────────────────────────────────────────────────────────────────────
pacing_pairs = []

for i in range(len(HIGH_INTENSITY)):
    for j in range(i + 1, len(HIGH_INTENSITY)):
        if random.random() < 0.4:
            pacing_pairs.append((HIGH_INTENSITY[i], HIGH_INTENSITY[j], round(random.uniform(0.75, 1.0), 2)))

for i in range(len(LOW_INTENSITY)):
    for j in range(i + 1, len(LOW_INTENSITY)):
        if random.random() < 0.4:
            pacing_pairs.append((LOW_INTENSITY[i], LOW_INTENSITY[j], round(random.uniform(0.75, 1.0), 2)))

for h in HIGH_INTENSITY:
    for l in LOW_INTENSITY:
        if random.random() < 0.15:
            pacing_pairs.append((h, l, round(random.uniform(0.0, 0.2), 2)))

random.shuffle(pacing_pairs)
pacing_path = os.path.join(OUTPUT_DIR, 'pacing_pairs.csv')
with open(pacing_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['sentence1', 'sentence2', 'label'])
    writer.writerows(pacing_pairs)

print(f"[✓] Pacing pairs generated: {len(pacing_pairs)} samples → {pacing_path}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Generate Cliffhanger Dataset (70 samples)
# ─────────────────────────────────────────────────────────────────────────────
CLIFFHANGER_DATA = [
    # --- High cliffhangers (70-100) ---
    ("She opened the envelope and her face went pale. The letter said: 'We have your daughter. Don't call the police.' What had she done?", 92),
    ("He reached the door just as the lights went out. A voice whispered from the darkness: 'You should have stayed dead.'", 95),
    ("The trap had been sprung. They were all inside. And Marcus was the one who had locked the door.", 90),
    ("She realized the killer was still in the room — and she had left her phone downstairs.", 88),
    ("He pulled back the curtain. The body was gone. But the blood was still fresh.", 91),
    ("The bomb had already gone off. But that wasn't the worst part. The second one was still ticking.", 96),
    ("She screamed but no one came. And then — three quiet knocks on the basement door.", 89),
    ("He finally knew the truth: there was no escape. The island was a prison, and they were all inmates.", 85),
    ("She looked at the photo again. The killer had been standing right behind her in every single one.", 93),
    ("Run. That was the only word in the message. But it was already too late.", 94),
    ("He confessed. He had killed her. And the detective had been his alibi.", 87),
    ("They had found the cure — but it only worked for one person. And there were seventeen of them left.", 86),
    ("The ship began to sink. And the only lifeboat had already gone.", 83),
    ("Her name was on the list. Right below the last victim's. And tomorrow was the date.", 91),
    ("He turned around. The stranger was wearing his face.", 97),
    ("Just before the signal cut out, she transmitted one final message: 'The virus is already inside.'", 89),
    ("He had always known she was capable of it. He just never thought she'd do it to him.", 80),
    ("The safe was empty. The money was gone. And so was Maria.", 78),
    ("She pressed play on the recording. It was her own voice confessing to the murder.", 92),
    ("He stepped out of the shadows. The man they had buried three years ago was very much alive.", 95),
    ("She pulled the trigger. Click. Empty. He smiled and took a step closer.", 96),
    ("The doors sealed shut. The countdown began. None of them had the code.", 93),
    ("He read the last line of the file. His hands started shaking. His own name. His own signature.", 94),
    ("She picked up the phone. On the other end — silence. Then breathing. Then: 'I see you.'", 97),
    ("The child looked up at her. 'Mommy,' he said, 'the man behind you told me to say goodbye.'", 99),
    ("He deleted the message. But it was already sent. To everyone.", 82),
    ("She thought she was alone. The shadow on the wall told her otherwise.", 88),
    ("They had him surrounded. Then the lights went out. When they came back — he was gone.", 91),
    ("The antidote was destroyed. And she had twelve minutes.", 94),
    ("He whispered the name. The colour drained from the detective's face. It was her.", 90),

    # --- Medium cliffhangers (35-65) ---
    ("She knew something was wrong, but she couldn't quite place it. The house felt different somehow.", 50),
    ("He didn't answer the phone. Third time that morning. She had a bad feeling.", 42),
    ("The evidence pointed in a direction no one wanted to follow.", 38),
    ("She left before he could explain. And he wasn't sure she'd come back.", 45),
    ("He had made his choice. He just wasn't sure it was the right one.", 40),
    ("The test results came in. The doctor went quiet for a long moment.", 60),
    ("She sent the email. Whatever came next was out of her hands.", 36),
    ("The negotiation had stalled. Someone was going to have to make the first move.", 55),
    ("He didn't recognize the car parked outside his house. It hadn't been there yesterday.", 58),
    ("She found the note tucked under her windshield: 'I know what you did.'", 65),
    ("The door to the archive was unlocked. It was never unlocked.", 62),
    ("He noticed that one of the files had been accessed at 3am. He hadn't done it.", 60),
    ("Her flight was cancelled. And her phone was dead. And no one knew she was here.", 55),
    ("The photograph showed three people. The caption named only two.", 52),
    ("Something about his smile wasn't right. She just couldn't figure out what.", 44),
    ("He opened the drawer. The gun was still there. He hadn't decided yet.", 48),
    ("The call dropped. She tried again. No signal. She was completely alone.", 57),
    ("He didn't trust the new partner. Not since that look she gave him at the courthouse.", 46),
    ("The money transfer cleared. But the account it went to — didn't exist.", 63),
    ("She watched him walk away. Something told her it wasn't the last time she'd see him.", 39),

    # --- Low cliffhangers (0-25) ---
    ("She went to bed early and slept through the night. Tomorrow would be another day.", 5),
    ("He finished his coffee and put the mug in the sink. The afternoon passed quietly.", 3),
    ("They said goodbye at the airport. It had been a good visit.", 8),
    ("She completed the report and filed it before the deadline.", 2),
    ("He decided to take a different route home. The traffic was lighter that way.", 6),
    ("The meeting was productive. Everyone agreed on the next steps.", 4),
    ("She read two chapters of her book and fell asleep on the couch.", 3),
    ("He called his sister. They talked for an hour about nothing in particular.", 7),
    ("The weather cleared up in the afternoon. She sat in the garden for a while.", 5),
    ("He signed the contract and shook the other man's hand. Business concluded.", 2),
    ("She made dinner, watched television, and went to bed at ten.", 1),
    ("He organized his desk and reviewed his schedule for the next week.", 3),
    ("The children had gone home. The park was empty and quiet.", 6),
    ("She sent the birthday card and hoped it would arrive on time.", 4),
    ("He watered the plants and turned off the kitchen light. A quiet evening.", 2),
    ("She finished her tea, washed the cup, and put it away carefully.", 1),
    ("He smiled at the news. It had worked out better than expected.", 5),
    ("The train arrived on time. She found a window seat and settled in.", 3),
    ("He passed the exam. Relief washed over him as he read the result.", 4),
    ("She returned the library books and walked home through the park.", 2),
]

cliffhanger_path = os.path.join(OUTPUT_DIR, 'cliffhanger_dataset.csv')
with open(cliffhanger_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['text', 'score'])
    for text, score in CLIFFHANGER_DATA:
        writer.writerow([text, score])

print(f"[✓] Cliffhanger dataset generated: {len(CLIFFHANGER_DATA)} samples → {cliffhanger_path}")
print()
print("Next steps:")
print("  python training/train_cliffhanger_classifier.py")
