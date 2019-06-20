import logging
from subprocess import run
from os.path import getsize


loger = logging.getLogger("Bot")
loger.setLevel(logging.INFO)
log_file = logging.FileHandler("history_work.log")
loger.addHandler(log_file)


def write_info(proxy):
    # Проверяем, что прокси пришёл в полном формате
    try:
        loger.info('IP: {ip}; Порт: {port}; Страна: {country};'.format(ip=proxy['ip'],
                                                                       port=proxy['port'],
                                                                       country=proxy['country']))
    # Если прокси не в полном формате
    # значит бот попал в бан и использует резервный прокси из файла
    except KeyError:
        loger.error('Прокси не пришел\n')


def write_error(description_error):
    loger.error('Прокси отвалился с ошибкой {error}\n'.format(error=description_error))


def check_log_size():
    # Проверяем размер файла
    # Если он больше или равен 1 Мб или же 1 048 576 байт, то удаляем лог
    if (getsize('history_work.log') >= 1048576):
        # Запускаем процесс для удаления файла
        run(['rm', 'history_work.log'])
        loger.info('Чистка лога\n')


# Проверяем файл при каждой загрузке модуля
check_log_size()
