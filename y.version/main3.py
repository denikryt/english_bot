# from main import bot
# from flask import Flask, request
# from flask_sslify import SSLify
from telebot import TeleBot, types
from bot import BOT as bot
# import yaml
# import os
# import context
# import default


@bot.message_handler(commands=['start'])
def welcome(message):
    pass

@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(message.chat.id, 'hello')



if __name__ == "__main__":
    """Client code"""





# # CONFIGFILE = 'config.yaml'
# SECRET = 'ifposldnnf333'
# URL = 'https://kentus.pythonanywhere.com/' + SECRET

# # with open(CONFIGFILE, 'r') as f:
# #     token = yaml.load(f, Loader=yaml.FullLoader)['config']['token']

# # bot = TeleBot(token, threaded=False)

# app = Flask(__name__)

# @app.route('/'+SECRET, methods=['POST'])
# def get_message():
#     update = types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200

# @app.route('/'+SECRET)
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url=URL)
#     return 'ok', 200


    # context = context.Context(default.Default())
    # app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))