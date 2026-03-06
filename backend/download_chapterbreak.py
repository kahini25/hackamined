import urllib.request
import json
import os

url = "https://huggingface.co/datasets/simsun131/chapterbreak/resolve/main/chapterbreak_ctx_1024.json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    print(f"Downloading {url}...")
    response = urllib.request.urlopen(req, timeout=30)
    data = json.loads(response.read().decode('utf-8'))
    print(f"Downloaded {len(data)} records.")
    with open("chapterbreak_subset.json", "w") as f:
        json.dump(data, f)
except Exception as e:
    print(f"Failed: {e}")
