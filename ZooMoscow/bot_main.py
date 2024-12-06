
"""
Модуль представляет собой основной файл для запуска телеграм-бота.

Использует библиотеку telepot для взаимодействия с API Telegram и
обрабатывает входящие сообщения через функцию handle_message.

Настроено логирование для отслеживания событий и ошибок.

Основные функции:
- Инициализация бота с токеном.
- Запуск цикла обработки сообщений.
- Логирование успешного старта бота.

Перед использованием убедитесь, что token указан в config.py
"""
import telepot
import logging
from telepot.loop import MessageLoop
from config import TOKEN
from handlers import handle_message

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

bot = telepot.Bot(TOKEN)
# Запуск цикла обработки сообщений. При поступлении сообщения вызывается функция handle_message
MessageLoop(bot, lambda msg: handle_message(msg, bot)).run_as_thread()
logging.info("Бот успешно запущен и ожидает сообщений.")

# Бесконечный цикл, чтобы бот продолжал работать. Пока нет других задач, используется pass.
while True:
    pass