import os
import random
import asyncio
import aiohttp
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import logging

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Headers
def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

# Env vars
api_id = int(os.environ.get("API_ID", 23241238))
api_hash = os.environ.get("API_HASH", "e6ff6e3068dbea75500865ac49c3608f")
bot_token = os.environ.get("BOT_TOKEN", "8110926083:AAHuuv8B5V_GIfkyPNdrrs8vZBHL2Gl-i24")
channel_id = os.environ.get("CHANNEL_ID", "-1002665953559")

try:
    channel_id = int(channel_id)
except ValueError:
    pass

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

# Fallback Dummy Data
DUMMY_DATA = [
    {
        "thumbnail": "https://placehold.co/600x400?text=No+Data",
        "name": "Sample Video",
        "description": "API কাজ না করায় এটি ডামি ভিডিও।",
        "content_url": "https://example.com/video"
    }
]

API_LIST = [
    "https://you-pom-lover.vercel.app/xnxx/10/school",
    "https://you-pom-lover.vercel.app/xnxx/10/desi",
    "https://you-pom-lover.vercel.app/xnxx/college",
    "https://you-pom-lover.vercel.app/xnxx/10/bhabhi"
]

async def fetch_api_data(session, api_url):
    try:
        async with session.get(api_url, headers=get_random_headers(), timeout=20) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("data", [])
            else:
                logger.warning(f"API status: {resp.status} from {api_url}")
    except Exception as e:
        logger.error(f"API Fetch Error from {api_url}: {e}")
    return []
async def auto_post():
    logger.info("🔁 Auto post started...")
    
    # Helper function to check if URL is a video
    def is_video(url):
        video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
        return url.lower().endswith(video_exts)
    
    while True:
        try:
            selected_api = random.choice(API_LIST)
            logger.info(f"Selected API: {selected_api}")

            async with aiohttp.ClientSession() as session:
                api_data = await fetch_api_data(session, selected_api)

            if not api_data:
                logger.warning("No data from API, using fallback dummy data.")
                api_data = DUMMY_DATA

            success_count = 0
            for idx, item in enumerate(api_data[:10]):
                # Validate required fields
                required = ['name', 'content_url']
                if not all(k in item for k in required):
                    logger.warning(f"Invalid item at index {idx}: Missing required fields")
                    continue
                
                # Prepare media URL (prioritize video)
                media_url = None
                is_video_post = False
                
                if item.get('video_url') and is_video(item['video_url']):
                    media_url = item['video_url']
                    is_video_post = True
                elif item.get('thumbnail'):
                    media_url = item['thumbnail']
                else:
                    logger.warning(f"Invalid item at index {idx}: No usable media")
                    continue
                
                # Handle invalid thumbnail formats
                if not is_video_post:
                    if not media_url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        media_url = "https://placehold.co/600x400?text=Image+Unavailable"

                # Prepare caption and buttons
                caption = f"🔥 {item['name']}\n\n{item.get('description', 'No description')}"
                buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📽️ ভিডিও দেখুন", url=item['content_url'])]])
                
                try:
                    # Send video or photo based on type
                    if is_video_post:
                        await bot.send_video(
                            chat_id=channel_id,
                            video=media_url,
                            caption=caption,
                            reply_markup=buttons,
                            thumb="https://placehold.co/600x400?text=Video+Thumb"  # Optional thumbnail
                        )
                    else:
                        await bot.send_photo(
                            chat_id=channel_id,
                            photo=media_url,
                            caption=caption,
                            reply_markup=buttons
                        )
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to post item {idx}: {e}")

                if idx < 9:
                    await asyncio.sleep(10)  # Short pause between posts

            logger.info(f"✅ সফলভাবে {success_count} টি পোস্ট করা হয়েছে।")
            await asyncio.sleep(300)  # Wait 5 minutes before next batch

        except Exception as e:
            logger.exception(f"❗ Auto post error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    logger.info("🤖 Bot is starting...")

    async def start_all():
        await bot.start()
        asyncio.create_task(auto_post())

        # Keep alive manually (Pyrogram doesn't use bot.idle)
        while True:
            await asyncio.sleep(3600)

    asyncio.run(start_all())
