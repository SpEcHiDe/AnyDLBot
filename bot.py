#!/usr/bin/env python3
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# the PTB
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# the Telegram trackings
from botan import Botan

import subprocess
import requests
import os
import json
# the secret configuration specific things
from config import Config
# the Strings used for this "thing"
from translation import Translation


## The telegram Specific Functions
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def start(bot, update):
    # botan.track(Config.BOTAN_IO_TOKEN, update.message, update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text=Translation.START_TEXT, reply_to_message_id=update.message.message_id)


def echo(bot, update):
    # botan.track(Config.BOTAN_IO_TOKEN, update.message, update.message.chat_id)
    if(update.message.text.startswith("http")):
        url = update.message.text
        t_response = subprocess.check_output(["youtube-dl", "-j", url])
        x_reponse = t_response.decode("UTF-8")
        response_json = json.loads(x_reponse)
        inline_keyboard = []
        for formats in response_json["formats"]:
            ikeyboard = [
                # InlineKeyboardButton(formats["format"], callback_data=formats["format_id"]),
                InlineKeyboardButton(formats["format"], callback_data=formats["format_id"])
            ]
            inline_keyboard.append(ikeyboard)
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        bot.send_message(chat_id=update.message.chat_id, text='Select the desired format: ', reply_markup=reply_markup, reply_to_message_id=update.message.message_id)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=Translation.START_TEXT, reply_to_message_id=update.message.message_id)


def button(bot, update):
    query = update.callback_query
    youtube_dl_format = query.data
    youtube_dl_url = query.message.reply_to_message.text
    t_response = subprocess.check_output(["youtube-dl", "-j", youtube_dl_url])
    x_reponse = t_response.decode("UTF-8")
    response_json = json.loads(x_reponse)
    download_directory = Config.DOWNLOAD_LOCATION + "/" + str(response_json["_filename"]) + ""
    bot.edit_message_text(
        text="Trying to download link",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )
    # if os.path.exists(download_directory):
    #    bot.edit_message_text(
    #        text="Free users can download only 1 URL per day",
    #        chat_id=query.message.chat_id,
    #        message_id=query.message.message_id
    #    )
    # else:
    t_response = subprocess.check_output(["youtube-dl", "-f", youtube_dl_format, youtube_dl_url, "-o", download_directory])
    bot.edit_message_text(
        text="Trying to upload file",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )
    file_size = os.stat(download_directory).st_size
    if file_size > Config.MAX_FILE_SIZE:
        bot.edit_message_text(
            text="size greater than maximum allowed size",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        # just send a link
        file_link = Config.HTTP_DOMAIN + "" + download_directory.replace("./", "")
        bot.send_message(chat_id=query.message.chat_id, text=file_link)
    else:
        # try to upload file
        bot.send_document(chat_id=query.message.chat_id, document=open(download_directory, 'rb'), caption="@AnyDLBot")
        # TODO: delete the file after successful upload
        # os.remove(download_directory)


if __name__ == "__main__" :
    botan = Botan()
    # create download directory, if not exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=Config.TG_BOT_TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
