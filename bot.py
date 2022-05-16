import datetime
from typing import NewType, TypeVar
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from telegramcalendar import create_calendar

UDT = NewType("user_time", datetime.datetime)  # non-aware datetime
RDT = NewType("real_time", datetime.datetime)  # timezone aware datetime
DatetimeLike = TypeVar("DatetimeLike", UDT, RDT)

TELEGRAM_TOKEN = '5122837886:AAGJxEAaIHq0kOmlNoC23JWsvCp5VSrfdYs'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

report = {'standard': int, 'premium': int, 'fruit': int, 'location': int,
          'stuff_time_report': UDT, 'real_time_report': RDT, 'id': int}


# start message
@bot.message_handler(commands=['start'])
def start_message(message):
    report['id'] = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('Отправить отчёт')
    markup.add(item1)
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)



@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")


@bot.message_handler(commands=['calendar'])
def get_calendar(message):
    now = datetime.datetime.now()  # Текущая дата
    chat_id = message.chat.id
    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Сохраним текущую дату в словарь
    markup = create_calendar(now.year, now.month)
    bot.send_message(message.chat.id, "Пожалйста, выберите дату", reply_markup=markup)

def get_date(message):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              c.message.chat.id,
                              c.message.message_id)



@bot.message_handler(commands=['date'])
def get_date(message):
    current_dt = datetime.datetime.now().strftime("%y.%m.%d %H:%M:%S")
    c_date, c_time = current_dt.split()
    msg = f"Текущая дата: {c_date}\nТекущее время: {c_time}"
    user = message.from_user.id
    bot.send_message(user, msg)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text.lower() == 'отправить отчёт':  # сделать автоисправлние слова 'ОТЧËТ'
        get_standard(message)


# GET LOCATION
def get_location(message):
    bot.send_message(message.chat.id, "Выберите локацию:", reply_markup=gen_markup_location())
    # bot.send_message(message.chat.id, "Отправьте /confirm для подтверждения")

    # bot.register_next_step_handler(mes, get_simple)  # Next message will call the name_handler function


def gen_markup_location():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Караоке-бар "Друзья"', callback_data="cb_druzia"),
               InlineKeyboardButton('Друзья.Пляж', callback_data="cb_druzia_plyazh"),
               InlineKeyboardButton('Ресторан "Лебяжий"', callback_data="cb_lebagiy"),
               InlineKeyboardButton('Дримлэнд', callback_data="cb_dreamland"),
               )
    return markup


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    bot.send_message(call.message.chat.id, 'Data: {}'.format(str(call.data)))
    if call.data == "cb_druzia":
        report['location'] = 1
    elif call.data == "cb_druzia_plyazh":
        report['location'] = 2
    elif call.data == "cb_lebagiy":
        report['location'] = 3
    elif call.data == "cb_dreamland":
        report['location'] = 4
    print(report)
    bot.answer_callback_query(call.id)


# GET STANDARD
def get_standard(message):
    send = bot.send_message(message.chat.id, "Введите число стандартных кольянов:")
    bot.register_next_step_handler(send, count_of_standard)  # Next message will call the name_handler function


def count_of_standard(message):
    report['standard'] = message.text
    get_premium(message)


# GET PREMIUM
def get_premium(message):
    send = bot.send_message(message.chat.id, "Введите число премиум кольянов:")
    bot.register_next_step_handler(send, count_of_preimum)  # Next message will call the name_handler function


def count_of_preimum(message):
    report['premium'] = message.text
    get_fruit(message)


# GET FRUIT
def get_fruit(message):
    send = bot.send_message(message.chat.id, "Введите число фруктовых кольянов:")
    bot.register_next_step_handler(send, count_of_fruit)  # Next message will call the name_handler function


def count_of_fruit(message):
    report['fruit'] = message.text
    get_location(message)


def confirm_report(message):
    bot.send_message(message.chat.id, "есть")


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
    # print('Connection successfully')
    # bot.polling(non_stop=True)

# message bof at all screen
# bot.answer_callback_query(call.id, show_alert=True, text=' Выбран Караоке-бар "Друзья"')
