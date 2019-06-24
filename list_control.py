import db
import locale
from telebot import types
from threading import Timer
from datetime import datetime, date, time


# Ставим локаль для правильного вывода месяца
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def make_list_purchase(string_purchase):
    list_purchase = string_purchase.split(', ')
    return list_purchase


def make_string_purchase(list_purchase):
    string_purchase = ', '.join(list_purchase)
    return string_purchase


def create_inline_keyboard(list_purchase):
    inline_keyboard = types.InlineKeyboardMarkup()
    for item in list_purchase:
        button = types.InlineKeyboardButton(item, callback_data=item)
        inline_keyboard.add(button)
    return inline_keyboard


def write_purchase(string_purchase, chat_id):
    cursor, connection = db.connect()
    sql_request = "INSERT INTO purchase VALUES (?, ?);"
    cursor.execute(sql_request, (string_purchase, chat_id))
    connection.commit()


def read_purchase(chat_id):
    cursor, connection = db.connect()
    sql_request = "SELECT purchase_list FROM purchase WHERE id=?"
    cursor.execute(sql_request, (chat_id, ))
    sql_response = cursor.fetchall()
    return str(sql_response[0][0])


def update_purchase(string_purchase, chat_id):
    cursor, connection = db.connect()
    sql_request = "UPDATE purchase SET purchase_list=? WHERE id=?"
    cursor.execute(sql_request, (string_purchase, chat_id))
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


def get_timedelta(string_datetime_reminder):
    datetime_reminder = datetime.fromisoformat(string_datetime_reminder)

    datetime_now = datetime.now()
    delta = datetime_reminder - datetime_now
    return delta.seconds


def set_reminder(datetime_reminder, bot, chat_id):
    def remind(delay=False):
        cursor, connection = db.connect()
        sql_request = "DELETE FROM reminder_purchase WHERE id=?;"
        cursor.execute(sql_request, (chat_id, ))
        connection.commit()

        purchase_list = make_list_purchase(read_purchase(chat_id))
        inline_keyboard = create_inline_keyboard(purchase_list)
        bot.send_message(chat_id, 'Ты просил напомнить про покупки.\rВот список',
                         reply_markup=inline_keyboard)

        if delay is False:
            timer.cancel()

    if datetime_reminder < datetime.now():
        remind(delay=True)
    else:
        time_delta = get_timedelta(datetime_reminder)
        timer = Timer(time_delta, remind)
        timer.start()


def write_datetime_notify(datetime_notify, chat_id):
    cursor, connection = db.connect()
    sql_request = "INSERT INTO shoplist_timer VALUES (?, ?);"
    cursor.execute(sql_request, (str(datetime_notify), chat_id))
    connection.commit()


def read_data_timer():
    cursor, connection = db.connect()
    sql_request = "SELECT * FROM shoplist_timer;"
    cursor.execute(sql_request)
    sql_response = cursor.fetchall()
    return sql_response


def reboot_timer(bot):
    data_timer = read_data_timer()
    for data in data_timer:
        datetime_notify = datetime.fromisoformat(data[0])
        set_notify(datetime_notify, bot, data[1])
