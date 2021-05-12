from telebot import types
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
Чтобы создать список, попроси меня об этом и перечисли, что нужно купить или сделать через запятую.
Например вот так: что-то, ещё что-то, и ещё что-то'''.format(message.from_user.first_name)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_new_list_button = types.KeyboardButton('Новый список')
    keyboard.add(create_new_list_button)
    bot.send_message(message.chat.id, about_me, reply_markup=keyboard)


@bot.message_handler(regexp='Новый список')
def create_list(message):
    msg_obj = bot.send_message(
        message.chat.id,
        'Записываю что покупать, главное пиши через запятую',
        )
    bot.register_next_step_handler(msg_obj, parse_list)


def parse_list(message):
    user_item_list = shoper.Purchases(purchases=message.text)
    user_item_list.save_purchase(message.chat.id)
    users_purchases_data[message.chat.id] = user_item_list
    keyboard = user_item_list.create_inline_keyboard()
    bot.send_message(message.chat.id, 'Готово', reply_markup=keyboard)


@bot.message_handler(commands=['log'])
def send_log(message):
    user_id = str(message.from_user.id)
    hex_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
    if hex_user_id in config['permissions']['log_permissions']:
        log = open('./bot.log')
        bot.send_document(message.chat.id, log, caption='Держи логи')
        bot_logger.info(
            'issuing a log to a user with access, user – {}'.format(
                message.from_user.username,
                ),
            )
    else:
        bot_logger.warning(
            'request a log from a user without access, user – {}'.format(
                message.from_user.username,
                ),
            )
        bot.send_message(message.chat.id, 'У вас нет доступа к логу')


@bot.callback_query_handler(lambda query: True)
def delete_button_from_list(query):
    chat_id = query.message.chat.id
    purchases = None
    try:
        purchases = users_purchases_data[chat_id]
    except KeyError:
        bot_logger.error(
            'restore list after reconnecting, user – {}'.format(
                query.message.from_user.username,
                ),
            )
        purchases = shoper.get_purchases(chat_id)
        users_purchases_data[chat_id] = purchases
    inline_keyboard = purchases.edit_purchase(query, chat_id)
    bot.answer_callback_query(query.id, 'Убрала из списка')
    if not inline_keyboard.keyboard:
        purchases.delete_purchase(bot, chat_id, query)
    else:
        bot.edit_message_reply_markup(chat_id, query.message.message_id,
                                      reply_markup=inline_keyboard)


try:
    bot.polling()
except OSError:
    bot_logger.exception('Disconnected, restart bot')
