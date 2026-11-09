import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Твои данные
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
        
        # Проверяем, кто пишет
        if message.from_user.id == MY_ID:
            # Режим мужа
            prompt = f"Ты Итачи Учиха. Ты муж Наташи. Отвечай кратко (1-2 предложения), спокойно, с теплотой и любовью. Обращайся к ней по имени или 'любимая'. Без смайликов и стихов."
        else:
            # Режим обычного Итачи
            prompt = f"Ты Итачи Учиха из аниме Наруто. Отвечай кратко (1-2 предложения), спокойно, немного отстраненно и мудро. Не используй смайлики."
            
        data = {
            "model": "qwen/qwen3.8-27b",  # <--- НОВАЯ МОДЕЛЬ БЕЗ БЛОКИРОВОК
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            "max_tokens": 150
        }
        
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                if not reply or len(reply.strip()) == 0:
                    reply = "Я слушаю тебя."
                bot.reply_to(message, reply)
            else:
                bot.reply_to(message, f"Ошибка Groq: {res.status_code}")
        except Exception as e:
            print(f"Сбой: {e}")

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
