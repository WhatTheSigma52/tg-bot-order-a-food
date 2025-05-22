import os
import telebot
from dotenv import load_dotenv
from telebot import types
import json
from menu import menu_items, ITEMS_PER_PAGE
# import re
import string


load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


def open_json_file():
    '''return data from JSON-file.'''
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def close_json_file(data):
    '''Dump data in JSON_file.'''
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def correct_number(phone_number):
    '''Check user's phone num is it correct or not.'''
    phone_lst = []
    for i in phone_number:
        try:
            phone_lst.append(int(i))
        except:
            if i == '+' or i == ' ':
                del i
            else:
                return False
    end_num = (''.join(map(str, phone_lst)))
    if int(end_num) and len(end_num) == 11:
        return True
    else:
        return False
    # pattern = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
    # print(phone_number)
    # if pattern.match(phone_number):
    #     return True
    # return False


def get_cart(id):
    '''Get user's cart from JSON_file.'''
    data = open_json_file()
    for i in data['clients']:
        if i['id'] == str(id):
            return i['cart']


def order_cart(message):
    '''Make keyboard for order.'''
    bot.send_message(message.chat.id,
                     'Ваша корзина:')
    markup = types.ReplyKeyboardMarkup(row_width=2,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    cart = get_cart(message.chat.id)
    if cart:
        for name in cart:
            bot.send_message(message.chat.id,
                             f'✨ {name}')
        markup.add(
            types.KeyboardButton(text='Да✅'),
            types.KeyboardButton(text='Нет❌')
        )
        bot.send_message(message.chat.id,
                         text='Все позиции в корзине.'
                         ' Жду подтверждения.',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         'У вас пустая корзина.')


def make_cart(message):
    '''Make cart and products can be added or delete.'''
    cart = get_cart(message.chat.id)
    if cart:
        markup = types.InlineKeyboardMarkup(row_width=3)
        for name in cart:
            btn1 = types.InlineKeyboardButton(text='-',
                                              callback_data=f'minus;{name}')
            btn2 = types.InlineKeyboardButton(text='+',
                                              callback_data=f'plus;{name}')
            btn3 = types.InlineKeyboardButton(text=f'x{cart[name]} {name}',
                                              callback_data='pass')
            markup.add(btn1, btn3, btn2)
        return markup
    else:
        bot.send_message(message.chat.id, 'У вас нет позиций в корзине')


def menu(page=0):
    '''Make menu keyboard.'''
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    for i in menu_items[start_index:end_index]:
        markup.add(
            types.InlineKeyboardButton(
                text=f'{i['name']}: {i['price']}',
                callback_data=f'menu;{i['name']}')
            )
    if page > 0:
        markup.add(
            types.InlineKeyboardButton(
                    text='<--',
                    callback_data=f'page;{page - 1}')
                )
    if end_index < len(menu_items):
        markup.add(
            types.InlineKeyboardButton(
                text='-->',
                callback_data=f'page;{page + 1}')
            )
    return markup


def save_client(name, phone_number, id, message):
    '''Save client in JSON-file.'''
    if correct_number(phone_number):
        phone_number = phone_number.replace(' ', '')
        for i in string.punctuation:
            phone_number = phone_number.replace(i, '')
        data = open_json_file()
        data['clients'].append({"id": f"{id}",
                                "name": f"{name}",
                                "phone": f"{phone_number}",
                                "cart": {}})
        close_json_file(data)
        bot.send_message(message.chat.id, 'Ваши данные сохранены')
    else:
        bot.send_message(message.chat.id,
                         'Вы ввели неправильные личные данные')


def add_info(message):
    '''Ask user for personal info.'''
    bot.send_message(message.chat.id,
                     'Введите вашe имя, номер телефона через запятую:')
    bot.register_next_step_handler_by_chat_id(message.chat.id,
                                              lambda message:
                                              save_client(
                                                message.text.split(',')[0],
                                                message.text.split(',')[1],
                                                message.chat.id,
                                                message))


@bot.message_handler(commands=['start'])
def start(message):
    '''Main menu with buttons and check user in JSON-data'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=False,
                                       row_width=3)
    button1 = types.KeyboardButton('Меню🍜')
    button2 = types.KeyboardButton('Корзина🧺')
    button3 = types.KeyboardButton('Заказать✅')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id,
                     'Добро пожаловать в доставку ...',
                     reply_markup=markup)
    data = open_json_file()
    for i in data["clients"]:
        if str(message.chat.id) in i["id"]:
            break
    else:
        bot.register_next_step_handler_by_chat_id(message,
                                                  add_info(message))


@bot.message_handler(func=lambda message: True)
def handler_all(message):
    '''Check which button was pressed.'''
    if message.text == 'Меню🍜':
        bot.send_message(message.chat.id,
                         'Меню:',
                         reply_markup=menu())
    if message.text == 'Корзина🧺':
        bot.send_message(message.chat.id,
                         'Корзина:',
                         reply_markup=make_cart(message))
    if message.text == 'Заказать✅':
        bot.send_message(message.chat.id,
                         text='✨✨✨',
                         reply_markup=order_cart(message))
    if message.text.startswith('Нет'):
        bot.send_message(message.chat.id,
                         'Вы отменили заказ.'
                         ' Чтобы вернуться в главное меню нажмите: /start')
    if message.text.startswith('Да'):
        bot.send_message(message.chat.id,
                         'Вы подтвердили заказ. Ожидайте доставки.'
                         ' Чтобы вернуться в главное меню нажмите: /start')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    '''Callback data.'''
    if call.data.startswith('plus'):
        _, name = call.data.split(';')
        data = open_json_file()
        for client in data["clients"]:
            if client['id'] == str(call.message.chat.id):
                for item in client["cart"]:
                    if item == name:
                        client["cart"][item] += 1
                        break
                else:
                    client["cart"][item] = 1
        close_json_file(data)
        bot.edit_message_text(text='Корзина:',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=make_cart(call.message))
    if call.data.startswith('minus'):
        _, name = call.data.split(';')
        data = open_json_file()
        for client in data["clients"]:
            if client['id'] == str(call.message.chat.id):
                for item in client["cart"]:
                    if client["cart"][item] < 2:
                        del client["cart"][item]
                    else:
                        client["cart"][item] -= 1
        close_json_file(data)
        bot.edit_message_text(text='Корзина:',
                              message_id=call.message.message_id,
                              chat_id=call.message.chat.id,
                              reply_markup=make_cart(call.message))
    if call.data.startswith('page'):
        _, page = call.data.split(';')
        markup = menu(int(page))
        bot.edit_message_text(text='Корзина:',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup)
    if call.data.startswith('menu'):
        _, name = call.data.split(';')
        data = open_json_file()
        for client in data['clients']:
            if client['id'] == str(call.message.chat.id):
                if name not in client["cart"]:
                    client["cart"][name] = 1
                else:
                    client["cart"][name] += 1
                bot.send_message(call.message.chat.id,
                                 f'{name} добавлен.')
        close_json_file(data)


bot.infinity_polling()
