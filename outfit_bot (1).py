#!/usr/bin/env python3
"""
Mastodon Daily Outfit Inspiration Bot
Fetches fashion images from public domain sources and posts daily to Mastodon
"""

import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from mastodon import Mastodon
from image_sources import fetch_from_unsplash, fetch_from_pexels, fetch_from_open_images

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outfit_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MASTODON_URL = os.getenv('MASTODON_INSTANCE_URL')
MASTODON_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
PEXELS_KEY = os.getenv('PEXELS_API_KEY')

# Create directories
IMAGE_CACHE_DIR = Path('outfit_cache')
IMAGE_CACHE_DIR.mkdir(exist_ok=True)


def get_random_outfit_inspo():
    """
    Fetch a random outfit inspiration from available sources
    Returns: dict with 'image_path', 'description', 'attribution'
    """
    sources = []
    
    # Try each source
    if UNSPLASH_KEY:
        try:
            logger.info("Attempting to fetch from Unsplash...")
            photo = fetch_from_unsplash(UNSPLASH_KEY, IMAGE_CACHE_DIR)
            if photo:
                sources.append(photo)
                logger.info(f"✓ Got image from Unsplash: {photo['filepath']}")
        except Exception as e:
            logger.warning(f"Unsplash fetch failed: {e}")
    
    if PEXELS_KEY:
        try:
            logger.info("Attempting to fetch from Pexels...")
            photo = fetch_from_pexels(PEXELS_KEY, IMAGE_CACHE_DIR)
            if photo:
                sources.append(photo)
                logger.info(f"✓ Got image from Pexels: {photo['filepath']}")
        except Exception as e:
            logger.warning(f"Pexels fetch failed: {e}")
    
    try:
        logger.info("Attempting to fetch from Open Images...")
        photo = fetch_from_open_images(IMAGE_CACHE_DIR)
        if photo:
            sources.append(photo)
            logger.info(f"✓ Got image from Open Images: {photo['filepath']}")
    except Exception as e:
        logger.warning(f"Open Images fetch failed: {e}")
    
    if not sources:
        raise Exception("No image sources available! Check API keys and internet connection.")
    
    # Pick random source
    chosen = random.choice(sources)
    logger.info(f"Selected outfit from: {chosen['source']}")
    return chosen


def post_to_mastodon(image_path, description, attribution):
    """
    Upload image and post to Mastodon instance
    """
    try:
        mastodon = Mastodon(
            access_token=MASTODON_TOKEN,
            api_base_url=MASTODON_URL
        )
        
        # Upload media
        logger.info(f"Uploading image: {image_path}")
        media = mastodon.media_post(
            image_path,
            mime_type='image/jpeg',
            description=f"Fashion outfit inspiration: {description}"
        )
        
        # Create caption
        caption = f"✨ Today's outfit inspo ✨\n\n{description}\n\n{attribution}\n\n#FashionInspo #OOTD #DailyStyle"
        
        # Post status
        logger.info("Posting to Mastodon...")
        status = mastodon.status_post(
            caption,
            media_ids=[media['id']]
        )
        
        logger.info(f"✓ Posted successfully! Status ID: {status['id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to post to Mastodon: {e}")
        raise


def cleanup_old_images(days=7):
    """Remove cached images older than N days"""
    try:
        import time
        cutoff = time.time() - (days * 86400)
        removed = 0
        
        for img in IMAGE_CACHE_DIR.glob('*.jpg'):
            if os.path.getmtime(img) < cutoff:
                os.remove(img)
                removed += 1
        
        if removed:
            logger.info(f"Cleaned up {removed} old cached images")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")


def main():
    """Main bot function - fetch outfit and post"""
    logger.info("=" * 60)
    logger.info("Starting Daily Outfit Bot")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # Fetch outfit inspiration
        outfit = get_random_outfit_inspo()
        
        # Post to Mastodon
        post_to_mastodon(
            outfit['filepath'],
            outfit['description'],
            outfit['attribution']
        )
        
        # Cleanup old cache
        cleanup_old_images(days=7)
        
        logger.info("✓ Bot completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Bot failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
