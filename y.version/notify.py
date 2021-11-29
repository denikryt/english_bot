# from main import WORKING_USERS, CHAT_ID
import time
from learn import Learn

def wait():
    while True:
        time.sleep(1)
        active = [user for user in WORKING_USERS if WORKING_USERS[user]]
        for user in active:           
            waiting = WORKING_USERS[user]
            WORKING_USERS[user] = waiting - 1 
            if WORKING_USERS[user] == 0:
                WORKING_USERS[user] = False
            print('MINUS', user, WORKING_USERS[user])

def notification():
    send_list = []
    while True:
        for user in WORKING_USERS:
            active = WORKING_USERS[user]

            if not active:
                print('PLUS')
                send_list.append(user)
        send_list = [183278535]
        send(CHAT_ID, send_list)

        send_list.clear()
        time.sleep(10)

def send(chat_id, send_list):
    for user_id in send_list:
        user_name = list(chat_id.keys())[list(chat_id.values()).index(user_id)]

        Learn.hello(Learn, user_name, user_id)