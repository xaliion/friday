import telebot as tb
from modules import proxy_changer


proxy = proxy_changer.read_proxy()
bot = tb.TeleBot('759079522:AAEG7X-toPb_SZxmQhBKLKJltlYaw6dh60Q', threaded=False)
tb.apihelper.proxy = proxy_changer.set_proxy(proxy)


@bot.message_handler(commands=['proxy'])
def send_proxy_info(message):
    proxy_info = proxy_changer.proxy_info(proxy)
    ip = proxy_info['ip']
    country = proxy_info['country']
    city = proxy_info['city']
    bot.send_message(message.chat.id, f'Сижу на айпи {ip}, страна: {country}, город: {city}')


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    bot.reply_to(message, 'НОМАНО')


try:
    # Запускаем бота
    bot.polling()

# Если прокси отваливается
except OSError as e:
    bot.stop_polling()

    # Ждём пять секунд, чтобы не словить бан за слишком частые запросы
    proxy = proxy_changer.get_proxy()
    proxy_changer.write_proxy(proxy)

    bot.polling()
