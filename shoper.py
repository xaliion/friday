import db_request
from telebot import types


class Purchases():
    def __init__(self, title, purchases, data_remind=None):
        self.title = title
        self.purchases = self.__make_firstletter_capital(purchases, return_type='string')
        self.remind = data_remind
    
    def __purchase_to_list(self, purchase_string):
        purchase_list = purchase_string.split(', ')
        return purchase_list

    def __purchase_to_string(self, purchase_list):
        purchase_string = ', '.join(purchase_list)
        return purchase_string
    
    def __make_firstletter_capital(self, purchase_string, return_type):
        purchase_list = self.__purchase_to_list(purchase_string)
        for item_index in range(len(purchase_list)):
            purchase_list[item_index] = purchase_list[item_index].capitalize()
        if return_type == 'list':
            return purchase_list
        return self.__purchase_to_string(purchase_list)

    def create_inline_keyboard(self):
        purchase_list = self.__purchase_to_list(self.purchases)
        inline_keyboard = types.InlineKeyboardMarkup()
        for item in purchase_list:
            button = types.InlineKeyboardButton(item, callback_data=item)
            inline_keyboard.add(button)
        return inline_keyboard

    def edit_purchase(self, query, chat_id):
        self.purchases = db_request.read_purchase(chat_id)[1]
        purchase_list = self.__purchase_to_list(self.purchases)
        inline_keyboard = self.create_inline_keyboard()

        # Удаляем кнопку
        for button in inline_keyboard.keyboard:
            if button[0]['callback_data'] == query.data:
                # Удаляем из клавиатуры
                button_index = inline_keyboard.keyboard.index(button)
                del inline_keyboard.keyboard[button_index]
                # Удаляем из списка
                purchase_list.remove(button[0]['text'])
                # Обновляем список в базе
                self.purchases = self.__purchase_to_string(purchase_list)
                db_request.update_purchase(self.title, self.purchases, chat_id)
        return inline_keyboard

    def delete_purchase(self, bot, chat_id, query):
        db_request.delete_purchase(chat_id)
        bot.delete_message(chat_id, query.message.message_id)

    def save_purchase(self, chat_id):
        db_request.write_purchase(self.title, self.purchases, chat_id)