#!/usr/bin/env python3
"""
Debug version - shows what's happening at each step
"""

import os
import sys
import requests
from pathlib import Path

print("=" * 60)
print("MASTODON OUTFIT BOT - DEBUG MODE")
print("=" * 60)

# Check Python version
print(f"\\nPython version: {sys.version}")

# Check environment variables
print("\\n--- Environment Variables ---")
MASTODON_URL = os.getenv('MASTODON_INSTANCE_URL')
MASTODON_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

print(f"MASTODON_INSTANCE_URL: {MASTODON_URL}")
print(f"MASTODON_ACCESS_TOKEN: {'***' + MASTODON_TOKEN[-10:] if MASTODON_TOKEN else 'NOT SET'}")
print(f"UNSPLASH_ACCESS_KEY: {'***' + UNSPLASH_KEY[-10:] if UNSPLASH_KEY else 'NOT SET'}")

# Validate
print("\\n--- Validation ---")
all_good = True

if not MASTODON_URL:
    print("❌ MASTODON_INSTANCE_URL is missing!")
    all_good = False
else:
    print(f"✓ MASTODON_INSTANCE_URL: {MASTODON_URL}")

if not MASTODON_TOKEN:
    print("❌ MASTODON_ACCESS_TOKEN is missing!")
    all_good = False
else:
    print(f"✓ MASTODON_ACCESS_TOKEN is set ({len(MASTODON_TOKEN)} chars)")

if not UNSPLASH_KEY:
    print("❌ UNSPLASH_ACCESS_KEY is missing!")
    all_good = False
else:
    print(f"✓ UNSPLASH_ACCESS_KEY is set ({len(UNSPLASH_KEY)} chars)")

if not all_good:
    print("\\n❌ FATAL: Missing required environment variables!")
    sys.exit(1)

# Step 1: Fetch from Unsplash
print("\\n--- Step 1: Fetching from Unsplash ---")
try:
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": "fashion outfit clothing",
        "per_page": 1,
        "order_by": "random"
    }
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    
    print(f"Request URL: {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    response.raise_for_status()
    data = response.json()
    print(f"Response keys: {data.keys()}")
    
    if not data.get('results'):
        print(f"❌ No results in response: {data}")
        sys.exit(1)
    
    photo = data['results'][0]
    image_url = photo['urls']['regular']
    description = photo.get('description') or photo.get('alt_description', 'Outfit inspo')
    photographer = photo['user']['name']
    
    print(f"✓ Got image from: {photographer}")
    print(f"✓ Description: {description[:50]}...")
    print(f"✓ Image URL: {image_url[:60]}...")
    
    # Download image
    print(f"\\nDownloading image...")
    img_response = requests.get(image_url, timeout=10)
    img_response.raise_for_status()
    print(f"✓ Downloaded {len(img_response.content)} bytes")
    
    # Save image
    image_path = Path('temp_outfit.jpg')
    image_path.write_bytes(img_response.content)
    print(f"✓ Saved to: {image_path}")
    
except Exception as e:
    print(f"❌ Error in Step 1: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Upload to Mastodon
print("\\n--- Step 2: Uploading to Mastodon ---")
try:
    print(f"Mastodon URL: {MASTODON_URL}")
    print(f"Token length: {len(MASTODON_TOKEN)}")
    
    # Upload media
    upload_url = f"{MASTODON_URL}/api/v1/media"
    print(f"Upload URL: {upload_url}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        headers = {"Authorization": f"Bearer {MASTODON_TOKEN}"}
        
        media_response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            timeout=30
        )
    
    print(f"Status Code: {media_response.status_code}")
    print(f"Response: {media_response.text[:200]}")
    
    media_response.raise_for_status()
    media_data = media_response.json()
    media_id = media_data['id']
    print(f"✓ Media uploaded with ID: {media_id}")
    
    # Create post
    print(f"\\nCreating post...")
    caption = f"✨ Today's outfit inspo ✨\\n\\n{description}\\n\\n📸 Photo by {photographer}\\n\\n#FashionInspo #OOTD #DailyStyle"
    
    status_url = f"{MASTODON_URL}/api/v1/statuses"
    print(f"Status URL: {status_url}")
    
    status_response = requests.post(
        status_url,
        headers=headers,
        json={
            "status": caption,
            "media_ids": [media_id],
            "visibility": "public"
        },
        timeout=30
    )
    
    print(f"Status Code: {status_response.status_code}")
    print(f"Response: {status_response.text[:200]}")
    
    status_response.raise_for_status()
    status = status_response.json()
    print(f"✓ Posted! Status ID: {status['id']}")
    print(f"✓ URL: {status['url']}")
    
except Exception as e:
    print(f"❌ Error in Step 2: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
print("\\n--- Cleanup ---")
try:
    image_path.unlink()
    print(f"✓ Removed temp file")
except Exception as e:
    print(f"⚠ Cleanup failed: {e}")

print("\\n" + "=" * 60)
print("✅ BOT COMPLETED SUCCESSFULLY!")
print("=" * 60)
