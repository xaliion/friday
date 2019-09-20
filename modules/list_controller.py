from .core import db_request
import locale
from telebot import types


# Ставим локаль для правильного вывода месяца
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def purchase_to_list(purchase_string):
    purchase_list = purchase_string.split(', ')
    return purchase_list


def purchase_to_string(purchase_list):
    purchase_string = ', '.join(purchase_list)
    return purchase_string


def make_firstletter_capital(purchase_string):
    purchase_list = purchase_to_list(purchase_string)
    for item_index in range(len(purchase_list)):
        purchase_list[item_index] = purchase_list[item_index].capitalize()
    return purchase_to_string(purchase_list)


def create_inline_keyboard(purchase_list):
    inline_keyboard = types.InlineKeyboardMarkup()
    for item in purchase_list:
        button = types.InlineKeyboardButton(item, callback_data=item)
        inline_keyboard.add(button)
    return inline_keyboard


def write_purchase(purchase_string, chat_id):
    connection, cursor = db_request.connect()
    sql_request = 'INSERT INTO purchase (purchase_list, id) VALUES (?, ?);'
    cursor.execute(sql_request, (purchase_string, chat_id))
    connection.commit()


def read_purchase(chat_id):
    connection, cursor = db_request.connect()
    sql_request = 'SELECT purchase_list FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id, ))
    return cursor.fetchall()[0][0]


def update_purchase(purchase_string, chat_id):
    connection, cursor = db_request.connect()
    sql_request = 'UPDATE purchase SET purchase_list=? WHERE id=?;'
    cursor.execute(sql_request, (purchase_string, chat_id))
    connection.commit()


def delete_purchase(chat_id):
    connection, cursor = db_request.connect()
    sql_request = 'DELETE FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id,))
    connection.commit()
