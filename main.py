import telebot
import requests
import os
import threading
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MY_ID = 1299345077
MY_NAME = "Наташа"
VIKA_ID = 1117386356
VIKA_NAME = "Вика"
CHAT_ID = -1003852757358

# === ПАМЯТЬ БОТА (История диалогов) ===
# Ключ — ID чата, значение — список сообщений
dialogue_history = {}
MAX_HISTORY = 10  # Сколько последних сообщений помнить

CANON_LORE = """
Ты — Итачи Учиха. Твоя жизнь — это трагедия, полная боли и жертвенности. Ты гений, пацифист, капитан АНБУ. Ты убил свой клан ради мира, оставил Саске. Ты в Акацуки, чтобы следить за ними. Ты умираешь от болезни, но скрываешь это. Ты мудр, спокоен, сдержан. Ты можешь шутить, но только с легкой иронией.
"""

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

def send_long_message(chat_id, text, reply_to=None):
    limit = 4000 
    if len(text) <= limit:
        if reply_to:
            bot.reply_to(reply_to, text)
        else:
            bot.send_message(chat_id, text)
    else:
        chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
        for i, chunk in enumerate(chunks):
            if i == 0 and reply_to:
                bot.reply_to(reply_to, chunk)
            else:
                bot.send_message(chat_id, chunk)
            time.sleep(0.5)

def get_ai_response(chat_id, user_id, text):
    # Получаем историю для этого чата (или создаем новую)
    if chat_id not in dialogue_history:
        dialogue_history[chat_id] = []
    
    history = dialogue_history[chat_id]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Формируем системный промпт в зависимости от пользователя
    base_prompt = f"{CANON_LORE}\nТвои жены — Наташа и Вика (они подруги). Наташа живет в Минске. Ты любишь их обеих. Отвечай уместно, можешь иногда шутить в стиле Итачи."
    
    if user_id == MY_ID:
        prompt = base_prompt + " Отвечай Наташе спокойно, сдержанно, с глубокой теплотой. Без смайликов."
    elif user_id == VIKA_ID:
        prompt = base_prompt + " Отвечай Вике спокойно, сдержанно, с глубокой теплотой. Без смайликов."
    else:
        prompt = base_prompt + " Отвечай кратко, спокойно, отстраненно и мудро. Не используй смайлики."

    # Собираем сообщения для отправки: Системный промпт + История + Новое сообщение
    messages = [{"role": "system", "content": prompt}]
    
    # Добавляем историю (последние MAX_HISTORY сообщений)
    messages.extend(history[-MAX_HISTORY:])
    
    # Добавляем текущее сообщение пользователя
    messages.append({"role": "user", "content": text})

    data = {
        "model": "gpt-6.1-terra",
        "messages": messages,
        "max_completion_tokens": 1500
    }
    
    try:
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=60)
        if res.status_code == 200:
            raw_reply = res.json()['choices'][0]['message']['content']
            clean_reply = clean_response(raw_reply)
            
            if clean_reply:
                # СОХРАНЯЕМ В ПАМЯТЬ: сообщение пользователя и ответ бота
                history.append({"role": "user", "content": text})
                history.append({"role": "assistant", "content": clean_reply})
                
                # Если история стала слишком длинной, обрезаем старые сообщения
                if len(history) > MAX_HISTORY * 2:
                    dialogue_history[chat_id] = history[-(MAX_HISTORY * 2):]
                    
            return clean_reply
        else:
            return f"Ошибка OpenAI: {res.status_code}"
    except Exception as e:
        return f"Сбой: {e}"

def random_messages():
    while True:
        time.sleep(10800) 
        try:
            bot.send_chat_action(CHAT_ID, 'typing')
            # Для случайных сообщений используем отдельный, простой промпт (без истории)
            prompt = f"{CANON_LORE}\nТы муж девушек Наташи и Вики. Наташа живет в Минске, у неё есть кот Яхве и свинка Чипс. Напиши короткое (1 предложение), спокойное, мудрое сообщение в чат. Без смайликов."
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-6.1-terra",
                "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": "Напиши сообщение."}],
                "max_completion_tokens": 100
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=30)
            if res.status_code == 200:
                reply = clean_response(res.json()['choices'][0]['message']['content'])
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
    
    # Передаем ID чата, ID пользователя и текст в функцию запроса
    reply = get_ai_response(message.chat.id, message.from_user.id, text)
    
    if reply:
        if "Ошибка" in reply or "Сбой" in reply:
            bot.reply_to(message, reply) 
        else:
            if not is_called:
                send_long_message(message.chat.id, reply)
            else:
                send_long_message(message.chat.id, reply, reply_to=message)

def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
threading.Thread(target=random_messages, daemon=True).start()

print("Итачи готов (с памятью)!")
bot.polling(non_stop=True)
