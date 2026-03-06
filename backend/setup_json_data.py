import urllib.request
import json
import time

url = "https://huggingface.co/datasets/simsun131/chapterbreak/resolve/main/chapterbreak_ctx_1024.json"
print(f"Downloading {url}...")

# Add timeout and User-Agent
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req, timeout=120)
    data = json.loads(response.read().decode('utf-8'))
    
    subset = []
    # format: {"pg19": {"id": [{"ctx": "..."}]}}
    for domain, domain_data in data.items():
        if isinstance(domain_data, dict):
            for doc_id, blocks in domain_data.items():
                if isinstance(blocks, list):
                    for block in blocks:
                        if 'ctx' in block:
                            subset.append(block['ctx'])
                            if len(subset) >= 100:
                                break
                if len(subset) >= 100:
                    break
        if len(subset) >= 100:
            break

    print(f"Extracted {len(subset)} records.")
    with open("chapterbreak_subset.json", "w", encoding='utf-8') as f:
        json.dump(subset, f)
    print("Done!")
except Exception as e:
    print(f"Failed: {e}")
