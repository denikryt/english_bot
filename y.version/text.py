from deep_translator import GoogleTranslator
from telebot import types
from state import State
from bot import BOT as bot
from database import connect#, db, sql
from users import write
# from main import LAST_MESSAGES
# from gtts import gTTS
import re
import emoji

class Text(State):
    """
    Description
    """

    langs = {
        'Английский' : 'en',
        'Турецкий' : 'tr' ,
        'Французский' : 'fr',
        'Итальянский' : 'it',
        'Китайский' : 'zh-tw',
    }

    slicer = 0
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

    changing_lang = False
    new_translate = False
    free_input = False
    changing = False
    adding = False
    adding_input = False
    all_text = False
    reverse = False
    wiki = False

    building = None

    def language(self, message=None, call=None):
        user_id = message.chat.id
        user_name = message.from_user.first_name
        message_id = message.message_id
        self.changing_lang = True
        self.messages_while_changing += 2

        items = ['Английский', 'Турецкий', 'Французский', 'Итальянский', 'Китайский']

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in items]
        markup.add(*items)

        bot.send_message(user_id, 'C каким языком будешь работать?', reply_markup=markup)
        write(user_name, user_id, message_id=message_id+1, target='last message')


    def reset(self):
        self.changing_lang = False
        self.messages_while_changing = 0
        self.slicer = 0
        self.sent_id = 0
        self.sent_count = 0
        self.text_count = 0
        self.output_messages = 0
        self.input_messages = 0
        self.index_word = 0
        self.last_message_id = 0

        self.text_window = 0
        self.trans_window = 0
        self.question_window = 0

        self.word = ''
        self.word_to_write = ''
        self.user_past = ''
        self.sent = ''
        self.translated_word = ''
        self.temp_word = ''
        self.lang = 'en'
        self.text = ''

        self.sents = []
        self.words = []
        self.current_ids = []
        self.all_texts = []

        self.new_translate = False
        self.free_input = False
        self.changing = False
        self.adding = False
        self.adding_input = False
        self.all_text = False
        self.reverse = False
        self.wiki = False

        self.building = None

    def data_base(self, message=None, call=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
        if call:
            user_name = call.from_user.first_name
            user_id = call.from_user.id

        folder_name = user_name + '(' + str(user_id) + ')'
        db, sql = connect(folder_name)
        return db, sql

    def inline_buttons(self, message=None, call=None):
        if call.message:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            if call.data == 'write':
                self.write_word(message, call)

            if call.data == 'change':
                self.changing = True
                self.adding_input = True
                # self.translated_word = 'Кинь свой перевод!'
                self.menu(message, call)

            if call.data == 'adding':
                self.adding = True
                self.adding_input = True
                # self.translated_word = 'Добавь перевод!'
                self.menu(message, call)


            if call.data == 'translate':
                self.sentence_buttons(message, call)
                return

            if call.data == 'original':
                self.sentence_buttons(message, call)
                return


            if call.data == 'next':
                user_name, user_id, message_id = self.vars(message,call)
                db, sql = self.data_base(message, call)

                self.reverse = False

                if len(self.all_texts) == 1:
                    return

                elif self.text_count == len(self.all_texts)-1:
                    self.text_count = 0
                    next_text = self.all_texts[self.text_count]
                    self.text = next_text

                elif self.text_count >= 0:
                    self.text_count += 1
                    next_text = self.all_texts[self.text_count]
                    self.text = next_text

                if self.wiki:
                    sql.execute(f"UPDATE wiki SET sentence='{self.text_count}' WHERE title='{self.wiki_page}'")
                    db.commit()

                if self.building:
                    self.sent_count = 0
                    bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                    bot.delete_message(chat_id=chat_id, message_id=self.trans_window)
                    self.text_to_sents(message, call)

                self.sentence_buttons(message, call)
                return

            if call.data == 'previous':
                user_name, user_id, message_id = self.vars(message,call)
                db, sql = self.data_base(message, call)

                self.reverse = False

                if len(self.all_texts) == 1:
                    return

                elif self.text_count == 0:
                    self.text_count = len(self.all_texts)-1
                    previus_text = self.all_texts[self.text_count]
                    self.text = previus_text

                elif self.text_count <= len(self.all_texts)-1:
                    self.text_count -= 1
                    previus_text = self.all_texts[self.text_count]
                    self.text = previus_text

                if self.wiki:
                    sql.execute(f"UPDATE wiki SET sentence='{self.text_count}' WHERE title='{self.wiki_page}'")
                    db.commit()

                if self.building:
                    self.sent_count = 0
                    bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                    bot.delete_message(chat_id=chat_id, message_id=self.trans_window)
                    self.text_to_sents(message, call)

                self.sentence_buttons(message, call)
                return

            if call.data == 'previous_sent':
                self.reverse = False
                if self.sent_count > 0:
                    self.sent_count -= 1
                    # self.sent = self.sents[self.count]
                else:
                    return

                if self.building:
                    bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                    bot.delete_message(chat_id=chat_id, message_id=self.trans_window)
                    self.sents_to_words(message, call, sents=None)

                self.sentence_buttons(message, call)
                return

            if call.data == 'next_sent':
                self.reverse = False
                if self.sent_count < len(self.sents)-1:
                    self.sent_count += 1
                    # self.sent = self.sents[self.count]
                else:
                    return

                if self.building:
                    bot.delete_message(chat_id=chat_id, message_id=self.question_window)
                    bot.delete_message(chat_id=chat_id, message_id=self.trans_window)
                    self.sents_to_words(message, call, sents=None)

                self.sentence_buttons(message, call)
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
                self.sent_count = 0
                # self.sent = self.sents[self.count]

                self.building = True
                self.input_sentences = False
                self.new_sentence = True
                # self.question_window = message_id
                # self.trans_window = message_id
                self.text_to_sents(message, call)
                self.sentence_buttons(message, call)

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

            # if call.data == 'voice':
            #     user_name = call.from_user.first_name
            #     folder_name = user_name + '(' + str(chat_id) + ')'
            #     tts = gTTS(self.text)
            #     audio = 'my.mp3'#self.text+'.mp3'
            #     tts.save(folder_name+'\\'+audio)
            #     bot.send_audio(chat_id=chat_id, audio=open(folder_name+'\\'+audio, 'rb'))

            if call.data == 'previus_plus':
                if not self.free_input:
                    if self.current_ids[0] == 0:
                        pass
                    else:
                        self.current_ids[:0] = [self.current_ids[0]-1]
                        self.printing(message, call)

            if call.data == 'next_plus':
                if not self.free_input:
                    if self.current_ids[-1] == len(self.words)-1:
                        pass
                    else:
                        self.current_ids.append(self.current_ids[-1] + 1)
                        self.printing(message, call)

            if call.data == 'previus_minus':
                if not self.free_input:
                    if len(self.current_ids) == 1:
                        pass
                    else:
                        self.current_ids.pop(0)
                        self.printing(message, call)

            if call.data == 'next_minus':
                if not self.free_input:
                    if len(self.current_ids) == 1:
                        pass
                    else:
                        self.current_ids.pop()
                        self.printing(message, call)


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

            # if call.data == 'okey':

            #     bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Нажми на <b>'перевод'</b>, чтобы перевести предложение\nНажми на <b>'следующее'</b> чтобы перейти к следующему предложению\n\nИспользуй"+emoji.emojize(':heavy_plus_sign:')+"чтобы добавить следующее слово\n\Используй"+emoji.emojize(':heavy_minus_sign:')+"чтобы убрать добавленное слово\n\nТы можешь записать сколько угодно слов с предложения, <b>только не записывай одинаковые!</b>", parse_mode='html')

            #     markup = types.InlineKeyboardMarkup(row_width=2)
            #     item = types.InlineKeyboardButton('погнали!', callback_data='go')
            #     markup.add(item)

            #     bot.send_message(call.from_user.id,
            #     "Нажав на кнопку <b>'записать'</b>, позже ты сможешь поучить это слово\n<b>Запиши хотя бы одно слово из предложения!!</b>\nИначе я сломаюсь:)", reply_markup=markup, parse_mode='html')

            # if call.data == 'go':
            #     bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Нажав на кнопку <b>'записать'</b>, позже ты сможешь поучить это слово\n<b>Запиши хотя бы одно слово из предложения!!</b>\nИначе я сломаюсь:)", parse_mode='html')

            #     self.sent_to_words(message, call)

    def sentence_buttons(self, message=None, call=None, state=None):
        if call:
            chat_id = call.from_user.id
        if message:
            chat_id = message.chat.id

        markup = types.InlineKeyboardMarkup(row_width=3)
        prev = types.InlineKeyboardButton('предыдущий', callback_data='previous')
        trans = types.InlineKeyboardButton('перевод', callback_data='translate')
        next = types.InlineKeyboardButton('следующий', callback_data='next')
        build = types.InlineKeyboardButton('разобрать', callback_data='build')
        # voice = types.InlineKeyboardButton('озвучить', callback_data='voice')
        delete = types.InlineKeyboardButton('удалить', callback_data='delete')

        if self.building:

            button = 'закончить'
            callback = 'end'
            build = types.InlineKeyboardButton(button, callback_data=callback)
            reverse = types.InlineKeyboardButton('поменять язык', callback_data='reverse')

            if self.all_text:
                text = self.text
                button = 'cвернуть'
                callback = 'roll_up'
            else:
                text = self.sent
                button = 'весь текст'
                callback = 'all_text'

            # if len(self.sents) > 1:
            prev_s = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='previous_sent')
            sents = types.InlineKeyboardButton(button, callback_data=callback)
            next_s = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='next_sent')
                # if self.all_text:
                #     markup.add(sents)

        else:
            text = self.text

        if call:
            if call.data == 'translate':

                def has_cyrillic(text):
                    return bool(re.search('[а-яА-Я]', text))

                if has_cyrillic(text):
                    target = self.lang
                else:
                    target = 'ru'

                self.translated_sent = GoogleTranslator(source='auto', target=target).translate(text)
                text = self.translated_sent
                button = 'оригинал'
                callback = 'original'
                trans = types.InlineKeyboardButton(button, callback_data=callback)

            if call.data == 'original':
                # text = self.text
                button = 'перевод'
                callback = 'translate'
                trans = types.InlineKeyboardButton(button, callback_data=callback)

        if self.building:
            if self.all_text:
                # items = [types.KeyboardButton(item) for item in self.sents]
                # markup.add(*items)
                if len(self.sents) > 1:
                    markup.row(sents)
                markup.add(prev, trans, next, reverse, build)
            else:
                if len(self.sents) > 1:
                # markup.row(prev_s, sents, next_s)
                    markup.add(prev_s, sents, next_s, prev, trans, next, reverse, build)
                else:
                    markup.add(prev, trans, next, reverse, build)
        else:
            markup.add(prev, trans, next, build, delete)# voice)
        # if not self.all_text:
        #     markup.row(prev_s, sents,item4, item5, item6,)
        # else:
        #     try:
        #         markup.add(prev_s, sents, next_s, prev, trans, next, build, delete)
        #     except UnboundLocalError:
        #         markup.add(prev, trans, next, build, delete)
            # raise
        self.visual_text = text
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=self.text_window,reply_markup=markup, parse_mode='html')

    def printing(self, message=None, call=None):

        current_words = []
        self.word = None
        for x in self.current_ids:
            current_words.append(self.words[x])
        self.word = ' '.join(current_words)

        self.menu(message, call)

    def menu(self, message=None, call=None): #chat_id=None):
        if message:
            user_name = message.from_user.first_name
            chat_id = message.chat.id
        if call:
            user_name = call.from_user.first_name
            chat_id = call.from_user.id

        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='previus_plus')
        item3 = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='next_plus')
        item2 = types.InlineKeyboardButton('добавить', callback_data='adding')
        item4 = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='previus_minus')
        item6 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='next_minus')
        item5 = types.InlineKeyboardButton('изменить', callback_data='change')
        item7 = types.InlineKeyboardButton('записать', callback_data='write')

        markup.add(item1,item2,item3,item4,item5,item6,item7)

        sign = ''

        db, sql = self.data_base(message, call)

        sql.execute("SELECT translate FROM english WHERE word = ?", (self.word,))
        self.exist_word = sql.fetchall()

        if self.exist_word or self.changing or self.adding:

            if self.exist_word:
                x = [x for x in self.exist_word[0]]
                self.translated_word = ', '.join(x)
                sign = 'Это слово уже есть!\n'

            if self.changing:
                if self.new_translate:
                    self.translated_word = self.temp_word
                else:
                    sign = '<b>Кинь свой перевод!</b>\n'

            if self.adding:
                if self.new_translate:
                    self.translated_word = self.translated_word + ', ' + self.temp_word
                else:
                    sign = '<b>Добавь перевод!</b>\n'
        else:
            def has_cyrillic(text):
                return bool(re.search('[а-яА-Я]', text))

            if has_cyrillic(self.word):
                target = self.lang
            else:
                target = 'ru'

            self.translated_word = GoogleTranslator(source='auto', target=target).translate(self.word)

        text = sign+'<b>'+self.word+'</b>' + '\nозначает:\n' + '<b>'+self.translated_word+'</b>'

        bot.edit_message_text(chat_id=chat_id, message_id=self.trans_window, text=text, reply_markup=markup, parse_mode='html')

    def vars(self, message=None, call=None, sents=None, count=None, lang=None):
        pass

    def sents_to_words(self, message=None, call=None, sents=None):

        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
        if call:
            user_name = call.from_user.first_name
            user_id = call.from_user.id

        # folder_name = user_name + '(' + str(user_id) + ')'

        # if sents:
        #     self.sents = sents
        #     if call:
        #         if call.data == 'continue':
        #             with open(folder_name+'\\count.txt', 'r') as c:
        #                 count = c.readlines()
        #                 self.count = int(count[0])
        #     if message:
        #         if message.text == 'new_text':
        #             message.text = ''
        #             self.count = 0

        # print(self.count, len(self.sents))

        # if self.count >= len(self.sents):
        #     self.count = 0
        #     bot.edit_message_text(chat_id=user_id, message_id=self.trans_window, text='Это всё!')

        #     # bot.end_message(user_id,'Это всё!')

        #     with open(folder_name+'\\count.txt', 'w') as c:
        #         c.write(str(self.count))
        #     return

        # if self.count < 0:
        # self.count = 0

        #     return
        if sents:
            self.sents = sents
        self.sent = self.sents[self.sent_count]
        # # self.sent = message.text
        # self.words = re.findall(r"[\w']+", self.sent)

        # with open(folder_name+'\\count.txt', 'w') as c:
        #     c.write(str(self.count))

        self.buttons(message, call)

    def buttons(self, message=None, call=None):

        self.words = re.findall(r"[\w']+", self.sent)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in self.words]
        markup.add(*items)

        if call:

            user_id = call.message.chat.id
            message_id = call.message.message_id
            user_name = call.from_user.first_name

            self.question_window = self.last_message_id+1
            self.trans_window = self.last_message_id+2
            self.last_message_id = self.trans_window

            bot.send_message(user_id, 'Какое слово тебе не знакомо?', reply_markup=markup)
            bot.send_message(user_id, 'Выбери слово')
            write(user_name, user_id, message_id=self.last_message_id, target='last message')


            return

    def name_id(self, message=None, call=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
        if call:
            user_name = call.from_user.first_name
            user_id = call.from_user.id

        return user_name, user_id

    def write_word(self, message=None, call=None):
        # if message:
        #     user_name = message.from_user.first_name
        #     user_id = message.chat.id
        # if call:
        #     user_name = call.from_user.first_name
        #     user_id = call.from_user.id

        user_name, user_id = self.name_id(message, call)

        db, sql = self.data_base(message, call)

        if self.exist_word:
            sql.execute(f"UPDATE english SET translate = '{self.translated_word}' WHERE word = '{self.word}'")
            db.commit()
        else:
            if self.free_input:
                sql.execute("INSERT INTO english VALUES (?, ?, ?)", (self.word, self.translated_word, None))
                db.commit()
            else:
                sql.execute("INSERT INTO english VALUES (?, ?, ?)", (self.word, self.translated_word, self.sent))
                db.commit()

        # for value in sql.execute("SELECT * FROM english"):
        #     print(value)

        bot.edit_message_text(chat_id=user_id, message_id=self.trans_window, text='Записано!\n' + '<b>'+self.word+'</b>' + ':\n' + '<b>'+self.translated_word+'</b>', parse_mode='html')

    def instructions(self, message=None, call=None):

        user_name = message.from_user.first_name
        message_id = message.message_id
        user_id = message.chat.id
        self.last_message_id = message_id
        write(user_name, user_id, message_id=self.last_message_id, target='last message')

        db, sql = self.data_base(message, call)

        if self.changing_lang:
            self.messages_while_changing += 1

            if message.text in self.langs:
                self.lang = self.langs[message.text]
                self.changing_lang = False

                for m in range(self.messages_while_changing):
                    bot.delete_message(chat_id=user_id, message_id=message_id-m)
                self.messages_while_changing = 0
            return

        if self.input_sentences:
            self.text = message.text
            self.all_texts.append(self.text)
            # self.sents = self.text_to_sents(message)
            sql.execute("INSERT INTO texts VALUES (?, ?)", (message_id, self.text))
            db.commit()
            bot.delete_message(chat_id=user_id, message_id=message_id)

            self.sentence_buttons(message)
            return

        if self.new_sentence:
            self.new_sentence = False

        if self.adding_input:
            self.temp_word = message.text
            self.new_translate = True
            bot.delete_message(chat_id=user_id, message_id=message_id)
            self.menu(message, call)

            self.new_translate = False
            self.adding = False
            self.changing = False
            self.adding_input = False

            return

        self.word = message.text

        try:
            index_word = self.words.index(self.word)
            self.current_ids = [index_word]
            self.free_input = False
        except ValueError:
            self.free_input = True

        # if self.question_window:
        #     # bot.delete_message(chat_id=user_id, message_id=self.question_window)
        #     # self.question_window = None

        bot.delete_message(chat_id=user_id, message_id=message_id)

        self.menu(message, call)#chat_id)

    def vars(self, message=None, call=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
            message_id = message.message_id
        if call:
            user_name = call.from_user.first_name
            user_id = call.message.chat.id
            message_id = call.message.message_id
        return user_name, user_id, message_id

    def hello(self, message=None, call=None, data=None, reason=None, last_message=None, wiki_page=None):
        user_name, user_id, message_id = self.vars(message,call)
        db, sql = self.data_base(message, call)

        self.text_count = 0
        self.sent_count = 0
        self.input_sentences = True

        if not reason:
            self.last_message_id = message_id
            sql.execute("SELECT text FROM texts")
            try:
                self.all_texts = [text[0] for text in sql.fetchall()]
                self.text = self.all_texts[0]
            except IndexError :
                pass

        if reason == 'wiki':
            self.wiki = True
            self.wiki_page = wiki_page
            sql.execute("SELECT sentence FROM wiki WHERE title = ?",(wiki_page,))
            index = sql.fetchall()[0][0]
            if index == None:
                sql.execute(f"UPDATE wiki SET sentence='{0}' WHERE title='{wiki_page}'")
                db.commit()
            else:
                self.text_count = index
            # заполнить пуcтые ячейки в sentences
            # self.titles = titles
            self.last_message_id = last_message
            symbols = 500

            for title in data:
                text = data[title]
                l = len(data[title])
                parts = int(len(text)/symbols) +1
                part_index = 0
                part = 0

                while not part == parts:
                    part += 1
                    if parts > 1:
                        text = data[title][part_index:]
                        slice = text[0:symbols]

                        if '.' not in slice:
                            while '.' not in slice:
                                if len(slice)+symbols < 4000:
                                    slice = text[0:symbols+1000]
                                    part += 1
                                if len(slice) == len(data[title]):
                                    break
                            text = slice
                        else:
                            end = slice.rindex('.')
                            part_index += end+1
                            text = slice[0:end+1]
                    else:
                        pass

                    htmltitle = '<b>'+title+'</b>'
                    all_text = htmltitle +'\n'+ text
                    self.all_texts.append(all_text)

            self.text = self.all_texts[self.text_count]

        bot.send_message(user_id, 'Получаю сообщения!')
        self.last_message_id += 1
        self.text_window = self.last_message_id
        write(user_name, user_id, message_id=self.last_message_id, target='last message')

        if self.text:
            self.sentence_buttons(message, call)

    def random_words(self, message):
        pass

    def text_to_sents(self, message, call):

        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"

        def split_into_sentences(text):

            text = " " + text + "  "
            # text = text.replace('-\n', '')
            # text = text.replace("\n"," ")
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
            if len(sentences) > 1:
                sentences = sentences[:-1]
            sentences = [s.strip() for s in sentences]
            # print(sentences)
            return sentences

        if call.data == 'build':
            text = call.message.text

        sents = split_into_sentences(self.text)
        # return sents
        # print(call.message.message_id)
        self.sents_to_words(message, call, sents)