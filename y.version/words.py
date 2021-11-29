from state import State
from main import bot
from deep_translator import GoogleTranslator
from telebot import types
from main import sql, db
from text import Text
 

class Words(State):
    """
    Description
    """

    _state = None
    _word = None
    _translated = None
    _sentence = None

    def inline_buttons(self, message=None, call=None):
        user_id = call.from_user.id
        message_id = call.message.message_id

        if call.data == 'write':
            self._state = 'sentence'
            bot.send_message(user_id, 'Кинь предложение!')
        
        if call.data == 'add':
            self._state = 'translate'
            bot.send_message(user_id, 'Кинь перевод!')

        if call.data == 'change':
            self._state = 'change'
            bot.send_message(user_id, 'Давай свой перевод!')

        if call.data == 'cancel':
            bot.delete_message(chat_id=user_id, message_id=message_id)

    def printing(self, chat_id=None):
        pass
    
    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message=None, call=None) -> None:
        user_name = message.from_user.first_name
        user_id = message.chat.id

        bot.send_message(user_id, 'Кидай мне предложение!')
        self._state = 'word'

    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def random_words(self):
        pass

    def buttons(self, call):
        pass
         
    def instructions(self, message):

        sentence = message.text

        self.context.transition_to(Text())
        self.context.sent_to_words(message, call=None)
        return

        user_id = message.chat.id
        message = message.text

        if self._state == 'word':
            self._word = message
            sql.execute("SELECT translate FROM english WHERE word = ?", (self._word,))
            self._translated = sql.fetchall()

            if not self._translated:
                self._translated = GoogleTranslator(source='auto', target='ru').translate(self._word)

                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton('Записать', callback_data='write')
                item3 = types.InlineKeyboardButton('Изменить перевод', callback_data='change')
                item2 = types.InlineKeyboardButton('Отменить', callback_data='cancel')
                markup.add(item1, item2, item3)

                bot.send_message(user_id, f'<b>{self._word}</b> значит <b>{self._translated}</b>', reply_markup=markup, parse_mode='html')
                # bot.send_message(user_id, 'Кинь предложение!')
                # self._state = 'sentence'
            else:
                x = [x for x in self._translated[0]]
                self._translated = ' '.join(x)
                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton('Добавить перевод', callback_data='add')
                markup.add(item1)
                bot.send_message(user_id, f'Cлово <b>{self._word}</b> уже есть!\n<b>{self._word}</b> означает <b>{self._translated}</b>', reply_markup=markup, parse_mode='html')
                
            return

        if self._state == 'translate':
            self._translated = self._translated + ', ' + message
            bot.send_message(user_id, self._translated)
            sql.execute(f"UPDATE english SET translate = '{self._translated}' WHERE word = '{self._word}'")
            db.commit()
            self._state = 'word'
            return
        
        if self._state == 'change':
            self._translated = message
            bot.send_message(user_id, 'Кинь предложение!')
            self._state = 'sentence'
            return

        if self._state == 'sentence':
            self._sentence = message
            
            sql.execute(f"INSERT INTO english VALUES (?, ?, ?)", (self._word, self._translated, self._sentence))
            db.commit()

            bot.send_message(user_id, f'Записано!\n{self._word} - {self._translated}\n{self._sentence}')


            for value in sql.execute("SELECT * FROM english"):
                print(value)

        self._word = None
        self._translated = None
        self._sentence = None
        self._state = 'word'
        return