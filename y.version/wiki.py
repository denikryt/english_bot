import requests
import wikipediaapi
import re
from bot import BOT as bot
from bs4 import BeautifulSoup
from database import connect
from telebot import types
from text import Text
from nltk import tokenize 

class Wiki():
    navigator = False
    question_window = 0
    menu_window = 0
    last_message = 0
    title = ''
    url = ''
    titles = []
    urls = []
    paragraphs = {}

    def inline_buttons(self, message=None, call=None):
        db, sql = self.data_base(message,call)
        user_name, user_id = self.name_id(message,call)

        if call.data == 'delete_wiki':
            sql.execute("DELETE FROM wiki WHERE title=(?)", (self.title,))
            db.commit()
            self.titles.remove(self.title)
            bot.delete_message(chat_id=user_id, message_id=self.question_window)
            bot.delete_message(chat_id=user_id, message_id=self.menu_window)
            self.navigator = False

            self.hello(message,call)

        if call.data == 'read':
            self.transition(message, call)

    def menu(self, message=None, call=None):
        db, sql = self.data_base(message,call)
        user_name, user_id = self.name_id(message,call)

        sql.execute("SELECT url FROM wiki WHERE title=(?)",(self.title,))
        url = sql.fetchone()[0]
        summary = self.get_page(message, call).summary
        summary = tokenize.sent_tokenize(summary)[0]
        text = '<b>'+self.title+'</b>' + '\n' + summary 

        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton('ссылка', url=url)
        item2 = types.InlineKeyboardButton('читать', callback_data='read')
        item3 = types.InlineKeyboardButton('удалить', callback_data='delete_wiki')
        markup.add(item1, item2, item3)
        
        if self.navigator:
            bot.delete_message(chat_id=user_id, message_id=self.last_message)
            bot.edit_message_text(chat_id=user_id, message_id=self.menu_window, text=text, reply_markup=markup, parse_mode='html')
        else:
            bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
            self.last_message += 1
            self.menu_window = self.last_message
            self.navigator = True

    def name_id(self, message=None, call=None, get=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
            message_id = message.message_id
        if call:
            user_name = call.from_user.first_name
            user_id = call.from_user.id
            message_id = call.message.message_id
        if get == 'message_id':
            return message_id
        return user_name, user_id

    def data_base(self, message=None, call=None):
        user_name, user_id = self.name_id(message,call)

        folder_name = user_name + '(' + str(user_id) + ')'
        db, sql = connect(folder_name)
        return db, sql

    def get_title(self, message=None, call=None):
        url = message.text
        response = requests.get(url=url,)
        print(response.status_code)

        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find(id="firstHeading")
        print(title.string)
        return url, title.string

    def hello(self, message=None, call=None):
        db, sql = self.data_base(message,call)
        user_name, user_id = self.name_id(message,call)

        if not call:
            self.last_message = message.message_id

        sql.execute("SELECT title FROM wiki")
        result_t = sql.fetchall()
        sql.execute("SELECT url FROM wiki")
        result_u = sql.fetchall()

        self.titles = []
        self.urls = []

        if result_t:
            for title in result_t:
                self.titles.append(title[0])
            for url in result_u:
                self.urls.append(url[0])
            
        self.say_what(message, call)

    def say_what(self, message, call, i_title=0):
        user_name, user_id = self.name_id(message,call)

        if self.titles:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            items = [types.KeyboardButton(item) for item in self.titles]
            markup.add(*items)
            bot.send_message(user_id, "че читаем?", reply_markup=markup)

            self.last_message += 1
            self.question_window = self.last_message
            self.title = self.titles[i_title]

            self.menu(message,call)
        else:
            bot.send_message(user_id, "Кинь мне ссылку на вики!")
            self.last_message += 1

    def instructions(self, message=None, call=None):
        db, sql = self.data_base(message,call)
        user_name, user_id = self.name_id(message,call)
        self.last_message = message.message_id

        if message.text.startswith('https://'):
            url, title = self.get_title(message,call)
            bot.delete_message(chat_id=user_id, message_id=self.last_message)
            

            if not url in self.urls:
                sql.execute("INSERT INTO wiki VALUES (?, ?)", (url, title))
                db.commit()
                self.titles.append(title)
                self.urls.append(url)

                bot.delete_message(chat_id=user_id, message_id=self.menu_window)
                bot.delete_message(chat_id=user_id, message_id=self.question_window)
                self.navigator = False
                
                self.say_what(message,call, i_title=len(self.titles)-1)
            return
            
        elif message.text in self.titles:
            if message.text == self.title:
                bot.delete_message(chat_id=user_id, message_id=self.last_message)
                return
            self.title = message.text
            self.menu(message, call)
            return
        else:
            bot.send_message(user_id, "чо?")
            self.last_message += 1

    def get_page(self, message, call):
        db, sql = self.data_base(message,call)
        sql.execute("SELECT url FROM wiki WHERE title=(?)",(self.title,))
        url = sql.fetchone()[0]
        lang = re.findall(r'https://(\w+)', url)[0]

        wiki_wiki = wikipediaapi.Wikipedia(lang)
        page_py = wiki_wiki.page(self.title)

        self.paragraphs['Summary'] = page_py.summary

        return page_py

    def transition(self, message=None, call=None):
        user_name, user_id = self.name_id(message,call)

        def print_sections(sections, level=0):
            # text = [page_py.summary]
            for s in sections:
                # text.append(s.text)
                # print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text))
                self.paragraphs[s.title] = s.text
                print_sections(s.sections, level + 1)

        page_py = self.get_page(message, call)
        print_sections(page_py.sections)
        bot.delete_message(chat_id=user_id, message_id=self.question_window)

        self.context.transition_to(Text())
        self.context.hello(message,call, data=self.paragraphs, reason='wiki', last_message=self.last_message)


        
        

