import telebot
from telebot import types

import env
import gpt

bot = telebot.TeleBot(token=env.telegram_token)


@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    bot.send_message(message.from_user.id, text=f"Приветствую тебя, {user_name}!")
    bot.send_message(message.chat.id,
                     'Это бот-GPT! В этом боте вы можете получить ответы на некоторые вопросы. '
                     'Я надеюсь, что вам понравится моя работа и вы прорекламируете меня друзьям!😁'
                     '(Еще бот умеет отвечать на простые сообщения, типа - (привет) или (пока)')
    bot.send_message(message.chat.id, "Это список команд, которые я умею выполнять:\n"
                                      "/start - Начать работу с ботом.\n")
    show_keyboard(message.chat.id)

@bot.message_handler(commands=['debug'])
def debug_command(message):
    user_id = message.from_user.id
    user_gpt = gpt.GPT(user_id)
    if not user_gpt.last_error_message:
        bot.send_message(message.chat.id, "ошибок нет")
    else:
        bot.send_message(message.chat.id, f"ошибка:\n\n{user_gpt.last_error_message}")
    show_keyboard(message.chat.id)


@bot.message_handler(content_types=['text'])
def callback(message):
    user_id = message.from_user.id
    user_gpt = gpt.GPT(user_id)
    user_request = message.text
    if "Запрос" in user_request:
        bot.send_message(message.chat.id, "Введите запрос:", reply_markup=types.ReplyKeyboardRemove())
        return
    if user_request != "Продолжить":
        request_tokens = user_gpt.count_tokens(user_request)
        while request_tokens > user_gpt.MAX_TOKENS:
            bot.send_message(message.chat.id, "Запрос несоответствует кол-ву токенов. Исправьте запрос: ")
            request_tokens = user_gpt.count_tokens(user_request)
    gpt_response = user_gpt.send_request(user_request)
    if not gpt_response.status:
        bot.send_message(message.chat.id, "упс...")
    else:
        bot.send_message(message.chat.id, gpt_response.message)
    show_keyboard(message.chat.id)


def show_keyboard(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    start_btn = types.KeyboardButton(text="Запрос")
    continue_btn = types.KeyboardButton(text="Продолжить")
    keyboard.add(start_btn, continue_btn)
    bot.send_message(chat_id, "Выберите команду", reply_markup=keyboard)


bot.polling()
