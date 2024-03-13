import logging

import telebot
from telebot import types

import config
import database
import gpt

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)

bot = telebot.TeleBot(token=config.telegram_token)


def create_keyboard(options):
    buttons = (types.KeyboardButton(text=option) for option in options)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


def show_keyboard_subject(chat_id, message):
    keyboard = create_keyboard(["/help_with_maths", "/help_with_cook"])
    bot.send_message(chat_id, message, reply_markup=keyboard)


def show_keyboard_subject_and_continue(chat_id, message):
    keyboard = create_keyboard(["/help_with_maths", "/help_with_cook", "continue_answer"])
    bot.send_message(chat_id, message, reply_markup=keyboard)


def show_keyboard_level(chat_id, message):
    keyboard = create_keyboard(['beginner', 'advanced'])
    bot.send_message(chat_id, message, reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    show_keyboard_subject(message.chat.id,
                          f"Приветствую тебя, {user_name}! Я бот-помощник для решения задач по разным предметам!")
    bot.register_next_step_handler(message, subject_command)


def subject_command(message):
    if message.text not in ["/help_with_maths", "/help_with_cook"]:
        start_command(message)
        return

    user_id = message.from_user.id
    db = database.DB()
    db.delete_data(user_id)
    db.insert_data(user_id, message.text)

    show_keyboard_level(message.chat.id, "Выбери свой уровень знаний:")
    bot.register_next_step_handler(message, level_command)


def level_command(message):
    if message.text not in ["beginner", "advanced"]:
        subject_command(message)
        return

    user_id = message.from_user.id
    db = database.DB()
    db.update_data(user_id, 'level', message.text)

    show_keyboard_level(message.chat.id, "Отлично! Теперь напиши сообщение со своей задачей:")


@bot.message_handler(commands=['debug'])
def debug_command(message):
    with open(config.log_file, "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['text'])
def callback(message):
    user_id = message.from_user.id

    db = database.DB()
    subject = db.select_data(user_id).subject
    level = db.select_data(user_id).level

    if not subject:
        show_keyboard_subject(message.chat.id, "Пожалуйста, выбери предмет, нажав на кнопку")
        return

    if not level:
        show_keyboard_level(message.chat.id, "Пожалуйста, выбери уровень сложности")
        return

    task = message.text
    system_prompt = config.get_gpt_system_content(subject, level)
    user_gpt = gpt.GPT(system_prompt)

    if task != "continue_answer":
        request_tokens = user_gpt.count_tokens(task)
        while request_tokens > user_gpt.MAX_TOKENS:
            bot.send_message(message.chat.id, "Сообщение не соответствует кол-ву токенов. Исправь сообщение:")
            request_tokens = user_gpt.count_tokens(task)
        db.update_data(user_id, 'task', task)
        db.update_data(user_id, 'answer', None)

    task = db.select_data(user_id).task
    bot.send_message(message.chat.id, "Решаю...")
    answer = db.select_data(user_id).answer
    if not answer:
        answer = " "
    gpt_response = user_gpt.send_request(task, answer)
    if gpt_response.status:
        db.update_data(user_id, 'answer', " ".join([answer, gpt_response.message]))
    if not gpt_response.message:
        show_keyboard_subject_and_continue(message.chat.id, 'Извини, у меня лапки:(')
    else:
        show_keyboard_subject_and_continue(message.chat.id, gpt_response.message)


bot.polling()
