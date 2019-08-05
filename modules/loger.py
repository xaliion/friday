import logging
from subprocess import run
from os.path import getsize


loger = logging.getLogger("Bot")
loger.setLevel(logging.INFO)
log_file = logging.FileHandler("history_work.log")
loger.addHandler(log_file)


def get_loger():
    return loger


def write_proxy_info(proxy):
    # Проверяем, что прокси пришёл в полном формате
    try:
        loger.info('IP: {ip}; Порт: {port}; Страна: {country};'.format(ip=proxy['ip'],
                                                                       port=proxy['port'],
                                                                       country=proxy['country']))
    # Если прокси не в полном формате
    # значит бот попал в бан и использует резервный прокси из файла
    except KeyError:
        loger.error('Прокси не пришел\nИспользую резервный прокси')


def write_proxy_error(description_error):
    loger.error('Прокси отвалился с ошибкой {error}\n'.format(error=description_error))


def check_log_size():
    # Если файл больше или равен 1 Мб, то удаляем лог
    if (getsize('history_work.log') >= 1048576):
        run(['rm', 'history_work.log'])
        loger.info('Чистка лога\n')


check_log_size()
