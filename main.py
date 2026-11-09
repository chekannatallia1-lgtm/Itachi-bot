import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Твой токен
TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"

# Твой ключ Groq (одной строкой)
GROQ_API_KEY = "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"

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
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-70b-8192",  # <--- ТУТ АКТУАЛЬНАЯ МОДЕЛЬ
            "messages": [
                {"role": "system", "content": f"Ты Итачи Учиха. Ты муж Наташи. Отвечай коротко (1-2 предложения), сдержанно, без смайликов и без поэзии. Ты любишь её. Не повторяй одну и ту же фразу про защиту, отвечай по существу."},
                {"role": "user", "content": text}
            ]
        }
        
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                bot.reply_to(message, reply)
            else:
                bot.reply_to(message, f"Ошибка Groq: {res.status_code}")
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
