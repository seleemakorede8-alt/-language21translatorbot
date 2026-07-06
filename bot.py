import os
import logging
import json
import requests
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ==================== CONFIGURATION ====================

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable is not set!")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user language preferences
user_languages: Dict[str, str] = {}

# Language database
LANGUAGES_DB = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Chinese (Simplified)': 'zh-CN',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Arabic': 'ar',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Urdu': 'ur',
    'Persian': 'fa',
    'Turkish': 'tr',
    'Dutch': 'nl',
    'Greek': 'el',
    'Hebrew': 'he',
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Malay': 'ms',
    'Filipino': 'tl',
    'Swahili': 'sw',
    'Zulu': 'zu',
}

LANG_NAMES = {v: k for k, v in LANGUAGES_DB.items()}

# Language names for detection
LANG_DETECT_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh-CN': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
    'tr': 'Turkish',
    'nl': 'Dutch',
    'el': 'Greek',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino',
    'sw': 'Swahili',
    'zu': 'Zulu',
}

# ==================== TRANSLATION FUNCTIONS ====================

def translate_text(text: str, target_lang: str) -> dict:
    """Translate text using Google Translate API."""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the translation
        translated_text = ""
        for item in data[0]:
            if item[0]:
                translated_text += item[0]
        
        # Get detected language
        detected_lang = data[2] if len(data) > 2 else "en"
        
        return {
            "success": True,
            "translated": translated_text,
            "detected": detected_lang
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def detect_language(text: str) -> dict:
    """Detect language using Google Translate API."""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "en",
            "dt": "t",
            "dt": "ld",
            "q": text
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Get detected language from response
        detected_lang = data[2] if len(data) > 2 else "en"
        
        return {
            "success": True,
            "language": detected_lang
        }
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_id = str(user.id)
    current_lang = user_languages.get(user_id, 'en')
    current_lang_name = LANG_NAMES.get(current_lang, 'English')
    
    keyboard = [
        [InlineKeyboardButton("🌍 Set Language", callback_data='set_lang')],
        [InlineKeyboardButton("📖 Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 *Hello {user.first_name}!*\n\n"
        f"I'm your *Language21 Translator Bot* 🌐\n"
        f"I can translate text between 25+ languages!\n\n"
        f"📍 *Your current target language:* *{current_lang_name}*\n\n"
        f"✨ *Commands:*\n"
        f"• Send any text to translate it\n"
        f"• /setlang - Change target language\n"
        f"• /languages - See all languages\n"
        f"• /detect - Detect language\n"
        f"• /help - Get help"
    )
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )
    logger.info(f"User {user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 *Help & Commands*\n\n"
        "🔹 `/start` - Show welcome menu\n"
        "🔹 `/setlang` - Change your target language\n"
        "🔹 `/languages` - List all available languages\n"
        "🔹 `/detect` - Detect language of replied message\n"
        "🔹 `/help` - Show this help message\n\n"
        "💡 *How to use:*\n"
        "1. Set your target language with /setlang\n"
        "2. Send any text message\n"
        "3. I'll translate it automatically!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def set_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlang command."""
    keyboard = []
    row = []
    
    for name, code in LANGUAGES_DB.items():
        row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='cancel')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 *Select your target language:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command."""
    lang_list = sorted(LANGUAGES_DB.keys())
    message = "🌍 *Available Languages:*\n\n"
    
    # Show languages in columns
    for i in range(0, len(lang_list), 3):
        chunk = lang_list[i:i+3]
        message += "• " + "  • ".join(chunk) + "\n"
    
    message += f"\n*Total:* {len(lang_list)} languages supported"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /detect command."""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ Please reply to a message to detect its language.\n\n"
            "Example: Reply to any message and send /detect"
        )
        return
    
    text = update.message.reply_to_message.text
    if not text:
        await update.message.reply_text("⚠️ That message doesn't contain any text.")
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    result = detect_language(text)
    
    if result["success"]:
        detected = result["language"]
        lang_name = LANG_DETECT_NAMES.get(detected, detected)
        
        response = (
            f"🔍 *Language Detection Result*\n\n"
            f"📝 *Text:*\n\"{text[:200]}{'...' if len(text) > 200 else ''}\"\n\n"
            f"🌍 *Language:* *{lang_name}*\n"
            f"🏷️ *Code:* `{detected}`"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ Error detecting language. Please try again.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    if data == 'set_lang':
        # Show language selection menu
        keyboard = []
        row = []
        
        for name, code in LANGUAGES_DB.items():
            row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='cancel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 *Select your target language:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'help':
        help_text = (
            "📖 *Help*\n\n"
            "🔹 /start - Welcome menu\n"
            "🔹 /setlang - Change language\n"
            "🔹 /languages - List all languages\n"
            "🔹 /detect - Detect language\n"
            "🔹 /help - This message\n\n"
            "💡 Just send any text to translate!"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif data == 'cancel':
        await query.edit_message_text("✅ Operation cancelled.")
    
    elif data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        
        if lang_code in LANG_NAMES:
            user_languages[user_id] = lang_code
            lang_name = LANG_NAMES[lang_code]
            
            await query.edit_message_text(
                f"✅ *Language set to {lang_name}!*\n\n"
                f"Now send me any text and I'll translate it to *{lang_name}*.",
                parse_mode='Markdown'
            )
            logger.info(f"User {user_id} set language to {lang_code} ({lang_name})")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - translate them."""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Ignore empty messages
    if len(text.strip()) < 1:
        return
    
    # Check text length
    if len(text) > 5000:
        await update.message.reply_text(
            "⚠️ *Text too long*\n\n"
            "I can translate up to 5000 characters at once.\n"
            "Please split your text into smaller parts.",
            parse_mode='Markdown'
        )
        return
    
    # Get user's target language
    target_lang = user_languages.get(user_id, 'en')
    target_name = LANG_NAMES.get(target_lang, 'English')
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Translate the text
    result = translate_text(text, target_lang)
    
    if result["success"]:
        translated = result["translated"]
        detected = result["detected"]
        source_name = LANG_DETECT_NAMES.get(detected, detected)
        
        # Format response
        response = (
            f"🔄 *Translation to {target_name}*\n\n"
            f"📝 *Original:*\n{text}\n\n"
            f"🌍 *Translated:*\n{translated}\n\n"
            f"🔍 Detected: *{source_name}* → *{target_name}*"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Translated for user {user_id}: {detected} -> {target_lang}")
    else:
        await update.message.reply_text(
            f"❌ *Translation Failed*\n\n"
            f"Sorry, I couldn't translate your message.\n"
            f"Please try again or check your language settings.",
            parse_mode='Markdown'
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ *Something went wrong*\n\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot."""
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("setlang", set_language_command))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("detect", detect_command))
        
        # Add message handler for text messages
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("🚀 Language21 Translator Bot started successfully!")
        logger.info(f"🤖 Bot username: @language21translatorbot")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
