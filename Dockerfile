# Используем базовый образ для нашего
FROM python:stretch

# Создаём директорию бота
RUN mkdir /friday

# Копируем все файлы из текущей директории в директорию бота
COPY . /friday

# Устанавливаем рабочую директорию
WORKDIR /friday

# Устанавливаем pytelegrambotapi и apiai
RUN pip3 install --no-cache-dir pytelegrambotapi
RUN pip3 install --no-cache-dir apiai
RUN pip3 install --no-cache-dir configparser

# Устанавливаем тайм зону
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем локаль
RUN apt update && apt install -y --no-install-recommends locales; \
rm -rf /var/lib/apt/lists/*; \
sed -i '/^#.* ru_RU.UTF-8 /s/^#//' /etc/locale.gen; \
locale-gen

# Указываем команды для выполнения после запуска контейнера
CMD ["python3", "bot.py"]
