from telebot import TeleBot, types
import yaml
from flask import Flask, request
import os

token = '1452119723:AAGpVlSMu9uVKesX-i1gXtOas2RxxJd5WkI'
secret = 'ifposldnnf333'
url = 'https://kentus.pythonanywhere.com/' + secret


bot = TeleBot(token, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)

app = Flask(__name__)
@app.route('/'+secret, methods=['POST'])
def webhook():
    update = types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 'hello')

if __name__ == '__webhook_bot__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

