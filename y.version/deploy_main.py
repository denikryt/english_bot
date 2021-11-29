from __future__ import annotations
from telebot import types
import yaml
import context
import default
import os
# import shutil
# from time import sleep, time
import sqlite3 as sql3
from flask import Flask, request
from bot import BOT as bot
import database #import connect
from flask_sslify import SSLify

#общая переменная для последнего сообщения

URL = 'kentus.pythonanywhere.com'
app = Flask(__name__)
sslify = SSLify(app)

text_window = 0
chat_id = []

# with open('chat_id.txt', 'w') as c:
#     pass
c = open('chat_id.txt', 'r')
chat_id = c.read().splitlines()
print(chat_id)
c.close()

bot.remove_webhook()
bot.set_webhook(url=URL)

context = context.Context(default.Default())

@bot.message_handler(commands=['lang'])
def language(message):

    user_id = message.chat.id

    if context._state.__module__ == 'text':
        # context.transition_to(default.Default())
        context.reset()
        context.transition_to(default.Default())

    items = ['Английский', 'Турецкий', 'Французский', 'Итальянский']

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton(item) for item in items]
    markup.add(*items)

    bot.send_message(user_id, 'C каким языком будешь работать?', reply_markup=markup)

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        # gfdf +=1
    # return
        if str(message.chat.id) not in chat_id:

            user_name = message.from_user.first_name
            user_id = message.chat.id
            folder_name = user_name + '(' + str(user_id) + ')'

            if os.path.isdir(folder_name) == False:
                os.mkdir(folder_name)

            c = open(folder_name+'/count.txt', 'w')
            c.close()

            c = open('chat_id.txt', 'a')
            chat_id.append(message.chat.id)
            c.write(str(message.chat.id)+'\n')
            c.close()

            db, sql = database.connect(folder_name)
            database.create(db, sql)


        # if message.text == 'Загрузить предложения':
        #     text_window = message.message_id+1

        items = ['Работать с текстом', 'Загрузить предложения']

        if context._state.__module__ == 'text':
            # context.transition_to(default.Default())
            context.reset()
            context.transition_to(default.Default())

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in items]
        markup.add(*items)
        bot.send_message(message.chat.id, 'Что будем делать?', reply_markup=markup)

    # except:
    except Exception as e:
        bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

@bot.message_handler(content_types=['text'])
def lalala(message):
    try:
        context.instructions(message)
    except Exception as e:
        bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')
    # print(message.text)
    # if message.text == 'Загрузить предложения':
    #     pass
    # else:
    #     context.instructions(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == 'learn':
            context.transition_to(default.Default())
            context.inline_buttons(None, call)

        if call.data == 'main_menu':
            context.transition_to(default.Default())
            context.inline_buttons(None, call)

        else:
            context.inline_buttons(None,call)
    except Exception as e:
        bot.send_message(183278535, "<b>ERROR!</b> {0}".format(str(e.args[0])).encode("utf-8"), parse_mode='html')

@app.route('/', methods=['POST', 'GET'])
def get_message():
    update = types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

bot.send_message(183278535, 'helo')

# if __name__ == "__main__":
#     """Client code"""
#     # import context
#     # import default

#     context = context.Context(default.Default())
#     # app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
#     # while True:
#     #     try:
#     bot.remove_webhook()
#     bot.polling(none_stop=False)
#     #     except:
#     #         # context.transition_to(default.Default())
#     #         # sleep(10)
#     #         raise

