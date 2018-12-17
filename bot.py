#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import subprocess
import math
import requests
import os
import json

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

# https://stackoverflow.com/a/37631799/4723940
from PIL import Image

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
# the Strings used for this "thing"
from translation import Translation

# the Telegram trackings
from chatbase import Message


def TRChatBase(chat_id, message_text, intent):
    msg = Message(api_key=Config.CHAT_BASE_TOKEN,
              platform="Telegram",
              version="1.3",
              user_id=chat_id,
              message=message_text,
              intent=intent)
    resp = msg.send()


import pyrogram


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
    # TRChatBase(update.from_user.id, update.text, "error")
    logger.warning('Update "%s" caused error "%s"', update, error)


def start(bot, update):
    logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/start")
    bot.send_message(
        chat_id=update.from_user.id,
        text=Translation.START_TEXT,
        reply_to_message_id=update.message_id
    )


def save_photo(bot, update):
    logger.info(update)
    TRChatBase(update.from_user.id, update.text, "save_photo")
    download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    bot.download_media(
        message=update,
        file_name=download_location
    )
    bot.send_message(
        chat_id=update.from_user.id,
        text=Translation.SAVED_CUSTOM_THUMB_NAIL,
        reply_to_message_id=update.message_id
    )


def echo(bot, update):
    logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/echo")
    if str(update.from_user.id) not in Config.AUTH_USERS:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    bot.send_chat_action(
        chat_id=update.from_user.id,
        action="typing"
    )
    text = update.text
    if(text.startswith("http")):
        url = text
        # logger = "<a href='" + url + "'>url</a> by <a href='tg://user?id=" + str(update.from_user.id) + "'>" + str(update.from_user.id) + "</a>"
        # bot.send_message(chat_id=-1001364708459, text=logger, parse_mode="HTML")
        if "noyes.in" not in url:
            try:
                command_to_exec = ["youtube-dl", "--no-warnings", "-j", url]
                logger.info(command_to_exec)
                t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
                # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
            except subprocess.CalledProcessError as exc:
                # print("Status : FAIL", exc.returncode, exc.output)
                bot.send_message(
                    chat_id=update.from_user.id,
                    text=exc.output.decode("UTF-8"),
                    reply_to_message_id=update.message_id
                )
            else:
                logger.info(t_response)
                x_reponse = t_response.decode("UTF-8")
                response_json = json.loads(x_reponse)
                logger.info(response_json)
                inline_keyboard = []
                for formats in response_json["formats"]:
                    format_id = formats["format_id"]
                    format_string = formats["format"]
                    format_ext = formats["ext"]
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    ikeyboard = [
                        pyrogram.InlineKeyboardButton(
                            "[" + format_string + "] (" + format_ext + " - " + approx_file_size + ")",
                            callback_data=(format_id + ":" + format_ext).encode("UTF-8")
                        )
                    ]
                    inline_keyboard.append(ikeyboard)
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton("MP3 " + "(" + "medium" + ")", callback_data="5:mp3".encode("UTF-8"))
                ])
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton("MP3 " + "(" + "best" + ")", callback_data="0:mp3".encode("UTF-8"))
                ])
                reply_markup = pyrogram.InlineKeyboardMarkup(inline_keyboard)
                logger.info(reply_markup)
                thumbnail = "https://placehold.it/50x50"
                if "thumbnail" in response_json:
                    thumbnail = response_json["thumbnail"]
                thumbnail_image = "https://placehold.it/50x50"
                if "thumbnail" in response_json:
                    response_json["thumbnail"]
                thumb_image_path = DownLoadFile(thumbnail_image, Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg")
                bot.send_message(
                    chat_id=update.from_user.id,
                    text=Translation.FORMAT_SELECTION.format(thumbnail),
                    reply_markup=reply_markup,
                    parse_mode=pyrogram.ParseMode.HTML,
                    reply_to_message_id=update.message_id
                )
        else:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.NOYES_URL,
                reply_to_message_id=update.message_id
            )
    else:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.START_TEXT,
            reply_to_message_id=update.message_id
        )


def button(bot, update):
    logger.info(update)
    if str(update.from_user.id) not in Config.AUTH_USERS:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    if update.data.find(":") == -1:
        return ""
    youtube_dl_format, youtube_dl_ext = update.data.split(":")
    youtube_dl_url = update.message.reply_to_message.text
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    bot.edit_message_text(
        text=Translation.DOWNLOAD_START,
        chat_id=update.from_user.id,
        message_id=update.message.message_id
    )
    description = " " + " \r\n© @AnyDLBot"
    download_directory = ""
    command_to_exec = []
    if "mp3" in youtube_dl_ext:
        download_directory = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "_" + youtube_dl_format + "." + youtube_dl_ext + ""
        command_to_exec = [
            "youtube-dl",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        download_directory = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "_" + youtube_dl_format + "." + youtube_dl_ext + ".mp4"
        # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        command_to_exec = [
            "youtube-dl",
            "--embed-subs",
            "-f", youtube_dl_format,
            "--recode-video", "mp4", "-k",
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    logger.info(command_to_exec)
    try:
        t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        # print("Status : FAIL", exc.returncode, exc.output)
        bot.edit_message_text(
            chat_id=update.from_user.id,
            message_id=update.message.message_id,
            text=exc.output.decode("UTF-8"),
            # reply_markup=reply_markup
        )
    else:
        logger.info(t_response)
        bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.from_user.id,
            message_id=update.message.message_id
        )
        file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            bot.edit_message_text(
                text=Translation.RCHD_TG_API_LIMIT,
                chat_id=update.from_user.id,
                message_id=update.message.message_id
            )
        else:
            # resize image
            # ref: https://t.me/PyrogramChat/44663
            # https://stackoverflow.com/a/21669827/4723940
            Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
            img = Image.open(thumb_image_path)
            # https://stackoverflow.com/a/37631799/4723940
            new_img = img.resize((90, 90))
            new_img.save(thumb_image_path + ".jpg", "JPEG", optimize=True)
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            metadata = extractMetadata(createParser(download_directory))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            metadata = extractMetadata(createParser(thumb_image_path + ".jpg"))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
            # get the correct width, height, and duration for videos greater than 10MB
            # try to upload file
            if download_directory.endswith("mp3"):
                bot.send_audio(
                    chat_id=update.from_user.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path + ".jpg",
                    reply_to_message_id=update.message.reply_to_message.message_id
                )
            else:
                bot.send_video(
                    chat_id=update.from_user.id,
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path + ".jpg",
                    reply_to_message_id=update.message.reply_to_message.message_id
                )
            """else:
                bot.send_document(
                    chat_id=update.from_user.id,
                    document=download_directory,
                    caption=description,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path + ".jpg",
                    reply_to_message_id=update.message.reply_to_message.message_id
                )"""
            os.remove(download_directory)
            os.remove(thumb_image_path)
            os.remove(thumb_image_path + ".jpg")
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=update.message.message_id,
                disable_web_page_preview=True
            )


if __name__ == "__main__" :
    # create download directory, if not exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    app = pyrogram.Client(
        session_name=Config.TG_BOT_TOKEN,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH
    )
    app.add_handler(pyrogram.MessageHandler(start, pyrogram.Filters.command(["start"])))
    app.add_handler(pyrogram.MessageHandler(echo, pyrogram.Filters.text))
    app.add_handler(pyrogram.MessageHandler(save_photo, pyrogram.Filters.photo))
    app.add_handler(pyrogram.CallbackQueryHandler(button))
    app.run()
