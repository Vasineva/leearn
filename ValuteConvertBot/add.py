import telebot
from config import keys, TOKEN
from ClassExcept import ConvertionException, ValuteConvertor

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
# Функция, которая будет довать сообщение, где будут команды /start или /help
def help(message: telebot.types.Message):
    text = "Чтобы начать работу введите команду боту в следующем формате: \n <имя валюты> \
<в какую валюту перевести> \
<количество переводимой валюты> \n Увидеть список всех доступных валют: /values"
    bot.reply_to(message, text) # Ответ пользователю с инструкцией

@bot.message_handler(commands=['values', ])
def values(message: telebot.types.Message):
    text = "Доступные валюты:"
    # Цикл для добавления всех доступных валют в текст
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:

        # Разделение введенной строки из чата, на составляющие и перевод в нижний регистр
        values = message.text.lower().split(' ')
        if len(values) != 3:
            raise ConvertionException("Слишком много или слишком мало параметров.")

        quote, base, amount = values
        # Возврашаем из еxception значения
        converted_amount, conversion_rate = ValuteConvertor.convert(base, quote,  amount, )

    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя \n{e}')

    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду \n{e}')
    else:

        text = f'За {amount} {base} в получите  - {converted_amount} {quote} , цена за один {base} : {conversion_rate} {quote}'
        bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)