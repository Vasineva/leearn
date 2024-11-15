
import telebot
import requests
import json

TOKEN = '7773434731:AAHffwX4HSmrnoU9cjizVzZTeHALwxSfWuA'

bot = telebot.TeleBot(TOKEN)

keys = {
    'рубль': 'RUB',
    'евро' : 'EUR',
    'доллар' : 'USD',
}

class ConvertionException(Exception):
    pass

class CryptoConvertor:
    @staticmethod
    def convert (quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionException(f'Невозмо перевести одинаковые валюты {base}.')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionException(f'Неудалось обработать валюту {quote}.')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionException(f'Неудалось обработать валюту {base}.')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionException(f'Неудалось обработать количество {amount}.')
        r = requests.get(
            f'https://v6.exchangerate-api.com/v6/2c4a11f9a43f67a82a7d2f8f/pair/{quote_ticker}/{base_ticker}/{amount}')
        total_base = json.loads(r.content)
        return total_base['conversion_result']



@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = "Чтобы начать работу введите команду боту в следуюшем формате: \n <имя валюты> \
<в какую валюту перевести> \
<количество переводимой валюты> \n Увидеть список всех доступных валют: /values"
    bot.reply_to(message, text)

@bot.message_handler(commands=['values', ])
def values(message: telebot.types.Message):
    text = "Доступные валюты:"
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    values = message.text.split(' ')

    if len(values) != 3:
        raise ConvertionException("Слишком много параметров.")

    quote, base, amount = values
    total_base = CryptoConvertor.convert(quote, base, amount, )
    text = f'Цена {amount} {quote} в {base} - {total_base} {base}'
    bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)


