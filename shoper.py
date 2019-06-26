from core import loger, list_controller


def create_purchase(purchase_list_from_ai):
    purchase_string = list_controller.make_firstletter_capital(purchase_list_from_ai)
    return purchase_string


def save_purchase(purchase_string, chat_id):
    try:
        list_controller.write_purchase(purchase_string, chat_id)
    except (Exception.Error.DatabaseError, Exception.Error.InterfaceError) as error:
        shoper_loger = loger.get_loger()
        shoper_loger.error('Ошибка базы данных при сохранении списка покупок.\nОшибка: {}').format(error)
    else:
        return True
    return False


def create_inline_keyboard(purchase_string):
    purchase_list = list_controller.make_purchase_list(purchase_string)
    inline_keyboard = list_controller.create_inline_keyboard(purchase_list)
    return inline_keyboard


def create_reminder(datetime_remind_from_ai, chat_id):
    datetime_reminder = list_controller.get_datetime_reminder(datetime_remind_from_ai['time'],
                                                              datetime_remind_from_ai['date'])
    list_controller.write_data_reminder(datetime_reminder, chat_id)
    return datetime_reminder


def set_reminder(datetime_reminder, bot, chat_id):
    list_controller.set_reminder(datetime_reminder, bot, chat_id)
    message_to_recap = list_controller.get_message_time_reminder(datetime_reminder)
    return message_to_recap


def reboot_timer(bot):
    data_timer = list_controller.read_data_reminder()
    for data in data_timer:
        set_reminder(data[0], bot, data[1])


def edit_purchase(query, chat_id):
    purchase_string = list_controller.read_purchase(chat_id)
    purchase_list = list_controller.make_purchase_list(purchase_string)
    inline_keyboard = list_controller.create_inline_keyboard(purchase_list)

    # Удаляем кнопку
    for button in inline_keyboard.keyboard:
        if button[0]['callback_data'] == query.data:
            # Удаляем из клавиатуры
            button_index = inline_keyboard.keyboard.index(button)
            del inline_keyboard.keyboard[button_index]
            # Удаляем из списка
            purchase_list.remove(button[0]['text'])
            # Обновляем список в базе
            purchase_string = list_controller.make_purchase_string(purchase_list)
            list_controller.update_purchase(purchase_string, chat_id)
    return inline_keyboard
