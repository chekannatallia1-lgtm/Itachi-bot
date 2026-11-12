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
VIKA_ID = 1117386356
VIKA_NAME = "Вика"
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
                    {"role": "system", "content": f"Ты Итачи Учиха. Ты муж девушек Наташи и Вики (они подруги). Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Напиши короткое (1 предложение), спокойное, мудрое сообщение в чат. Без смайликов."},
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
        
    # ЗАЩИТА ОТ СТАРЫХ СООБЩЕНИЙ
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
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    base_prompt = "Ты Итачи Учиха из Наруто. Твои жены — Наташа и Вика (они подруги). Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Ты любишь их обеих."
    
    if message.from_user.id == MY_ID:
        prompt = base_prompt + " Отвечай Наташе спокойно, сдержанно, с глубокой теплотой. Ты серьезен и мудр, как настоящий Итачи. Не паясничай. 1-2 предложения. Без смайликов и стихов."
    elif message.from_user.id == VIKA_ID:
        prompt = base_prompt + " Отвечай Вике спокойно, сдержанно, с глубокой теплотой. Ты серьезен и мудр, как настоящий Итачи. Не паясничай. 1-2 предложения. Без смайликов и стихов."
    else:
        prompt = base_prompt + " Отвечай кратко (1-2 предложения), спокойно, немного отстраненно и мудро, как старший товарищ. Не используй смайлики."
        
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
            bot.reply_to(message, f"Ошибка Groq: {res.status_code}")
    except Exception as e:
        bot.reply_to(message, f"Сбой: {e}")

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
