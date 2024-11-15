import requests
import json
from config import keys

# Определяем исключение для обработки ошибок конвертации
class ConvertionException(Exception):
    pass

# Определяем класс для конвертации валют
class ValuteConvertor:
    @staticmethod
    def convert (base: str, quote: str,  amount: str):
        # Проверка на равенство валют, они не могут быть одинаковыми
        if quote == base:
            raise ConvertionException(f'Невозмо перевести одинаковые валюты {base}.')

        # Пытаемся получить тикер базовой валюты из словаря keys
        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionException(f'Неудалось обработать валюту {base}.')

        # Пытаемся получить тикер валюты, в которую будем конвертировать
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionException(f'Неудалось обработать валюту {quote}.')

        try:
            # Проверка, что количество для конвертации является числом
            amount = float(amount)
        except ValueError:
            raise ConvertionException(f'Неудалось обработать количество {amount}. Введите число.')
        # Отправляем GET-запрос к API для получения курсов валют
        r = requests.get(
            f'https://v6.exchangerate-api.com/v6/2c4a11f9a43f67a82a7d2f8f/pair/{base_ticker}/{quote_ticker}/{amount}')
        # Парсим ответ JSON, чтобы получить результат конвертации
        converted_amount = json.loads(r.content)['conversion_result']
        conversion_rate = json.loads(r.content)['conversion_rate']
        # Возвращаем преобразованное количество и курс конвертации
        return converted_amount, conversion_rate