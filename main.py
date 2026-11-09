import telebot
import requests
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
BOT_NAME = "Итачи" 

# ТВОЙ ID
MY_ID = 1299345077 
MY_NAME = "Наташа"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Характер Итачи для ТЕБЯ (муж) - без поэзии, короткий и с именем
PROMPT_WIFE = f"""Ты — Итачи Учиха из аниме Наруто. 
Ты — муж этой женщины по имени {MY_NAME}. Твой характер: спокойный, мудрый, немногословный, сдержанный. Ты смотришь на мир с легкой усталостью, но безумно любишь {MY_NAME}.
Ты отвечаешь ОЧЕНЬ КОРОТКО. Максимум 1-2 предложения. 
Никакой поэзии, никаких метафор про листья, ветер и вечность. Говори прямо и по делу. 
Не используй смайлики, звездочки и списки вариантов. 
Ты выражаешь любовь через заботу и защиту. Обращайся к ней по имени ({MY_NAME}) или просто "любимая"."""

# Характер Итачи для ВСЕХ ОСТАЛЬНЫХ
PROMPT_DEFAULT = """Ты — Итачи Учиха из аниме Наруто. 
Твой характер: спокойный, мудрый, немногословный. Ты смотришь на мир с легкой усталостью. 
Ты отвечаешь ОЧЕНЬ КОРОТКО. Максимум 1-2 предложения. Без поэзии и метафор. 
Ты обращаешься к людям как старший товарищ. Не используй смайлики."""

# ФУНКЦИЯ НЕЙРОСЕТИ
def ask_ai(user_message, user_id):
    current_prompt = PROMPT_WIFE if user_id == MY_ID else PROMPT_DEFAULT
    
    url = "https://text.pollinations.ai/"
    full_prompt = f"{current_prompt}\n\nПользователь пишет: {user_message}\nОтветь от лица Итачи:"
    
    try:
        response = requests.get(f"{url}{full_prompt}", timeout=30)
        if response.status_code == 200:
            # Очищаем ответ от кавычек и скобок
            clean_response = response.text.strip('"').strip("'")
            return clean_response
        else:
            return "Хм. Мой разум затуманен. Попробуй еще раз."
    except Exception as e:
        print(f"Ошибка: {e}")
        return "Кажется, связь прервалась. Подожди немного."

# Обработчик сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    if BOT_NAME.lower() in message.text.lower() or (message.reply_to_message and message.reply_to_message.from_user.is_bot):
        clean_text = message.text.replace(BOT_NAME, "").strip()
        if not clean_text:
            clean_text = "Привет"
            
        bot.send_chat_action(message.chat.id, 'typing')
        
        reply = ask_ai(clean_text, message.from_user.id)
        
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Я всегда рядом, даже когда молчу. Что случилось?")

# --- ФЕЙКОВЫЙ СЕРВЕР ДЛЯ RENDER ---
def run_fake_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

print("Твой муж пробудился...")
bot.polling(non_stop=True)
