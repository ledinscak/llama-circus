#!/usr/bin/env python3
"""Debug script to test image search and display."""

import os
from sys import argv
import tempfile
import subprocess
import requests
from ddgs import DDGS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://duckduckgo.com/",
}

if len(argv) < 2:
    print(f"Usage: {argv[0]} <term1> [term2] [term3] ...")
    print(f"Example: {argv[0]} llama cat dog")
    search_terms = ["llama"]
    print(f"No search terms provided, using default: {search_terms[0]}\n")
else:
    search_terms = argv[1:]

print("=== Testing Image Search & Display ===")
print(f"Search terms: {', '.join(search_terms)}\n")

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


def search_and_display(query):
    """Search for images and display all results."""
    print(f"\n--- Searching: {query} ---")

    # Search
    print(f"[2] DuckDuckGo image search for '{query}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=3))
        print(f"    ✓ Found {len(results)} images")
        for i, r in enumerate(results, 1):
            print(f"    [{i}] {r.get('image', 'NO URL')[:80]}...")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

    # Download and display all images
    print("\n[3] Downloading and displaying images...")
    success_count = 0
    for i, r in enumerate(results, 1):
        image_url = r.get("image", "")
        if not image_url:
            continue
        try:
            response = requests.get(image_url, timeout=10, headers=HEADERS, stream=True)
            response.raise_for_status()
            print(f"    ✓ [{i}] Downloaded from: {image_url[:60]}...")
            print(
                f"    Content-Type: {response.headers.get('content-type', 'unknown')}"
            )
            print(f"    Size: {len(response.content)} bytes")

            # Display with chafa
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            result = subprocess.run(
                ["chafa", "--size=40x20", "--colors=256", tmp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"\n=== {query.upper()} [{i}] ===")
                print(result.stdout)
                success_count += 1
            else:
                print(f"    ✗ chafa failed: {result.stderr}")

            os.unlink(tmp_path)
        except Exception as e:
            print(f"    ✗ [{i}] Failed: {e}")

    if success_count == 0:
        print("    ✗ All downloads/displays failed")
        return False

    return True


for term in search_terms:
    search_and_display(term)

print("\n=== Test Complete ===")
