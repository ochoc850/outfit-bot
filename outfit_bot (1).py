#!/usr/bin/env python3
"""
Simple Mastodon Outfit Bot - Minimal Dependencies
"""

import os
import json
import requests
from pathlib import Path

# Get secrets from environment
MASTODON_URL = os.getenv('MASTODON_INSTANCE_URL')
MASTODON_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

print(f"Starting bot...")
print(f"Mastodon URL: {MASTODON_URL}")
print(f"Token exists: {bool(MASTODON_TOKEN)}")
print(f"Unsplash key exists: {bool(UNSPLASH_KEY)}")

# Check if secrets are set
if not MASTODON_URL or not MASTODON_TOKEN or not UNSPLASH_KEY:
    print("ERROR: Missing required secrets!")
    print(f"  MASTODON_INSTANCE_URL: {MASTODON_URL}")
    print(f"  MASTODON_ACCESS_TOKEN: {'SET' if MASTODON_TOKEN else 'NOT SET'}")
    print(f"  UNSPLASH_ACCESS_KEY: {'SET' if UNSPLASH_KEY else 'NOT SET'}")
    exit(1)

# Fetch image from Unsplash
print("\\nFetching image from Unsplash...")
try:
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params={
            "query": "fashion outfit clothing",
            "per_page": 1,
            "order_by": "random"
        },
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        print("ERROR: No images found from Unsplash")
        exit(1)
    
    photo = data['results'][0]
    image_url = photo['urls']['regular']
    description = photo.get('description') or photo.get('alt_description', 'Cute outfit inspo')
    photographer = photo['user']['name']
    
    print(f"✓ Got image: {description}")
    print(f"✓ Photographer: {photographer}")
    
    # Download the image
    img_response = requests.get(image_url, timeout=10)
    img_response.raise_for_status()
    
    # Save image temporarily
    image_path = Path('temp_outfit.jpg')
    image_path.write_bytes(img_response.content)
    print(f"✓ Image saved: {image_path}")
    
except Exception as e:
    print(f"ERROR fetching from Unsplash: {e}")
    exit(1)

# Upload to Mastodon
print("\\nUploading to Mastodon...")
try:
    # Upload media
    with open(image_path, 'rb') as f:
        files = {'file': f}
        media_response = requests.post(
            f"{MASTODON_URL}/api/v1/media",
            headers={"Authorization": f"Bearer {MASTODON_TOKEN}"},
            files=files
        )
    
    media_response.raise_for_status()
    media_data = media_response.json()
    media_id = media_data['id']
    print(f"✓ Media uploaded: {media_id}")
    
    # Create post
    caption = f"✨ Today's outfit inspo ✨\\n\\n{description}\\n\\n📸 Photo by {photographer}\\n\\n#FashionInspo #OOTD #DailyStyle"
    
    status_response = requests.post(
        f"{MASTODON_URL}/api/v1/statuses",
        headers={"Authorization": f"Bearer {MASTODON_TOKEN}"},
        json={
            "status": caption,
            "media_ids": [media_id],
            "visibility": "public"
        }
    )
    
    status_response.raise_for_status()
    status = status_response.json()
    print(f"✓ Posted! Status ID: {status['id']}")
    print(f"✓ URL: {status['url']}")
    
except Exception as e:
    print(f"ERROR posting to Mastodon: {e}")
    if 'media_response' in locals():
        print(f"Media response: {media_response.text}")
    if 'status_response' in locals():
        print(f"Status response: {status_response.text}")
    exit(1)

# Cleanup
try:
    image_path.unlink()
    print("\\n✓ Cleanup complete")
except:
    pass

print("\\n🎉 Bot completed successfully!")
```

**4. Click Commit changes**

---

## 5. Update requirements.txt

**Go to:** https://github.com/ochoc850/outfit-bot/blob/main/requirements.txt

**Click ✏️ edit and replace with:**
```
requests==2.31.0
