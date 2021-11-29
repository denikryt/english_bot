from state import State
from collections import OrderedDict
from main import bot
import random
import string


class Game(State):
    """
    Description
    """

    available_words =[]
    repeat = []
    vocab = {}
    sents = {}
    rand = ''
    rand_eng = ''

    def inline_buttons(self, call):
        pass

    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message=None, call=None) -> None:
        w = open('words.txt', 'r', encoding='utf-8')
        t = open('trans.txt', 'r')
        s = open('sents.txt', 'r', encoding='utf-8')
        # l = open('last.txt', 'r')
        r = open('repeat.txt', 'r', encoding='utf-8')
        
        repeat = r.read().splitlines()
        words = w.read().splitlines()

        split_t = t.read().splitlines()
        trans = [j for i in split_t for j in [i.split(';')]]
        # print(trans)

        split_s = s.read().splitlines()
        sents = [o for p in split_s for o in [p.split(';')]]

        w.close()
        t.close()
        s.close()
        r.close()
        # l.close()
                   
        self.vocab = OrderedDict(zip(words, trans))
        self.sents = OrderedDict(zip(words, sents))

        self.available_words = words.copy()
        self.random_words()

    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def buttons(self, message):
        pass

    def random_words(self, message=None, call=None):
        if not message == None:
            user_ID = message.chat.id
            message_id = message.message_id
        if not call == None:
            user_ID = call.from_user.id
            message_ID = call.message.message_id

        self.rand_eng = random.choice(self.available_words)
        rand_rus = self.vocab[self.rand_eng]

        choose_list = [self.rand_eng, rand_rus]
        rand_choice = random.choice(choose_list)

        if type(rand_choice) is list:
            self.rand = random.choice(rand_choice)
            # key = '7'
            bot.send_message(user_ID, "Переведи это '{}': ".format(self.rand))
            # print("Переведи это '{}': ".format(self.rand))
        if type(rand_choice) is str:
            self.rand = rand_choice
            # key = '8'
            bot.send_message(user_ID, "Переведи это '{}': ".format(self.rand))
            # print("'пример' для примера\nПереведи это {}: ".format(self.rand))

        
    def instructions(self, message) -> None:
        user = message.text
        print(user)
        def game():

            # def is_english_check(rand):
            #     char_set = string.ascii_letters+' '
            #     return all((True if x in char_set else False for x in self.rand))
            # is_english = is_english_check(self.rand)

            # if user.rstrip() == 'пример':
            #     for x,y in enumerate(self.sents[self.rand]):
            #         print(str(x+1)+')', y) 
            #     return False

            # if user.rstrip() == 'show':
            #     print('не подсматривай', self.vocab[self.rand])
            #     return False

            # if user.rstrip() == '1':
            #     print('Da!')
            #     self.available_words.remove(self.rand)
            #     return True
            
            # elif user.rstrip() == 'q':
            #     print('pussy')
            #     return False

            # if type(rand_choice) is list:
                
            # if type(rand_choice) is str:

            # if is_english is True:

            
            
            # return True

            self.available_words.remove(self.rand_eng)

            if user.rstrip() == 'n':
                print('Иди учи!')
                if self.rand_eng not in self.repeat:
                    self.repeat.append(self.rand_eng)
                return True 

            try:    
                if user.rstrip() in self.vocab[self.rand_eng]:
                    print('Da!')
                    if self.rand_eng in self.repeat:
                        self.repeat.remove(self.rand_eng)
                return True 
            except:
                raise

            if user.rstrip() == self.rand_eng:
                print('Da!')
                if self.rand_eng in self.repeat:
                    self.repeat.remove(self.rand_eng)
                return True 
                
            
            # else:
            #     if user.rstrip() == 'n':
            #         print('Иди учи!')
            #         self.available_words.remove(self.rand_eng)
            #         if self.rand_eng not in self.repeat:
            #             self.repeat.append(self.rand_eng)
            #         return True               
                
            #     if user.rstrip() == self.rand_eng:
            #         print('Da!')
            #         self.available_words.remove(self.rand_eng)
            #         if user.rstrip() in self.repeat:
            #             self.repeat.remove(self.rand_eng)
            #         return True
            #     else:
            #         if self.rand_eng not in self.repeat:
            #             self.repeat.append(self.rand_eng)

            if user.rstrip() == 'ебать ты лох':
                print('Ты угадал секретное слово!')
            else:
                if self.rand not in self.repeat:
                    self.repeat.append(self.rand_eng)
                print('come on!')

        if game() == False:
            return
        else:
            if len(self.available_words) == 0:
                print('Молодец! Это всё!')

                with open('repeat.txt', 'w') as r:
                    for x in self.repeat:
                        r.write(x+'\n')
                return
            else:
                self.random_words()