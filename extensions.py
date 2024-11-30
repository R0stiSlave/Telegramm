import requests
from Config import keys
from decimal import Decimal


class ConvertionException(Exception):
    pass


class APIConverter:

    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionException(f'Невозможно перевести одинаковые валюты {base}')

        try:
            base_ticker = keys[base]
            quote_ticker = keys[quote]
            amount = Decimal(amount)
        except (KeyError, ValueError) as e:
            raise ConvertionException(f'Ошибка ввода данных: {e}')

        try:
            r = requests.get(
                f'https://v6.exchangerate-api.com/v6/b522cd91907c714644575981/pair/{quote_ticker}/{base_ticker}')
            r.raise_for_status()
            total_base = r.json()['conversion_rate']
            total_base = Decimal(str(total_base)) * amount
            return total_base
        except requests.exceptions.RequestException as e:
            raise ConvertionException(f'Ошибка при обращении к API: {e}')
        except KeyError as e:
            raise ConvertionException(f'Ошибка в ответе API: {e}')
        except ValueError as e:
            raise ConvertionException(f'Ошибка конвертации: {e}')
