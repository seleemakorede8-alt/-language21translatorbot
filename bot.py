import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from googletrans import Translator, LANGUAGES

# ==================== CONFIGURATION ====================

# Environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable is not set!")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# User language preferences (in-memory cache)
user_languages: Dict[str, str] = {}

# Language database with names and codes
LANGUAGES_DB = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Chinese (Simplified)': 'zh-cn',
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

# Reverse mapping for display
LANG_NAMES = {v: k for k, v in LANGUAGES_DB.items()}

# ==================== HELPER FUNCTIONS ====================

def get_user_language(user_id: str) -> str:
    """Get user's preferred language or default to English."""
    return user_languages.get(user_id, 'en')

def get_language_name(lang_code: str) -> str:
    """Get display name for language code."""
    return LANG_NAMES.get(lang_code, 'English')

def format_translation_result(text: str, translated: str, source_lang: str, target_lang: str) -> str:
    """Format the translation result message."""
    source_name = LANGUAGES.get(source_lang, source_lang).title()
    target_name = get_language_name(target_lang)
    
    return (
        f"🔄 *Translation Complete*\n\n"
        f"📝 *Original:*\n{text}\n\n"
        f"🌍 *Translated to {target_name}:*\n{translated}\n\n"
        f"🔍 Detected: *{source_name}* → *{target_name}*"
    )

# ==================== BOT COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_id = str(user.id)
    current_lang = get_user_language(user_id)
    current_lang_name = get_language_name(current_lang)
    
    keyboard = [
        [InlineKeyboardButton("🌍 Set Language", callback_data='set_lang')],
        [InlineKeyboardButton("📖 Help", callback_data='help')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 *Hello {user.first_name}!*\n\n"
        f"I'm your *Language21 Translator Bot* 🌐\n"
        f"I can translate text between 25+ languages instantly!\n\n"
        f"✨ *Quick Commands:*\n"
        f"• Send any text to translate it\n"
        f"• /setlang - Choose your target language\n"
        f"• /languages - See all available languages\n"
        f"• /detect - Detect language of a message\n"
        f"• /help - Get detailed help\n\n"
        f"📍 *Your current target language:* *{current_lang_name}*"
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
        "🔹 `/help` - Show this help message\n"
        "🔹 `/about` - About this bot\n\n"
        "💡 *How to use:*\n"
        "1. Set your target language with /setlang\n"
        "2. Send any text message\n"
        "3. I'll translate it to your chosen language!\n\n"
        "🔄 *Pro tip:* You can reply to a message and use /detect\n"
        "to find out what language it's written in."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    about_text = (
        "ℹ️ *About Language21 Translator Bot*\n\n"
        "🌐 *Version:* 2.0.0\n"
        "🔧 *Powered by:* Google Translate API\n"
        "📚 *Languages:* 25+ supported\n"
        "👨‍💻 *Created for:* Language21 Project\n"
        "🚀 *Deployed on:* Railway\n\n"
        "✨ *Features:*\n"
        "• Instant text translation\n"
        "• Language detection\n"
        "• 25+ languages supported\n"
        "• User-specific preferences\n"
        "• Interactive keyboard menus\n\n"
        "📝 *Source code:*\n"
        "Available on GitHub\n\n"
        "Made with ❤️ by the Language21 Team"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')


async def set_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlang command - Show language selection."""
    keyboard = []
    row = []
    
    # Create 2-column layout
    for name, code in LANGUAGES_DB.items():
        row.append(InlineKeyboardButton(name, callback_data=f'lang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='cancel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 *Select your target language:*\n\n"
        "Choose the language you want your text translated into.\n"
        "This setting will be saved for your account.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command - List all languages."""
    # Split languages into chunks for readability
    lang_list = sorted(LANGUAGES_DB.keys())
    chunks = [lang_list[i:i+10] for i in range(0, len(lang_list), 10)]
    
    message = "🌍 *Available Languages:*\n\n"
    for i, chunk in enumerate(chunks, 1):
        message += f"📌 *Group {i}:*\n"
        for lang in chunk:
            message += f"• {lang}\n"
        message += "\n"
    
    message += f"*Total:* {len(lang_list)} languages supported"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /detect command - Detect language of replied message."""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ *Please reply to a message* to detect its language.\n\n"
            "Example: Reply to a message and send /detect",
            parse_mode='Markdown'
        )
        return
    
    text = update.message.reply_to_message.text
    if not text:
        await update.message.reply_text(
            "⚠️ That message doesn't contain any text to detect.",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Detect language
        detection = translator.detect(text)
        lang_name = LANGUAGES.get(detection.lang, detection.lang).title()
        confidence = detection.confidence * 100
        
        response = (
            f"🔍 *Language Detection Result*\n\n"
            f"📝 *Text:*\n\"{text[:200]}{'...' if len(text) > 200 else ''}\"\n\n"
            f"🌍 *Detected Language:* *{lang_name}*\n"
            f"🏷️ *Language Code:* `{detection.lang}`\n"
            f"📊 *Confidence:* {confidence:.1f}%\n\n"
            f"💡 *Tip:* Use /setlang to set your translation target!"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Detected language {detection.lang} with {confidence:.1f}% confidence")
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        await update.message.reply_text(
            f"❌ Error detecting language. Please try again.\n\n"
            f"Error: {str(e)}",
            parse_mode='Markdown'
        )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command."""
    await update.message.reply_text(
        "✅ *Operation cancelled*\n\n"
        "Your language preference remains unchanged.",
        parse_mode='Markdown'
    )


# ==================== CALLBACK QUERY HANDLER ====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    logger.info(f"Callback received: {data} from user {user_id}")
    
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
            "📖 *Help & Commands*\n\n"
            "🔹 `/start` - Show welcome menu\n"
            "🔹 `/setlang` - Change your target language\n"
            "🔹 `/languages` - List all available languages\n"
            "🔹 `/detect` - Detect language of replied message\n"
            "🔹 `/help` - Show this help message\n"
            "🔹 `/about` - About this bot\n\n"
            "💡 *Quick Tip:*\n"
            "Just send any text and I'll translate it automatically!"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif data == 'about':
        about_text = (
            "ℹ️ *About Language21 Translator Bot*\n\n"
            "🌐 *Version:* 2.0.0\n"
            "🔧 *Powered by:* Google Translate\n"
            "📚 *Languages:* 25+ supported\n"
            "👨‍💻 *Project:* Language21\n\n"
            "✨ *Features:*\n"
            "• Instant translation\n"
            "• Language detection\n"
            "• 25+ languages\n"
            "• User preferences\n"
            "• Interactive menus"
        )
        await query.edit_message_text(about_text, parse_mode='Markdown')
    
    elif data == 'cancel':
        await query.edit_message_text(
            "✅ Operation cancelled.\n\n"
            "Your language preference remains unchanged."
        )
    
    elif data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        
        if lang_code in LANG_NAMES:
            user_languages[user_id] = lang_code
            lang_name = LANG_NAMES[lang_code]
            
            await query.edit_message_text(
                f"✅ *Language set to {lang_name}!*\n\n"
                f"Now send me any text and I'll translate it to *{lang_name}*.\n"
                f"📍 Your preference has been saved.",
                parse_mode='Markdown'
            )
            logger.info(f"User {user_id} set language to {lang_code} ({lang_name})")
        else:
            await query.edit_message_text(
                "❌ Invalid language selection.\n\n"
                "Please try again using /setlang."
            )


# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages - Translate them."""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Ignore messages that are too short or too long
    if len(text.strip()) < 1:
        return
    
    if len(text) > 5000:
        await update.message.reply_text(
            "⚠️ *Text too long*\n\n"
            "I can translate up to 5000 characters at once.\n"
            "Please split your text into smaller parts.",
            parse_mode='Markdown'
        )
        return
    
    # Get user's target language
    target_lang = get_user_language(user_id)
    target_name = get_language_name(target_lang)
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Translate
        result = translator.translate(text, dest=target_lang)
        
        # Detect source language
        detection = translator.detect(text)
        source_lang = detection.lang
        source_name = LANGUAGES.get(source_lang, source_lang).title()
        
        # Format response
        response = (
            f"🔄 *Translation*\n\n"
            f"📝 *Original:*\n{text}\n\n"
            f"🌍 *Translated to {target_name}:*\n{result.text}\n\n"
            f"🔍 Detected: *{source_name}* → *{target_name}*"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Translated message for user {user_id}: {source_lang} -> {target_lang}")
        
    except Exception as e:
        logger.error(f"Translation error for user {user_id}: {e}")
        await update.message.reply_text(
            f"❌ *Translation Failed*\n\n"
            f"Sorry, I couldn't translate your message.\n"
            f"Please try again or check your language settings.\n\n"
            f"Error: {str(e)[:100]}",
            parse_mode='Markdown'
        )


# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ *Something went wrong*\n\n"
                "Please try again later.\n"
                "If the problem persists, contact the bot administrator.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("setlang", set_language_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("detect", detect_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Add message handler for text messages (with higher priority for commands)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Add callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 Language21 Translator Bot started successfully!")
    logger.info(f"🤖 Bot username: @language21translatorbot")
    logger.info(f"📊 User languages in memory: {len(user_languages)}")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
