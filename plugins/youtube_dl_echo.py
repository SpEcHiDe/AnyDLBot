#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import json
import math
import os
import requests
import subprocess
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from sample_config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import humanbytes
from helper_funcs.help_uploadbot import DownLoadFile


@pyrogram.Client.on_message(pyrogram.Filters.regex(pattern=".*http.*"))
def echo(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/echo")
    # bot.send_chat_action(
    #     chat_id=update.chat.id,
    #     action="typing"
    # )
    if str(update.from_user.id) in Config.BANNED_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.ABUSIVE_USERS,
            reply_to_message_id=update.message_id,
            disable_web_page_preview=True,
            parse_mode=pyrogram.ParseMode.HTML
        )
        return
    logger.info(update.from_user)
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if url is not None:
            url = url.strip()
        if file_name is not None:
            file_name = file_name.strip()
        # https://stackoverflow.com/a/761825/4723940
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
        logger.info(url)
        logger.info(file_name)
    else:
        for entity in update.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]
    try:
        if ("hotstar.com" in url) and (Config.HTTP_PROXY != ""):
            command_to_exec = [
                "youtube-dl",
                "--no-warnings",
                "--youtube-skip-dash-manifest",
                "-j",
                url,
                "--proxy", Config.HTTP_PROXY
            ]
        else:
            command_to_exec = [
                "youtube-dl",
                "--no-warnings",
                "--youtube-skip-dash-manifest",
                "-j",
                url
            ]
        if youtube_dl_username is not None:
            command_to_exec.append("--username")
            command_to_exec.append(youtube_dl_username)
        if youtube_dl_password is not None:
            command_to_exec.append("--password")
            command_to_exec.append(youtube_dl_password)
        logger.info(command_to_exec)
        t_response = subprocess.check_output(
            command_to_exec, stderr=subprocess.STDOUT)
        # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
    except subprocess.CalledProcessError as exc:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = exc.output.decode("UTF-8").replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            reply_to_message_id=update.message_id,
            parse_mode=pyrogram.ParseMode.HTML,
            disable_web_page_preview=True
        )
    else:
        # logger.info(t_response)
        x_reponse = t_response.decode("UTF-8").strip()
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")
                approx_file_size = ""
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                cb_string_file = "{}|{}|{}".format(
                    "file", format_id, format_ext)
                if format_string is not None and not "audio only" in format_string:
                    ikeyboard = [
                        pyrogram.InlineKeyboardButton(
                            "S" + format_ext  + "Video [" + format_string +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        pyrogram.InlineKeyboardButton(
                           "D" + format_ext  + "File [" + format_string +
                           "]",
                           callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                    if duration is not None:
                        cb_string_video_message = "{}|{}|{}".format(
                            "vm", format_id, format_ext)
                        ikeyboard.append(
                            pyrogram.InlineKeyboardButton(
                                "VM",
                                callback_data=(
                                    cb_string_video_message).encode("UTF-8")
                            )
                        )
                else:
                    # special weird case :\
                    ikeyboard = [
                        pyrogram.InlineKeyboardButton(
                            "SVideo [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        pyrogram.InlineKeyboardButton(
                            "DFile [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton(
                        "MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                    pyrogram.InlineKeyboardButton(
                        "MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton(
                        "MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}|{}|{}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                pyrogram.InlineKeyboardButton(
                    "SVideo",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                pyrogram.InlineKeyboardButton(
                    "DFile",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
        reply_markup = pyrogram.InlineKeyboardMarkup(inline_keyboard)
        # logger.info(reply_markup)
        thumbnail = Config.DEF_THUMB_NAIL_VID_S
        thumbnail_image = Config.DEF_THUMB_NAIL_VID_S
        if "thumbnail" in response_json:
            if response_json["thumbnail"] is not None:
                thumbnail = response_json["thumbnail"]
                thumbnail_image = response_json["thumbnail"]
        thumb_image_path = DownLoadFile(
            thumbnail_image,
            Config.DOWNLOAD_LOCATION + "/" +
            str(update.from_user.id) + ".jpg",
            Config.CHUNK_SIZE,
            None,  # bot,
            Translation.DOWNLOAD_START,
            update.message_id,
            update.chat.id
        )
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            parse_mode=pyrogram.ParseMode.HTML,
            reply_to_message_id=update.message_id
        )
