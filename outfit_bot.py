#!/usr/bin/env python3
"""
Simple Mastodon Outfit Bot
"""

import os
import requests
import random
from pathlib import Path

# Get secrets
MASTODON_URL = os.getenv('MASTODON_INSTANCE_URL')
MASTODON_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

if not all([MASTODON_URL, MASTODON_TOKEN, UNSPLASH_KEY]):
    print("ERROR: Missing required environment variables")
    exit(1)

# Fashion search terms for variety
fashion_queries = [
    "fashion outfit",
    "casual style",
    "clothing aesthetic",
    "street style fashion",
    "outfit of the day",
    "women fashion",
    "style inspiration",
    "daily look",
    "fashion inspiration",
    "trendy outfit",
    "summer fashion",
    "spring outfit",
    "elegant style",
    "casual clothing",
    "fashion look"
]

# Fetch image from Unsplash
try:
    # Pick random search term for variety
    query = random.choice(fashion_queries)
    
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params={
            "query": query,
            "per_page": 1,
            "order_by": "random"
        },
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        print("ERROR: No images found")
        exit(1)
    
    photo = data['results'][0]
    image_url = photo['urls']['regular']
    description = photo.get('description') or photo.get('alt_description', 'Cute outfit inspo')
    photographer = photo['user']['name']
    
    # Download image
    img_response = requests.get(image_url, timeout=10)
    img_response.raise_for_status()
    
    # Save image
    image_path = Path('temp_outfit.jpg')
    image_path.write_bytes(img_response.content)
    
except Exception as e:
    print(f"ERROR fetching image: {e}")
    exit(1)

# Upload to Mastodon
try:
    # Upload media
    with open(image_path, 'rb') as f:
        files = {'file': f}
        media_response = requests.post(
            f"{MASTODON_URL}/api/v1/media",
            headers={"Authorization": f"Bearer {MASTODON_TOKEN}"},
            files=files,
            timeout=30
        )
    
    media_response.raise_for_status()
    media_data = media_response.json()
    media_id = media_data['id']
    
    # Create post with proper line breaks
    caption = f"""✨ Today's outfit inspo ✨

{description}

📸 Photo by {photographer}

#FashionInspo #OOTD #DailyStyle"""
    
    status_response = requests.post(
        f"{MASTODON_URL}/api/v1/statuses",
        headers={"Authorization": f"Bearer {MASTODON_TOKEN}"},
        json={
            "status": caption,
            "media_ids": [media_id],
            "visibility": "public"
        },
        timeout=30
    )
    
    status_response.raise_for_status()
    print("✓ Post successful!")
    
except Exception as e:
    print(f"ERROR posting: {e}")
    exit(1)

# Cleanup
try:
    image_path.unlink()
except:
    pass
