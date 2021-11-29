# from state import State
from collections import OrderedDict
from telebot import types
from bot import BOT as bot
import random
from database import connect
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

    def data_base(user_name, user_id):
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

        if call.data == 'True':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_ID, text='Да!\n' + '<b>'+str(self.rand_choice)+'</b>' + ' :\n' + str(self.rand_tran1), parse_mode='html')
            self.repeat.remove(self.random_word)

            if len(self.temp_choise_list) == 0:
                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton('выйти в главное меню', callback_data='main_menu')
                markup.add(item1)

                bot.send_message(call.message.chat.id,'Это всё, ты молодец!')
                bot.send_message(call.message.chat.id,'Те слова, которые ты не угадал ты можешь подучить в следующий раз!')
                bot.send_message(call.message.chat.id,'Теперь ты можешь прислать мне новый текст, да присылай побольше! :)', reply_markup=markup)
                
                # folder_name = user_name + '(' + str(user_id) + ')'
                
                # with open(folder_name+'\\repeat.txt', 'w', encoding='utf-8') as r:
                #     for x in self.repeat:
                #         r.write(x+'\n')

                return
            else:
                self.random_words(message, call)

            return True

        if call.data == 'False':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_ID, text='Ne!\nПравильный ответ:\n' + str(self.rand_choice) + ' : ' + str(self.rand_tran1))

            if len(self.temp_choise_list) == 0:
                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton('выйти в главное меню', callback_data='main_menu')
                markup.add(item1)

                bot.send_message(call.message.chat.id,'Это всё, ты молодец!')
                bot.send_message(call.message.chat.id,'Те слова, которые ты не угадал ты можешь подучить в следующий раз!')
                bot.send_message(call.message.chat.id,'Теперь ты можешь прислать мне новый текст, да присылай побольше! :)', reply_markup=markup)
                

                # folder_name = user_name + '(' + str(user_id) + ')'
                
                # with open(folder_name+'\\repeat.txt', 'w', encoding='utf-8') as r:
                #     for x in self.repeat:
                #         r.write(x+'\n')
                return
            else:
                self.random_words(message, call)
                
        if call.data == 'repeat':
            self.temp_choise_list, self.repeat = self.words.copy(), self.words.copy()
            self.random_words(message, call)

    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, user_name, user_id) -> None:

        # if not message == None:
        #     user_name = message.from_user.first_name
        #     user_id = message.chat.id
        # if not call == None:
        #     user_name = call.from_user.first_name
        #     user_id = call.from_user.id


        # words = []
        # translate = []
        # sentence = []

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
        # folder_name = user_name + '(' + str(user_id) + ')'

        # w = open(folder_name+'\\words.txt', 'r', encoding='utf-8') #, encoding='utf-8'
        # t = open(folder_name+'\\trans.txt', 'r')
        # s = open(folder_name+'\\sents.txt', 'r', encoding='utf-8')
        # r = open(folder_name+'\\repeat.txt', 'r', encoding='utf-8')
        
        # self.words = w.read().splitlines()
        # self.repeat = r.read().splitlines()

        # split_t = t.read().splitlines()
        # self.trans = [j for i in split_t for j in [i.split(';')]]

        # split_s = s.read().splitlines()
        # sents = [o for p in split_s for o in [p.split(';')]]

        # w.close()
        # t.close()
        # s.close()
        # r.close()
                   
        self.vocab = OrderedDict(zip(self.words, self.trans))
        self.sents = OrderedDict(zip(self.words, sents))
        self.temp_choise_list = self.repeat.copy()
        self.random_words(self, user_name, user_id)

    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def buttons(self, message):
        pass

    def random_words(self, user_name, user_ID):

        # if not message == None:
        #     user_ID = message.chat.id
        #     message_ID = message.message_id
        # if not call == None:
        #     user_ID = call.from_user.id
        #     message_ID = call.message.message_id

        if len(self.temp_choise_list) == 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton('Повторить по новой', callback_data='repeat')
            markup.add(item1)
            bot.send_message(user_ID,'Слов для повтора нету!\n', reply_markup=markup)
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
        bot.send_message(user_ID, 'Переведи слово:\n' + str(self.rand_choice), reply_markup=markup)


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

    def instructions(self, message) -> None:
        user = message.text
        def test():

            # if user.rstrip() == 'q':
            #     user_name = message.from_user.first_name
            #     user_id = message.chat.id
            #     folder_name = user_name + '(' + str(user_id) + ')'
                
            #     with open(folder_name+'\\repeat.txt', 'w', encoding='utf-8') as r:
            #         for x in self.repeat:
            #             r.write(x+'\n')
            #     return 'back'
                
            try:
                if user == self.rand_tran1:
                    bot.send_message(message.chat.id,'Да!')
                    self.repeat.remove(self.random_word)
                    return True

                else:
                    bot.send_message(message.chat.id,'Ne!')
                    bot.send_message(message.chat.id,'Правильный ответ: ' + str(self.rand_tran1))
                    return True

            except ValueError:
                print('Цифру!')
                return False
                
        if test() == True:
            if len(self.temp_choise_list) == 0:
                bot.send_message(message.chat.id,'Всё!')

                user_name = message.from_user.first_name
                user_id = message.chat.id
                folder_name = user_name + '(' + str(user_id) + ')'
                
                # with open(folder_name+'\\repeat.txt', 'w', encoding='utf-8') as r:
                #     for x in self.repeat:
                #         r.write(x+'\n')
                return
            else:
                self.random_words(message)
        else:
            return