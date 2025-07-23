from database.models import engine, Base
import config
from telebot import TeleBot

bot = TeleBot(config.TOKEN)
Base.metadata.create_all(bind=engine)