import yaml
from telebot import TeleBot
from path import CURR_DIR

CONFIGFILE = 'config.yaml'

with open(CURR_DIR+'\\'+CONFIGFILE, 'r') as f:
    token = yaml.load(f, Loader=yaml.FullLoader)['config']['token']

BOT = TeleBot(token, threaded=False)
