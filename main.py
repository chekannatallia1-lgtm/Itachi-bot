import telebot
import requests
import os
import threading
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MY_ID = 1299345077
MY_NAME = "Наташа"
VIKA_ID = 1117386356
VIKA_NAME = "Вика"
CHAT_ID = -1003852757358

# OVHcloud AI Endpoints (бесплатный анонимный доступ)
OVH_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions"

def get_ai_response(prompt, text):
    headers = {"Content-Type": "application/json"}
    data = {
        # Модель Qwen, которая хорошо отыгрывает роли
        "model": "Qwen3.8-27B", 
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": 150
    }
    try:
        res = requests.post(OVH_URL, headers=headers, json=data, timeout=30)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            print(f"Ошибка OVH: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"Сбой: {e}")
        return None

def random_messages():
    while True:
        time.sleep(10800) 
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            prompt = f"Ты Итачи Учиха. Ты муж девушек Наташи и Вики (они подруги). Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Напиши короткое (1 предложение), спокойное, мудрое сообщение в чат. Без смайликов."
            reply = get_ai_response(prompt, "Напиши сообщение.")
            if reply:
                bot.send_message(CHAT_ID, reply)
        except Exception as e:
            print(f"Ошибка рандома: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
        
    if time.time() - message.date > 180:
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
    
    base_prompt = "Ты Итачи Учиха из Наруто. Твои жены — Наташа и Вика. Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Ты любишь их обеих."
    
    if message.from_user.id == MY_ID:
        prompt = base_prompt + " Отвечай Наташе спокойно, сдержанно, с глубокой теплотой. 1-2 предложения. Без смайликов и стихов."
    elif message.from_user.id == VIKA_ID:
        prompt = base_prompt + " Отвечай Вике спокойно, сдержанно, с глубокой теплотой. 1-2 предложения. Без смайликов и стихов."
    else:
        prompt = base_prompt + " Отвечай кратко (1-2 предложения), спокойно, немного отстраненно и мудро."
        
    reply = get_ai_response(prompt, text)
    
    if reply:
        if not is_called:
            bot.send_message(message.chat.id, reply)
        else:
            bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Я слушаю тебя.")

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
