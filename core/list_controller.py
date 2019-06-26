import locale
from telebot import types
from threading import Timer
from core import database_connector as db_connect
from datetime import datetime, date, time


# Ставим локаль для правильного вывода месяца
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def make_purchase_list(purchase_string):
    purchase_list = purchase_string.split(', ')
    return purchase_list


def make_purchase_string(purchase_list):
    purchase_string = ', '.join(purchase_list)
    return purchase_string


def make_firstletter_capital(purchase_string):
    purchase_list = make_purchase_list(purchase_string)
    for item_index in range(len(purchase_list)):
        purchase_list[item_index] = purchase_list[item_index].capitalize()
    return make_purchase_string(purchase_list)


def create_inline_keyboard(purchase_list):
    inline_keyboard = types.InlineKeyboardMarkup()
    for item in purchase_list:
        button = types.InlineKeyboardButton(item, callback_data=item)
        inline_keyboard.add(button)
    return inline_keyboard


def write_purchase(purchase_string, chat_id):
    connection, cursor = db_connect.connect()
    sql_request = 'INSERT INTO purchase VALUES (?, ?);'
    cursor.execute(sql_request, (purchase_string, chat_id))
    connection.commit()


def read_purchase(chat_id):
    connection, cursor = db_connect.connect()
    sql_request = 'SELECT purchase_list FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id,))
    return cursor.fetchall()[0][0]


def update_purchase(purchase_string, chat_id):
    connection, cursor = db_connect.connect()
    sql_request = 'UPDATE purchase SET purchase_list=? WHERE id=?;'
    cursor.execute(sql_request, (purchase_string, chat_id))
    connection.commit()


def delete_purchase(chat_id):
    connection, cursor = db_connect.connect()
    sql_request = 'DELETE FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id,))
    connection.commit()


def get_datetime_reminder(string_time_reminder, string_date_reminder):
    def calculating_date_reminder():
        if string_date_reminder == '':
            return date.today()
        return date.fromisoformat(string_date_reminder)

    parsed_time_reminder = time.fromisoformat(string_time_reminder)
    parsed_date_reminder = calculating_date_reminder()
    string_datetime_reminder = str(datetime.combine(parsed_date_reminder, parsed_time_reminder))
    return string_datetime_reminder


def get_message_time_reminder(string_datetime_reminder):
    datetime_reminder = datetime.fromisoformat(string_datetime_reminder)

    if datetime_reminder.day == datetime.today().day:
        time_remind = datetime_reminder.strftime('%H:%M')
        to_recap_message = 'Напомню сегодня в {}'.format(time_remind)
        return to_recap_message
    else:
        datetime_remind = datetime_reminder.strftime('%d %b, в %H:%M')
        to_recap_message = 'Напомню {}'.format(datetime_remind)
        return to_recap_message


def get_timedelta(datetime_reminder):
    datetime_now = datetime.now()
    delta = datetime_reminder - datetime_now
    return delta.seconds


def set_reminder(string_datetime_reminder, bot, chat_id):
    def remind(delay=False):
        purchase_list = make_purchase_list(read_purchase(chat_id))
        inline_keyboard = create_inline_keyboard(purchase_list)
        bot.send_message(chat_id, 'Ты просил напомнить про покупки.\rВот список',
                         reply_markup=inline_keyboard)

        connection, cursor = db_connect.connect()
        sql_request = 'DELETE FROM reminder_purchase WHERE id=?;'
        cursor.execute(sql_request, (chat_id,))
        connection.commit()

        if delay is False:
            timer.cancel()

    datetime_reminder = datetime.fromisoformat(string_datetime_reminder)
    if datetime_reminder < datetime.now():
        remind(delay=True)
    else:
        time_delta = get_timedelta(datetime_reminder)
        timer = Timer(time_delta, remind)
        timer.start()


def write_data_reminder(string_datetime_reminder, chat_id):
    connection, cursor = db_connect.connect()
    sql_request = 'INSERT INTO reminder_purchase VALUES (?, ?);'
    cursor.execute(sql_request, (string_datetime_reminder, chat_id))
    connection.commit()


def read_data_reminder():
    connection, cursor = db_connect.connect()
    sql_request = 'SELECT * FROM reminder_purchase;'
    cursor.execute(sql_request)
    return cursor.fetchall()
