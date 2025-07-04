import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

# === CONFIGURATION === #
BOT_TOKEN = "7763733692:AAFv_DrMMQ7KkgFWlUDvz3wj1HxUGjrTJXw"
BOT_USERNAME = "sh_tiktok_downloader_bot"
MAIN_CHANNEL_URL = "https://t.me/your_main_channel"  # Replace with your channel

# URLs for other platform bots (replace with your actual bot links)
PLATFORM_BOTS = {
    "tiktok": "https://t.me/sh_tiktok_downloader_bot",
    "pinterest": "https://t.me/sh_pinterest_downloader_bot",
    "linkedin": "https://t.me/sh_linkein_downloader_bot",
    "instagram": "https://t.me/sh_instagram_downloader_bot",
    "youtube": "https://t.me/sh_youtube_downloader_bot" 
}

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = 10

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === RATE LIMITING CLASS === #
class RateLimiter:
    def __init__(self):
        self.user_activity = defaultdict(list)
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        self.user_activity[user_id] = [
            t for t in self.user_activity[user_id]
            if now - t < timedelta(minutes=1)
        ]
        
        if len(self.user_activity[user_id]) >= MAX_REQUESTS_PER_MINUTE:
            return True
        
        self.user_activity[user_id].append(now)
        return False

rate_limiter = RateLimiter()

# === HELPER FUNCTIONS === #
def get_main_menu() -> InlineKeyboardMarkup:
    """Returns the main menu with advertisement and platform buttons."""
    keyboard = [
        [InlineKeyboardButton("📌 Join Our Main Channel", url=MAIN_CHANNEL_URL)],
        [InlineKeyboardButton("🎥 YouTube Downloader", url=PLATFORM_BOTS["youtube"])],
        [InlineKeyboardButton("📷 Pinterest Downloader", url=PLATFORM_BOTS["pinterest"])],
        [InlineKeyboardButton("🔗 LinkedIn Downloader", url=PLATFORM_BOTS["linkedin"])],
        [InlineKeyboardButton("📸 Instagram Downloader", url=PLATFORM_BOTS["instagram"])],
        [InlineKeyboardButton("🎵 TikTok Downloader", callback_data="tiktok")]
    ]
    return InlineKeyboardMarkup(keyboard)

# === HANDLERS === #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message"""
    if await rate_limiter.check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
        return
    
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to Social Media Downloader Hub!\n"
        "Choose a platform to download content from:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu()
    )

async def tiktok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle TikTok download requests"""
    query = update.callback_query
    await query.answer()
    
    if await rate_limiter.check_rate_limit(query.from_user.id):
        await query.edit_message_text("⚠️ Too many requests! Please wait a minute.")
        return
    
    await query.edit_message_text(
        text="📥 You selected TikTok downloader.\n"
             "Please send a valid TikTok video link now.\n\n"
             "Example: https://www.tiktok.com/@username/video/123456789"
    )
    # Here you would typically set a state to expect a TikTok URL next

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_user'):
        user_id = update.effective_user.id
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ An error occurred. Please try again later."
            )
        except Exception as e:
            logger.error(f"Couldn't send error message to user {user_id}: {e}")

# === MAIN FUNCTION === #
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(tiktok_handler, pattern="^tiktok$"))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🚀 Starting Social Media Downloader Hub Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()