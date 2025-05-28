import os
import telebot
from dotenv import load_dotenv
from telebot import types
import json
from menu import menu_items, ITEMS_PER_PAGE
import re


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
    pattern = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
    if pattern.match(phone_number):
        return True
    return False


def get_cart(id):
    '''Get user's cart from JSON_file.'''
    data = open_json_file()
    return data[str(id)].get("cart")


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


def ask_geo_mark(message):
    '''Ask user for address.'''
    msg = bot.send_message(message.chat.id,
                           'Введите адрес текстом или геометкой Telegram.')
    bot.register_next_step_handler(msg,
                                   geo_mark)

def geo_mark(message):
    '''Send user's address to user.'''
    bot.send_message(message.chat.id,
                     f'Вы выбрали адрес: message.text')
    total = calculate_cart_total(message.chat.id)
    bot.send_message(message.chat.id,
                     f'Стоимость заказа: {total} рублей.\n'
                     'Доступна только оплата наличными курьеру.\n'
                     'Заказ принят в работу🚀')
    

def calculate_cart_total(id):
    cart = get_cart(id)
    count = 0
    for item in menu_items:
        if item["name"] in cart:
            count += (int(item["price"].split()[0]) * cart[item["name"]])
    return count


def make_cart(message):
    '''Make cart and products can be added or delete.'''
    cart = get_cart(str(message.chat.id))
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
    if str(message.chat.id) in data:
        pass
    else:
        msg = bot.send_message(message.chat.id,
                     'Введите ваше имя:')
        bot.register_next_step_handler(msg,
                                        ask_phone)


def ask_phone(message):
    '''Ask user for personal info.'''
    user_info =  {
        "name": message.text,
        "cart": {}
    }
    data = open_json_file()
    data[str(message.chat.id)] = user_info
    close_json_file(data)
    bot.send_message(message.chat.id,
                            'Введите ваш номер телефона:')
    bot.register_next_step_handler(message,
                                    save_info)


def save_info(message):
    if correct_number(message.text):
        data = open_json_file()
        data[str(message.chat.id)]["phone"] = message.text
        bot.send_message(message.chat.id,
                                 'Сохранено')
        close_json_file(data)
    else:
        bot.send_message(message.chat.id,
                         'Проверьте корректность введенного номера телефона.'
                         'Повторите попытку: /start')


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
        ask_geo_mark(message)



@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    '''Callback data.'''
    if call.data.startswith('plus'):
        _, name = call.data.split(';')
        data = open_json_file()
        client_cart_plus = data[str(call.message.chat.id)].get("cart")
        if name in client_cart_plus:
            client_cart_plus[name] += 1
        else:
            client_cart_plus[name] = 1
        close_json_file(data)
        bot.edit_message_text(text='Корзина:',
                              message_id=call.message.message_id,
                              chat_id=call.message.chat.id,
                              reply_markup=make_cart(call.message))
    if call.data.startswith('minus'):
        _, name = call.data.split(';')
        data = open_json_file()
        client_cart_minus = data[str(call.message.chat.id)].get("cart")
        if client_cart_minus[name] <= 1:
            del client_cart_minus[name]
        else:
            client_cart_minus[name] -= 1
        close_json_file(data)
        bot.edit_message_text(text='Корзина:',
                              message_id=str(call.message.message_id),
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
        menu_cart = data[str(call.message.chat.id)].get("cart")
        if name not in menu_cart:
            menu_cart[name] = 1
        else:
            menu_cart[name] += 1
        bot.send_message(call.message.chat.id,
                                 f'{name} добавлен.')
        close_json_file(data)


bot.infinity_polling()
