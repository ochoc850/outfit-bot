"""
Image source fetchers for outfit bot
Supports: Unsplash, Pexels, Open Images Dataset
"""

import requests
import logging
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


def fetch_from_unsplash(api_key, cache_dir):
    """
    Fetch random fashion/outfit image from Unsplash API
    License: Free commercial use, no attribution required (but we do it anyway)
    """
    try:
        # Search for outfit/fashion images
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": "fashion outfit clothing flat lay",
                "per_page": 1,
                "order_by": "random"
            },
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if not data['results']:
            logger.warning("No Unsplash results found")
            return None
        
        photo = data['results'][0]
        
        # Download image
        img_response = requests.get(photo['urls']['regular'], timeout=10)
        img_response.raise_for_status()
        
        # Validate and resize if needed
        img = Image.open(BytesIO(img_response.content))
        if img.size[0] > 2000:  # Resize if too large
            img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
        
        # Save locally
        filename = f"unsplash_{photo['id']}.jpg"
        filepath = cache_dir / filename
        img.save(filepath, quality=85)
        
        # Build description
        description = photo.get('description') or photo.get('alt_description', 'Fashion outfit inspiration')
        description = description[:150]  # Limit length
        
        # Attribution
        photographer = photo['user']['name']
        unsplash_url = f"https://unsplash.com/@{photo['user']['username']}"
        attribution = f"📸 Photo by {photographer} on Unsplash"
        
        return {
            'filepath': str(filepath),
            'description': description,
            'attribution': attribution,
            'source': 'Unsplash',
            'url': photo['links']['html']
        }
        
    except Exception as e:
        logger.error(f"Unsplash fetch error: {e}")
        return None


def fetch_from_pexels(api_key, cache_dir):
    """
    Fetch random fashion/outfit image from Pexels API
    License: Free for personal and commercial use, attribution appreciated but not required
    """
    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            params={
                "query": "fashion outfit clothing style",
                "per_page": 1,
                "page": 1
            },
            headers={"Authorization": api_key},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if not data['photos']:
            logger.warning("No Pexels results found")
            return None
        
        photo = data['photos'][0]
        
        # Download image (use medium size to save bandwidth)
        img_response = requests.get(photo['src']['medium'], timeout=10)
        img_response.raise_for_status()
        
        # Validate
        img = Image.open(BytesIO(img_response.content))
        
        # Save locally
        filename = f"pexels_{photo['id']}.jpg"
        filepath = cache_dir / filename
        img.save(filepath, quality=85)
        
        # Build description
        description = f"Stylish outfit inspiration from Pexels"
        
        # Attribution
        photographer = photo['photographer']
        attribution = f"📸 Photo by {photographer} on Pexels"
        
        return {
            'filepath': str(filepath),
            'description': description,
            'attribution': attribution,
            'source': 'Pexels',
            'url': photo['photographer_url']
        }
        
    except Exception as e:
        logger.error(f"Pexels fetch error: {e}")
        return None


def fetch_from_open_images(cache_dir):
    """
    Fetch from Open Images Dataset (Google)
    License: CC-BY 4.0 - requires attribution
    
    Note: This is a simplified version. For production, you might want to:
    1. Download the Open Images metadata
    2. Filter by 'Clothing' label
    3. Use a local cache of image URLs
    """
    try:
        # This is a fallback list of high-quality, CC-licensed clothing images
        # In production, you'd query the Open Images Dataset directly
        fallback_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/T-shirt_front_and_back.jpg/640px-T-shirt_front_and_back.jpg",
            "https://images.unsplash.com/photo-1594938298603-c8148c4dae35",  # CC0
        ]
        
        img_url = fallback_urls[0]
        
        # Download
        img_response = requests.get(img_url, timeout=10)
        img_response.raise_for_status()
        
        # Validate
        img = Image.open(BytesIO(img_response.content))
        
        # Save
        filename = f"openimages_{hash(img_url) % 100000}.jpg"
        filepath = cache_dir / filename
        img.save(filepath, quality=85)
        
        return {
            'filepath': str(filepath),
            'description': 'Fashion outfit from open dataset',
            'attribution': '📸 Image from Open Images Dataset (CC-BY 4.0)',
            'source': 'Open Images',
            'url': img_url
        }
        
    except Exception as e:
        logger.error(f"Open Images fetch error: {e}")
        return None


def format_attribution(photos_list):
    """
    Format attribution for multiple photos (if combining them)
    """
    return " | ".join([p['attribution'] for p in photos_list if 'attribution' in p])
