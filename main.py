import os
import telebot
from dotenv import load_dotenv
from telebot import types


load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    button1 = types.KeyboardButton('Меню🍜')
    button2 = types.KeyboardButton('Корзина🧺')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, 
                     'Добро пожаловать в доставку ...',
                     reply_markup=markup)


# @bot.message_handler(content_types=['text']) # только текст
# def text_handler(message):
#     if message.text == 'Меню🍜':
#         bot.send_message(message.chat.id, 'Вы в меню')
    

@bot.message_handler(func=lambda message: True) # любое сообщение
def handler_all(message):
    if message.text == 'Меню🍜':
        bot.send_message(message.chat.id, 
                         'Вы в меню')
    if message.text == 'Корзина🧺':
        bot.send_message(message.chat.id, 
                         'Вы в корзине')


bot.polling(none_stop=True)