import telebot as tb
from modules import proxy_changer
from dialogflow import df


proxy = proxy_changer.read_proxy()
bot = tb.TeleBot('759079522:AAEG7X-toPb_SZxmQhBKLKJltlYaw6dh60Q', threaded=False)
tb.apihelper.proxy = proxy_changer.set_proxy(proxy)
action = 'test'


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
    bot.send_message(message.chat.id, f'{df.response_ai(response)}')


try:
    # Запускаем бота
    bot.polling()

# Если прокси отваливается
except OSError:
    bot.stop_polling()

    proxy = proxy_changer.get_proxy()
    proxy_changer.write_proxy(proxy)

    bot.polling()
