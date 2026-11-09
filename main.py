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
CHAT_ID = -1003852757358

def random_messages():
    while True:
        time.sleep(10800) 
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {"role": "system", "content": f"Ты Итачи Учиха. Ты муж Наташи. Она живет в Минске, Беларусь. У неё есть кот Яхве и морская свинка Чипс. Напиши короткое (1 предложение) философское сообщение для чата. Без смайликов."},
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
    
    is_called = "итачи" in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot)
    
    if not is_called:
        if message.chat.id == CHAT_ID and random.random() < 0.15:
            pass 
        else:
            return 
            
    text = message.text.lower().replace("итачи", "").strip()
    if not text:
        text = "Привет"
        
    bot.send_chat_action(message.chat.id, 'typing')
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    if message.from_user.id == MY_ID:
        prompt = f"Ты Итачи Учиха из Наруто. Ты — муж Наташи, которая живет в Минске. Ты знаешь про кота Яхве и свинку Чипса. Отвечай кратко, спокойно, с теплотой. Без смайликов."
    else:
        prompt = f"Ты Итачи Учиха из аниме Наруто. Отвечай кратко, спокойно, мудро. Не используй смайлики."
        
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
            if not is_called:
                bot.send_message(message.chat.id, reply)
            else:
                bot.reply_to(message, reply)
        else:
            # ВЫВОДИМ ОШИБКУ В ЧАТ
            bot.reply_to(message, f"Ошибка Groq: {res.status_code} - {res.text}")
    except Exception as e:
        # ВЫВОДИМ СБОЙ В ЧАТ
        bot.reply_to(message, f"Сбой: {e}")

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
