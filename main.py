import os
import telebot
from dotenv import load_dotenv
from telebot import types
import json


load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


def open_json_file():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def close_json_file(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def correct_number(phone_number):
    if isinstance(phone_number, int):
        return True
    else:
        return False


def save_client(name, phone_number, id, message):
    if phone_number == 'wrong':
        return 'Вы ввели неправильные личные данные'
    else:
        data = open_json_file()
        data['clients'].append({"id": f"{id}",
                                "name": f"{name}",
                                "phone": f"{phone_number}"})
        close_json_file(data)
    bot.send_message(message.chat.id, 'Ваши данные сохранены')


@bot.message_handler(commands=['add_info'])
def add_info(message):
    bot.send_message(message.chat.id,
                     'Введите ваше имя, номер телефона через запятую:')
    bot.register_next_step_handler_by_chat_id(message.chat.id,
                                              lambda message:
                                              save_client(
                                                message.text.split(',')[0],
                                                message.text.split(',')[1],
                                                message.chat.id,
                                                message))


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=False)
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


@bot.message_handler(func=lambda message: True)
def handler_all(message):
    if message.text == 'Меню🍜':
        bot.send_message(message.chat.id,
                         'Вы в меню')
    if message.text == 'Корзина🧺':
        bot.send_message(message.chat.id,
                         'Вы в корзине')


bot.polling(none_stop=True)
