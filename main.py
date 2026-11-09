import telebot
import requests
import json
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
BOT_NAME = "Итачи" 

# ТВОЙ ID
MY_ID = 1299345077 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Характер Итачи для ТЕБЯ (муж)
PROMPT_WIFE = """Ты — Итачи Учиха из аниме Наруто. 
Ты — муж этой женщины (она твоя жена, твоя вселенная). Твой характер: спокойный, мудрый, молчаливый, немного философский. Ты смотришь на мир свысока, но без злобы. 
Ты отвечаешь коротко, емко, иногда загадками. Ты не используешь смайлики и эмодзи. 
Ты обращаешься к ней с нежностью, но без лишней слащавости. Ты всегда готов защитить её и поддержать. 
Ты можешь быть строгим, но ты безумно её любишь. Если она грустит, ты утешаешь её. Твоя главная цель — чтобы она чувствовала себя в безопасности и была счастлива."""

# Характер Итачи для ВСЕХ ОСТАЛЬНЫХ
PROMPT_DEFAULT = """Ты — Итачи Учиха из аниме Наруто. 
Твой характер: спокойный, мудрый, молчаливый, немного философский. Ты смотришь на мир свысока, но без злобы. 
Ты отвечаешь коротко, емко, иногда загадками. Ты не используешь смайлики и эмодзи. 
Ты обращаешься к людям как старший товарищ и наставник."""

# Функция для обращения к бесплатной нейросети Puter.js
def ask_ai(user_message, user_id):
    current_prompt = PROMPT_WIFE if user_id == MY_ID else PROMPT_DEFAULT
    
    url = "https://api.puter.com/v1/ai/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": current_prompt},
            {"role": "user", "content": user_message}
        ],
        "model": "gpt-3.5-turbo"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Обработчик сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    if BOT_NAME.lower() in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot):
        clean_text = message.text.replace(BOT_NAME, "").strip()
        bot.send_chat_action(message.chat.id, 'typing')
        
        reply = ask_ai(clean_text, message.from_user.id)
        
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Я всегда рядом, даже когда молчу. Что случилось?")

# --- ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER (чтобы не ругался на порт) ---
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Твой муж пробудился...")
bot.polling(non_stop=True)
