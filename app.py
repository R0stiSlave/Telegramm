import decimal
import telebot
from Config import keys, TOKEN
from extensions import APIConverter, ConvertionException
from decimal import Decimal, ROUND_HALF_UP
from telebot import types

bot = telebot.TeleBot(TOKEN)

currencies = list(keys.keys())

user_data = {}


def create_keyboard(items, row_width=2):
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    buttons = [types.InlineKeyboardButton(text=item, callback_data=item) for item in items]
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=['start', 'help'])
def help(message: types.Message):
    text = 'Чтобы начать работу, выберите валюту:'
    markup = create_keyboard(currencies)
    bot.reply_to(message, text, reply_markup=markup)


@bot.message_handler(commands=['values'])
def values(message: types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)


@bot.callback_query_handler(func=lambda call: call.data in currencies)
def handle_currency_selection(call: types.CallbackQuery):
    if 'quote' not in user_data:
        user_data['quote'] = call.data
        text = 'Теперь выберите валюту, в которую хотите перевести:'
        markup = create_keyboard(currencies)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup)
    else:
        user_data['base'] = call.data
        text = 'Введите количество:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=None)
        bot.register_next_step_handler(call.message, handle_amount)


def handle_amount(message: types.Message):
    try:
        amount = Decimal(message.text)
        total_base = APIConverter.get_price(user_data['quote'], user_data['base'], amount)
        rounded_total = total_base.quantize(Decimal("0.00"), ROUND_HALF_UP)
        text = f'Цена {amount} {user_data["quote"]} в {user_data["base"]} = {rounded_total}'
        bot.send_message(message.chat.id, text)
        user_data.clear()
    except ConvertionException as e:
        bot.reply_to(message, f"Ошибка конвертации: {e}")
    except decimal.InvalidOperation:
        bot.reply_to(message, "Неверный формат числа.")
    except Exception as e:
        bot.reply_to(message, f"Произошла непредвиденная ошибка: {e}")


bot.polling()

"""Рабочий вариант"""
