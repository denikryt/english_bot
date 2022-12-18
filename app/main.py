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
# from notification import notify
# from user import User
from learn import Learn
# from users import LAST_MESSAGE
from path import directory
from users import write
import datetime

from flask_sslify import SSLify
from flask import Flask, request

time_to_wait = 10#600
notify_delay = 10#3600

# LAST_MESSAGES = {}
USER_ACTIVITY = {}
NAME_ID = {}
STATUS = {}
FIRST_MESSAGE = False
global UPDATED
UPDATED = False
ACTIVE_TIMER = 10 #sec
NOTIFY_DELAY = 10 #min

MY_ID = 183278535

# URL = 'kentus.pythonanywhere.com'
# bot.set_webhook(url=URL)

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
        USER_ACTIVITY[id] = False
    # for name in result.keys():
        NAME_ID[name] = id
        # STATUS[id] = 'notify'
    # print(USER_ACTIVITY)

@bot.message_handler(commands=['wiki'])
def language(message):
    global FIRST_MESSAGE
    global UPDATED
    FIRST_MESSAGE = True

    user_name, user_id = get_name_id(message)

    USER_ACTIVITY[user_id] = ACTIVE_TIMER

    # try:
    if not UPDATED: 
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
    # return
    global FIRST_MESSAGE
    global UPDATED
    # if not FIen
    FIRST_MESSAGE = True

    # try:
    user_name, user_id, message_id = get_name_id(message, get='message_id')

    USER_ACTIVITY[user_id] = ACTIVE_TIMER

    if user_id not in NAME_ID.values():
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
    # return
    global FIRST_MESSAGE
    # if not FIRST_MESSAGE:
    #     return
    FIRST_MESSAGE = True
    try:
    # return
        user_name, user_id, message_id = get_name_id(message, get='message_id')

        # USER_ACTIVITY[user_id] = ACTIVE_TIMER
        # print(f'ОБНОВЛЯЮ {USER_ACTIVITY[user_id]}')

        # folder_name = user_name + '(' + str(user_id) + ')'
        # db, sql = database.connect(folder_name)
        # database.create(db, sql)

        if user_id not in NAME_ID.values():
            bot.send_message(user_id, 'напиши /start !')
        else:
            write(user_name, user_id, message_id=message_id, target='last message')

            context.instructions(message)

    except Exception as e:
        send_error(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # return

    user_name, user_id = get_name_id(call=call)

    USER_ACTIVITY[user_id] = ACTIVE_TIMER
    # print(f'ОБНОВЛЯЮ {USER_ACTIVITY[user_id]}')
    try:
    # if not FIRST_MESSAGE:
    #     return

    # if call.data == 'guess' or 'new':
    #     if context._state.__module__ != 'learn':
    #         context.transition_to(default.Learn())
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
    bot.send_message(183278535, "<b>ERROR!</b> {0} \npress /start".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

def update_database(user_id, user_name):
    folder_name = user_name + '(' + str(user_id) + ')'
    db, sql = database.connect(folder_name)
    database.create(db, sql)

def new_user(user_id, user_name):
    global UPDATED
    folder_name = user_name + '(' + str(user_id) + ')'
    # USER_ACTIVITY[user_id] = time_to_wait
    NAME_ID[user_name] = user_id

    if os.path.isdir(directory(folder_name)) == False:
        os.mkdir(directory(folder_name))

    write(user_name, user_id, target='new user')

    # c = open(directory('count.txt'), 'w')
    # c.close()

    db, sql = database.connect(folder_name)
    database.create(db, sql)
    UPDATED = True

def notify():
    last_notify = datetime.datetime.now()

    while True:
        time.sleep(1)

        if USER_ACTIVITY[MY_ID] != False:
            USER_ACTIVITY[MY_ID] -= 1
            print(f'УДАЛЯЮ {USER_ACTIVITY[MY_ID]}')
            if USER_ACTIVITY[MY_ID] == 0:
                USER_ACTIVITY[MY_ID] = False
                last_notify = datetime.datetime.now()
        else:
            if datetime.datetime.now().hour >= 8 <= 23: #?????
                now = datetime.datetime.now()

                time_passed = now - last_notify 
                time_passed = int(time_passed.total_seconds()//60)
                print(f'ПРОШЛО ВРЕМЕНИ {time_passed}')

                if time_passed >= NOTIFY_DELAY:
                    last_notify = datetime.datetime.now()
                    context.transition_to(default.Learn())
                    context.hello(case='notify', user_name='Ö', user_id=MY_ID,)


def host_bot():

    URL = 'kentus.pythonanywhere.com'
    app = Flask(__name__)
    sslify = SSLify(app)

    bot.remove_webhook()
    bot.set_webhook(url=URL)

    bot.send_message(183278535, 'helo')
    context = context.Context(default.Default())

# @app.route('/', methods=['POST', 'GET'])
# def get_message():
#     update = types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200

# host_bot()

if __name__ == "__main__":
    """Client code"""
    # tmp = threading.Thread(target=notify, args=())
    # tmp.start()

    context = context.Context(default.Default())
    # context.transition_to(default.Learn())
    # context.hello(case='notify', user_name='Ö', user_id=MY_ID,)
    bot.remove_webhook()
    bot.polling(none_stop=True)

    
#     # tmp2 = threading.Thread(target=wait, args=())
#     # tmp2.start()




