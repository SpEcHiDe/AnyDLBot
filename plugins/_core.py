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

from plugins.helper_funcs.chat_base import TRChatBase

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


def DownLoadFile(url, file_name):
    if not os.path.exists(file_name):
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
                fd.write(chunk)
    return file_name


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(math.floor(size)) + " " + Dic_powerN[n] + 'B'


def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".png"
    command_to_execute = " ".join([
        "ffmpeg",
        "-i ", "\"" + video_file + "\"",
        "-ss", ttl,
        " -vframes", "1",
        out_put_file_name
    ])
    # https://stackoverflow.com/a/42592614/4723940
    t_response = os.system(command_to_execute)
    return out_put_file_name


def cult_small_video(video_file, output_directory, start_time, end_time):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".mp4"
    command_to_execute = " ".join([
        "ffmpeg",
        "-i ", "\"" + video_file + "\"",
        "-ss", start_time,
        "-to", end_time,
        # "-strict experimental",
        # "-async 1 -strict -2",
        "-c copy",
        out_put_file_name
    ])
    # https://stackoverflow.com/a/42592614/4723940
    t_response = os.system(command_to_execute)
    return out_put_file_name


@pyrogram.Client.on_message(pyrogram.Filters.text & pyrogram.Filters.private, group=1)
def echo(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/echo")
    bot.send_chat_action(
        chat_id=update.from_user.id,
        action="typing"
    )
    text = update.text
    if(text.startswith("http")):
        url = text
        if "|" in url:
            if str(update.from_user.id) not in Config.SUPER_DLBOT_USERS:
                bot.send_message(
                    chat_id=update.from_user.id,
                    text=Translation.NOT_AUTH_USER_TEXT,
                    reply_to_message_id=update.message_id
                )
                return
            thumb_image_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
            else:
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                new_img = img.resize((90, 90))
                new_img.save(thumb_image_path, "JPEG", optimize=True)
            url, file_name = url.split("|")
            url = url.strip()
            # https://stackoverflow.com/a/761825/4723940
            file_name = file_name.strip()
            logger.info(url)
            logger.info(file_name)
            a = bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.DOWNLOAD_START,
                reply_to_message_id=update.message_id
            )
            after_download_path = DownLoadFile(
                url, Config.DOWNLOAD_LOCATION + "/" + file_name)
            description = Translation.CUSTOM_CAPTION_UL_FILE
            bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            file_size = os.stat(after_download_path).st_size
            if file_size > Config.TG_MAX_FILE_SIZE:
                bot.edit_message_text(
                    text=Translation.RCHD_TG_API_LIMIT,
                    chat_id=update.from_user.id,
                    message_id=a.message_id
                )
            else:
                # try to upload file
                bot.send_document(
                    chat_id=update.from_user.id,
                    document=after_download_path,
                    caption=description,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id
                )
                bot.edit_message_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    chat_id=update.from_user.id,
                    message_id=a.message_id,
                    disable_web_page_preview=True
                )
            try:
                os.remove(after_download_path)
                os.remove(thumb_image_path)
            except:
                pass
        else:
            try:
                if "hotstar.com" in url:
                    command_to_exec = [
                        "youtube-dl", "--no-warnings", "-j", url, "--proxy", Config.HTTP_PROXY]
                else:
                    command_to_exec = ["youtube-dl",
                                       "--no-warnings", "-j", url]
                logger.info(command_to_exec)
                t_response = subprocess.check_output(
                    command_to_exec, stderr=subprocess.STDOUT)
                # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
            except subprocess.CalledProcessError as exc:
                # print("Status : FAIL", exc.returncode, exc.output)
                bot.send_message(
                    chat_id=update.from_user.id,
                    text=exc.output.decode("UTF-8"),
                    reply_to_message_id=update.message_id
                )
            else:
                # logger.info(t_response)
                x_reponse = t_response.decode("UTF-8")
                response_json = json.loads(x_reponse)
                # logger.info(response_json)
                inline_keyboard = []
                if "formats" in response_json:
                    for formats in response_json["formats"]:
                        format_id = formats["format_id"]
                        format_string = formats["format"]
                        format_ext = formats["ext"]
                        approx_file_size = ""
                        if "filesize" in formats:
                            approx_file_size = humanbytes(formats["filesize"])
                        cb_string = "{}|{}|{}".format(
                            "video", format_id, format_ext)
                        if not "audio only" in format_string:
                            ikeyboard = [
                                pyrogram.InlineKeyboardButton(
                                    "[" + format_string +
                                    "] (" + format_ext + " - " +
                                    approx_file_size + ")",
                                    callback_data=(cb_string).encode("UTF-8")
                                )
                            ]
                            inline_keyboard.append(ikeyboard)
                    cb_string = "{}|{}|{}".format("audio", "5", "mp3")
                    inline_keyboard.append([
                        pyrogram.InlineKeyboardButton(
                            "MP3 " + "(" + "medium" + ")", callback_data=cb_string.encode("UTF-8"))
                    ])
                    cb_string = "{}|{}|{}".format("audio", "0", "mp3")
                    inline_keyboard.append([
                        pyrogram.InlineKeyboardButton(
                            "MP3 " + "(" + "best" + ")", callback_data=cb_string.encode("UTF-8"))
                    ])
                else:
                    format_id = response_json["format_id"]
                    format_ext = response_json["ext"]
                    cb_string = "{}|{}|{}".format(
                        "file", format_id, format_ext)
                    inline_keyboard.append([
                        pyrogram.InlineKeyboardButton(
                            "unknown video format", callback_data=cb_string.encode("UTF-8"))
                    ])
                reply_markup = pyrogram.InlineKeyboardMarkup(inline_keyboard)
                logger.info(reply_markup)
                thumbnail = Config.DEF_THUMB_NAIL_VID_S
                thumbnail_image = Config.DEF_THUMB_NAIL_VID_S
                if "thumbnail" in response_json:
                    thumbnail = response_json["thumbnail"]
                    thumbnail_image = response_json["thumbnail"]
                thumb_image_path = DownLoadFile(
                    thumbnail_image, Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg")
                bot.send_message(
                    chat_id=update.from_user.id,
                    text=Translation.FORMAT_SELECTION.format(thumbnail),
                    reply_markup=reply_markup,
                    parse_mode=pyrogram.ParseMode.HTML,
                    reply_to_message_id=update.message_id
                )
    elif "===" in text:
        logger.info("cult_small_video")
        if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.NOT_AUTH_USER_TEXT,
                reply_to_message_id=update.message_id
            )
            return
        if update.reply_to_message is not None:
            a = bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.DOWNLOAD_START,
                reply_to_message_id=update.message_id
            )
            url = update.reply_to_message.text
            for entity in update.reply_to_message.entities:
                if entity.type == "text_link":
                    url = entity.url
            start_time, end_time = text.split("===")
            mp4_file = cult_small_video(
                url, Config.DOWNLOAD_LOCATION, start_time, end_time)
            bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            thumb_image_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".jpg"
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            metadata = extractMetadata(createParser(mp4_file))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
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
                new_img = img.resize((90, 90))
                new_img.save(thumb_image_path, "JPEG", optimize=True)
            else:
                thumb_image_path = None
            # try to upload file
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            bot.send_video(
                chat_id=update.from_user.id,
                video=mp4_file,
                # caption=description,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                # reply_markup=reply_markup,
                thumb=thumb_image_path,
                reply_to_message_id=update.reply_to_message.message_id
            )
            os.remove(mp4_file)
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
        else:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.START_TEXT,
                reply_to_message_id=update.message_id
            )
    elif ":" in text:
        logger.info("take_screen_shot")
        if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.FF_MPEG_RO_BOT_RE_SURRECT_ED,
                reply_to_message_id=update.message_id
            )
            return
        if update.reply_to_message is not None:
            a = bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.DOWNLOAD_START,
                reply_to_message_id=update.message_id
            )
            url = update.reply_to_message.text
            for entity in update.reply_to_message.entities:
                if entity.type == "text_link":
                    url = entity.url
            img_file = take_screen_shot(url, Config.DOWNLOAD_LOCATION, text)
            # try to upload file
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            bot.send_document(
                chat_id=update.from_user.id,
                document=img_file,
                # caption=description,
                # reply_markup=reply_markup,
                # thumb=thumb_image_path,
                reply_to_message_id=update.message_id
            )
            bot.send_photo(
                chat_id=update.from_user.id,
                photo=img_file,
                # caption=description,
                # reply_markup=reply_markup,
                # thumb=thumb_image_path,
                reply_to_message_id=update.message_id
            )
            os.remove(img_file)
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
        else:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.FF_MPEG_RO_BOT_RE_SURRECT_ED,
                reply_to_message_id=update.message_id
            )


@pyrogram.Client.on_callback_query()
def button(bot, update):
    # logger.info(update)
    cb_data = update.data.decode("UTF-8")
    if cb_data.find("|") == -1:
        return ""
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
    youtube_dl_url = update.message.reply_to_message.text
    if (str(update.from_user.id) not in Config.UTUBE_BOT_USERS) and (("hls" in youtube_dl_format) or ("hotstar.com" in youtube_dl_url)):
        bot.edit_message_text(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            message_id=update.message.message_id
        )
        return
    thumb_image_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".jpg"
    bot.edit_message_text(
        text=Translation.DOWNLOAD_START,
        chat_id=update.from_user.id,
        message_id=update.message.message_id
    )
    description = Translation.CUSTOM_CAPTION_UL_FILE
    download_directory = ""
    command_to_exec = []
    if tg_send_type == "audio":
        download_directory = Config.DOWNLOAD_LOCATION + "/" + \
            str(update.from_user.id) + "_" + \
            youtube_dl_format + "." + youtube_dl_ext + ""
        command_to_exec = [
            "youtube-dl",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        download_directory = Config.DOWNLOAD_LOCATION + "/" + \
            str(update.from_user.id) + "_" + \
            youtube_dl_format + "." + youtube_dl_ext
        # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        command_to_exec = [
            "youtube-dl",
            "--embed-subs",
            "-f", youtube_dl_format,
            "-k",
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if "hotstar.com" in youtube_dl_url:
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    logger.info(command_to_exec)
    try:
        t_response = subprocess.check_output(
            command_to_exec, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        logger.info("Status : FAIL", exc.returncode, exc.output)
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
            url = "https://transfer.sh/{}".format(download_directory)
            max_days = "5"
            command_to_exec = [
                "curl",
                # "-H", 'Max-Downloads: 1',
                "-H", 'Max-Days: 5',  # + max_days + '',
                "--upload-file", download_directory,
                url
            ]
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            try:
                logger.info(command_to_exec)
                t_response = subprocess.check_output(
                    command_to_exec, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                logger.info("Status : FAIL", exc.returncode, exc.output)
                bot.edit_message_text(
                    chat_id=update.from_user.id,
                    text=exc.output.decode("UTF-8"),
                    message_id=a.message_id
                )
            else:
                t_response_arry = t_response.decode(
                    "UTF-8").split("\n")[-1].strip()
                bot.edit_message_text(
                    chat_id=update.from_user.id,
                    text=Translation.AFTER_GET_DL_LINK.format(
                        t_response_arry, max_days),
                    parse_mode=pyrogram.ParseMode.HTML,
                    message_id=a.message_id,
                    disable_web_page_preview=True
                )
                try:
                    os.remove(after_download_file_name)
                except:
                    pass
        else:
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            metadata = extractMetadata(createParser(download_directory))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            metadata = extractMetadata(createParser(thumb_image_path))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                new_img = img.resize((90, 90))
                new_img.save(thumb_image_path, "JPEG", optimize=True)
            else:
                thumb_image_path = None
            # try to upload file
            if tg_send_type == "audio":
                bot.send_audio(
                    chat_id=update.from_user.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id
                )
            elif tg_send_type == "file":
                bot.send_document(
                    chat_id=update.from_user.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    # reply_markup=reply_markup,
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
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id
                )
            try:
                os.remove(download_directory)
                os.remove(thumb_image_path)
            except:
                pass
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=update.message.message_id,
                disable_web_page_preview=True
            )
