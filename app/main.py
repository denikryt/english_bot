from __future__ import annotations
from telebot import types
import traceback
import yaml
import context
import default
import os
import time
import threading
import sqlite3 as sql3
from bot import BOT as bot
import database
from path import directory
from users import write
import datetime

from flask_sslify import SSLify
from flask import Flask, request
import nltk

nltk.download('punkt')

NAME_ID = {}

MY_ID = 183278535

file_name = 'users.yaml'

file_exists = os.path.exists(directory(file_name))

if not file_exists:
    with open(directory(file_name), 'w', encoding='utf-8') as f:
        data = {
            'users':{}
        }
        yaml.safe_dump(data, f)

with open(directory(file_name), 'r', encoding='utf-8') as f:
    try:
        result = yaml.load(f, Loader=yaml.FullLoader)['users']
    except TypeError:
        raise

if result:
    for id, data in result.items():
        name = result[id]['name']
        NAME_ID[id] = name

@bot.message_handler(commands=['wiki'])
def language(message):
    # return
    try:
        user_name, user_id = get_name_id(message)

        context.transition_to(default.Default())
        context.instructions(message)

    except Exception as e:
        send_error(e)

@bot.message_handler(commands=['lang'])
def lang(message):
    try:
        context.language(message, None)

    except Exception as e:
        send_error(e)

@bot.message_handler(commands=['start'])
def welcome(message):

    try:
        user_name, user_id, message_id = get_name_id(message, get='message_id')

        if user_id not in NAME_ID.keys():
            new_user(user_id, user_name)

        if user_id != 183278535:
            text = f"""<b>{user_name} ({user_id})</b>\n{message.text}"""
            bot.send_message(183278535, text, parse_mode='html')

        items = ['Тестики', 'Загрузить текст']

        if context._state.__module__ == 'text':
            context.reset()
        context.transition_to(default.Default())

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in items]
        markup.add(*items)
        write(user_name, user_id, message_id=message_id+1, target='last message')
        bot.send_message(user_id, 'Что будем делать?', reply_markup=markup)

    except Exception as e:
        send_error(e)

@bot.message_handler(content_types=['text'])
def lalala(message):
    # return
    try:
        user_name, user_id, message_id = get_name_id(message, get='message_id')

        if user_id not in NAME_ID.keys():
            bot.send_message(user_id, 'напиши /start !')
        else:
            if user_id != 183278535:
                text = f"""<b>{user_name} ({user_id})</b>\n{message.text}"""
                bot.send_message(183278535, text, parse_mode='html')
            write(user_name, user_id, message_id=message_id, target='last message')

            context.instructions(message)

    except Exception as e:
        send_error(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # return
    user_name, user_id = get_name_id(call=call)

    try:
        context.inline_buttons(None,call)

    except Exception as e:
        send_error(e)

def get_name_id(message=None, call=None, get=None):
    if message:
        user_name = message.from_user.first_name
        user_id = message.chat.id
        message_id = message.message_id
    if call:
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        message_id = call.message.message_id
    if get == 'message_id':
        return user_name, user_id, message_id
    return user_name, user_id

def send_error(e):
    tb = traceback.format_exc()
    bot.send_message(183278535, "<b>ERROR!</b> {0} \npress /start".format(str(tb)+'\n'+str(e.args[0])).encode("utf-8"), parse_mode='html')
    # bot.send_message(183278535, "<b>ERROR!</b> {0} \npress /start".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

def update_database(user_id, user_name):
    folder_name = user_name + '(' + str(user_id) + ')'
    db, sql = database.connect(folder_name)
    database.create(db, sql)

def new_user(user_id, user_name):
    folder_name = user_name + '(' + str(user_id) + ')'
    NAME_ID[user_id] = user_name

    if os.path.isdir(directory(folder_name)) == False:
        os.mkdir(directory(folder_name))

    write(user_name, user_id, target='new user')

    db, sql = database.connect(folder_name)
    database.create(db, sql)


# URL = 'kentus.pythonanywhere.com'
# app = Flask(__name__)
# sslify = SSLify(app)

# bot.remove_webhook()
# bot.set_webhook(url=URL)

# bot.send_message(183278535, 'helo')
# context = context.Context(default.Default())

# @app.route('/', methods=['POST', 'GET'])
# def get_message():
#     update = types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200

# host_bot()

if __name__ == "__main__":
    """Client code"""

    context = context.Context(default.Default())
    bot.remove_webhook()
    bot.polling(none_stop=True)




