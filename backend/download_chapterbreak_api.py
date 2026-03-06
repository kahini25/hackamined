import requests
import json
import os

url = "https://datasets-server.huggingface.co/rows?dataset=simsun131/chapterbreak&config=default&split=pg19&offset=0&length=100"
print(f"Fetching from {url}...")
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    rows = data.get("rows", [])
    print(f"Fetched {len(rows)} rows.")
    
    # Extract the contexts 
    extracted = []
    for r in rows:
        row_data = r.get("row", {})
        ctx = row_data.get("ctx", "")
        if ctx:
            extracted.append(ctx)
            
    print(f"Extracted {len(extracted)} valid contexts.")
    with open("chapterbreak_subset.json", "w") as f:
        json.dump(extracted, f)
        
    print("Saved to chapterbreak_subset.json")
except Exception as e:
    print(f"Failed: {e}")
