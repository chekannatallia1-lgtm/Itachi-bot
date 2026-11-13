import telebot
import requests
import os
import threading
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

# === БЕЗОПАСНОСТЬ ===
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === ТВОИ ДАННЫЕ ===
MY_ID = 1299345077
MY_NAME = "Наташа"
VIKA_ID = 1117386356
VIKA_NAME = "Вика"
CHAT_ID = -1003852757358

# === КАНОНИЧНЫЙ ЛОР ИТАЧИ ===
CANON_LORE = """
Ты — Итачи Учиха. Твоя жизнь — это трагедия, полная боли и жертвенности. Ты гений, пацифист, капитан АНБУ. Ты убил свой клан ради мира, оставил Саске. Ты в Акацуки, чтобы следить за ними. Ты умираешь от болезни, но скрываешь это. Ты мудр, спокоен, сдержан. Ты можешь шутить, но только с легкой иронией.
"""

# === ФИЛЬТР РЕКЛАМЫ ===
def clean_response(text):
    if not text:
        return None
    
    ad_markers = [
        "реклама", "промокод", "подпишись", "переходи по ссылке", 
        "спонсор", "https://", "http://", "t.me/", "@", 
        "купить", "скидка", "бесплатно", "канал", "подписывайтесь"
    ]
    
    for marker in ad_markers:
        if marker in text.lower():
            parts = text.lower().split(marker)
            if parts[0].strip():
                text = text[:len(parts[0])].strip()
            else:
                return None
                
    text = text.strip('"').strip("'").strip()
    
    if len(text) < 2:
        return None
    return text

# === ФУНКЦИЯ РАЗБИВКИ ДЛИННЫХ СООБЩЕНИЙ ===
def send_long_message(chat_id, text, reply_to=None):
    # Телеграм разрешает максимум 4096 символов
    limit = 4000 
    if len(text) <= limit:
        if reply_to:
            bot.reply_to(reply_to, text)
        else:
            bot.send_message(chat_id, text)
    else:
        # Разбиваем текст на части
        chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
        for i, chunk in enumerate(chunks):
            if i == 0 and reply_to:
                bot.reply_to(reply_to, chunk)
            else:
                bot.send_message(chat_id, chunk)
            time.sleep(0.5) # Пауза между сообщениями, чтобы они шли по порядку

# === ЗАПРОС К НЕЙРОСЕТИ ===
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
        "max_completion_tokens": 1500 # УВЕЛИЧЕНО ДЛЯ ДЛИННЫХ ОТВЕТОВ
    }
    try:
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=60)
        if res.status_code == 200:
            raw_reply = res.json()['choices'][0]['message']['content']
            return clean_response(raw_reply)
        else:
            return f"Ошибка OpenAI: {res.status_code}"
    except Exception as e:
        return f"Сбой: {e}"

# === СЛУЧАЙНЫЕ СООБЩЕНИЯ ===
def random_messages():
    while True:
        time.sleep(10800) 
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            prompt = f"{CANON_LORE}\nТы муж девушек Наташи и Вики. Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Напиши короткое (1 предложение), спокойное, мудрое сообщение в чат. Без смайликов."
            reply = get_ai_response(prompt, "Напиши сообщение.")
            if reply:
                send_long_message(CHAT_ID, reply)
        except Exception as e:
            print(f"Ошибка рандома: {e}")

# === ОБРАБОТЧИК СООБЩЕНИЙ ===
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
    
    base_prompt = f"{CANON_LORE}\nТвои жены — Наташа и Вика (они подруги). Наташа живет в Минске. Ты любишь их обеих. Отвечай уместно, можешь иногда шутить в стиле Итачи. Ты можешь давать развернутые ответы, если тебя об этом просят."
    
    if message.from_user.id == MY_ID:
        prompt = base_prompt + " Отвечай Наташе спокойно, сдержанно, с глубокой теплотой. Без смайликов."
    elif message.from_user.id == VIKA_ID:
        prompt = base_prompt + " Отвечай Вике спокойно, сдержанно, с глубокой теплотой. Без смайликов."
    else:
        prompt = base_prompt + " Отвечай кратко, спокойно, отстраненно и мудро. Не используй смайлики."
        
    reply = get_ai_response(prompt, text)
    
    if reply:
        if "Ошибка" in reply or "Сбой" in reply:
            bot.reply_to(message, reply) 
        else:
            if not is_called:
                send_long_message(message.chat.id, reply)
            else:
                send_long_message(message.chat.id, reply, reply_to=message)

# === ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER ===
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов!")
bot.polling(non_stop=True)
