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

subprocess.run(["python", "database/models.py"]) if "DataBase" in os.listdir("data") else ...
tasks_ids = json.load(open("data/tasks.json", "r"))["tasks"]
count = int((len(tasks_ids))/5)
bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if add_user(user_id=message.chat.username.lower(), admin=True if message.chat.username.lower() == "jamshed1737377" else False) == "Пользователь уже существует":
        if is_admin(message.chat.username.lower()):
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
    bot.send_message(message.chat.id, text= """
Привет! 👋 Это мини-тренажёр по JavaScript, который поможет тебе не забывать основы. Работает просто:

*📌 Основные команды:*
- */start* - Перезапустить бота
- *Выбрать таску* - Список задач с пагинацией
- *Случайная таска* - Рандомная непройденная задача
- *Решённые таски* - Список выполненных задач

*🔧 Как работать с задачами:*
1. Выбираешь задачу (или получаешь случайную)
2. Читаешь условие и *пишешь решение прямо в чат*
3. Бот проверяет код и говорит результат
4. Если ошибся - можно попробовать снова

*💡 Фишки:*
- Задачи разного уровня сложности (от `лёгких` до `хардкорных`)
- Можно переключаться между задачами кнопками
- Прогресс сохраняется (видно по галочкам ✅)

*⚠️ Важно:*
- Пиши код *точно* как в примерах
- Можно использовать любые JS-методы
- Если застрял - жми "← Назад" и начинай заново

Поехали? Жми *"Случайная таска"* или выбирай из списка!

*P.S.* Если найдёшь баги - пиши @jamshed17, исправлю
""", parse_mode="Markdown")

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

def task_print(message, task_id: int, skript: str):
    bot.clear_step_handler(message)
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    if skript == "random":
        markup.add(InlineKeyboardButton("↻ Другая", callback_data="another-random-task"), InlineKeyboardButton("GO!", callback_data=f"task-go=={task_id}"))
    elif skript == "back":
        markup.add(InlineKeyboardButton("← Назад", callback_data="to-page"), InlineKeyboardButton("GO!", callback_data=f"task-go=={task_id}"))
    bot.send_message(message.chat.id, text=this_task[0], reply_markup=markup, parse_mode="Markdown")

def task_try(message, task_id: int):
    this_task = task_work.task_info(task_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("← Назад", callback_data="to-page"))
    bot.send_message(message.chat.id, text=f"{this_task[0]}\nОтправьте решение в чат", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: testing_tasks(msg, task_id))

def testing_tasks(message, task_id: int):
    if message.text.lower() in ["/start", "отмена", "назад"]:
        user_panel(message)  # Возвращаем в меню
        return
    if hasattr(message, 'data') and message.data == "to-page":
        return
    request_try = task_work.task_trying(task_id, message.text, message.chat.username)
    if type(request_try) == str:
        bot.send_message(message.chat.id, text=f"Задание провалено:\n{request_try}")
        task_try(message, task_id)
    else:
        bot.send_message(message.chat.id, text=f"Задание прйдено!")
        start(message)

@bot.message_handler(func=lambda m: m.text == "Случайная таска")
def random_task(message):
    username = message.chat.username
    total_tasks = len(tasks_ids)
    completed_tasks = {str(t) for t in complites_use(username)}
    available_tasks = [t for t in range(1, total_tasks + 1) if str(t) not in completed_tasks]
    
    if not available_tasks:
        bot.send_message(message.chat.id, "Вы уже решили все задачи!")
        return

    task_id = available_tasks[random.randint(0, len(available_tasks) - 1)]  # Быстрее чем random.choice()
    task_print(message, task_id, "random")


@bot.message_handler(func=lambda m: m.text == "Решённые таски")
def my_complite_tasks(message):
    bot.send_message(message.chat.id, text=task_work.complite_tasks(message.chat.username), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    page = user_page_number(call.message.chat.username)
    req = call.data.split('_')
    #Обработка кнопки - скрыть
    if "task-n==" in req[0]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_print(message=call.message, task_id=int(req[0].replace("task-n==", "")), skript="back")

    elif "task-go==" in req[0]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        task_try(call.message, task_id=int(req[0].replace("task-go==", "")))

    elif req[0] == "to-page":
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
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

    elif req[0] == "another-random-task":
        random_task(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)


bot.infinity_polling()