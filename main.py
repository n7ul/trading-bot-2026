import telebot
from flask import Flask
from threading import Thread
import requests
import time
import os

# استخدام المتغيرات من إعدادات السيرفر
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
bot = telebot.TeleBot(BOT_TOKEN)

# إعداد السيرفر للبقاء نشطاً 24/7
app = Flask('')
@app.route('/')
def home(): return "Trading Bot Active!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()

# قائمة العملات الـ 10 المختارة
symbols = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 
    'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'LINKUSDT', 
    'MATICUSDT', 'DOTUSDT'
]
prices = {symbol: [] for symbol in symbols}

def send_alert(symbol, side, price):
    # استخدام 0.01 كنسبة للـ SL و TP (أي 1%)
    sl = price * 0.99 if side == "BUY" else price * 1.01
    tp = price * 1.01 if side == "BUY" else price * 0.99
    
    msg = f"🔔 {side} Signal: {symbol}\nPrice: {price:.4f}\nSL: {sl:.4f}\nTP: {tp:.4f}"
    try:
        bot.send_message(CHAT_ID, msg)
    except Exception as e:
        print(f"Telegram Error: {e}")

# حلقة التداول
while True:
    for symbol in symbols:
        try:
            res = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
            data = res.json()
            if 'price' in data:
                price = float(data['price'])
                prices[symbol].append(price)
                if len(prices[symbol]) > 50: prices[symbol].pop(0)

                # تحليل البيانات بعد جمع 50 قراءة
                if len(prices[symbol]) >= 50:
                    avg = sum(prices[symbol]) / 50
                    # شرط التحرك بنسبة 0.01 (0.0001)
                    diff = abs(price - avg) / avg
                    if diff >= 0.0001: 
                        side = "BUY" if price > avg else "SELL"
                        send_alert(symbol, side, price)
                        print(f"Sent {side} alert for {symbol} at {price:.4f}")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    time.sleep(60) # فحص السوق كل دقيقة
