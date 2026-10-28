import sys
import requests
import json
import os

sys.stdout.reconfigure(encoding='utf-8')

url = "https://huggingface.co/datasets/ZombitX64/xauusd-gold-price-historical-data-2004-2025/resolve/main/XAU_15m_data.jsonl"
jsonl_file = "XAU_15m_data.jsonl"
csv_file = "XAUUSD_15M_all.csv"

if not os.path.exists(jsonl_file) or os.path.getsize(jsonl_file) < 40000000:
    print(f"Downloading {url} to {jsonl_file}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded = 0
        with open(jsonl_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"Downloaded {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB...")
    print("Download complete!")
else:
    print(f"File {jsonl_file} already exists and is {os.path.getsize(jsonl_file)/(1024*1024):.1f} MB.")

# Convert to clean CSV
print("Converting jsonl to CSV...")
import csv

with open(jsonl_file, 'r', encoding='utf-8') as fin, open(csv_file, 'w', newline='', encoding='utf-8') as fout:
    writer = csv.writer(fout)
    writer.writerow(["time", "open", "high", "low", "close", "volume"])
    count = 0
    first_time = ""
    last_time = ""
    for line in fin:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        # Expected keys: Date, Open, High, Low, Close, Volume
        t = row.get("Date") or row.get("time") or row.get("timestamp")
        o = row.get("Open") or row.get("open")
        h = row.get("High") or row.get("high")
        l = row.get("Low") or row.get("low")
        c = row.get("Close") or row.get("close")
        v = row.get("Volume") or row.get("volume", 0)
        
        if count == 0:
            first_time = t
        last_time = t
        writer.writerow([t, o, h, l, c, v])
        count += 1

print(f"Done! Converted {count} rows. Span: {first_time} -> {last_time}. Saved to {csv_file}")
