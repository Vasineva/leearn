"""
Модуль обработки сообщений для телеграм-бота.
Содержит функции для обработки текстовых сообщений, управление
викторинами, взаимодействие с пользователем и администратором, а
также управление отзывами.

Основные функции:
- handle_message: Основная функция, обрабатывающая входящие сообщения
  и выполняющая соответствующие действия в зависимости от команды
  пользователя или состояния диалога.
"""
import logging
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from config import admin_chat_id, care_program_text, questions
from victorina import start_victorina, user_scores, user_questions
from utils import save_feedback, reply_to_user, show_start_keyboard


def handle_message(msg, bot):
    chat_id = msg['chat']['id']
    command = msg.get('text')

    # Обработка мультимедийных сообщений
    if any(key in msg for key in ['photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice']):
        bot.sendMessage(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")
        logging.warning(f"Мультимедийное сообщение проигнорировано от пользователя {chat_id}.")
        return
    if not command:
        logging.warning(f"Получено сообщение без текста от пользователя {chat_id}: {msg}")
        return

    if chat_id == int(admin_chat_id):
        if reply_to_user(msg, bot, user_questions):
            return
    if command == '/start':
        show_start_keyboard(bot, chat_id)
    elif command == 'Вернуться в главное меню':
        show_start_keyboard(bot, chat_id)
    # Команды викторины
    elif command == 'Узнать свое тотемное животное':
        start_victorina(chat_id, bot)
    elif command == 'Запустить вопросы заново':
        start_victorina(chat_id, bot)
    elif command == 'Остановить викторину':
        logging.info(f"Пользователь {chat_id} остановил викторину")
        show_start_keyboard(bot, chat_id)
        user_scores[chat_id] = {'score': 0, 'current_question': 0}
    # Обработка ответа на вопросы викторины
    elif chat_id in user_scores and user_scores[chat_id]['current_question'] < len(questions) and command in \
            questions[user_scores[chat_id]['current_question']]["answers"]:
        index = questions[user_scores[chat_id]['current_question']]["answers"].index(command)
        user_scores[chat_id]['score'] += questions[user_scores[chat_id]['current_question']]['points'][index]
        user_scores[chat_id]['current_question'] += 1
        logging.info(f"Пользователь {chat_id} ответил на вопрос, ответом '{command}'")
        start_victorina(chat_id, bot)
    # Обработка общения с администратором
    elif command == 'Узнать подробнее':
        logging.info(f"Пользователь {chat_id} инициировал диалог с администратором.")
        result = user_scores.get(chat_id, {}).get('result',
                                                  "Пользователь ещё не проходил викторину или результат был сброшен.")
        bot.sendMessage(chat_id, "Введите свой вопрос:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Остановить разговор')]], resize_keyboard=True))
        user_questions[chat_id] = {'state': 'active', 'question_msg_id': None, 'result': result}
    elif chat_id in user_questions and user_questions[chat_id]['state'] == 'active':
        if command == 'Остановить разговор':
            logging.info(f"Пользователь {chat_id} завершил диалог с администратором.")
            bot.sendMessage(admin_chat_id, f"Пользователь с ID {chat_id} завершил диалог.")
            show_start_keyboard(bot, chat_id)
            user_questions.pop(chat_id, None)
        else:
            if chat_id in user_scores:
                result = user_questions[chat_id].get('result', "Результат викторины не определён.")
                user_question_text = msg.get('text')
                question_msg = bot.sendMessage(admin_chat_id, f"Вопрос от пользователя {chat_id}:\n"
                                                              f"{user_question_text}\n\n"
                                                              f"Результат викторины: {result}")
                user_questions[chat_id]['question_msg_id'] = question_msg['message_id']
                bot.sendMessage(chat_id, "Ваш вопрос отправлен администратору, ждите ответа.")
                logging.info(f"Пользователь {chat_id} отправил сообщение администратору: {user_question_text}")
    # Команды для отзыва
    elif command == 'Оставить отзыв':
        logging.info(f"Пользователь {chat_id} начал оставлять отзыв.")
        with open('Pig/feedbacks.jpg', 'rb') as photo:
            bot.sendPhoto(chat_id, photo=photo)
        bot.sendMessage(chat_id, "Пожалуйста, оставьте свой отзыв:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True))
        user_questions[chat_id] = {'state': 'waiting_for_feedback'}
    elif command == 'Отмена' and chat_id in user_questions:
        logging.info(f"Пользователь {chat_id} отменил оставление отзыва.")
        show_start_keyboard(bot, chat_id)
        user_questions.pop(chat_id, None)
    elif chat_id in user_questions and user_questions[chat_id].get('state') == 'waiting_for_feedback':
        feedback_text = msg.get('text')
        save_feedback(feedback_text, chat_id)
        bot.sendMessage(chat_id, "Ваш отзыв был отправлен. Спасибо!", reply_markup=show_start_keyboard(bot, chat_id))
        user_questions.pop(chat_id, None)
    # Команда программы опеки
    elif command == 'Посмотреть программу опеки':
        logging.info(f"Пользователь {chat_id} запросил программу опеки.")
        with open('Pig/programm.jpg', 'rb') as photo:
            bot.sendPhoto(chat_id, photo=photo)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Узнать свое тотемное животное')],
                      [KeyboardButton(text='Вернуться в главное меню')]],
            resize_keyboard=True
        )
        bot.sendMessage(chat_id, care_program_text, reply_markup=keyboard, parse_mode="Markdown")
    # Ответ по умолчанию для нераспознанных команд
    else:
        logging.warning(f"Пользователь {chat_id} отправил нераспознанную команду: {command}")
        bot.sendMessage(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")
