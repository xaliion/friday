import db
import locale
from telebot import types
from threading import Timer
from datetime import datetime, date, time


# problem with docker
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def make_shop_list(shop_list):
    shop_list = shop_list.split(', ')
    for item in range(len(shop_list)):
        shop_list[item] = shop_list[item].capitalize()

    return shop_list


def make_shop_string(shop_list):
    shop_list_string = ', '.join(shop_list)
    return shop_list_string


def create_buttons(shop_list):
    markup = types.InlineKeyboardMarkup()
    for item in shop_list:
        button = types.InlineKeyboardButton(item, callback_data=item)
        markup.add(button)

    return markup


def write_list(shop_list, chat_id):
    cursor, connection = db.connect()
    sql_request = "INSERT INTO shoplist VALUES (?, ?);"
    cursor.execute(sql_request, (shop_list, chat_id))
    connection.commit()


def read_list(chat_id):
    cursor, connection = db.connect()
    sql_request = "SELECT shop_list FROM shoplist WHERE id=?"
    cursor.execute(sql_request, (chat_id, ))
    sql_response = cursor.fetchall()

    return str(sql_response[0][0])


def update_list(shop_list, chat_id):
    cursor, connection = db.connect()
    sql_request = "UPDATE shoplist SET shop_list=? WHERE id=?"
    cursor.execute(sql_request, (shop_list, chat_id))
    connection.commit()


def get_datetime_notify(time_notify, date_notify=None):
    def calculating_date():
        if date_notify == '':
            return date.today()
        return date.fromisoformat(date_notify)

    parsed_time_notify = time.fromisoformat(time_notify)
    parsed_date_notify = calculating_date()

    datetime_notify = datetime.combine(parsed_date_notify, parsed_time_notify)
    return datetime_notify


def send_datetime_notify(datetime_notify, bot, chat_id):
    if datetime_notify.day == datetime.today().day:
        time_remind = datetime_notify.strftime('в %H:%M')
        bot.send_message(chat_id, 'Напомню сегодня {}'.format(time_remind))
    else:
        datetime_remind = datetime_notify.strftime('%d %b, в %H:%M')
        bot.send_message(chat_id, 'Напомню {}'.format(datetime_remind))


def get_time_delta(datetime_notify):
    datetime_now = datetime.now()

    delta = datetime_notify - datetime_now
    delta_seconds = delta.seconds
    return delta_seconds


def set_notify(datetime_notify, bot, chat_id):
    def notify():
        cursor, connection = db.connect()
        sql_request = "DELETE FROM shoplist_timer WHERE id=?;"
        cursor.execute(sql_request, (chat_id, ))
        connection.commit()

        shop_list = make_shop_list(read_list(chat_id))
        markup = create_buttons(shop_list)
        bot.send_message(chat_id, 'Ты просил напомнить про покупки.\rВот список',
                         reply_markup=markup)
        try:
            timer.cancel()
        except NameError:
            pass

    if datetime_notify < datetime.now():
        notify()
    else:
        time_delta = get_time_delta(datetime_notify)
        timer = Timer(time_delta, notify)
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
