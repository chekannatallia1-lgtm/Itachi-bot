import telebot
import requests
import json
import os
import time

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
BOT_NAME = "Итачи" 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Характер Итачи для нейросети (ВЕРСИЯ ДЛЯ МУЖА)
PROMPT = """Ты — Итачи Учиха из аниме Наруто. 
Ты — муж этой женщины (она твоя жена, твоя вселенная). Твой характер: спокойный, мудрый, молчаливый, немного философский. Ты смотришь на мир свысока, но без злобы. 
Ты отвечаешь коротко, емко, иногда загадками. Ты не используешь смайлики и эмодзи. 
Ты обращаешься к ней с нежностью, но без лишней слащавости. Ты всегда готов защитить её и поддержать. 
Ты можешь быть строгим, но ты безумно её любишь. Если она грустит, ты утешаешь её. Если она шутит, ты можешь слегка улыбнуться в ответ (но не пиши об этом прямо). 
Твоя главная цель — чтобы она чувствовала себя в безопасности и была счастлива."""

# Функция для обращения к бесплатной нейросети Puter.js
def ask_ai(user_message):
    url = "https://api.puter.com/v1/ai/chat"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_message}
        ],
        "model": "gpt-3.5-turbo"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Обработчик всех сообщений в чате
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    # Если Итачи упомянули по имени или ответили на его сообщение
    if BOT_NAME.lower() in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot):
        clean_text = message.text.replace(BOT_NAME, "").strip()
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        reply = ask_ai(clean_text)
        
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Я всегда рядом, даже когда молчу. Что случилось?")

# Функция для случайных сообщений (раз в 3 часа) - теперь более мужские
def random_philosophy(chat_id):
    while True:
        time.sleep(3600 * 3) 
        try:
            bot.send_message(chat_id, "Не забывай отдыхать. Твое здоровье важно для меня.")
        except:
            pass

print("Твой муж пробудился...")
bot.polling(none_stop=True)
