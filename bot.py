#!/usr/bin/env python3
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# the PTB
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, DispatcherHandlerStop, run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, ChatAction

import subprocess
import math
import requests
import os
import json

from telethon import TelegramClient
from telethon.errors import (
    RPCError, BrokenAuthKeyError, ServerError,
    FloodWaitError, FloodTestPhoneWaitError, FileMigrateError,
    TypeNotFoundError, UnauthorizedError, PhoneMigrateError,
    NetworkMigrateError, UserMigrateError, SessionPasswordNeededError
)
from telethon.utils import get_display_name
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeVideo


# the secret configuration specific things
from config import Config
# the Strings used for this "thing"
from translation import Translation

# the Telegram trackings
from chatbase import Message
ABUSIVE_SPAM = []

def TRChatBase(chat_id, message_text, intent):
    msg = Message(api_key=Config.CHAT_BASE_TOKEN,
              platform="Telegram",
              version="1.3",
              user_id=chat_id,
              message=message_text,
              intent=intent)
    resp = msg.send()


def DownLoadFile(url, file_name):
    if not os.path.exists(file_name):
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
                fd.write(chunk)
    return file_name


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    #2**10 = 1024
    if not size:
      return ""
    power = 2**10
    n = 0
    Dic_powerN = {0 : ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /=  power
        n += 1
    return str(math.floor(size)) + " " + Dic_powerN[n] + 'B'


## The telegram Specific Functions
def error(bot, update, error):
    """Log Errors caused by Updates."""
    # TRChatBase(update.message.chat_id, update.message.text, "error")
    logger.warning('Update "%s" caused error "%s"', update, error)


@run_async
def start(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "/start")
    bot.send_message(
        chat_id=update.message.chat_id,
        text=Translation.START_TEXT,
        reply_to_message_id=update.message.message_id
    )


@run_async
def echo(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "echo")
    if str(update.message.chat_id) in ABUSIVE_SPAM:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=Translation.ABS_TEXT,
            reply_to_message_id=update.message.message_id
        )
    else:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        text = update.message.text
        if(text.startswith("http")):
            url = text
            # logger = "<a href='" + url + "'>url</a> by <a href='tg://user?id=" + str(update.message.chat_id) + "'>" + str(update.message.chat_id) + "</a>"
            # bot.send_message(chat_id=-1001364708459, text=logger, parse_mode="HTML")
            if "noyes.in" not in url:
                try:
                    command_to_exec = ["youtube-dl", "--no-warnings", "-j", url]
                    t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
                    # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
                except subprocess.CalledProcessError as exc:
                    # print("Status : FAIL", exc.returncode, exc.output)
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text=exc.output.decode("UTF-8"),
                        reply_to_message_id=update.message.message_id
                    )
                else:
                    x_reponse = t_response.decode("UTF-8")
                    # print(x_reponse)
                    response_json = json.loads(x_reponse)
                    inline_keyboard = []
                    for formats in response_json["formats"]:
                        format_id = formats["format_id"]
                        format_string = formats["format"]
                        format_ext = formats["ext"]
                        approx_file_size = ""
                        if "filesize" in formats:
                            approx_file_size = humanbytes(formats["filesize"])
                        ikeyboard = [
                            InlineKeyboardButton(
                                "[" + format_string + "] (" + format_ext + " - " + approx_file_size + ")",
                                callback_data=format_id + ":" + format_ext
                            )
                        ]
                        inline_keyboard.append(ikeyboard)
                    inline_keyboard.append([
                        InlineKeyboardButton("MP3 " + "(" + "medium" + ")", callback_data="5:mp3")
                    ])
                    inline_keyboard.append([
                        InlineKeyboardButton("MP3 " + "(" + "best" + ")", callback_data="0:mp3")
                    ])
                    reply_markup = InlineKeyboardMarkup(inline_keyboard)
                    logger.info(reply_markup)
                    thumbnail = "https://placehold.it/50x50"
                    if "thumbnail" in response_json:
                        thumbnail = response_json["thumbnail"]
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text='Select the desired format: [file size might be approximate](' + thumbnail + ') ',
                        reply_markup=reply_markup,
                        parse_mode="Markdown",
                        reply_to_message_id=update.message.message_id
                    )
            else:
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text="@GetPublicLinkBot URL detected. Please do not abuse the service!",
                    reply_to_message_id=update.message.message_id
                )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text=Translation.START_TEXT,
                reply_to_message_id=update.message.message_id
            )


def button(bot, update):
    query = update.callback_query
    if query.data.find(":") == -1:
        return ""
    youtube_dl_format, youtube_dl_ext = query.data.split(":")
    ggyyy = bot.getChatMember("@MalayalamTrollVoice", query.message.chat_id)
    if ggyyy.status != "left":
    # if "1" != "2":
        youtube_dl_url = query.message.reply_to_message.text
        command_to_exec = ["youtube-dl", "--no-warnings", "-j", youtube_dl_url]
        t_response = subprocess.check_output(command_to_exec)
        x_reponse = t_response.decode("UTF-8")
        response_json = json.loads(x_reponse)
        thumbnail_image = "https://placehold.it/50x50"
        if "thumbnail" in response_json:
            response_json["thumbnail"]
        thumb_image_path = DownLoadFile(thumbnail_image, Config.DOWNLOAD_LOCATION + "/" + str(query.message.chat_id) + ".jpg")
        format_url = "https://da.gd/help"
        if "url" in response_json:
            format_url = requests.get("https://da.gd/s?url=" + str(response_json["url"])).text
        inline_keyboard = []
        inline_keyboard.append([
            InlineKeyboardButton(" Direct DownLoad Link ", url=format_url)
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        # file_name_ext = response_json["_filename"].split(".")[-1]
        bot.edit_message_text(
            text="trying to download",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        description = " " + " \r\n© @AnyDLBot"
        if "description" in response_json:
            description = " " + str(response_json["description"])[0:150] + " \r\n© @AnyDLBot"
        download_directory = ""
        command_to_exec = []
        output_file_name, output_real_file_ext = response_json["_filename"].split(".", maxsplit=1)
        if "mp3" in youtube_dl_ext:
            download_directory = Config.DOWNLOAD_LOCATION + "/" + str(output_file_name)[0:97] + "_" + youtube_dl_format + "." + youtube_dl_ext + ""
            command_to_exec = [
                "youtube-dl",
                "--extract-audio",
                "--audio-format", youtube_dl_ext,
                "--audio-quality", youtube_dl_format,
                youtube_dl_url,
                "-o", download_directory
            ]
        else:
            download_directory = Config.DOWNLOAD_LOCATION + "/" + str(output_file_name)[0:97] + "_" + youtube_dl_format + "." + youtube_dl_ext + ""
            # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
            command_to_exec = [
                "youtube-dl",
                "--embed-subs",
                "-f", youtube_dl_format,
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]
        print(command_to_exec)
        try:
            t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            # print("Status : FAIL", exc.returncode, exc.output)
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=exc.output.decode("UTF-8"),
                reply_markup=reply_markup
            )
        else:
            logger.info(t_response)
            bot.edit_message_text(
                text="trying to upload",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
            file_size = os.stat(download_directory).st_size
            if file_size > Config.MAX_FILE_SIZE:
                bot.edit_message_text(
                    text="size greater than maximum allowed size (50MB). Neverthless, trying to upload.",
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
                if file_size > Config.TG_MAX_FILE_SIZE:
                    bot.edit_message_text(
                        text="Sorry. But, I cannot upload files greater than 1.5GB due to telegram API limitations. ",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
                else:
                    return_response = DoUpload(
                        query.message.chat_id,
                        download_directory,
                        description,
                        thumb_image_path,
                        query.message.reply_to_message.message_id
                    )
                    os.remove(thumb_image_path)
                    os.remove(download_directory)
                    bot.delete_message(
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id
                    )
            else:
                # try to upload file
                if download_directory.endswith("mp3"):
                    bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=open(download_directory, 'rb'),
                        caption=description,
                        duration=response_json["duration"],
                        performer=response_json["uploader"],
                        title=response_json["title"],
                        reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to=query.message.reply_to_message.message_id
                    )
                elif download_directory.endswith("mp4"):
                    bot.send_video(
                        chat_id=query.message.chat_id,
                        video=open(download_directory, 'rb'),
                        caption=description,
                        # duration=response_json["duration"],
                        # width=response_json["width"],
                        # height=response_json["height"],
                        supports_streaming=True,
                        reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to=query.message.reply_to_message.message_id
                    )
                else:
                    bot.send_document(
                        chat_id=query.message.chat_id,
                        document=open(download_directory, 'rb'),
                        caption=description,
                        reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to=query.message.reply_to_message.message_id
                    )
                os.remove(download_directory)
                os.remove(thumb_image_path)
                bot.delete_message(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
    else:
        bot.edit_message_text(
            text=Translation.ABS_TEXT,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )


def DoUpload(chat_id, video_file, caption, thumb_image, message_id):
    metadata = extractMetadata(createParser(video_file))
    client.send_file(
        chat_id,
        file=video_file,
        caption=caption,
        force_document=False,
        thumb=thumb_image,
        reply_to=message_id,
        allow_cache=False,
        attributes=[
            DocumentAttributeVideo(
                duration=metadata.get("duration").seconds,
                w=metadata.get("width"),
                h=metadata.get("height"),
                round_message=False,
                supports_streaming=True
            )
        ]
    )



if __name__ == "__main__" :
    # create download directory, if not exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=Config.TG_BOT_TOKEN)
    client = TelegramClient(
        Config.TL_SESSION,
        Config.APP_ID,
        Config.API_HASH
    )
    client.connect()
    if not client.is_user_authorized():
        # https://github.com/LonamiWebs/Telethon/issues/36#issuecomment-287735063
        client.sign_in(bot_token=Config.TG_BOT_TOKEN)
    me = client.get_me()
    logger.info(me.stringify())
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK), echo)
    dispatcher.add_handler(echo_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
