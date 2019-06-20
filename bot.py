import db
import json
import loger
import apiai
import list_control
import telebot as tb
import proxy_changer
from time import sleep


working_proxy = proxy_changer.read_proxy()
tb.apihelper.proxy = {'https': 'https://{ip}:{port}'.format(ip=working_proxy['ip'],
                                                            port=working_proxy['port'])}
bot = tb.TeleBot('866766786:AAFCv_DZQGF884qEKImJj7rpg5D2cqGHmhw', threaded=False)

# Если бот падал, то восстанавливаем таймер
try:
    list_control.reboot_timer(bot)
# Если нет, не делаем ничего
except IndexError:
    pass


@bot.message_handler(commands=['start'])
def send_welcome(message):
    about_me = '''Привет.
Я помогу со списком покупок, но пока что я не могу работать с несколькими списками.
Попроси меня сделать список или пойти в магазин'''
    bot.send_message(message.chat.id, about_me)


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    chat_id = message.chat.id

    # Токен API к Dialogflow
    request = apiai.ApiAI('b661608649e348f1bd8f89497a02b288').text_request()

    # На каком языке будет послан запрос
    request.lang = 'ru'

    # ID Сессии диалога чтобы потом учить бота
    request.session_id = 'Friday'

    # Посылаем запрос к серверу с сообщением от юзера
    request.query = message.text

    # Получаем ответ от сервера и декодируем в utf-8
    response_json = json.loads(request.getresponse().read().decode('utf-8'))

    # Достаём ответ ИИ
    response_from_ai = response_json['result']['fulfillment']['speech']
    # Достаём текущее намерение
    action = response_json['result']['action']

    # Создаем список покупок
    if action == 'create_list.shop_list':
        # Достаём список покупок от пользователя
        parameters_list = response_json['result']['parameters']
        # Записываем его в бд
        list_control.write_list(parameters_list['list'][0], chat_id)
        # Считываем из бд
        shop_list = list_control.read_list(chat_id)
        # Создаем список из строки
        shop_list = list_control.make_shop_list(shop_list)
        markup = list_control.create_buttons(shop_list)
        bot.send_message(chat_id, 'Записала. Вот список', reply_markup=markup)

    # Создаем напоминание
    elif action == 'create_list.shop_list.notify':
        parameters_datetime = response_json['result']['parameters']
        # Если бот не смог распарсить время
        if not parameters_datetime['time']:
            bot.send_message(chat_id, 'Не могу прочитать время')
        else:
            datetime_notify = list_control.get_datetime_notify(parameters_datetime['time'],
                                                               parameters_datetime['date'])
            list_control.send_datetime_notify(datetime_notify, bot, chat_id)
            list_control.write_datetime_notify(datetime_notify, chat_id)
            list_control.set_notify(datetime_notify, bot, chat_id)
    # Ответ бота на любые другие вопросы
    else:
        bot.send_message(chat_id, response_from_ai)


@bot.callback_query_handler(lambda query: True)
def delete_button_from_list(query):
    chat_id = query.message.chat.id
    # Получаем список из бд
    bd_shop_list = list_control.read_list(chat_id)
    shop_list = list_control.make_shop_list(bd_shop_list)
    # Создаём список из кнопок
    markup = list_control.create_buttons(shop_list)

    # Удаляем кнопку
    for button in markup.keyboard:
        if button[0]['callback_data'] == query.data:
            index_for_remove = markup.keyboard.index(button)
            del markup.keyboard[index_for_remove]
            shop_list.remove(button[0]['text'])
            shop_list_string = list_control.make_shop_string(shop_list)
            list_control.update_list(shop_list_string, chat_id)

    # Если список пустой – удаляем сообщение с ним
    if not markup.keyboard:
        bot.delete_message(chat_id, query.message.message_id)
        cursor, connection = db.connect()
        sql_request = "DELETE FROM shoplist WHERE id=?"
        cursor.execute(sql_request, (chat_id, ))
        connection.commit()
    # Если не пустой, обновляем сообщение с ним
    else:
        bot.edit_message_reply_markup(chat_id, query.message.message_id,
                                      reply_markup=markup)


try:
    # Запускаем бота
    bot.polling()

# Если прокси отваливается
except OSError as e:
    # Тормозим бота
    bot.stop_polling()

    # Записываем в лог имя ошибки прокси
    loger.write_error(type(e).__name__)

    # Ждём пять секунд, чтобы не словить бан за слишком частые запросы
    sleep(5)

    # Получаем данные о прокси
    proxy = proxy_changer.get_proxy()

    # Обновляем адрес прокси, чтобы бот выводил текущий адрес
    working_proxy = '{ip}:{port}'.format(ip=proxy['ip'], port=proxy['port'])

    # Ставим прокси
    tb.apihelper.proxy = {'https': 'https://{ip_port}'.format(ip_port=working_proxy)}

    # Перезаписываем в файл
    proxy_changer.write_proxy(proxy)

    # Записываем данные нового прокси
    loger.write_info(proxy)

    # Запускаем бота
    bot.polling()
