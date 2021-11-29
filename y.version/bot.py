import yaml
from telebot import TeleBot
from path import directory

CONFIGFILE = 'config.yaml'

with open(directory(CONFIGFILE), 'r') as f:
    token = yaml.load(f, Loader=yaml.FullLoader)['config']['token']

BOT = TeleBot(token, threaded=False)
