from telebot import types
from bot import BOT as bot


@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(183278535, 'loh')
    pass

if __name__ == "__main__":
    """Client code"""
    bot.remove_webhook()
    bot.polling(none_stop=False)