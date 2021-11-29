# from flask import Flask, request
# from flask_sslify import SSLify
# from telebot import types
# from bot import BOT as bot
try:
    execfile('error.py')
except:
    print('oh')


# app = Flask(__name__)
# sslify = SSLify(app)

# @app.route('/', methods=['POST', 'GET'])
# def get_message():
#     update = types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200
