from deep_translator import GoogleTranslator
from telebot import types
from state import State
from main import bot
from text import Text
import re

class LoadText(State):
    """
    Description
    """
    
    count = 0
    # user_plus = ''
    # user_past = ''
    sents = []
    lang = 'en'
    text = ''
    new_text = False
    # sent = ''
    # words = []

    def inline_buttons(self, message=None, call=None):
        if call.data == 'foreign_ru':
            self.lang = 'ru'
        if call.data == 'foreign_en':
            self.lang = 'en'
        if call.data == 'foreign_fr':
            self.lang = 'fr'

        with open('default_text.txt', 'r',encoding='utf-8') as text:
            text = text.read()
            translated = GoogleTranslator(source='fr', target=self.lang).translate(text)
            call.message.text = translated
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        self.text_to_sents(None, call)

    def hello(self, message=None, call=None) -> None:
        if call:
            user_id = call.from_user.id
            if call.data == 'new':
                self.new_text = True
        if message:
            user_id = message.chat.id
        bot.send_message(user_id, 'Пришли мне текст!')
        # if message.text == 'давай':

        #     # markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
        #     # items = ['русский','english','francais']

        #     # items = [types.KeyboardButton(item) for item in self.words]
        #     # markup.add(*items)

        #     markup = types.InlineKeyboardMarkup(row_width=2)
        #     # item1 = types.InlineKeyboardButton('русский', callback_data='foreig_-ru')
        #     item2 = types.InlineKeyboardButton('english', callback_data='foreign_en')
        #     item3 = types.InlineKeyboardButton('francais', callback_data='foreign_fr')
        #     items = [item2, item3]
        #     markup.add(*items)


        #     say = "Скажи, какой язык ты учишь?"
        #     bot.send_message(message.chat.id, say, reply_markup=markup)

        # else:
        #     self.count = 0
        
            # bot.send_message(call.from_user.id, 'Пришли мне текст на любом языке')
        
    def text_to_sents(self, message=None, call=None):

        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"

        def split_into_sentences(text):
        
            text = " " + text + "  "
            text = text.replace('-\n', '')
            text = text.replace("\n"," ") 
            text = re.sub(prefixes,"\\1<prd>",text)
            text = re.sub(websites,"<prd>\\1",text)
            if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
            text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
            text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
            text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
            text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
            text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
            text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
            text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
            if "”" in text: text = text.replace(".”","”.")
            if "\"" in text: text = text.replace(".\"","\".")
            if "!" in text: text = text.replace("!\"","\"!")
            if "?" in text: text = text.replace("?\"","\"?")
            text = text.replace(".",".<stop>")
            text = text.replace("?","?<stop>")
            text = text.replace("!","!<stop>")
            text = text.replace("<prd>",".")
            sentences = text.split("<stop>")
            sentences = sentences[:-1]
            sentences = [s.strip() for s in sentences]
            # print(sentences)
            return sentences
        
        # if type(call) == str:
        #     self.sents = split_into_sentences(call)
        #     self.context.transition_to(Text())
        #     self.context.vars(message, call, self.sents, self.count, self.lang)
        #     return

        # if call:
        #     text = call.message.text
        #     # self.sents = split_into_sentences(call.message.text)
        # if message:
        #     text = message.text
        # if not message == None:
        if call.data == 'build':
            self.text = call.message.text 
        sents = split_into_sentences(self.text)

        return sents
        # self.context.transition_to(Text())

        if self.new_text:
            message.text = 'new_text'
            self.new_text = False
            self.context.sents_to_words(message, call, sents)
            return

        # self.context.sents_to_words(message, call, sents)

    def sents_to_words(self, message=None, call=None, sents=None):
        # print(call.message.text)
        if not message == None:
            user_name = message.from_user.first_name
            user_id = message.chat.id
        if not call == None:
            user_name = call.from_user.first_name
            user_id = call.from_user.id
            user_text = call.message

        folder_name = user_name + '(' + str(user_id) + ')'

        with open(folder_name+'\\text.txt', 'r') as t:
            # call.message.text = t.read()
            self.text = t.read()
            # print('!!!!!!!!!!', self.text)
        # print(type(message.text), message.text)


        with open(folder_name+'\\count.txt', 'r') as c:
            count = c.readlines()
            self.count = int(count[0])

        print('COUNT', self.count)

        self.text_to_sents(message, call)

    def instructions(self, message) -> None:
        # if message.text == 'русский':
        #     with open('default_text.txt', 'r',encoding='utf-8') as text:
        #         text = text.read()
        #     self.lang = 'ru'
        #     self.text_to_sents(message, text)

        # if message.text == 'english':
        #     with open('default_text.txt', 'r',encoding='utf-8') as text:
        #         text = text.read()
        #     self.lang = 'en'
        #     self.text_to_sents(message, text)

        # if message.text == 'francais':
        #     with open('default_text.txt', 'r',encoding='utf-8') as text:
        #         text = text.read()
        #     self.lang = 'fr'
        #     self.text_to_sents(message, text)

        # else:
        user_name = message.from_user.first_name
        chat_id = message.chat.id
        self.text = message.text

        folder_name = user_name + '(' + str(chat_id) + ')'

        with open(folder_name+'\\text.txt', 'w',encoding='utf-8') as text:
            text.write(self.text)

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
        
        self.text_to_sents(message,None)


    def buttons(self, message):
        pass

    def write_word(self, message):
        pass
    
    def vars(self, message, sents, count):
        pass

    def random_words(self, message):
        pass

    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass