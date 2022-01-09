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

    def data_base(self, user_name, user_id):
        # if message:
        #     user_name = message.from_user.first_name
        #     user_id = message.chat.id
        # if call:
        #     user_name = call.from_user.first_name
        #     user_id = call.from_user.id

        folder_name = user_name + '(' + str(user_id) + ')'
        db, sql = connect(folder_name)
        return db, sql
        # return super().data_base(message, call)

    def inline_buttons(self, message=None, call=None):
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        message_ID = call.message.message_id

        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('дальше', callback_data='next')
        markup.add(item1)

        if call.data == 'new':
            self.send_message(message, call, case='delete', message_id=self.game_window)
            self.start(message, call)

        if call.data == 'prompt':
            if self.prompt > 0:
                self.prompt -= 1
                self.spelling += self.chars[self.char]
                self.char += 1

                self.send_message(message, call, case='prompt')
            else:
                return
            # return

        if call.data == 'give_up':
            self.send_message(message, call, case='loose')


    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message, call) -> None:
        user_name, user_id = self.name_id(message, call)

        db, sql = self.data_base(user_name, user_id)

        sql.execute("SELECT word FROM english")
        result = sql.fetchall()

        for row in result:
            for word in row:
                self.words.append(word)

        sql.execute("SELECT translate  FROM english")
        result = sql.fetchall()

        split_t = []

        for row in result:
            for translate in row:
                split_t.append(translate)

        sql.execute("SELECT sentence FROM english")
        result = sql.fetchall()

        sents = []

        for row in result:
            for sentence in row:
                sents.append(sentence)

        self.repeat = self.words.copy()
        self.trans = [j for i in split_t for j in [i.split(',')]]

        self.vocab = OrderedDict(zip(self.words, self.trans))
        self.sents = OrderedDict(zip(self.words, sents))
        self.temp_choise_list = self.repeat.copy()
        self.start(message, call)

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

        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
        if call :
            user_name = call.from_user.first_name
            user_id = call.from_user.id

        if len(self.temp_choise_list) == 0:
            # markup = types.InlineKeyboardMarkup(row_width=2)
            # item1 = types.InlineKeyboardButton('Повторить по новой', callback_data='repeat')
            # markup.add(item1)
            # bot.send_message(user_id,'Слов для повтора нету!\n', reply_markup=markup)
            return
        else:
            self.random_word = random.choice(self.temp_choise_list)

        which_rand = [self.random_word, self.vocab[self.random_word]]
        self.rand_choice = random.choice(which_rand)
        list_for_answers = self.words.copy()

        if type(self.rand_choice) == str:
            self.temp_choise_list.remove(self.random_word)
            list_for_answers.remove(self.random_word)

            r_trans = random.sample(list_for_answers, 2)
            self.rand_tran1 = random.choice(self.vocab[self.random_word])
            rand_tran2 = random.choice(self.vocab[r_trans[0]])
            rand_tran3 = random.choice(self.vocab[r_trans[1]])
            # rand_tran4 = random.choice(self.vocab[r_trans[2]])
            # rand_tran5 = random.choice(self.vocab[r_trans[3]])
            # rand_tran6 = random.choice(self.vocab[r_trans[4]])

        if type(self.rand_choice) == list:
            self.temp_choise_list.remove(self.random_word)
            list_for_answers.remove(self.random_word)

            r_trans = random.sample(list_for_answers, 2)
            self.rand_tran1 = self.random_word
            rand_tran2 = r_trans[0]
            rand_tran3 = r_trans[1]
            # rand_tran4 = r_trans[2]
            # rand_tran5 = r_trans[3]
            # rand_tran6 = r_trans[4]


        item1 = types.InlineKeyboardButton(self.rand_tran1, callback_data='True')
        item2 = types.InlineKeyboardButton(rand_tran2, callback_data='False')
        item3 = types.InlineKeyboardButton(rand_tran3, callback_data='False')
        # item4 = types.InlineKeyboardButton(rand_tran4, callback_data='False')
        # item5 = types.InlineKeyboardButton(rand_tran5, callback_data='False')
        # item6 = types.InlineKeyboardButton(rand_tran6, callback_data='False')

        self.rand_answers = [item1, item2, item3]#, item4, item5]
        random.shuffle(self.rand_answers)

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*self.rand_answers)

        file_name = 'users.yaml'

        # with open(directory(file_name), 'r', encoding='utf-8') as f:
        #     try:
        #         result = yaml.load(f, Loader=yaml.FullLoader)['users'][user_name]
        #     except TypeError:
        #         pass

        try:
            last_notify = open_yaml()['users'][user_name]['last notify']
            bot.delete_message(user_id, message_id=last_notify)
        except KeyError:
            pass
        except apihelper.ApiTelegramException:
            print('НЕ УДАЛИЛОСЬ!')


        bot.send_message(user_id, 'Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)
        # write(user_name, user_id, target='last message')
        write(user_name, user_id, target='last notify')


        # if not message == None:
        #     self.test_window = message_ID+1
        #     self.result_window = message_ID+2
        #     bot.send_message(user_ID, 'Выбери вариант')
        #     bot.send_message(user_ID, 'Выбери вариант')

        # if not call == None:
        #     if call.data == 'learn': # or call.data == 'repeat'
        #         self.test_window = message_ID+1
        #         self.result_window = message_ID+2
        #         bot.send_message(user_ID, 'Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)
        #         bot.send_message(user_ID, 'Выбери вариант')

        #     elif call.data == 'repeat':
        #         bot.edit_message_text(chat_id=user_ID, message_id=message_ID, text='Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)
        #         bot.send_message(user_ID, 'Выбери вариант')

        #     else:
        #         bot.edit_message_text(chat_id=user_ID, message_id=message_ID+1, text='Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)
        #         bot.send_message(user_ID, 'Выбери вариант')
        #         # bot.send_message(user_ID, 'Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)
        #         # bot.send_message(user_ID, 'Выбери вариант')

    def start(self, message, call):
        user_name, user_id = self.name_id(message, call)
        if not call:
            self.last_message = message.message_id

        self.random_word = random.choice(self.temp_choise_list)
        self.translate = ','.join(self.vocab[self.random_word])

        self.loose = False
        self.attempts = 3
        self.prompt = 3
        self.spelling = ''
        self.chars = []
        self.chars = [char.lower() for char in self.random_word]
        self.char = 0

        self.send_message(message, call, case='send')

    def instructions(self, message=None, call=None):
        self.last_message = message.message_id

        text = message.text.strip().lower()
        word = self.random_word.lower()
        char = self.chars[self.char]

        self.send_message(message, call, case='delete', message_id=self.last_message)

        if self.attempts > 0:
            if text == word:
                self.spelling = word
                self.send_message(message, call, case='fast_win')
                return

            if text == char:
                self.spelling += char
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
                    self.send_message(message,call, case='loose')
        else:
            if self.loose:
                return
            else:
                self.send_message(message, call, case='loose')
                self.loose = True

    def send_message(self, message=None, call=None, case=None, message_id=None):
        user_name, user_id = self.name_id(message, call)
        cases = ['correct', 'incorrect', 'prompt']

        text = f'Переведи слово\n<b>{self.translate}</b>\n{self.spelling}\nПопыток: {str(self.attempts)}\nПодсказок: {str(self.prompt)}'

        markup = types.InlineKeyboardMarkup(row_width=2)

        item1 = types.InlineKeyboardButton('Подсказка', callback_data='prompt')
        item2 = types.InlineKeyboardButton('Сдаюсь', callback_data='give_up')
        item3 = types.InlineKeyboardButton('Новое слово', callback_data='new')

        markup.add(item1,item2)

        if case == 'send':
            bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
            self.last_message += 1
            self.game_window = self.last_message

        if case in cases:
            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'delete':
            bot.delete_message(chat_id=user_id, message_id=message_id)

        if case == 'win':
            text = f'Правильно!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3)

            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'fast_win':
            text = f'СУПЕР!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3)

            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        if case == 'loose':
            text = f'Проиграл!\n<b>{self.translate}</b>\noзначает\n<b>{self.random_word}</b>'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(item3)

            bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

        return
