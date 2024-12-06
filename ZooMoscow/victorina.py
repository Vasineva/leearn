"""
Функция запуска викторины для Telegram-бота
Модуль содержит функции для инициализации викторины,
обработки вопросов и управления взаимодействием с пользователем.

Основные функции:
- start_victorina: Запускает викторину, отправляет вопросы пользователю
  и обрабатывает результаты. Также предусмотрена возможность поделиться результатом
  в соцсетях с ссылкой на Telegram-бота.
  """
import logging
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import results, questions, TELEGRAM_BOT_LINK

user_scores = {}
user_questions = {}

def start_victorina(chat_id, bot):
    # Инициализация пользователя, если это его первый запуск викторины
    if chat_id not in user_scores:
        user_scores[chat_id] = {'score': 0, 'current_question': 0}
    # Если пользователь только начал викторину
    if user_scores[chat_id]['current_question'] == 0:
        with open('Pig/victorina.jpg', 'rb') as photo:
            bot.sendPhoto(chat_id, photo=photo)
        bot.sendMessage(chat_id, "Давайте узнаем, какое ваше тотемное животное! Отвечайте на вопросы викторины.",
                        parse_mode='HTML')
        logging.info(f"Пользователь {chat_id} начал викторину.")
    # Если вопросы еще не закончены
    if user_scores[chat_id]['current_question'] < len(questions):
        question = questions[user_scores[chat_id]['current_question']]
        answers = question["answers"]
        answer_pairs = [answers[i:i + 2] for i in range(0, len(answers), 2)]
        # Формирование клавиатуры для ответа на вопросы
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=ans) for ans in pair] for pair in answer_pairs] +
                     [[KeyboardButton(text='Остановить викторину')]],
            resize_keyboard=True
        )
        bot.sendMessage(chat_id, question["question"], reply_markup=keyboard)
        logging.info(f"Отправлен вопрос {user_scores[chat_id]['current_question'] + 1} пользователю {chat_id}.")
    # Если все вопросы завершены, выводим результат
    else:
        total_score = user_scores[chat_id]['score']
        result = next((res for res in results if res['min_score'] <= total_score <= res['max_score']), None)
        if result:
            user_scores[chat_id]['result'] = result['text']
            bot.sendPhoto(chat_id, photo=result['image_url'])
            bot.sendMessage(chat_id, result['text'], parse_mode='HTML')

            care_program_message = ("\n\nКстати, не забудьте ознакомиться с нашей программой опеки животных! "
                                    "Вы можете поддержать любимое животное в зоопарке.")
            bot.sendMessage(chat_id, care_program_message)

            # Кнопки для социальных сетей
            social_buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Поделиться в ВКонтакте",
                        url=f"https://vk.com/share.php?url={TELEGRAM_BOT_LINK}&title={result['text']}&image={result['image_url']}"
                    )],
                    [InlineKeyboardButton(
                        text="Поделиться в Моем Мире",
                        url=f"https://connect.mail.ru/share?url={TELEGRAM_BOT_LINK}&title={result['text']}"
                    )],
                ]
            )
            bot.sendMessage(chat_id, "Поделитесь результатом с друзьями!", reply_markup=social_buttons)

        else:
            bot.sendMessage(chat_id, "Произошла ошибка при определении результата. Попробуйте снова.")
            logging.warning(f"Пользователь {chat_id} завершил викторину с неопределённым результатом.")
        # Клавиатура для выбора действий после завершения викторины
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Запустить вопросы заново')],
                [KeyboardButton(text='Вернуться в главное меню'),
                 KeyboardButton(text='Узнать подробнее')]
            ],
            resize_keyboard=True
        )
        bot.sendMessage(chat_id, "Вы можете начать викторину заново или вернуться в главное меню.\n"
                                 "Нажав на кнопку 'Узнать подробнее' вы можете связаться с сотрудником зоопарка "
                                 "для получения дополнительной информации.",
                        reply_markup=keyboard)
        # Сбросить данные о викторине
        user_scores[chat_id] = {'score': 0, 'current_question': 0, 'result': user_scores[chat_id].get('result')}
        logging.info(f"Пользователь {chat_id} завершил викторину с результатом: {total_score}.")