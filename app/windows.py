from telebot import types
from bot import BOT as bot

class Window():
    def __init__(self, id, text=None, markup=None):
        self.id = id
        self.text = text
        self.markup = markup

    def send(self, user_id):
        msg = bot.send_message(user_id, self.text, reply_markup=self.markup)
        self.id = msg.message_id

    def edit(self, user_id):
        bot.edit_message_text(chat_id=user_id, text=self.text, message_id=self.id, reply_markup=self.markup)

    def delete(self, user_id):
        bot.delete_message(chat_id=user_id, message_id=self.id)