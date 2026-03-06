from datasets import load_dataset
import random

def main():
    print("Loading ChapterBreak dataset via streaming...")
    try:
        # Stream the dataset to avoid downloading the whole thing
        ds = load_dataset("simsun131/chapterbreak", "pg19", split="train", streaming=True)
        
        print("\nDataset Info (Streaming):")
        
        count = 0
        for example in ds:
            print(f"\n--- Sample {count+1} ---")
            print("Keys:", example.keys())
            if count == 0:
                print("Context (ctx, first 200 chars):", example.get('ctx', '')[:200])
                print("Positive Next (pos, first 200 chars):", example.get('pos', '')[:200])
                print("Num Negs:", len(example.get('negs', [])))
            count += 1
            if count >= 3:
                break
                
        # Are there annotations in this dataset?
        print("\nDone streaming samples.")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")

if __name__ == "__main__":
    main()
