import telebot
from init import bot

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text="Привет мой друг в армии! Надеюсь эта штука тебе пригодится, чтобы не сойти с ума и не забыть как нажимат на кнопочки, чтобы получалась магия. Удачи, Джаваскриптизёр!")







bot.infinity_polling()