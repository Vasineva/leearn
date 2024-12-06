"""
Модуль обрабатывает взаимодействие с пользователями телеграм-бота,
включая создание клавиатуры, сохранение отзывов
и ответ администратору на вопросы пользователей.

Основные функции:
- show_start_keyboard: Отправляет приветственное сообщение с клавиатурой
  для взаимодействия и прикрепляет изображение.
- save_feedback: Сохраняет отзывы пользователей в файл с временной меткой.
- reply_to_user: Обрабатывает сообщения от администраторов и отправляет
  ответы пользователям на их вопросы.
"""
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import datetime
import logging

# Отправляет приветственное сообщение с клавиатурой для взаимодействия.
def show_start_keyboard(bot, chat_id):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Узнать свое тотемное животное'),
                   KeyboardButton(text='Посмотреть программу опеки')],
                  [KeyboardButton(text='Оставить отзыв')]],
        resize_keyboard=True
    )
    with open('Pig/start.jpg', 'rb') as photo:
        bot.sendPhoto(chat_id, photo=photo)
    bot.sendMessage(chat_id, 'Привет! Я — бот Московского зоопарка! Здесь вы можете пройти увлекательную викторину, '
                              'чтобы узнать свое тотемное животное, а также получить информацию о программе '
                              'опеки над нашими обитателями.\n\n'
                              '<b>Команда:</b> /start - запускает меня',
                    reply_markup=keyboard, parse_mode='HTML')
# Сохраняет отзывы пользователей в файл с временной меткой.
def save_feedback(feedback, chat_id):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('feedbacks.txt', 'a', encoding='utf-8') as f:
        f.write(f"Дата: {date}, ID чата: {chat_id}, Отзыв: {feedback}\n")
    logging.info(f"Сохранен отзыв от пользователя {chat_id}: {feedback}")


# Обрабатывает ответы администратора и отправляет ответы пользователям.
def reply_to_user(admin_msg, bot, user_questions):
    admin_chat_id = admin_msg['chat']['id']

    if 'reply_to_message' in admin_msg:
        reply_to_message = admin_msg['reply_to_message']
        reply_to_message_id = reply_to_message['message_id']

        for user_chat_id, question_info in user_questions.items():
            if question_info.get('question_msg_id') == reply_to_message_id:
                if admin_msg['text'].strip().lower() == '/end_dialog':
                    # Завершение диалога
                    bot.sendMessage(user_chat_id, "Администратор завершил диалог. Возвращаем вас в главное меню.")
                    show_start_keyboard(bot, user_chat_id)
                    del user_questions[user_chat_id]
                    bot.sendMessage(admin_chat_id, f"Диалог с пользователем {user_chat_id} завершён.")
                    logging.info(f"Администратор завершил диалог с пользователем {user_chat_id}.")
                    return True
                else:
                    # Отправка ответа от администратора пользователю
                    bot.sendMessage(user_chat_id, f"Ответ администратора: {admin_msg['text']}")
                    bot.sendMessage(admin_chat_id, f"Ответ отправлен пользователю с ID: {user_chat_id}")
                    logging.info(f"Администратор ответил пользователю {user_chat_id}: {admin_msg['text']}")
                    return True

        bot.sendMessage(admin_chat_id, "Ошибка: не удалось найти пользователя для ответа.")
    else:
        bot.sendMessage(admin_chat_id, "Ошибка: это сообщение не является ответом на вопрос пользователя.")
    return False


