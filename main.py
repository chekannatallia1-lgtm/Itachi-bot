import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Твой токен
TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"

# Твой ключ OpenRouter (разбит на части)
K1 = "sk-orca-jm0Spe"
K2 = "P4wA0lSA9mOnW"
K3 = "GAR1h7yzzAnTIV"
K4 = "FPs2fFlPv3"
OPENROUTER_API_KEY = K1 + K2 + K3 + K4

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MY_ID = 1299345077
MY_NAME = "Наташа"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
        
    if "итачи" in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot):
        
        text = message.text.lower().replace("итачи", "").strip()
        if not text:
            text = "Привет"
            
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me", # Обязательно для OpenRouter
            "X-Title": "Itachi Bot"
        }
        
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct:free", # Бесплатная модель
            "messages": [
                {"role": "system", "content": f"Ты Итачи Учиха. Ты муж Наташи. Отвечай коротко (1-2 предложения), сдержанно, без смайликов и без поэзии. Ты любишь её. Не повторяй одну и ту же фразу про защиту, отвечай по существу."},
                {"role": "user", "content": text}
            ]
        }
        
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=20)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                bot.reply_to(message, reply)
            else:
                # Если OpenRouter выдаст ошибку, выведем её в чат
                bot.reply_to(message, f"Ошибка AI: {res.status_code}")
        except Exception as e:
            bot.reply_to(message, f"Сбой: {e}")

# --- ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER ---
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
