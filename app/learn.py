# from state import State
from collections import OrderedDict
from telebot import types, apihelper
from bot import BOT as bot
import random
from database import connect
from path import directory
import yaml
from users import write, open_yaml
# from users import LAST_MESSAGE

class Learn():
    """
    Description
    """
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
            self.guessing = True
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
            self.send_message(message, call, case='give_up')

        if call.data == 'guess':
            self.guessing = True
            user_name, user_id = self.name_id(message, call)
            message_id = self.name_id(message, call, get='message_id')

            text = call.message.text
            text = text.replace('Переведи слово\n', '')

            user_name, user_id = self.name_id(message, call)
            db, sql = self.data_base(user_name, user_id)

            sql.execute("SELECT word FROM english WHERE translate = ?",(text,))
            result = sql.fetchall()
            result = result[0][0]

            self.random_word = result
            self.translate = text

            self.start()
            bot.delete_message(user_id, message_id=message_id)
            self.send_message(call=call, case = 'send')

        if call.data == 'finish':
            self.send_message(call=call, case = 'finish')


    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message=None, call=None, case=None, user_name=None, user_id=None):
        if case != 'notify':
            user_name, user_id = self.name_id(message, call)

        db, sql = self.data_base(user_name, user_id)

        sql.execute("SELECT word FROM english")
        result = sql.fetchall()

        if not self.test:
            self.guessed = []

        self.test = True
        self.words = []

        for row in result:
            for word in row:
                self.words.append(word)

        # sql.execute("SELECT translate  FROM english")
        # result = sql.fetchall()

        # split_t = []

        # for row in result:
        #     for translate in row:
        #         split_t.append(translate)

        # sql.execute("SELECT sentence FROM english")
        # result = sql.fetchall()

        # sents = []

        # for row in result:
        #     for sentence in row:
        #         sents.append(sentence)

        # self.repeat = self.words.copy()
        # self.trans = [j for i in split_t for j in [i.split(',')]]

        # self.vocab = OrderedDict(zip(self.words, self.trans))
        # self.sents = OrderedDict(zip(self.words, sents))
        # self.temp_choise_list = self.repeat.copy()

        self.random_word = self.select_word(sql)

        sql.execute(f"SELECT translate FROM english WHERE word='{self.random_word}'")
        self.translate = sql.fetchall()[0][0]

        sql.execute(f"SELECT level FROM english WHERE word='{self.random_word}'")
        self.mark = sql.fetchall()[0][0]

        self.start()

        if case == 'notify':
            self.send_message(user_id=user_id, case='new word')
        else:
            self.send_message(message, call, case='send', user_id=user_id)


    def select_word(self, sql):
        sql.execute("SELECT level FROM english")
        r = sql.fetchall()

        l = []
        for x in r:
            for y in x:
                l.append(y)
        w = []
        w = [100-x/len(l) for x in l]
        # relalive_weight = [x/sum(w) for x in w]

        return random.choices(self.words, weights=tuple(w), k=1)[0]

        l = list(set(l))

        for x in range(1,len(l)+1):
            w = w + (x,)
        w = tuple(reversed(w))

        self.chosen_level = random.choices(l, weights=w, k=1)[0]
        # print(c)

        sql.execute(f"SELECT word FROM english WHERE level = '{self.chosen_level}'") #,(text,)")
        r = sql.fetchall()

        l = []
        for x in r:
            for y in x:
                l.append(y) 

        return random.choice(l)


#список l от меньшего к большему, не повторяющиеся элементы 

    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def buttons(self, message):
        pass

    def name_id(self, message, call, get=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
            message_id = message.message_id
        if call :
            user_name = call.from_user.first_name
            user_id = call.from_user.id
            message_id = call.message.message_id
        if get == 'message_id':
            return message_id
        return user_name, user_id

    def random_words(self, message, call):
        pass

    def start(self, message=None, call=None, user_id=None):
        # user_name, user_id = self.name_id(message, call)

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

        # self.send_message(message, call, case='send', user_id=user_id)

    def instructions(self, message=None, call=None):

        # if self.guessing == False:
        #     return

        self.last_message = message.message_id

        text = message.text.strip().lower()
        word = self.random_word.lower()
        char = self.chars[self.char]

        if char == ' ':
            self.char += 1
            char = self.chars[self.char]

        self.send_message(message, call, case='delete', message_id=self.last_message)

        if self.attempts > 0:
            if text == word:
                self.spelling = word
                self.send_message(message, call, case='fast_win')
                return

            if text == char:
                self.stars[self.char] = char
                self.spelling = ''.join(self.stars)
                self.char += 1

                if self.spelling == word:
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
                    self.send_message(message,call, case='loose')
        else:
            if self.loose:
                return
            else:
                self.help = 0 
                self.attempts = 0
                self.send_message(message, call, case='loose')
                self.loose = True

    def send_message(self, message=None, call=None, case=None, message_id=None, user_id=None):
        # if not user_id:
        #     user_name, user_id = self.name_id(message, call)

        cases = ['correct', 'incorrect', 'help'] 
        result = ['win', 'fast_win', 'loose', 'give_up'] 

        markup = types.InlineKeyboardMarkup(row_width=2)

        item1 = types.InlineKeyboardButton('Подсказка', callback_data='help')
        item2 = types.InlineKeyboardButton('Сдаюсь', callback_data='give_up')
        item3 = types.InlineKeyboardButton('Новое слово', callback_data='new')
        item4 = types.InlineKeyboardButton('Отгадать', callback_data='guess')
        item5 = types.InlineKeyboardButton('Закончить', callback_data='finish')


        if case == 'new word':
            text = f'Переведи слово\n<b>{self.translate}</b>'
            markup.add(item2,item4)
            bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
        else:
            user_name, user_id = self.name_id(message, call)
            text = f'Переведи слово\n<b>{self.translate}</b>\n{self.spelling}\nПопыток: {str(self.attempts)}\nПодсказок: {str(self.help)}'
            markup.add(item1,item2)

            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            items = [types.KeyboardButton(item) for item in self.random_word]
            random.shuffle(items)
            markup2.add(*items)

            if case == 'send':
                msg = bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
                self.game_window = msg.message_id

                msg = bot.send_message(user_id, 'Выбери букву', reply_markup=markup2, parse_mode='html')
                self.keyboard_message = msg.message_id

                self.last_message = msg.message_id
                
                return

            if case in cases:
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'delete':
                bot.delete_message(chat_id=user_id, message_id=message_id)
                return

            if case in result:
                if case == 'give_up':
                    mark = 0
                else:
                    mark = self.attempts + self.help
                self.guessed.append(self.translate +' - '+ self.random_word +' : '+ str(self.mark) +' +'+ str(mark))    

            if case == 'win':
                self.guessing = False

                text = f'Правильно!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                db, sql = self.data_base(user_name, user_id)
            
                sql.execute(f"UPDATE english SET level = {self.attempts + self.help} WHERE word = '{self.random_word}'")
                db.commit()

                bot.delete_message(user_id,message_id=self.keyboard_message)
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'fast_win':
                self.guessing = False

                text = f'СУПЕР!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                db, sql = self.data_base(user_name, user_id)
                sql.execute(f""" UPDATE english SET level='{self.attempts + self.help}' WHERE word="{self.random_word}" """)
                db.commit()

                bot.delete_message(user_id,message_id=self.keyboard_message)
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'loose' or case == 'give_up':

                text = f'Проиграл!\n<b>{self.translate}</b>\noзначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                if self.guessing:
                    self.guessing = False
                    bot.delete_message(user_id,message_id=self.keyboard_message)
                
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'finish':
                self.test = False

                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3)

                text = f'Молодец!\nТвой результат:\n'
                for x in self.guessed:
                    text += x + '\n'
                
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')


        # return
