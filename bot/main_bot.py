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
import json

subprocess.run(["python", "database/models.py"]) if "DataBase" in os.listdir("data") else ...
tasks_ids = json.load(open("data/tasks.json", "r"))["tasks"]
count = int((len(json.load(open("data/tasks.json", "r"))["tasks"]))/5)
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
    global count
    page = user_page_number(message.chat.username)
    markup = InlineKeyboardMarkup()
    for task_id in range(page*5-4, (page*5)+1):
        markup.add(InlineKeyboardButton(text=f"{"✅" if is_complite(message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
            InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
    bot.send_message(message.chat.id, text="...tasks", reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    page = user_page_number(call.message.chat.username)
    req = call.data.split('_')
    #Обработка кнопки - скрыть
    if req[0] != 'next-page' and req[0] != 'back-page':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    #Обработка кнопки - вперед
    elif req[0] == 'next-page':
        if page < count and page != count-1:
            page = next_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅" if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif page == count-1:
            page = next_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅" if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    #Обработка кнопки - назад
    elif req[0] == 'back-page':
        if page > 2:
            page = pre_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅" if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif page == 2:
            page = pre_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅" if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'next-page'))
            bot.edit_message_text(f'Страница {page} из {count}', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)





@bot.message_handler(func=lambda m: m.text == "Случайная таска")
def random_task(message):
    bot.send_message(message.chat.id, text="...random_task")

@bot.message_handler(func=lambda m: m.text == "Решённые таски")
def my_complite_tasks(message):
    bot.send_message(message.chat.id, text="...user_complite")



bot.infinity_polling()