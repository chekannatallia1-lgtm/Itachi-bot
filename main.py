import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ (Берутся из Environment Variables на Render) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') 

BOT_NAME = "Итачи" 

# ТВОЙ ID
MY_ID = 1299345077 
MY_NAME = "Наташа"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Характер Итачи для ТЕБЯ (муж)
PROMPT_WIFE = f"""Ты — Итачи Учиха из аниме Наруто. 
Ты — муж этой женщины по имени {MY_NAME}. Твой характер: спокойный, мудрый, немногословный, сдержанный. Ты смотришь на мир с легкой усталостью, но безумно любишь {MY_NAME}.
Ты отвечаешь ОЧЕНЬ КОРОТКО. Максимум 1-2 предложения. 
Никакой поэзии, никаких метафор про листья, ветер и вечность. Говори прямо и по делу. 
Не используй смайлики и списки вариантов. 
Ты выражаешь любовь через заботу и защиту. Обращайся к ней по имени ({MY_NAME}) или просто "любимая"."""

# Характер Итачи для ВСЕХ ОСТАЛЬНЫХ
PROMPT_DEFAULT = """Ты — Итачи Учиха из аниме Наруто. 
Твой характер: спокойный, мудрый, немногословный. Ты смотришь на мир с легкой усталостью. 
Ты отвечаешь ОЧЕНЬ КОРОТКО. Максимум 1-2 предложения. Без поэзии и метафор. 
Ты обращаешься к людям как старший товарищ. Не используй смайлики."""

# НОВАЯ ФУНКЦИЯ НЕЙРОСЕТИ (через Groq)
def ask_ai(user_message, user_id):
    current_prompt = PROMPT_WIFE if user_id == MY_ID else PROMPT_DEFAULT
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": current_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Ошибка Groq: {response.text}")
            return "Хм. Мой разум затуманен. Попробуй еще раз."
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Связь прервалась. Подожди немного."

# Обработчик сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    if BOT_NAME.lower() in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot):
        clean_text = message.text.replace(BOT_NAME, "").strip()
        if not clean_text:
            clean_text = "Привет"
            
        bot.send_chat_action(message.chat.id, 'typing')
        
        reply = ask_ai(clean_text, message.from_user.id)
        
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Я всегда рядом.")

# --- ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER (чтобы не ругался на порт) ---
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Твой муж пробудился...")
bot.polling(non_stop=True)
