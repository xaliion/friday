import telebot as tb
from modules import list_controller
from dialogflow import df
import shoper


bot = tb.TeleBot('759079522:AAEG7X-toPb_SZxmQhBKLKJltlYaw6dh60Q', threaded=False)
users_purchases_data = {}


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    response = df.request_to_dialogflow(df.collect_request(message.text))
    list_title = bot.send_message(message.chat.id, f'{df.response_ai(response)}')
    if df.action(response) == 'create_list':
        bot.register_next_step_handler(list_title, set_list)

def set_list(message):
    users_purchases_data[message.chat.id] = {'list_title': message.text}
    response = df.request_to_dialogflow(df.collect_request(message.text))
    purchases = bot.send_message(message.chat.id, f'{df.response_ai(response)}')
    bot.register_next_step_handler(purchases, set_purchase)


def set_purchase(message):
    users_purchases_data[message.chat.id].update({'goods': message.text})
    current_user = users_purchases_data[message.chat.id]
    user_purchases = shoper.Purchases(title=current_user['list_title'], purchases=current_user['goods'])
    keyboard = user_purchases.create_inline_keyboard()
    bot.send_message(message.chat.id, 'Вот список, держи')
    bot.send_message(message.chat.id, f'{user_purchases.title}', reply_markup=keyboard)


bot.polling()
