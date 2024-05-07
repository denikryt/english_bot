from deep_translator import GoogleTranslator, single_detection
from telebot import types
from state import State
from bot import BOT as bot
from database import connect#, db, sql
from users import write
from path import directory
import re
import emoji
import mongodb_database
import yaml
from windows import Window
from iso639 import languages


CONFIGFILE = 'config.yaml'

class Text(State):
    """
    Descriptions
    """

    mongo_db = mongodb_database.MongoDataBase()

    with open(directory(CONFIGFILE), 'r') as f:
        lang_detect_token = yaml.load(f, Loader=yaml.FullLoader)['config']['detect_language']

    langs = {
        'Английский' : 'en',
        'Турецкий' : 'tr' ,
        'Французский' : 'fr',
        'Итальянский' : 'it',
        'Китайский' : 'zh-tw',
    }

    
    sent_id = 0
    sent_count = 0
    text_count = 0
    output_messages = 0
    input_messages = 0
    index_word = 0
    last_message_id = 0
    messages_while_changing = 0

    text_window = 0
    trans_window = 0
    question_window = 0

    word = ''
    word_to_write = ''
    user_past = ''
    sent = ''
    translated_word = ''
    translated_sent = ''
    temp_word = ''
    lang = 'en'
    text = ''

    sents = []
    words = []
    current_ids = []
    all_texts = []
    slicer = []

    translating_text = False
    translating_sent = False
    changing_lang = False
    new_translate = False
    free_input = False
    changing_word = False
    adding_word = False
    adding_input = False
    all_text = False
    reverse = False
    wiki = False
    translated = False

    building = None



    def inline_buttons(self, message=None, call=None):
        if call.message:
            user_id = call.message.chat.id
            message_id = call.message.message_id

            if call.data == 'save_word':
                result = self.save_word(user_id)

                if result:
                    self.word_window.text = f'Слово записано!\n{self.word_window.text}'
                else:
                    self.word_window.text = f'Слово не записано!\n{self.word_window.text}'

                self.word_window.edit(user_id=user_id)

            if call.data == 'change_translate':
                self.changing_word = True
                self.word_window.text = f'Кинь свой перевод!\n{self.word_window.text}'
                self.word_window.edit(user_id=user_id)

            if call.data == 'add_translate':
                self.adding_word = True
                self.word_window.text = f'Добавь перевод!\n{self.word_window.text}'
                self.word_window.edit(user_id=user_id)

            if call.data == 'translate_text':
                self.translating_text = True
                translated_text = self.translate(self.text)
                self.visual_text = translated_text

                self.text_window.text = self.visual_text
                self.text_window.markup = self.text_window_buttons()
                self.text_window.edit(user_id=user_id)

            if call.data == 'translate_sent':
                self.translating_sent = True
                translated_sent = self.translate(self.sent)

                self.sentence_window.text = translated_sent
                self.sentence_window.markup = self.sentence_window_buttons()    
                self.sentence_window.edit(user_id=user_id)

            if call.data == 'original_text':
                self.translating_text = False
                self.visual_text = self.text

                self.text_window.text = self.visual_text
                self.text_window.markup = self.text_window_buttons()
                self.text_window.edit(user_id=user_id)
            
            if call.data == 'original_sent':
                self.translating_sent = False
                
                self.sentence_window.text = self.sent
                self.sentence_window.markup = self.sentence_window_buttons()
                self.sentence_window.edit(user_id=user_id)

            if call.data == 'next_text':
                self.translating_text = False

                if len(self.all_texts) == 1:
                    return
                
                elif len(self.all_texts) == 0:
                    bot.send_message(user_id, 'Текстов нет')
                    return

                elif self.text_count == len(self.all_texts)-1:
                    self.text_count = 0
                    self.text = self.all_texts[0]

                elif self.text_count >= 0:
                    self.text_count += 1
                    self.text = self.all_texts[self.text_count]
                    
                self.visual_text = self.text
                self.text_window.text = self.visual_text
                self.text_window.markup = self.text_window_buttons()
                self.text_window.edit(user_id=user_id)

                if self.building:
                    self.build(message, call)
                
                return

            if call.data == 'previous_text':
                self.translating_text = False

                if len(self.all_texts) == 1:
                    return
                
                elif len(self.all_texts) == 0:
                    bot.send_message(user_id, 'Текстов нет')
                    return

                elif self.text_count == 0:
                    self.text_count = len(self.all_texts)-1
                    self.text = self.all_texts[self.text_count]

                elif self.text_count <= len(self.all_texts)-1:
                    self.text_count -= 1
                    self.text = self.all_texts[self.text_count]

                self.visual_text = self.text
                self.text_window.text = self.visual_text
                self.text_window.markup = self.text_window_buttons()
                self.text_window.edit(user_id=user_id)

                if self.building:
                    self.build(message, call)

                return

            if call.data == 'previous_sent':
                self.translating_sent = False

                if self.sent_count > 0:
                    self.sent_count -= 1
                    self.build_for_sents(message, call)
                
                return

            if call.data == 'next_sent':
                self.translating_sent = False

                if self.sent_count < len(self.sents)-1:
                    self.sent_count += 1
                    self.build_for_sents(message, call)
                
                return

            if call.data =='all_text':
                self.all_text = True
                self.sentence_buttons(message, call)
                return

            if call.data == 'roll_up':
                if len(self.sents) > 1:
                    self.all_text = False
                self.sentence_buttons(message, call)
                return

            if call.data == 'build':
                self.build(message, call)

            if call.data == 'end':
                self.reverse = False
                self.input_sentences = True
                self.building = False
                self.sentence_buttons(message, call)
                bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                bot.delete_message(chat_id=chat_id, message_id=self.trans_window)

            if call.data == 'delete':
                # return
                if not self.text and not self.text_window:
                    self.text = call.message.text
                    self.text_window = call.message.message_id

                text_to_delete = self.text

                db, sql = self.data_base(message, call)

                def delete():
                    sql.execute("DELETE FROM texts WHERE text=(?)", (text_to_delete,))
                    db.commit()
                    self.all_texts.remove(text_to_delete)

                if len(self.all_texts) == 1:
                    self.text_count = 0
                    self.text = None
                    delete()
                    bot.delete_message(chat_id=chat_id, message_id=self.text_window)
                    self.hello(message, call)
                    return

                elif self.text_count == len(self.all_texts)-1:
                    self.text_count -= 1
                    self.text = self.all_texts[self.text_count]

                elif self.text_count < len(self.all_texts)-1:
                    self.text = self.all_texts[self.text_count+1]

                delete()
                self.sentence_buttons(message, call)
                return

            if call.data == 'reverse':

                if self.reverse:
                    self.reverse = False
                    self.sent = self.original
                else:
                    self.original = self.sent
                    self.reverse = True

                    def has_cyrillic(text):
                        return bool(re.search('[а-яА-Я]', text))

                    if has_cyrillic(self.text):
                        target = self.lang
                    else:
                        target = 'ru'

                    self.sent = GoogleTranslator(source='auto', target=target).translate(self.sent)

                bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                bot.delete_message(chat_id=chat_id, message_id=self.trans_window)
                self.sentence_buttons(message, call)
                self.buttons(message, call)

            if call.data == 'previus_plus':
                if not self.free_input:
                    if self.slicer[0] > 0:
                        self.slicer[0] -= 1

                        self.word_window.text = self.print_words(message, call)
                        self.word_window.edit(user_id=user_id)

            if call.data == 'next_plus':
                if not self.free_input:
                    if self.slicer[1] < len(self.words):
                        self.slicer[1] += 1

                        self.word_window.text = self.print_words(message, call)
                        self.word_window.edit(user_id=user_id)

            if call.data == 'previus_minus':
                if not self.free_input:
                    if self.slicer[0] < self.slicer[1] -1:
                        self.slicer[0] += 1

                        self.word_window.text = self.print_words(message, call)
                        self.word_window.edit(user_id=user_id)

            if call.data == 'next_minus':
                if not self.free_input:
                    if self.slicer[1] > self.slicer[0] +1:
                        self.slicer[1] -= 1

                        self.word_window.text = self.print_words(message, call)
                        self.word_window.edit(user_id=user_id)

            if call.data == 'plus':
                self.slicer +=1
                first_word = self.words.index(self.past_message)
                last_word = first_word + self.slicer +1

                if last_word >= len(self.words)+1:
                    last_word = last_word - self.slicer +1
                    self.slicer += -1
                    return

                self.word_to_write = ' '.join([x for x in self.words[first_word:last_word]])
                # print('word_to_write',self.word_to_write)

                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton(emoji.emojize(':heavy_minus_sign:', use_aliases=True), callback_data='minus')
                item2 = types.InlineKeyboardButton(emoji.emojize(':heavy_plus_sign:', use_aliases=True), callback_data='plus')
                item3 = types.InlineKeyboardButton('записать', callback_data='write')
                markup.add(item1,item2,item3)

                translated = GoogleTranslator(source=self.lang, target='ru').translate(self.word_to_write)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=self.trans_window, text='<b>'+self.word_to_write+'</b>' + '\nозначает:\n' + translated, reply_markup=markup, parse_mode='html')

            if call.data == 'minus':
                self.slicer += -1
                first_word = self.words.index(self.past_message)
                last_word = first_word + self.slicer +1

                if last_word == first_word:
                    self.slicer += 1
                    last_word = first_word + self.slicer +1
                    return

                self.word_to_write = ' '.join([x for x in self.words[first_word:last_word]])

                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton(emoji.emojize(':heavy_minus_sign:', use_aliases=True), callback_data='minus')
                item2 = types.InlineKeyboardButton(emoji.emojize(':heavy_plus_sign:', use_aliases=True), callback_data='plus')
                item3 = types.InlineKeyboardButton('записать', callback_data='write')
                markup.add(item1,item2,item3)

                translated = GoogleTranslator(source=self.lang, target='ru').translate(self.word_to_write)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=self.trans_window, text='<b>'+self.word_to_write+'</b>' + '\nозначает:\n' + translated, reply_markup=markup, parse_mode='html')

    def translate(self, text):
        translated_text = GoogleTranslator(source='auto', target='ru').translate(text)

        return translated_text

    def print_words(self, message=None, call=None):

        self.visual_words = self.words[self.slicer[0]:self.slicer[1]]
        self.visual_words = ' '.join(self.visual_words)
        self.translated_word = self.translate(self.visual_words)

        return f'{self.visual_words}\nОзначает:\n{self.translated_word}'

    def menu(self, message=None, call=None):
        pass
    
    def sent_to_words(self, sent):
        words = re.findall(r"[\w']+", sent)
        return words

    def words_buttons(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in self.words]
        markup.add(*items)

        return markup

    def save_word(self, user_id):
        self.text_id = self.text_objects_list[self.text_count]['text_id']
        print(type(self.text_id))
        form = {
            'word' : self.visual_words,
            'translation' : self.translated_word.split('*'),
            'text_id' : self.text_id,
            'sent_id' : self.sent_count
        }

        result = self.mongo_db.add_new_word(user_id=user_id, language=self.language, form=form)

        if result:
            return True
        else:
            return False

    def instructions(self, userData, message=None, call=None):
        userData = self.get_userData(message, call)
        user_text = message.text
        self.user_text = user_text

        self.last_message_id = userData['message_id']
        self.mongo_db.update_last_message_id(user_id=userData['user_id'], message_id=self.last_message_id)

        bot.delete_message(chat_id=userData['user_id'], message_id=userData['message_id'])

        if self.building:
            if user_text in self.words:
                self.free_input = False
                
                self.word_id = self.words.index(user_text)
                self.slicer = [self.word_id, self.word_id+1]
                self.word_window.text = self.print_words(message, call)
                self.word_window.edit(userData['user_id'])

            else: 
                if self.changing_word:
                    self.translated_word = user_text
                    self.word_window.text = f'{self.visual_words}\nОзначает:\n{user_text}'
                    self.word_window.edit(userData['user_id'])
                    self.changing_word = False

                elif self.adding_word:
                    self.translated_word = f'{self.translated_word}*{user_text}'
                    self.word_window.text = f'{self.visual_words}\nОзначает:\n{self.translated_word}, {user_text}'
                    self.word_window.edit(userData['user_id'])
                    self.adding_word = False
                    
                else:
                    self.free_input = True
                    self.visual_words = user_text
                    self.translated_word = self.translate(user_text)
                    self.word_window.text = f'{user_text}\nОзначает:\n{self.translated_word}'
                    self.word_window.markup = self.word_window_buttons()
                    self.word_window.edit(userData['user_id'])

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
    
    def detect_language(self, text):
        language = single_detection(text, api_key=self.lang_detect_token)
        return language
    
    def get_language_fullname(self, language_code):
        try:
            language_info = languages.get(part1=language_code)
            return language_info.name
        except KeyError:
            return 'Unknown'

    def save_text(self, user_id, textData):
        lang = single_detection(text=textData.get('text'), api_key=self.lang_detect_token)
        language = self.get_language_fullname(lang)
        result = self.mongo_db.add_new_text(user_id, language, textData)
        
        if result:
            return True, language
        else:
            return False
        
    def text_window_buttons(self):
        markup = types.InlineKeyboardMarkup(row_width=3)
        prev = types.InlineKeyboardButton(emoji.emojize(':last_track_button:', use_aliases=True), callback_data='previous_text')
        next = types.InlineKeyboardButton(emoji.emojize(':next_track_button:', use_aliases=True), callback_data='next_text')
        delete = types.InlineKeyboardButton('удалить', callback_data='delete')     

        if self.translating_text:
            trans = types.InlineKeyboardButton('оригинал', callback_data='original_text')
        else:
            trans = types.InlineKeyboardButton('перевод', callback_data='translate_text')

        if self.building:
            build = types.InlineKeyboardButton('закончить', callback_data='end') 
        else: 
            build = types.InlineKeyboardButton('разобрать', callback_data='build')

        markup.add(prev, trans, next, delete, build)

        return markup
    
    def sentence_window_buttons(self):
        markup = types.InlineKeyboardMarkup(row_width=3)
        prev = types.InlineKeyboardButton(emoji.emojize(':fast_reverse_button:', use_aliases=True), callback_data='previous_sent')
        
        if self.translating_sent:
            trans = types.InlineKeyboardButton('оригинал', callback_data='original_sent')
        else:
            trans = types.InlineKeyboardButton('перевод', callback_data='translate_sent')

        next = types.InlineKeyboardButton(emoji.emojize(':fast-forward_button:', use_aliases=True), callback_data='next_sent')

        markup.add(prev, trans, next)

        return markup

    def word_window_buttons(self):
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='previus_plus')
        item3 = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='next_plus')
        item2 = types.InlineKeyboardButton('добавить', callback_data='add_translate')
        item4 = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='previus_minus')
        item6 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='next_minus')
        item5 = types.InlineKeyboardButton('изменить', callback_data='change_translate')
        item7 = types.InlineKeyboardButton('записать', callback_data='save_word')

        markup.add(item1,item2,item3,item4,item5,item6,item7)

        return markup

    def send_text_window(self, userData, language):
        self.text_count = 0
        self.last_message_id = userData['message_id']
        self.last_message_id += 1
        self.language = language

        self.text_objects_list =  self.mongo_db.get_all_texts(user_id=userData['user_id'], language=language)
        self.all_texts = [text_object['text'] for text_object in self.text_objects_list]
        self.text = self.all_texts[0]
        self.visual_text = self.text

        self.text_window = Window(id=self.last_message_id)
        self.text_window.text = self.visual_text
        self.text_window.markup = self.text_window_buttons()
        self.text_window.send(user_id=userData['user_id'])

    def build_for_sents(self, message, call):
        userData = self.get_userData(message, call)

        self.word_id = 0
        self.slicer = [0, 1]

        self.sent = self.sents[self.sent_count]
        self.words = self.sent_to_words(self.sent)
        self.word = self.words[self.word_id]

        self.sentence_window.text = self.sent
        self.word_window.text = self.print_words(message, call)
        
        self.sentence_window.markup = self.sentence_window_buttons()
        self.choose_word_window.markup = self.words_buttons()

        self.sentence_window.edit(user_id=userData['user_id'])
        self.word_window.edit(user_id=userData['user_id'])

        self.choose_word_window.delete(user_id=userData['user_id'])
        self.choose_word_window.send(user_id=userData['user_id'])
        self.choose_word_window.id = self.last_message_id+1

        self.last_message_id = self.choose_word_window.id
        self.mongo_db.update_last_message_id(user_id=userData['user_id'], message_id=self.last_message_id)

    def build(self, message, call):
        userData = self.get_userData(message, call)

        self.sent_count = 0
        self.word_id = 0
        self.slicer = [0, 1]

        if not self.building:
            self.sentence_window = Window(id=self.last_message_id+1)
            self.word_window = Window(id=self.last_message_id+2)
            self.choose_word_window = Window(id=self.last_message_id+3)
        
        self.sents = self.text_to_sents(self.text)
        self.sent = self.sents[self.sent_count]

        self.words = self.sent_to_words(self.sent)
        self.word = self.words[self.word_id]
        
        self.sentence_window.text = self.sent
        self.word_window.text = self.print_words(message, call)
        self.choose_word_window.text = 'Выбери слово'

        self.sentence_window.markup = self.sentence_window_buttons()
        self.word_window.markup = self.word_window_buttons()
        self.choose_word_window.markup = self.words_buttons()

        if not self.building:
            self.building = True

            self.text_window.markup = self.text_window_buttons()
            self.text_window.edit(user_id=userData['user_id'])

            self.sentence_window.send(user_id=userData['user_id'])
            self.word_window.send(user_id=userData['user_id'])
            self.choose_word_window.send(user_id=userData['user_id'])
        else:
            self.sentence_window.edit(user_id=userData['user_id'])
            self.word_window.edit(user_id=userData['user_id'])

            self.choose_word_window.delete(user_id=userData['user_id'])
            self.choose_word_window.send(user_id=userData['user_id'])
            self.choose_word_window.id = self.last_message_id+1

        self.last_message_id = self.choose_word_window.id
        self.mongo_db.update_last_message_id(user_id=userData['user_id'], message_id=self.last_message_id)

    def work_with_text(self, user_id, language, text_id, message=None, call=None):
        self.text = self.mongo_db.get_text_by_text_id(user_id=user_id, text_id=text_id, language=language)
        self.last_message_id = self.mongo_db.get_last_message_id(user_id=user_id)
        self.build(message, call)
        return

    def hello(self, message=None, call=None, data=None, reason=None, last_message=None, wiki_page=None):
        pass

    def random_words(self, message):
        pass

    def text_to_sents(self, text):
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return sentences
