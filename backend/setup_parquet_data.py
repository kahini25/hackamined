import urllib.request
import pyarrow.parquet as pq
import json

url = "https://huggingface.co/api/datasets/simsun131/chapterbreak/parquet/default/train/0.parquet"
print(f"Downloading {url}...")
try:
    urllib.request.urlretrieve(url, "0.parquet")
    print("Download complete. Reading parquet...")
    table = pq.read_table("0.parquet")
    
    subset = table.slice(0, 100).to_pylist()
    
    contexts = [row.get('ctx') for row in subset if row.get('ctx')]
    print(f"Extracted {len(contexts)} valid context segments.")
    
    with open("chapterbreak_subset.json", "w", encoding='utf-8') as f:
        json.dump(contexts, f)
        
    print("Saved to chapterbreak_subset.json")
except Exception as e:
    print(f"Failed: {e}")
