#!/usr/bin/env python3
"""Debug script to test image search and display."""

import os
import tempfile
import subprocess
import requests
from ddgs import DDGS

print("=== Testing Image Search & Display ===\n")

# 1. Test chafa
print("[1] Testing chafa installation...")
try:
    result = subprocess.run(["which", "chafa"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    ✓ chafa found: {result.stdout.strip()}")
    else:
        print("    ✗ chafa NOT found! Install with: sudo apt install chafa")
        exit(1)
except Exception as e:
    print(f"    ✗ Error: {e}")
    exit(1)

# 2. Test DuckDuckGo image search
print("\n[2] Testing DuckDuckGo image search...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.images("cat", max_results=3))
    print(f"    ✓ Found {len(results)} images")
    for i, r in enumerate(results, 1):
        print(f"    [{i}] {r.get('image', 'NO URL')[:80]}...")
except Exception as e:
    print(f"    ✗ Error: {e}")
    exit(1)

# 3. Test image download
print("\n[3] Testing image download...")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://duckduckgo.com/",
}

response = None
for i, r in enumerate(results, 1):
    image_url = r.get("image", "")
    if not image_url:
        continue
    try:
        response = requests.get(image_url, timeout=10, headers=HEADERS, stream=True)
        response.raise_for_status()
        print(f"    ✓ [{i}] Downloaded from: {image_url[:60]}...")
        print(f"    Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"    Size: {len(response.content)} bytes")
        break
    except Exception as e:
        print(f"    ✗ [{i}] Failed: {e}")
        response = None

if not response:
    print("    ✗ All downloads failed")
    exit(1)

# 4. Save and display with chafa
print("\n[4] Testing chafa display...")
try:
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    print(f"    Saved to: {tmp_path}")

    result = subprocess.run(
        ["chafa", "--size=40x20", "--colors=256", tmp_path],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0:
        print("    ✓ chafa succeeded!\n")
        print("=== IMAGE OUTPUT ===")
        print(result.stdout)
        print("=== END IMAGE ===")
    else:
        print(f"    ✗ chafa failed: {result.stderr}")

    os.unlink(tmp_path)
except Exception as e:
    print(f"    ✗ Error: {e}")

print("\n=== Test Complete ===")
