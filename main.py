import telebot
import os
from flask import Flask
from threading import Thread

# استخدام المتغيرات البيئية من إعدادات Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000) # Render يحتاج البورت 10000

if __name__ == '__main__':
    Thread(target=run).start()
    bot.polling()
