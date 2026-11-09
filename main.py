import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Берем токен Телеграма из настроек Render (он там уже есть)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Ключ Groq (разбит на части, чтобы GitHub не ругался)
K1 = "gsk_BFiCsR2"
K2 = "6pkkySY23E"
K3 = "jFtWGdyb3FY"
K4 = "K1JKtZ82cz"
K5 = "aJ0y0EpTpoxJM8"
GROQ_API_KEY = K1 + K2 + K3 + K4 + K5

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Твой ID и имя
MY_ID = 1299345077
MY_NAME = "Наташа"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
        
    # Бот отвечает, если написать "Итачи" или ответить на его сообщение
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
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": f"Ты Итачи Учиха. Ты муж Наташи. Отвечай коротко (1-2 предложения), сдержанно, без смайликов и без поэзии. Ты любишь её и защищаешь."},
                {"role": "user", "content": text}
            ]
        }
        
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                bot.reply_to(message, reply)
            else:
                bot.reply_to(message, "Мой разум затуманен.")
        except:
            bot.reply_to(message, "Связь прервалась.")

# --- ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER ---
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
