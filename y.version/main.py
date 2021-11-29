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
from notify import wait, notification
# from user import User 
from learn import Learn
from users import LAST_MESSAGE


time_to_wait = 30
LAST_MESSAGES = {}
WORKING_USERS = {}
CHAT_ID = {}

file_exists = os.exists('chat_id.yaml')
if not file_exists:
    with open('chat_id.yaml', 'w', encoding='utf-8') as f:
        write = {'users':None}
        yaml.safe_dump(write, f)

with open('chat_id.yaml', 'r', encoding='utf-8') as f:
    try:
        CHAT_ID = yaml.load(f, Loader=yaml.FullLoader)['users']
    except TypeError:
        pass

for id in CHAT_ID.values():
    WORKING_USERS[id] = False
print(WORKING_USERS)


@bot.message_handler(commands=['lang'])
def language(message):
    context.language(message, None)

@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name
    user_id = message.chat.id
    WORKING_USERS[user_id] = time_to_wait
    
    if str(user_id) not in CHAT_ID:
        # return
        new_user(user_id, user_name)
        
    items = ['Работать с текстом', 'Загрузить предложения']

    if context._state.__module__ == 'text':
        context.reset()
        context.transition_to(default.Default())
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton(item) for item in items]
    markup.add(*items)
    bot.send_message(user_id, 'Что будем делать?', reply_markup=markup)
     
@bot.message_handler(content_types=['text'])
def lalala(message):
    user_id = message.chat.id
    WORKING_USERS[user_id] = time_to_wait

    if WORKING_USERS[user_id] == False:
        Learn.instructions(message)

    context.instructions(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    WORKING_USERS[user_id] = time_to_wait

    if WORKING_USERS[user_id] == False:
        Learn.inline_buttons(None, call)

    if call.data == 'learn':
        context.transition_to(default.Default())
        context.inline_buttons(None, call)

    if call.data == 'main_menu':
        context.transition_to(default.Default())
        context.inline_buttons(None, call)

    else:
        context.inline_buttons(None,call)

def new_user(user_id, user_name):
    folder_name = user_name + '(' + str(user_id) + ')'
    WORKING_USERS[user_id] = time_to_wait
    CHAT_ID[user_name] = user_id

    chat_id = {
        'users': CHAT_ID
    }

    if os.path.isdir(folder_name) == False:
        os.mkdir(folder_name)

    with open('chat_id.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(chat_id, f, allow_unicode=True)

    c = open(folder_name+'\\count.txt', 'w')
    c.close()

    db, sql = database.connect(folder_name)
    database.create(db, sql)

# def wait():
#     while True:
#         time.sleep(1)
#         active = [user for user in WORKING_USERS if WORKING_USERS[user]]
#         for user in active:           
#             waiting = WORKING_USERS[user]
#             WORKING_USERS[user] = waiting - 1 
#             if WORKING_USERS[user] == 0:
#                 WORKING_USERS[user] = False
#             print('MINUS', user, WORKING_USERS[user])

# def notification():
#     send_list = []
#     while True:
#         for user in WORKING_USERS:
#             active = WORKING_USERS[user]

#             if not active:
#                 print('PLUS')
#                 send_list.append(user)
#         send_list = [183278535]
#         send(CHAT_ID, send_list)

#         send_list.clear()
#         time.sleep(10)

# def send(chat_id, send_list):
#     for user_id in send_list:
#         user_name = list(chat_id.keys())[list(chat_id.values()).index(user_id)]

#         Learn.hello(Learn, user_name, user_id)


if __name__ == "__main__":
    """Client code"""

    tmp = threading.Thread(target=notification, args=())
    tmp.start()
    tmp2 = threading.Thread(target=wait, args=())
    tmp2.start()

    context = context.Context(default.Default())
    bot.remove_webhook()
    bot.polling(none_stop=False)

            
