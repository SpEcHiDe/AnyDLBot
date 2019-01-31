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
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes
from helper_funcs.help_uploadbot import DownLoadFile, DetectFileSize

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_message(pyrogram.Filters.regex(pattern=".*http.*"))
def echo(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/echo")
    # bot.send_chat_action(
    #     chat_id=update.chat.id,
    #     action="typing"
    # )
    logger.info(update.from_user)
    if str(update.from_user.id) in Config.BANNED_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.ABUSIVE_USERS,
            reply_to_message_id=update.message_id,
            disable_web_page_preview=True,
            parse_mode=pyrogram.ParseMode.HTML
        )
        return
    url = update.text
    if "http" in url:
        if "|" in url:
            url, file_name = url.split("|")
            url = url.strip()
            # https://stackoverflow.com/a/761825/4723940
            file_name = file_name.strip()
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
            logger.info(command_to_exec)
            t_response = subprocess.check_output(
                command_to_exec, stderr=subprocess.STDOUT)
            # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
        except subprocess.CalledProcessError as exc:
            # print("Status : FAIL", exc.returncode, exc.output)
            bot.send_message(
                chat_id=update.chat.id,
                text=exc.output.decode("UTF-8"),
                reply_to_message_id=update.message_id
            )
        else:
            # logger.info(t_response)
            x_reponse = t_response.decode("UTF-8")
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
                                "S" + format_ext + "Video [" + format_string +
                                "] ( " +
                                approx_file_size + " )",
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            pyrogram.InlineKeyboardButton(
                                "D" + format_ext  + "File [" + format_string +
                                "] ( " +
                                approx_file_size + " )",
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]
                        if duration is not None and duration <= 30:
                            cb_string_video_message = "{}|{}|{}".format(
                                "vm", format_id, format_ext)
                            ikeyboard.append(
                                pyrogram.InlineKeyboardButton(
                                    "VMessage [" + format_string +
                                    "] ( " +
                                    approx_file_size + " )",
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
                tg_send_type = "file"
                if duration is not None:
                    tg_send_type = "video"
                cb_string = "{}|{}|{}".format(
                    tg_send_type, format_id, format_ext)
                inline_keyboard.append([
                    pyrogram.InlineKeyboardButton(
                        "unknown format", callback_data=cb_string.encode("UTF-8"))
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
                text=Translation.FORMAT_SELECTION.format(thumbnail),
                reply_markup=reply_markup,
                parse_mode=pyrogram.ParseMode.HTML,
                reply_to_message_id=update.message_id
            )
    else:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.INVALID_UPLOAD_BOT_URL_FORMAT,
            reply_to_message_id=update.message_id
        )


@pyrogram.Client.on_callback_query()
def button(bot, update):
    # logger.info(update)
    if str(update.from_user.id) in Config.BANNED_USERS:
        bot.edit_message_text(
            chat_id=update.message.chat.id,
            text=Translation.ABUSIVE_USERS,
            message_id=update.message.message_id,
            disable_web_page_preview=True,
            parse_mode=pyrogram.ParseMode.HTML
        )
        return
    cb_data = update.data.decode("UTF-8")
    if cb_data.find("|") == -1:
        return ""
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
    thumb_image_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".jpg"
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".json"
    try:
        with open(save_ytdl_json_path, "r") as f:
            response_json = json.load(f)
    except (FileNotFoundError) as e:
        bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.message_id,
            revoke=True
        )
        return False
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = str(response_json.get("title")) + \
        "_" + youtube_dl_format
    if "|" in youtube_dl_url:
        youtube_dl_url, custom_file_name = youtube_dl_url.split("|")
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    if (str(update.from_user.id) not in Config.UTUBE_BOT_USERS) and (("hls" in youtube_dl_format) or ("hotstar.com" in youtube_dl_url)):
        bot.edit_message_text(
            chat_id=update.message.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            message_id=update.message.message_id
        )
        return
    if "noyes.in" in youtube_dl_url:
        bot.edit_message_text(
            chat_id=update.message.chat.id,
            text=Translation.NOYES_URL,
            message_id=update.message.message_id
        )
        return
    bot.edit_message_text(
        text=Translation.DOWNLOAD_START,
        chat_id=update.message.chat.id,
        message_id=update.message.message_id
    )
    description = Translation.CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]
    if ("@" in custom_file_name) and (str(update.from_user.id) not in Config.UTUBE_BOT_USERS):
        bot.edit_message_text(
            chat_id=update.message.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            message_id=update.message.message_id
        )
        return
    download_directory = Config.DOWNLOAD_LOCATION + "/" + custom_file_name + "." + youtube_dl_ext + ""
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        download_directory_one = Config.DOWNLOAD_LOCATION + "/" + custom_file_name
        # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--embed-subs",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if "hotstar.com" in youtube_dl_url and Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    logger.info(command_to_exec)
    try:
        t_response = subprocess.check_output(
            command_to_exec, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        logger.info("Status : FAIL", exc.returncode, exc.output)
        bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.message_id,
            text=exc.output.decode("UTF-8")
        )
    else:
        # logger.info(t_response)
        os.remove(save_ytdl_json_path)
        bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id
        )
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = download_directory_one + "." + "mkv"
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.RCHD_TG_API_LIMIT,
                message_id=update.message.message_id
            )
        else:
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                img.thumbnail((90, 90))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            else:
                thumb_image_path = None
            # try to upload file
            if tg_send_type == "audio":
                bot.send_audio(
                    chat_id=update.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, update.message.message_id, update.message.chat.id)
                )
            elif tg_send_type == "file":
                bot.send_document(
                    chat_id=update.message.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, update.message.message_id, update.message.chat.id)
                )
            elif tg_send_type == "vm":
                bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, update.message.message_id, update.message.chat.id)
                )
            elif tg_send_type == "video":
                bot.send_video(
                    chat_id=update.message.chat.id,
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, update.message.message_id, update.message.chat.id)
                )
            else:
                logger.info("Did this happen? :\\")
            try:
                os.remove(download_directory)
                os.remove(thumb_image_path)
            except:
                pass
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                disable_web_page_preview=True
            )
