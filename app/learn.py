# from state import State
from collections import OrderedDict
from telebot import types, apihelper
from bot import BOT as bot
import random
from database import connect
from path import directory
import yaml
from users import write, open_yaml
import mongodb_database
from windows import Window


class Learn():
    """
    Description
    """

    mongo_db = mongodb_database.MongoDataBase()

    vocab = {}
    sents = {}

    temp_choise_list = []
    words = []
    trans = []
    repeat = []
    rand_answers = []

    rand_tran1 = ''
    rand_choice = ''
    random_word = ''

    test_window = 0
    result_window = 0

    guessing = False
    test = False

    def data_base(self, user_name, user_id):

        folder_name = user_name + '(' + str(user_id) + ')'
        db, sql = connect(folder_name)
        return db, sql

    def inline_buttons(self, message=None, call=None):

        self.game_window = call.message.message_id

        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('дальше', callback_data='next')
        markup.add(item1)

        if call.data == 'new':
            user_id = call.from_user.id
            message_id = call.message.message_id
            bot.delete_message(user_id, message_id=message_id)
            # bot.delete_message(user_id, message_id=self.keyboard_message)
            self.hello(message, call)
            return

        if call.data == 'help':
            if self.chars[self.char] == ' ':
                self.char += 1

            if self.help > 0:
                self.help -= 1

                self.stars[self.char] = self.chars[self.char]
                self.spelling = ''.join(self.stars)

                if self.spelling == self.random_word.lower():
                    self.send_message(message, call, case='loose')
                    return

                self.char += 1

                self.send_message(message, call, case='help')
            else:
                return

        if call.data == 'give_up':
            self.testing = False
            self.send_message(message, call, case='give_up')

        if call.data == 'guess':
            # self.guessing = True
            user_name, user_id = self.name_id(message, call)
            bot.send_message(user_id, 'cHO?')
            # message_id = self.name_id(message, call, get='message_id')

            # text = call.message.text
            # text = text.replace('Переведи слово\n', '')

            # user_name, user_id = self.name_id(message, call)
            # db, sql = self.data_base(user_name, user_id)

            # sql.execute("SELECT word FROM english WHERE translate = ?",(text,))
            # result = sql.fetchall()
            # result = result[0][0]

            # self.random_word = result
            # self.translate = text

            # self.start()
            # bot.delete_message(user_id, message_id=message_id)
            # self.send_message(call=call, case = 'send')

        if call.data == 'finish':
            self.test = False
            self.testing = False
            self.send_message(call=call, case = 'finish')


    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def reset(self):
        self.test = False
        self.testing = False
        self.guessed = []

    def get_userData(self, message=None, call=None):
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

    def hello(self, message=None, call=None):

        userData = self.get_userData(message, call)

        random_word_object = self.select_word(user_id=userData['user_id'])

        self.translate = random_word_object.get("translate")
        self.random_word = random_word_object.get("word")
        self.reset_attributes()

        self.send_message(message, call, case='new word')



    def select_word(self, user_id):

        word_objects = self.mongo_db.get_all_word_objects(user_id=user_id,language='English')

        words = [word_obj.get("word") for word_obj in word_objects]
        marks = [word_obj.get("mark") for word_obj in word_objects]

        #список весов для каждого слова, чем больше оценка, тем меньше вес
        w = [1/mark for mark in marks]

        word = random.choices(words, weights=tuple(w), k=1)[0]

        return word_objects[words.index(word)]
    


    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def buttons(self, message):
        pass

    def name_id(self, message, call, get=None):
        pass

    def random_words(self, message, call):
        pass

    def reset_attributes(self):
    
        self.loose = False
        self.attempts = 3
        self.help = 3
        self.char = 0
        self.spelling = ''
        self.chars = []
        self.chars = [char.lower() for char in self.random_word]
        self.stars = []
        self.stars = ['*' if not x == ' ' else ' ' for x in self.random_word]

        self.spelling = ''.join(self.stars)


    def instructions(self, message=None, call=None):

        self.last_message = message.message_id

        if not self.testing:
            return

        # if self.loose:
        #     return

        text = message.text.strip().lower()
        word = self.random_word.lower()
        char = self.chars[self.char]

        if char == ' ':
            self.char += 1
            char = self.chars[self.char]

        # if self.attempts > 0:
        if text == word:
            self.spelling = word
            self.testing = False
            self.send_message(message, call, case='fast_win')
            return

        if text == char:
            self.stars[self.char] = char
            self.spelling = ''.join(self.stars)
            self.char += 1

            if self.spelling == word:
                self.testing = False
                self.send_message(message, call, case='win')
            else:
                self.send_message(message, call, case='correct')
            return

        if not text == char:
            self.attempts -= 1
            if self.attempts > 0:
                self.send_message(message,call,case='incorrect')
            else:
                self.help = 0 
                # self.loose = True
                self.testing = False
                self.send_message(message,call, case='loose')
            return
        # else:
        #     self.help = 0 
        #     self.attempts = 0
        #     self.loose = True
        #     self.testing = False
        #     self.send_message(message, call, case='loose')
                

    def set_inlineKeyboard_markup(self, case=None):

        markup = types.InlineKeyboardMarkup(row_width=2)

        item1 = types.InlineKeyboardButton('Подсказка', callback_data='help')
        item2 = types.InlineKeyboardButton('Сдаюсь', callback_data='give_up')
        item3 = types.InlineKeyboardButton('Новое слово', callback_data='new')
        item4 = types.InlineKeyboardButton('Закончить', callback_data='finish')

        if case == 'new word':
            markup.add(item1, item2, item3)

        return markup

    def set_replyKeyboard_markup(self):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in self.random_word]
        random.shuffle(items)
        markup.add(*items)

        return markup
    
    def send_message(self, user_id, case=None):

        cases = ['correct', 'incorrect', 'help'] 
        result = ['win', 'fast_win', 'loose', 'give_up'] 

        if case in cases:
            self.game_window.text = f'Переведи слово\n<b>{self.translate}</b>\n{self.spelling}\nПопыток: {str(self.attempts)}\nПодсказок: {str(self.help)}'
            self.game_window.edit(user_id)

        if case == 'new word':

            self.game_window = Window(id=0)
            self.keyboard_window = Window(id=0)

            self.game_window.text = f'Переведи слово\n<b>{self.translate}</b>\n{self.spelling}\nПопыток: {str(self.attempts)}\nПодсказок: {str(self.help)}'
            self.keyboard_window.text = 'Выбери букву'

            self.game_window.markup = self.set_inlineKeyboard_markup(case)
            self.keyboard_window.markup = self.set_replyKeyboard_markup()
            
        if case in result:
            if case == 'give_up':
                mark = 0
            else:
                mark = self.attempts + self.help
            self.guessed.append(f"{self.translate} - {self.random_word} : {str(self.mark)} +{str(mark)}")    

        if case == 'win':

            text = f'Правильно!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3, item5)

            db, sql = self.data_base(user_name, user_id)

            new_level = self.mark+ self.attempts + self.help
            sql.execute(f"UPDATE english SET level = {new_level} WHERE word = '{self.random_word}'")
            db.commit()

            bot.delete_message(user_id,message_id=self.keyboard_message)
            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'fast_win':

            text = f'СУПЕР!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3, item5)

            db, sql = self.data_base(user_name, user_id)

            new_level = self.mark+ self.attempts + self.help
            sql.execute(f"UPDATE english SET level = {new_level} WHERE word = '{self.random_word}'")
            db.commit()

            bot.delete_message(user_id,message_id=self.keyboard_message)
            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'loose' or case == 'give_up':

            text = f'Проиграл!\n<b>{self.translate}</b>\noзначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3, item5)

            # if self.guessing:
            #     self.guessing = False
            bot.delete_message(user_id,message_id=self.keyboard_message)
            
            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'finish':

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3)

            text = f'Молодец!\nТвой результат:\n'
            for x in self.guessed:
                text += x + '\n'
            
            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')