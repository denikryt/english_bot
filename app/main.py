from __future__ import annotations
from telebot import types
import traceback
# import yamlext 
import context
import default
import text
import os
import time
import threading
import sqlite3 as sql3
from bot import BOT as bot
import database
from path import directory
from users import write
import datetime
import mongodb_database
from learn import Learn

NAME_ID = {}

MY_ID = 183278535

TARGET_CHANNEL_ID = -1002015277757

MONGO_DB = mongodb_database.MongoDataBase()

global FIRST_MESSAGE
FIRST_MESSAGE = False

@bot.channel_post_handler(func=lambda message: message.chat.id == TARGET_CHANNEL_ID)
def channel_handler(message):
    # return
    # Выводим информацию о сообщении из канала
    print(f"Получено сообщение из канала {message.chat.title} ({message.chat.id}):")
    print(f"Текст: {message.text}")
    
    textData = {
        'text' : message.text
    }

    context.transition_to(text.Text())
    result, language = context.save_text(user_id=MY_ID, textData=textData)

    if result:
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton('Разобрать', callback_data=f'work*{language}*{str(message.message_id)}')
        item2 = types.InlineKeyboardButton('Удалить', callback_data=f'delete*{language}*{str(message.message_id)}')

        markup.add(item1,item2)
        bot.send_message(MY_ID, f'Записал текст!\n{message.text}', reply_markup=markup)

    else:
        bot.send_message(MY_ID, 'There was an error while saving the text')

    last_message_id = MONGO_DB.get_last_message_id(user_id=MY_ID)
    MONGO_DB.update_last_message_id(user_id=MY_ID, message_id=last_message_id+1)

    return

@bot.message_handler(commands=['practice'])
def language(message):
    context.transition_to(learn.Learn())
    context.hello(message=message)

@bot.message_handler(commands=['texts'])
def command_texts(message):
    userData = get_user_data(message)
    global FIRST_MESSAGE
    FIRST_MESSAGE = True

    if user_exists(userData):
        context.transition_to(text.Text())
        context.send_text_window(userData=userData, language='English')
    else:
        bot.send_message(userData['user_id'], 'Press /start to register')

@bot.message_handler(commands=['start'])
def welcome(message):
    userData = get_user_data(message)
    global FIRST_MESSAGE
    FIRST_MESSAGE = True

    if user_exists(userData):
        bot.send_message(userData['user_id'], 'Welcome back!')
    else:
        MONGO_DB.add_new_user(userData)
        bot.send_message(userData['user_id'], 'Welcome! You are registered!')

    MONGO_DB.update_last_message_id(user_id=userData['user_id'], message_id=userData['message_id']+1)
    return

@bot.message_handler(content_types=['text'])
def lalala(message):
    # return
    try:
        userData = get_user_data(message=message)

        context.instructions(userData=userData, message=message)

    except Exception as e:
        send_error(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call): 
    if not FIRST_MESSAGE:
        return
    
    userData = get_user_data(call=call)
    context.inline_buttons(call=call)
    return

    try:
        action, language, text_id = call.data.split('*')

        if action == 'delete':
            result = MONGO_DB.delete_text_by_text_id(language=language, collection_name=userData['user_id'], text_id=int(text_id))
            bot.edit_message_text(text='Удалено!', chat_id=userData['user_id'], message_id=userData['message_id'])
            return
        
        if action == 'work':
            context.transition_to(text.Text())
            context.work_with_text(user_id=userData['user_id'], language=language, text_id=text_id, call=call)
            return
        
    except ValueError:
        try:
            if not context.current_state() == 'Text':
                context.transition_to(text.Text())

            context.inline_buttons(call=call)
        except Exception as e:
            raise
            # send_error(e)


def user_exists(userData):
    if MONGO_DB.is_user_collection_exists(user_id=userData['user_id']):
        return True
    else:
        return False

def get_user_data(message=None, call=None):
    if message:
        user_name = message.from_user.first_name
        user_id = message.chat.id
        message_id = message.message_id
    if call:
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        message_id = call.message.message_id

    return {'user_name' : user_name, 
            'user_id' : user_id, 
            'message_id': message_id}

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

    context = context.Context()
    bot.remove_webhook()
    bot.polling(none_stop=True)




