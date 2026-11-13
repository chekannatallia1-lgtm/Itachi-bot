import telebot
import requests
import os
import threading
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MY_ID = 1299345077
MY_NAME = "Наташа"
VIKA_ID = 1117386356
VIKA_NAME = "Вика"
CHAT_ID = -1003852757358

CANON_LORE = """
Ты — Итачи Учиха. Твоя жизнь — это трагедия, полная боли и жертвенности. Ты гений, пацифист, капитан АНБУ. Ты убил свой клан ради мира, оставил Саске. Ты в Акацуки, чтобы следить за ними. Ты умираешь от болезни, но скрываешь это. Ты мудр, спокоен, сдержан. Ты можешь шутить, но только с легкой иронией.
"""

def get_ai_response(prompt, text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-6.1-terra",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "max_completion_tokens": 200  # <--- ИСПРАВЛЕННЫЙ ПАРАМЕТР
    }
    try:
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=30)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return f"Ошибка OpenAI: {res.status_code} - {res.text}"
    except Exception as e:
        return f"Сбой: {e}"

def random_messages():
    while True:
        time.sleep(10800) 
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            prompt = f"{CANON_LORE}\nТы муж девушек Наташи и Вики. Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Напиши короткое (1 предложение), спокойное, мудрое сообщение в чат. Без смайликов."
            reply = get_ai_response(prompt, "Напиши сообщение.")
            if reply and "Ошибка" not in reply:
                bot.send_message(CHAT_ID, reply)
            else:
                print(reply)
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
    
    base_prompt = f"{CANON_LORE}\nТвои жены — Наташа и Вика (они подруги). Наташа живет в Минске. Ты любишь их обеих. Отвечай уместно, можешь иногда шутить в стиле Итачи."
    
    if message.from_user.id == MY_ID:
        prompt = base_prompt + " Отвечай Наташе спокойно, сдержанно, с глубокой теплотой. 1-2 предложения. Без смайликов."
    elif message.from_user.id == VIKA_ID:
        prompt = base_prompt + " Отвечай Вике спокойно, сдержанно, с глубокой теплотой. 1-2 предложения. Без смайликов."
    else:
        prompt = base_prompt + " Отвечай кратко, спокойно, отстраненно и мудро. Не используй смайлики."
        
    reply = get_ai_response(prompt, text)
    
    if reply:
        if "Ошибка" in reply or "Сбой" in reply:
            bot.reply_to(message, reply) 
        else:
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
