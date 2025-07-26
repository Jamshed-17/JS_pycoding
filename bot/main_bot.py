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
import task_work

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
        markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
    if page == 1:
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
    elif page == count:
        markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
    else:
        markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))

    bot.send_message(message.chat.id, text="Выберите таску", reply_markup=markup)

def task_print(message, task_id: int):
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("← Назад", callback_data="to-page"), InlineKeyboardButton("GO!", callback_data=f"task-go=={task_id}"))
    bot.send_message(message.chat.id, text=this_task[0], reply_markup=markup, parse_mode="Markdown")

def task_try(message, task_id: int):
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("← Назад", callback_data="to-page"))
    bot.send_message(message.chat.id, text=f"{this_task[0]}\nОтправьте решение в чат", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: testing_tasks(msg, task_id))

def testing_tasks(message, task_id: int):
    request_try = task_work.task_trying(task_id, message.text, message.chat.username)
    if type(request_try) == str:
        bot.send_message(message.chat.id, text=f"Задание провалено:\n{request_try}")
        task_try(message, task_id)
    else:
        bot.send_message(message.chat.id, text=f"Задание прйдено!")
        start(message)

@bot.message_handler(func=lambda m: m.text == "Случайная таска")
def random_task(message):
    bot.send_message(message.chat.id, text="...random_task")

@bot.message_handler(func=lambda m: m.text == "Решённые таски")
def my_complite_tasks(message):
    bot.send_message(message.chat.id, text="...user_complite")

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    page = user_page_number(call.message.chat.username)
    req = call.data.split('_')
    #Обработка кнопки - скрыть
    if "task-n==" in req[0]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_print(message=call.message, task_id=int(req[0].replace("task-n==", "")))

    elif "task-go==" in req[0]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_try(call.message, task_id=int(req[0].replace("task-go==", "")))

    elif req[0] == "to-page":
        page = user_page_number(call.message.chat.username)
        markup = InlineKeyboardMarkup()
        for task_id in range(page*5-4, (page*5)+1):
            markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
        if page == 1:
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
        elif page == count:
            markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
        else:
            markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
        bot.edit_message_text(f'Выберите таску', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        
    elif req[0] == 'next-page':
        if page < count and page != count-1:
            page = next_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
            bot.edit_message_text(f'Выберите таску', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif page == count-1:
            page = next_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
            bot.edit_message_text(f'Выберите таску', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif req[0] == 'back-page':
        if page > 2:
            page = pre_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'← Назад', callback_data=f'back-page'),InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
            bot.edit_message_text(f'Выберите таску', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif page == 2:
            page = pre_page(call.message.chat.username)
            markup = InlineKeyboardMarkup()
            for task_id in range(page*5-4, (page*5)+1):
                markup.add(InlineKeyboardButton(text=f"{"✅ " if is_complite(call.message.chat.username, task_id) else ""}{task_id} - {tasks_ids[task_id-1]["name"]} ({tasks_ids[task_id-1]["level"]})", callback_data=f"task-n=={task_id}"))
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                    InlineKeyboardButton(text=f'Вперёд →', callback_data=f'next-page'))
            bot.edit_message_text(f'Выберите таску', reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)


bot.infinity_polling()