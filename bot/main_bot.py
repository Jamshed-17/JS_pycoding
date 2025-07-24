import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import telebot
from admin_bot import *
import config
from database.crud import *
import os
import subprocess
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

subprocess.run(["python", "database/models.py"]) if "DataBase" in os.listdir("data") else ...

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if add_user(user_id=message.chat.username.lower(), admin=True if message.chat.username.lower() == "jamshed1737377" else False) == "Пользователь уже существует":
        if is_admin(message.chat.username.lower()):
            admin_panel(bot, message)
        else:
            user_panel(message)
    else:
        bot.send_message(message.chat.id, text="Hello world, epta!")

def user_panel(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("Инстукция")
    btn2 = KeyboardButton("Выбрать таску")
    btn3 = KeyboardButton("Случайная таска")
    btn4 = KeyboardButton("Решённые таски")
    keyboard.add(btn1, btn2).row(btn3, btn4)
    bot.send_message(message.chat.id, text="Что делать будем?", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "Инстукция")
def info(message):
    bot.send_message(message.chat.id, text="...info")

@bot.message_handler(func=lambda m: m.text == "Выбрать таску")
def tasks(message):
    bot.send_message(message.chat.id, text="...tasks")

@bot.message_handler(func=lambda m: m.text == "Случайная таска")
def random_task(message):
    bot.send_message(message.chat.id, text="...random_task")

@bot.message_handler(func=lambda m: m.text == "Решённые таски")
def my_complite_tasks(message):
    bot.send_message(message.chat.id, text="...user_complite")



bot.infinity_polling()
