import telebot
from flask import Flask
from threading import Thread
import requests
import time
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
bot = telebot.TeleBot(BOT_TOKEN)

# سيرفر البقاء نشطاً
app = Flask('')
@app.route('/')
def home(): return "Trading Bot Active!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'LINKUSDT', 'MATICUSDT', 'DOTUSDT']
prices = {symbol: [] for symbol in symbols}

def get_rsi(prices_list, period=14):
    if len(prices_list) < period + 1: return 50
    deltas = [prices_list[i+1] - prices_list[i] for i in range(len(prices_list)-1)]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def send_alert(symbol, side, price):
    msg = f"🚀 {side} Signal: {symbol}\nPrice: {price:.4f}\nالهدف: جني أرباح ذكي"
    try: bot.send_message(CHAT_ID, msg)
    except Exception as e: print(e)

while True:
    for symbol in symbols:
        try:
            res = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
            price = float(res.json()['price'])
            prices[symbol].append(price)
            if len(prices[symbol]) > 50: prices[symbol].pop(0)

            if len(prices[symbol]) >= 15:
                rsi = get_rsi(prices[symbol])
                # الاستراتيجية الذكية:
                # اشتري فقط إذا كان السوق في منطقة "تشبع بيعي" (RSI < 30)
                if rsi < 30:
                    send_alert(symbol, "BUY (فرصة شراء قوية)", price)
                # بع فقط إذا كان السوق في منطقة "تشبع شرائي" (RSI > 70)
                elif rsi > 70:
                    send_alert(symbol, "SELL (فرصة بيع قوية)", price)
        except: continue
    time.sleep(60)
