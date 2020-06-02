import telebot as tb
from dialogflow import df
import shoper


bot = tb.TeleBot('759079522:AAEG7X-toPb_SZxmQhBKLKJltlYaw6dh60Q', threaded=False)
users_purchases_data = {}


@bot.message_handler(content_types=['text'])
def response_to_user(message):
    response = df.request_to_dialogflow(df.collect_request(message.text))
    goods = bot.send_message(message.chat.id, f'{df.response_ai(response)}')
    print('tttttttttt')
    if df.action(response) == 'create_list':
        bot.register_next_step_handler(goods, set_purchase)

def set_purchase(message):
    print('lalall')
    users_purchases_data[message.chat.id] = {'goods': message.text}
    current_user = users_purchases_data[message.chat.id]
    print(users_purchases_data[message.chat.id])
    user_purchases = shoper.Purchases(purchases=current_user['goods'])
    print(user_purchases.purchases)
    user_purchases.save_purchase(message.chat.id)
    users_purchases_data[message.chat.id] = user_purchases
    keyboard = user_purchases.create_inline_keyboard()
    bot.send_message(message.chat.id, f'{user_purchases.purchases}', reply_markup=keyboard)


@bot.callback_query_handler(lambda query: True)
def delete_button_from_list(query):
    chat_id = query.message.chat.id
    try:
        purchase = users_purchases_data[chat_id]
    except KeyError:
        pass
    inline_keyboard = purchase.edit_purchase(query, chat_id)

    # Если список пустой – удаляем список
    if not inline_keyboard.keyboard:
        purchase.delete_purchase(bot, chat_id, query)
    # Если не пустой, обновляем сообщение с ним
    else:
        bot.edit_message_reply_markup(chat_id, query.message.message_id,
                                      reply_markup=inline_keyboard)


bot.polling()
