#!/usr/bin/env python3
# (c) Shrimadhav U K

# the logging things
# import logging
# logging.basicConfig(level=logging.VERBOSE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# the PTB
from telegram.ext import Updater
# the Telegram trackings
from botan import Botan

# the secret configuration specific things
from config import Config

# the Strings used for this "thing"
from string import String


## The telegram Specific Functions
def start(bot, update):
    botan.track(Config.BOTAN_IO_TOKEN, update.message, update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text=String.START_TEXT)


def echo(bot, update):
    botan.track(Config.BOTAN_IO_TOKEN, update.message, update.message.chat_id)
    if(update.message.text.startswith("http")):
        url = update.message.text
        print(url)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=String.START_TEXT)


if __name__ == "__main__" :
    botan = Botan()
    updater = Updater(token=Config.TG_BOT_TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()
