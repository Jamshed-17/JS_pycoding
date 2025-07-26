# -*- coding: utf-8 -*-
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
import random

# Автосоздание базы
subprocess.run(["python", "database/models.py"]) if "DataBase" in os.listdir("data") else ...

# Загрузка задач
tasks_ids = json.load(open(config.TASKS_PATH, "r"))["tasks"]
count = int((len(tasks_ids)) / 5)

bot = telebot.TeleBot(config.TOKEN)

def generate_tasks_markup(username, page):
    markup = InlineKeyboardMarkup()
    for task_id in range(page * 5 - 4, page * 5 + 1):
        if task_id > len(tasks_ids):
            continue
        task = tasks_ids[task_id - 1]
        status = "✅" if is_complite(username, task_id) else ""
        text = f"{status}{task_id} - {task['name']} ({task['level']})"
        markup.add(InlineKeyboardButton(text=text, callback_data=f"task-n=={task_id}"))

    if page == 1:
        markup.add(
            InlineKeyboardButton(text=f'{page}/{count}', callback_data=' '),
            InlineKeyboardButton(text='Вперёд →', callback_data='next-page')
        )
    elif page == count:
        markup.add(
            InlineKeyboardButton(text='← Назад', callback_data='back-page'),
            InlineKeyboardButton(text=f'{page}/{count}', callback_data=' ')
        )
    else:
        markup.add(
            InlineKeyboardButton(text='← Назад', callback_data='back-page'),
            InlineKeyboardButton(text=f'{page}/{count}', callback_data=' '),
            InlineKeyboardButton(text='Вперёд →', callback_data='next-page')
        )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    username = message.chat.username.lower()
    if add_user(user_id=username, admin=(username == "jamshed1737377")) == "Пользователь уже существует":
        if is_admin(username):
            admin_panel(bot, message)
        else:
            user_panel(message)
    else:
        bot.send_message(message.chat.id, text="Привет! Этот бот поможет тебе не забыть основы JS и сможет дать минимальную необходимую практику, чтобы не забыть совсем всё. Своего рода минимальная версия CodeWars прямо в телеграме.")
        user_panel(message)

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
    bot.send_message(message.chat.id, text="""
Привет! 👋 Это мини-тренажёр по JavaScript, который поможет тебе не забывать основы. Работает просто:

📌 Основные команды:
- /start — перезапуск
- "Выбрать таску" — список задач с пагинацией
- "Случайная таска" — рандомная непройденная
- "Решённые таски" — пройденные задания

🔧 Как работать:
1. Выбираешь задачу
2. Отправляешь JS-код прямо в чат
3. Бот проверяет решение

💡 Фишки:
- Прогресс сохраняется
- Рандом и кнопки удобства

⚠️ Важно:
- Пиши код *точно* как в примерах
- Решения проверяются автотестами

P.S. Нашёл баг? Пиши @jamshed17
""", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "Выбрать таску")
def tasks(message):
    page = user_page_number(message.chat.username)
    markup = generate_tasks_markup(message.chat.username, page)
    bot.send_message(message.chat.id, text="Выберите таску", reply_markup=markup)

def task_print(message, task_id: int, skript: str = "back"):
    bot.clear_step_handler(message)
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    if skript == "random":
        markup.add(
            InlineKeyboardButton("↻ Другая", callback_data="another-random-task"),
            InlineKeyboardButton("GO!", callback_data=f"task-go=={task_id}")
        )
    elif skript == "back":
        markup.add(
            InlineKeyboardButton("← Назад", callback_data="to-page"),
            InlineKeyboardButton("GO!", callback_data=f"task-go=={task_id}")
        )
    bot.send_message(message.chat.id, text=this_task[0], reply_markup=markup, parse_mode="Markdown")

def task_try(message, task_id: int):
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("← Назад", callback_data="to-page"))
    bot.send_message(message.chat.id, text=f"{this_task[0]}\nОтправьте решение в чат", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: testing_tasks(msg, task_id))

def testing_tasks(message, task_id: int):
    if message.text.lower() in ["/start", "отмена", "назад"]:
        user_panel(message)
        return
    request_try = task_work.task_trying(task_id, message.text, message.chat.username)
    if isinstance(request_try, str):
        bot.send_message(message.chat.id, text=f"Задание провалено:\n{request_try}")
        task_try(message, task_id)
    else:
        bot.send_message(message.chat.id, text="Задание пройдено!")
        start(message)

@bot.message_handler(func=lambda m: m.text == "Случайная таска")
def random_task(message):
    username = message.chat.username
    total_tasks = len(tasks_ids)
    completed = set(map(str, complites_use(username)))
    available = [t for t in range(1, total_tasks + 1) if str(t) not in completed]

    if not available:
        bot.send_message(message.chat.id, "Вы уже решили все задачи!")
        return

    task_id = random.choice(available)
    task_print(message, task_id, "random")

@bot.message_handler(func=lambda m: m.text == "Решённые таски")
def my_complite_tasks(message):
    bot.send_message(message.chat.id, text=task_work.complite_tasks(message.chat.username), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    username = call.message.chat.username
    page = user_page_number(username)
    data = call.data

    if data.startswith("task-n=="):
        task_id = int(data.split("==")[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_print(call.message, task_id, "back")

    elif data.startswith("task-go=="):
        task_id = int(data.split("==")[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_try(call.message, task_id)

    elif data == "to-page":
        markup = generate_tasks_markup(username, page)
        bot.edit_message_text("Выберите таску", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    elif data == "next-page":
        if page < count:
            next_page(username)
            page = user_page_number(username)
            markup = generate_tasks_markup(username, page)
            bot.edit_message_text("Выберите таску", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    elif data == "back-page":
        if page > 1:
            pre_page(username)
            page = user_page_number(username)
            markup = generate_tasks_markup(username, page)
            bot.edit_message_text("Выберите таску", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    elif data == "another-random-task":
        random_task(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)

bot.infinity_polling()
