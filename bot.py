from dialogflow import df
import telebot as tb
import configparser
import logging
import hashlib
import shoper


config = configparser.ConfigParser()
config.read('./config.ini')
bot = tb.TeleBot(config['bot']['token'], threaded=False)
bot_logger = logging.getLogger(config['logger']['title'])
logging.basicConfig(filename=config['logger']['filename'], level=logging.INFO,
                    format=config['logger']['text_format'],
                    datefmt=config['logger']['date_format'])
users_purchases_data = {}


@bot.message_handler(commands=['start'])
def say_hello(message):
    about_me = '''Привет, {}.
Я помогаю со списками покупок или дел.
Чтобы создать список, попроси меня об этом и перечисли что нужно купить или сделать через запятую
Например вот так: что-то, ещё что-то, и еще что-то'''.format(message.from_user.first_name)
    bot.send_message(message.chat.id, about_me)


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    response = df.request_to_dialogflow(df.collect_request(message.text))
    if df.action(response) == 'set_purchase_list':
        goods = df.parameters(response)['purchase_list']
        user_purchases = shoper.Purchases(purchases=goods)
        user_purchases.save_purchase(message.chat.id)
        users_purchases_data[message.chat.id] = user_purchases
        keyboard = user_purchases.create_inline_keyboard()
        bot.send_message(message.chat.id, f'{df.response_ai(response)}', reply_markup=keyboard)
    elif df.action(response) == 'purchase_reminder':
        datetime_remind_from_ai = df.parameters(response)
        if not datetime_remind_from_ai['time']:
            bot.send_message(message.chat.id, 'Не могу прочитать время')
        else:
            purchases = users_purchases_data[message.chat.id]
            datetime_reminder = purchases.create_reminder(datetime_remind_from_ai, message.chat.id)
            message_to_recap = purchases.set_reminder(datetime_reminder, bot, message.chat.id)
            bot.send_message(message.chat.id, message_to_recap)
    elif df.action(response) == 'send_log':
        user_id = '{}'.format(message.from_user.id)
        hex_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
        if hex_user_id in config['permissions']['log_permissions']:
            log = open('./bot.log')
            bot.send_document(message.chat.id, log, caption='Держи логи')
            bot_logger.info('issuing a log to a user with access, user – {}'.format(message.from_user.username))
        else:
            bot_logger.warning('request a log from a user without access, user – {}'.format(message.from_user.username))
            bot.send_message(message.chat.id, 'У вас нет доступа к логу')
    else:
        bot.send_message(message.chat.id, f'{df.response_ai(response)}')


@bot.callback_query_handler(lambda query: True)
def delete_button_from_list(query):
    chat_id = query.message.chat.id
    try:
        purchase = users_purchases_data[chat_id]
        inline_keyboard = purchase.edit_purchase(query, chat_id)
    except (KeyError, AttributeError):
        bot_logger.exception('exception is caught, the bot cannot edit the list after reconnecting, user – {}'.format(query.message.from_user.username))
        bot.send_message(chat_id, 'Я не могу отредактировать список после переподключения')

    # Если список пустой – удаляем список
    if not inline_keyboard.keyboard:
        purchase.delete_purchase(bot, chat_id, query)
    # Если не пустой, обновляем сообщение с ним
    else:
        bot.edit_message_reply_markup(chat_id, query.message.message_id,
                                      reply_markup=inline_keyboard)


try:
    bot.polling()
except:
    bot_logger.exception('Disconnected, restart bot')
