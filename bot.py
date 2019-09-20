import telebot as tb
from modules import proxy_changer
from modules import list_controller
from dialogflow import df


proxy = proxy_changer.read_proxy()
bot = tb.TeleBot('759079522:AAEG7X-toPb_SZxmQhBKLKJltlYaw6dh60Q', threaded=False)
tb.apihelper.proxy = proxy_changer.set_proxy(proxy)

user_save = {}


@bot.message_handler(commands=['proxy'])
def send_proxy_info(message):
    proxy_info = proxy_changer.proxy_info(proxy)
    ip = proxy_info['ip']
    country = proxy_info['country']
    city = proxy_info['city']
    bot.send_message(message.chat.id, f'Сижу на айпи {ip}, страна: {country}, город: {city}')


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    response = df.request_to_dialogflow(df.collect_request(message.text))
    name_list = bot.send_message(message.chat.id, f'{df.response_ai(response)}')
    if df.action(response) == 'create_list':
        bot.register_next_step_handler(name_list, set_list)


def set_list(message):
    user_save[message.chat.id] = {'name_list': message.text}
    response = df.request_to_dialogflow(df.collect_request(message.text))
    purchase = bot.send_message(message.chat.id, f'{df.response_ai(response)}')
    bot.register_next_step_handler(purchase, set_purchase)


def set_purchase(message):
    user_save[message.chat.id].update({'goods': message.text})
    list_name = user_save[message.chat.id]['name_list']
    list_goods = list_controller.make_firstletter_capital(user_save[message.chat.id]['goods'])
    keyboard = list_controller.create_inline_keyboard(list_controller.purchase_to_list(list_goods))
    bot.send_message(message.chat.id, 'Вот список, держи')
    bot.send_message(message.chat.id, f'{list_name}', reply_markup=keyboard)


try:
    # Запускаем бота
    bot.polling()

# Если прокси отваливается
except OSError:
    bot.stop_polling()

    proxy = proxy_changer.get_proxy()
    proxy_changer.write_proxy(proxy)

    bot.polling()
