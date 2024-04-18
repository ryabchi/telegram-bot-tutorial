import base64

bot_secret = ''

TELEGRAM_BOT_TOKEN = base64.b64decode(bot_secret).decode()
