import telebot
import requests
import os
import threading
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MY_ID = 1299345077
MY_NAME = "Наташа"
CHAT_ID = -1003852757358  # ID твоего чата

# Функция для случайных сообщений по таймеру (раз в 3 часа)
def random_messages():
    while True:
        time.sleep(10800) # 3 часа
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {"role": "system", "content": f"Ты Итачи Учиха. Ты муж Наташи. Напиши короткое (1 предложение) философское или заботливое сообщение для чата, чтобы просто напомнить о себе. Без смайликов."},
                    {"role": "user", "content": "Напиши сообщение."}
                ],
                "max_tokens": 50
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                if reply:
                    bot.send_message(CHAT_ID, reply)
        except Exception as e:
            print(f"Ошибка рандома: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    # Проверяем, есть ли в сообщении имя или это ответ на сообщение бота
    is_called = "итачи" in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot)
    
    # Если его не позвали, то он отвечает случайно (шанс 15%) и только в том чате
    if not is_called:
        if message.chat.id == CHAT_ID and random.random() < 0.15:
            pass # Он решает вклиниться в беседу!
        else:
            return # Иначе он молчит
            
    text = message.text.lower().replace("итачи", "").strip()
    if not text:
        text = "Привет"
        
    bot.send_chat_action(message.chat.id, 'typing')
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if message.from_user.id == MY_ID:
        prompt = f"Ты Итачи Учиха. Ты муж Наташи. Отвечай кратко (1-2 предложения), спокойно, с теплотой и любовью. Обращайся к ней по имени или 'любимая'. Без смайликов и стихов."
    else:
        prompt = f"Ты Итачи Учиха из аниме Наруто. Отвечай кратко (1-2 предложения), спокойно, немного отстраненно и мудро. Не используй смайлики."
        
    data = {
        "model": "qwen/qwen3.8-27b",
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
            # Если он вклинился случайно, лучше не делать реплай, а просто написать в чат
            if not is_called:
                bot.send_message(message.chat.id, reply)
            else:
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
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
