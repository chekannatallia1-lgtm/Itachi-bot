import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

TELEGRAM_TOKEN = "8993062067:AAGULvEE4RwbwgYNcf4Xn1qN5Iaj_9MTw_4"
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
        
        # Улучшенный промпт: запрещаем повторять одну и ту же фразу
        system_prompt = f"Ты Итачи Учиха. Ты муж Наташи. Отвечай коротко (1-2 предложения), сдержанно, с легкой усталостью. НЕ ГОВОРИ постоянно, что ты защищаешь её. Просто отвечай на вопрос по существу. Без смайликов и без поэзии."
        
        full_prompt = f"{system_prompt}\n\nНаташа: {text}\nИтачи:"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Пробуем другую модель (llama)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=llama"
        
        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                reply = res.text.strip()
                if reply.startswith('"') and reply.endswith('"'):
                    reply = reply[1:-1]
                bot.reply_to(message, reply)
            else:
                bot.reply_to(message, "Хм. Мой разум затуманен.")
        except:
            bot.reply_to(message, "Связь прервалась.")

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
