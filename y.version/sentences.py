import re
from state import State
from main import bot, sql, db
from telebot import types
# from text import Text
from deep_translator import GoogleTranslator

class Sentences(State):
    """
    Description
    """
    window = None
    text = None

    def inline_buttons(self, message=None, call=None):
        user_id = call.message.chat.id
        message_id = call.message.message_id
        message_text = call.message.text

        # print('TYPE', type(self.text))

        if call.data == 'delete':

            sql.execute("SELECT id FROM texts WHERE text=(?)", (call.message.text,))
            sent_id = sql.fetchone()[0]

            l = [x for x in sql.execute(f"SELECT text FROM texts WHERE id<{sent_id}")]
            try:
                self.text = l[-1][0]
            except IndexError:
                try:
                    l = [x for x in sql.execute(f"SELECT text FROM texts WHERE id>{sent_id}")]
                    self.text = l[0][0]
                except IndexError:
                    sql.execute("DELETE FROM texts WHERE text=(?)", (call.message.text,))
                    db.commit()
                    bot.edit_message_text(text='Предложения закончились!', chat_id=user_id, message_id=self.window)
                    return

            sql.execute("DELETE FROM texts WHERE text=(?)", (call.message.text,))
            db.commit()

            self.printing(user_id)

        if call.data == 'previous':

            sql.execute("SELECT id FROM texts WHERE text=(?)", (self.text,))
            sent_id = sql.fetchone()[0]

            l = [x for x in sql.execute(f"SELECT text FROM texts WHERE id<{sent_id}")]
            try:
                self.text = l[-1][0]
            except IndexError:
                sql.execute(f"SELECT text FROM texts")
                self.text = sql.fetchall()[-1][0]

            self.printing(user_id)
            return

        if call.data == 'next':
            sql.execute("SELECT id FROM texts WHERE text=(?)", (self.text,))
            sent_id = sql.fetchone()[0]

            l = [x for x in sql.execute(f"SELECT text FROM texts WHERE id>{sent_id}")]
            try:
                self.text = l[0][0]
            except IndexError:
                sql.execute(f"SELECT text FROM texts")
                self.text = sql.fetchall()[0][0]

            self.printing(user_id)
            return

        if call.data == 'build':
            pass
            # return 'hello'
            # if self.translated:
            #     call.data = 'original'
            # bot.edit_message_text(chat_id=user_id, message_id=message_id, text=self.text, reply_markup=markup)
            # self.context.transition_to(LoadText())
            # self.text_to_sents(message, call)

        if call.data == 'translate':
            # self.translated = True
            translated_sent = GoogleTranslator(source='auto', target='ru').translate(self.text)
            markup = types.InlineKeyboardMarkup(row_width=3)
            item1 = types.InlineKeyboardButton('предыдущее', callback_data='previous')
            item2 = types.InlineKeyboardButton('оригинал', callback_data='original')
            item3 = types.InlineKeyboardButton('следующее', callback_data='next')
            item4 = types.InlineKeyboardButton('разобрать', callback_data='build')
            item5 = types.InlineKeyboardButton('удалить', callback_data='delete')
            markup.add(item1, item2, item3, item4, item5)
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=translated_sent, reply_markup=markup)
        
        if call.data == 'original':
            # if self.translated:
            #     call.data = 'build'
            #     self.translated = False
            markup = types.InlineKeyboardMarkup(row_width=3)
            item1 = types.InlineKeyboardButton('предыдущее', callback_data='previous')
            item2 = types.InlineKeyboardButton('перевести', callback_data='translate')
            item3 = types.InlineKeyboardButton('следующее', callback_data='next')
            item4 = types.InlineKeyboardButton('разобрать', callback_data='build')
            item5 = types.InlineKeyboardButton('удалить', callback_data='delete')
            markup.add(item1, item2, item3, item4, item5)
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=self.text, reply_markup=markup)
            
    def printing(self, chat_id=None):
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton('предыдущее', callback_data='previous')
        item2 = types.InlineKeyboardButton('перевести', callback_data='translate')
        item3 = types.InlineKeyboardButton('следующее', callback_data='next')
        item4 = types.InlineKeyboardButton('разобрать', callback_data='build')
        item5 = types.InlineKeyboardButton('удалить', callback_data='delete')
        markup.add(item1, item2, item3, item4, item5)

        bot.edit_message_text(text=self.text, chat_id=chat_id, message_id=self.window,reply_markup=markup)
        
    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message=None, call=None) -> None:
        user_id = message.chat.id
        message_id = message.message_id
        self.window = message_id+1
        print('WINDOW', self.window)
        bot.send_message(user_id, 'Получаю сообщения!')

    def text_to_sents(self, message=None, call=None):
        pass

    def sents_to_words(self, message=None, call=None, sents=None):
        pass

    def buttons(self, call):
        pass

    def write_word(self, message):
        pass

    def random_words(self):
        pass
         
    def instructions(self, message) -> None:
        
        user_id = message.chat.id
        self.text = message.text
        message_id = message.message_id
        sql.execute("INSERT INTO texts VALUES (?, ?)", (message_id, self.text,))
        db.commit()
        bot.delete_message(chat_id=user_id, message_id=message_id)

        self.printing(user_id)
        return

        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('предыдущее', callback_data='previous')
        item2 = types.InlineKeyboardButton('следующее', callback_data='next')
        item3 = types.InlineKeyboardButton('разобрать', callback_data='build')
        item4 = types.InlineKeyboardButton('удалить', callback_data='delete')
        markup.add(item1, item2, item3, item4)

        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.edit_message_text(text=self.text, chat_id=user_id, message_id=self.window,reply_markup=markup)
        # bot.edit_message_reply_markup(chat_id=user_id,message_id=message_id,reply_markup=markup)

        # bot.copy_message(chat_id=user_id,message_id=message_id,reply_markup=markup)