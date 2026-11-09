import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"
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
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": f"Ты персонаж Итачи Учиха из Наруто. Ты муж Наташи. Отвечай кратко, спокойно, мудро. Обращайся к Наташе. Без смайликов и без стихов."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 150
        }
        
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=20)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                # Проверка: если нейросеть вернула пустоту, пишем заглушку
                if not reply or len(reply.strip()) == 0:
                    reply = "Хм. Кажется, я задумался. Спроси меня о чем-нибудь другом."
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
