from __future__ import annotations
from telebot import types
import yaml
import context
import default
import os
import time
import threading
import sqlite3 as sql3
from bot import BOT as bot
import database
# from notify import wait, notification
# from user import User
from learn import Learn
# from users import LAST_MESSAGE
from path import directory
from users import write
import datetime

from flask_sslify import SSLify
from flask import Flask, request

URL = 'kentus.pythonanywhere.com'
app = Flask(__name__)
sslify = SSLify(app)

bot.remove_webhook()
bot.set_webhook(url=URL)

bot.send_message(183278535, 'helo')
context = context.Context(default.Default())

time_to_wait = 10#600
notify_delay = 10#3600

# LAST_MESSAGES = {}
WORKING_USERS = {}
CHAT_ID = {}
STATUS = {}
FIRST_MESSAGE = False
global UPDATED
UPDATED = False

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
        pass

if result:
    for name, data in result.items():
        id = result[name]['id']
        # WORKING_USERS[id] = False
    # for name in result.keys():
        CHAT_ID[name] = id
        # STATUS[id] = 'notify'
    # print(WORKING_USERS)

@app.route('/', methods=['POST', 'GET'])
def get_message():
    update = types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['wiki'])
def language(message):
    global FIRST_MESSAGE
    global UPDATED
    FIRST_MESSAGE = True

    # try:
    if not UPDATED:
        user_name, user_id = name_id(message)
        update_database(user_id, user_name)

        UPDATED = True
    # try:
    context.transition_to(default.Default())
    context.instructions(message)

    # except Exception as e:
    #     send_error(e)

@bot.message_handler(commands=['lang'])
def lang(message):
    global FIRST_MESSAGE
    FIRST_MESSAGE = True
    # try:
    context.language(message, None)

    # except Exception as e:
    #     send_error(e)

@bot.message_handler(commands=['start'])
def welcome(message):
    global FIRST_MESSAGE
    global UPDATED
    # if not FIen
    FIRST_MESSAGE = True

    # try:
    user_name, user_id, message_id = name_id(message, get='message_id')

    if user_id not in CHAT_ID.values():
        # return
        new_user(user_id, user_name)

    if not UPDATED:
        update_database(user_id, user_name)
        UPDATED = True

    items = ['Тестики', 'Загрузить предложения']

    if context._state.__module__ == 'text':
        context.reset()
    context.transition_to(default.Default())

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton(item) for item in items]
    markup.add(*items)
    write(user_name, user_id, message_id=message_id+1, target='last message')
    bot.send_message(user_id, 'Что будем делать?', reply_markup=markup)

    # except Exception as e:
    #     send_error(e)

@bot.message_handler(content_types=['text'])
def lalala(message):
    global FIRST_MESSAGE
    # if not FIRST_MESSAGE:
    #     return
    FIRST_MESSAGE = True
    # try:
    # return
    user_name = message.from_user.first_name
    user_id = message.chat.id
    message_id = message.message_id

    folder_name = user_name + '(' + str(user_id) + ')'
    db, sql = database.connect(folder_name)
    database.create(db, sql)

    if user_id not in CHAT_ID.values():
        bot.send_message(user_id, 'напиши /start !')
    else:
        write(user_name, user_id, message_id=message_id, target='last message')

        context.instructions(message)

    # except Exception as e:
    #     send_error(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # try:
    if not FIRST_MESSAGE:
        return

    context.inline_buttons(None,call)

    # except Exception as e:
    #     send_error(e)

def name_id(message=None, call=None, get=None):
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
    bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

def update_database(user_id, user_name):
    folder_name = user_name + '(' + str(user_id) + ')'
    db, sql = database.connect(folder_name)
    database.create(db, sql)

def new_user(user_id, user_name):
    global UPDATED
    folder_name = user_name + '(' + str(user_id) + ')'
    # WORKING_USERS[user_id] = time_to_wait
    CHAT_ID[user_name] = user_id

    if os.path.isdir(directory(folder_name)) == False:
        os.mkdir(directory(folder_name))

    write(user_name, user_id, target='new user')

    # c = open(directory('count.txt'), 'w')
    # c.close()

    db, sql = database.connect(folder_name)
    database.create(db, sql)
    UPDATED = True

def wait():
    while True:
        time.sleep(1)
        active = [user for user in WORKING_USERS if WORKING_USERS[user]]
        for user in active:
            waiting = WORKING_USERS[user]
            WORKING_USERS[user] = waiting - 1
            if WORKING_USERS[user] == 0:
                WORKING_USERS[user] = False
                STATUS[user] = 'notify'
            print('MINUS', user, WORKING_USERS[user])

def notification():
    # try:
    send_list = []
    while True:
        time.sleep(notify_delay)
        for user in WORKING_USERS:
            active = WORKING_USERS[user]

            if not active:
                print('PLUS')
                send_list.append(user)
        # send_list = [183278535]
        send(CHAT_ID, send_list)

        send_list.clear()

    # except Exception as e:
    #     bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

def send(chat_id, send_list):
    # try:
    for user_id in send_list:
        user_name = list(chat_id.keys())[list(chat_id.values()).index(user_id)]

        d = datetime.datetime.utcnow()
        if d.hour >= 8 <= 24:
            Learn.hello(Learn, user_name, user_id)

    # except Exception as e:
    #     bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

# if __name__ == "__main__":
#     """Client code"""

#     context = context.Context(default.Default())
#     bot.remove_webhook()
#     bot.polling(none_stop=True)

#     # tmp = threading.Thread(target=notification, args=())
#     # tmp.start()
#     # tmp2 = threading.Thread(target=wait, args=())
#     # tmp2.start()




