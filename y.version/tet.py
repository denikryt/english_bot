import threading
from bot import BOT as bot
import time
import schedule
import queue

# working = False
# users = [183278535,183278535,183278535]
working_users = {
    183278535:False,
    430078812:False
}


@bot.message_handler(content_types=['text'])
def lalala(message):
    user_id = message.chat.id
    global working_users
    bot.send_message(user_id, 'loh')
    working_users[user_id] = 20
    print(working_users)
    # working = True

def wait():
    while True:
        time.sleep(1)
        active = [user for user in working_users if working_users[user]]
        for user in active:           
            waiting = working_users[user]
            working_users[user] = waiting - 1 
            if working_users[user] == 0:
                working_users[user] = False
            print('MINUS', user, working_users[user])

def notify():
    # global working_users
    send_list = []
    while True:
        for user in working_users:
            active = working_users[user]

            if not active:
                print('PLUS')
                send_list.append(user)

        for user_id in send_list:
            print('SEND', user_id)
            bot.send_message(user_id, 'helo')

        send_list.clear()
        time.sleep(10)

if __name__ == '__main__':
    tmp = threading.Thread(target=notify, args=())
    tmp.start()
    tmp2 = threading.Thread(target=wait, args=())
    tmp2.start()
    # finput()
    bot.remove_webhook()
    bot.polling(none_stop=False)


#-------------------------------------------------#
# def user():
#     global working
#     user_input = input('?')
#     if user_input:
#         working = True

# def send(user_id):
#     global working
#     # if working:
#     #     return
#     print('SEND') 
#     bot.send_message(user_id, 'helo')
#     # if working:
#     #     # return schedule.SkipJob
#     #     print('AGAIN')
#     #     working = False
#     #     return schedule.CancelJob
#     # return

# def again():
#     global working
#     working = False
#     print('FREE')
#     return schedule.CancelJob

# def job():
#     global working
#     if working:
#         print('WORKING')
#         schedule.every(10).seconds.do(again)
#         return schedule.SkipJob
#         # print('WORKING')
#         # return #schedule.CancelJob
#     send(user_id)
#     # print('SEND')
#     # return #send()
# # schedule.every(10).seconds.do(send)

# def notify(working_users):
#     # global working_users
#     while True:
#         for user_id in working_users:
#             time.sleep(1)
#             working = working_users[user_id]
#             if not working:
#                 bot.send_message(user_id, 'helo')
#                 # send(user_id)
#             else:
#                 if working == 0:
#                     working = False
#                 else:
#                     working -= 1
#         # schedule.run_pending()

# # schedule.every().second.do(job)

# def pend():
#     while True:
#         schedule.run_pending()
#         # schedule.SkipJob
#         time.sleep(1)



#-------------------------------------------------#

# def job():
#     # bot.send_message(user, 'helo')
#     print("I'm working")


# def worker_main():
#     while 1:
#         job_func = jobqueue.get()
#         job_func()
#         jobqueue.task_done()

# jobqueue = queue.Queue()

# send_list = [user for user in working_users if not working_users[user]]

# # items = [types.KeyboardButton(item) for item in self.words]
# # markup.add(*items)

# # sending = [schedule.every(10).seconds.do(jobqueue.put, job(user)) for user in send_list]

# # schedule.every(10).seconds.do(jobqueue.put, job(send_list[0]))
# # schedule.every(10).seconds.do(jobqueue.put, job(send_list[0]))
# schedule.every(10).seconds.do(jobqueue.put, job)
# schedule.every(10).seconds.do(jobqueue.put, job)
# schedule.every(10).seconds.do(jobqueue.put, job)

# worker_thread = threading.Thread(target=worker_main)
# worker_thread.start()

# # def notify():
# while 1:
#     schedule.run_pending()
#     time.sleep(1)





#     notification(working=True)

# def notification(working):
#     tmp = threading.Thread(target=send, args=(lambda: working, ))
#     tmp.start()
#     tmp.join()
#     # tmp = threading.Thread(target=send, args=(lambda: working, ))
#     # if working:
#     #     tmp.join()
#     # else:
#     #     tmp = threading.Thread(target=send, args=(lambda: working, ))
#     #     tmp.start()


# def send(stop):
#     time.sleep(10)
#     nexttime = time.time()
#     while True:
#         bot.send_message(183278535, 'helo')           # take t sec
#         nexttime += 10
#         sleeptime = nexttime - time.time()
#         if sleeptime > 0:
#             time.sleep(sleeptime)
#         if stop():
#             break

# if __name__ == '__main__':
#     # tmp = threading.Thread(target=send, args=(lambda: False, ))

#     # tmp = threading.Thread(target=send, args=(lambda: False, ))
#     # notification(working=False)
#     bot.polling(none_stop=False)


    # print("I am thread", id)
    # while True:
    #     print("I am thread {} doing something".format(id))
    #     if stop():
    #         print("  Exiting loop.")
    #         break
    # print("Thread {}, signing off".format(id))


    
    # tmp = threading.Thread(target=send, args=(lambda: stop_threads))
    # tmp.start()
    # working = False
    # stop_threads = False
    # workers = []
    # for id in range(0,3):
    #     tmp = threading.Thread(target=send_noti, args=(id, lambda: stop_threads))
    #     workers.append(tmp)
    #     tmp.start()
    # time.sleep(3)
    # print('main: done sleeping; time to stop the threads.')
    # stop_threads = True
    # for worker in workers:
    #     worker.join()
    # print('Finis.')



# def notification(working):
#     nexttime = time.time()
#     while not working:
#         bot.send_message(183278535, 'helo')           # take t sec
#         nexttime += 10
#         sleeptime = nexttime - time.time()
#         if sleeptime > 0:
#             time.sleep(sleeptime)

# def some(working):
#     while working:





# def main():
#     stop_threads = False
#     workers = []
#     for id in range(0,3):
#         tmp = threading.Thread(target=do_work, args=(id, lambda: stop_threads))
#         workers.append(tmp)
#         tmp.start()
#     time.sleep(3)
#     print('main: done sleeping; time to stop the threads.')
#     stop_threads = True
#     for worker in workers:
#         worker.join()
#     print('Finis.')

# if __name__ == '__main__':
#     main()


# thr = threading.Thread(target=no, args=(), kwargs={'working':True})
# thr.start()

# def check_time(working):
#     time.sleep(10)
#     notification(working=False)
    # pass

# thr = threading.Thread(target=no, args=(), kwargs={})
# thr.start()

# bot.polling(none_stop=False)