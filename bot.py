import json
import apiai
import shoper
import telebot as tb
from time import sleep
from core import loger, proxy_changer


working_proxy = proxy_changer.read_proxy()
bot = tb.TeleBot('866766786:AAFCv_DZQGF884qEKImJj7rpg5D2cqGHmhw', threaded=False)
tb.apihelper.proxy = {'https': 'https://{ip}:{port}'.format(ip=working_proxy['ip'],
                                                            port=working_proxy['port'])}

# Если бот падал, то восстанавливаем таймер
try:
    shoper.reboot_timer(bot)
# Если нет, не делаем ничего
except IndexError:
    pass


@bot.message_handler(commands=['start'])
def send_welcome(message):
    about_me = 'Привет.\r\n' \
               'Я помогу со списком покупок, попроси меня сделать список или пойти в магазин'
    bot.send_message(message.chat.id, about_me)


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    chat_id = message.chat.id

    # Настраиваем сессию с диалогфлоу
    request = apiai.ApiAI('b661608649e348f1bd8f89497a02b288').text_request()
    request.lang = 'ru'
    request.session_id = 'Friday'
    request.query = message.text
    response_json = json.loads(request.getresponse().read().decode('utf-8'))
    response_from_ai = response_json['result']['fulfillment']['speech']
    action = response_json['result']['action']

    # Создаем список покупок
    if action == 'purchase_name':
        list_name = response_json['result']['parameters']['list_name']
        bot.send_message(chat_id, f'Назову список {list_name}\r\nЧто будем покупать?')
    elif action == 'purchase_list':
        # Достаём список покупок от пользователя
        purchase_list_from_ai = response_json['result']['parameters']['list'][0]
        purchase_string = shoper.create_purchase(purchase_list_from_ai)
        # Записываем список в базу данных
        shoper.save_purchase(purchase_string, chat_id)
        inline_keyboard = shoper.create_inline_keyboard(purchase_string)
        bot.send_message(chat_id, 'Записала.\r\nВот список', reply_markup=inline_keyboard)
    # Создаем напоминание
    elif action == 'purchase_reminder':
        datetime_remind_from_ai = response_json['result']['parameters']
        print(datetime_remind_from_ai)
        if not datetime_remind_from_ai['time']:
            bot.send_message(chat_id, 'Не могу прочитать время')
        else:
            datetime_reminder = shoper.create_reminder(datetime_remind_from_ai, chat_id)
            message_to_recap = shoper.set_reminder(datetime_reminder, bot, chat_id)
            bot.send_message(chat_id, message_to_recap)
    # Ответ бота на любые другие вопросы
    else:
        bot.send_message(chat_id, response_from_ai)


@bot.callback_query_handler(lambda query: True)
def delete_button_from_list(query):
    chat_id = query.message.chat.id

    inline_keyboard = shoper.edit_purchase(query, chat_id)

    # Если список пустой – удаляем список
    if not inline_keyboard.keyboard:
        shoper.delete_purchase(bot, chat_id, query)
    # Если не пустой, обновляем сообщение с ним
    else:
        bot.edit_message_reply_markup(chat_id, query.message.message_id,
                                      reply_markup=inline_keyboard)


try:
    # Запускаем бота
    bot.polling()

# Если прокси отваливается
except OSError as e:
    bot.stop_polling()
    loger.write_proxy_error(type(e).__name__)

    # Ждём пять секунд, чтобы не словить бан за слишком частые запросы
    sleep(5)
    proxy = proxy_changer.get_proxy()
    tb.apihelper.proxy = {'https': 'https://{ip}:{port}'.format(ip=proxy['ip'], port=proxy['port'])}
    proxy_changer.write_proxy(proxy)

    loger.write_proxy_info(proxy)
    bot.polling()
