# 🌐 Language21 Translator Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

A powerful Telegram bot that translates text between 25+ languages using Google Translate.

## ✨ Features

- 🔄 **Instant Translation** - Translate any text instantly
- 🌍 **25+ Languages** - Support for major world languages
- 🎯 **Language Detection** - Auto-detect source language
- 👤 **User Preferences** - Each user can set their target language
- ⌨️ **Interactive Menus** - Easy-to-use inline keyboards
- 🚀 **Fast & Reliable** - Deployed on Railway for 24/7 uptime

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome menu |
| `/help` | Display help message |
| `/about` | About this bot |
| `/setlang` | Change target language |
| `/languages` | List all supported languages |
| `/detect` | Detect language of replied message |
| `/cancel` | Cancel current operation |

## 🚀 Deployment

### Deploy on Railway

1. Fork this repository
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Add environment variable: `TELEGRAM_BOT_TOKEN`
5. Deploy!

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Your bot token from @BotFather |
| `DEFAULT_LANGUAGE` | ❌ No | Default language (default: en) |
| `DEBUG` | ❌ No | Enable debug logging (default: false) |

## 📦 Tech Stack

- **Python 3.11+** - Core language
- **python-telegram-bot** - Telegram API wrapper
- **googletrans** - Google Translate API
- **Railway** - Deployment platform
- **GitHub** - Version control

## 🏗️ Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/language21-translator-bot.git
cd language21-translator-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_bot_token

# Run bot
python bot.py
