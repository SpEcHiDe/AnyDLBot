#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime
import json
import math
import os
import requests
import shutil
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
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from pydrive.drive import GoogleDrive


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
    if ":" in cb_data:
        # unzip formats
        extract_dir_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + "zipped" + "/"
        if not os.path.isdir(extract_dir_path):
            bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.message_id,
                revoke=True
            )
            return False
        zip_file_contents = os.listdir(extract_dir_path)
        type_of_extract, index_extractor, undefined_tcartxe = cb_data.split(":")
        if index_extractor == "NONE":
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.CANCEL_STR,
                message_id=update.message.message_id
            )
        elif index_extractor == "ALL":
            i = 0
            for file_content in zip_file_contents:
                current_file_name = os.path.join(extract_dir_path, file_content)
                start_time = time.time()
                bot.send_document(
                    chat_id=update.message.chat.id,
                    document=current_file_name,
                    # thumb=thumb_image_path,
                    caption=file_content,
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message.message_id,
                        update.message.chat.id,
                        start_time
                    )
                )
                i = i + 1
                os.remove(current_file_name)
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.ZIP_UPLOADED_STR.format(i, "0"),
                message_id=update.message.message_id
            )
        else:
            file_content = zip_file_contents[int(index_extractor)]
            current_file_name = os.path.join(extract_dir_path, file_content)
            start_time = time.time()
            bot.send_document(
                chat_id=update.message.chat.id,
                document=current_file_name,
                # thumb=thumb_image_path,
                caption=file_content,
                # reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update.message.message_id,
                    update.message.chat.id,
                    start_time
                )
            )
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.ZIP_UPLOADED_STR.format("1", "0"),
                message_id=update.message.message_id
            )
    elif "|" in cb_data:
        # youtube_dl extractors
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
        thumb_image_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".jpg"
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        try:
            with open(save_ytdl_json_path, "r", encoding="utf8") as f:
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
            "_" + youtube_dl_format + "." + youtube_dl_ext
        youtube_dl_username = None
        youtube_dl_password = None
        if "|" in youtube_dl_url:
            url_parts = youtube_dl_url.split("|")
            if len(url_parts) == 2:
                youtube_dl_url = url_parts[0]
                custom_file_name = url_parts[1]
            elif len(url_parts) == 4:
                youtube_dl_url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]
            else:
                for entity in update.message.reply_to_message.entities:
                    if entity.type == "text_link":
                        youtube_dl_url = entity.url
                    elif entity.type == "url":
                        o = entity.offset
                        l = entity.length
                        youtube_dl_url = youtube_dl_url[o:o + l]
            if youtube_dl_url is not None:
                youtube_dl_url = youtube_dl_url.strip()
            if custom_file_name is not None:
                custom_file_name = custom_file_name.strip()
            # https://stackoverflow.com/a/761825/4723940
            if youtube_dl_username is not None:
                youtube_dl_username = youtube_dl_username.strip()
            if youtube_dl_password is not None:
                youtube_dl_password = youtube_dl_password.strip()
            logger.info(youtube_dl_url)
            logger.info(custom_file_name)
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
        download_directory = Config.DOWNLOAD_LOCATION + "/" + custom_file_name
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
        if youtube_dl_username is not None:
            command_to_exec.append("--username")
            command_to_exec.append(youtube_dl_username)
        if youtube_dl_password is not None:
            command_to_exec.append("--password")
            command_to_exec.append(youtube_dl_password)
        logger.info(command_to_exec)
        start = datetime.now()
        try:
            t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT, timeout=Config.PROCESS_MAX_TIMEOUT)
        except subprocess.CalledProcessError as exc:
            logger.warn("Status : FAIL", exc.returncode, exc.output)
            error_message = exc.output.decode("UTF-8").replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=error_message
            )
        except subprocess.TimeoutExpired as exc:
            error_message = Translation.SLOW_URL_DECED
            bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=error_message
            )
        else:
            # logger.info(t_response)
            os.remove(save_ytdl_json_path)
            end_one = datetime.now()
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            file_size = Config.TG_MAX_FILE_SIZE + 1
            try:
                file_size = os.stat(download_directory).st_size
            except FileNotFoundError as exc:
                download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
                # https://stackoverflow.com/a/678242/4723940
                file_size = os.stat(download_directory).st_size
            if file_size > Config.TG_MAX_FILE_SIZE:
                time_taken_for_download = (end_one -start).seconds
                if str(update.from_user.id) in Config.G_DRIVE_AUTH_DRQ:
                    gauth = Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)]
                    # Create GoogleDrive instance with authenticated GoogleAuth instance.
                    drive = GoogleDrive(gauth)
                    file_inance = drive.CreateFile()
                    # Read file and set it as a content of this instance.
                    file_inance.SetContentFile(download_directory)
                    file_inance.Upload() # Upload the file.
                    end_two = datetime.now()
                    time_taken_for_upload = (end_two - end_one).seconds
                    bot.edit_message_text(
                        text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                        chat_id=update.message.chat.id,
                        message_id=update.message.message_id,
                        disable_web_page_preview=True
                    )
                else:
                    bot.edit_message_text(
                        chat_id=update.message.chat.id,
                        text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
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
                    if metadata is not None:
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
                    if tg_send_type == "vm":
                        height = width
                    # resize image
                    # ref: https://t.me/PyrogramChat/44663
                    # https://stackoverflow.com/a/21669827/4723940
                    Image.open(thumb_image_path).convert(
                        "RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    # https://stackoverflow.com/a/37631799/4723940
                    # img.thumbnail((90, 90))
                    img.resize((90, height))
                    img.save(thumb_image_path, "JPEG")
                    # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
                else:
                    thumb_image_path = None
                start_time = time.time()
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
                            Translation.UPLOAD_START,
                            update.message.message_id,
                            update.message.chat.id,
                            start_time
                        )
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
                            Translation.UPLOAD_START,
                            update.message.message_id,
                            update.message.chat.id,
                            start_time
                        )
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
                            Translation.UPLOAD_START,
                            update.message.message_id,
                            update.message.chat.id,
                            start_time
                        )
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
                            Translation.UPLOAD_START,
                            update.message.message_id,
                            update.message.chat.id,
                            start_time
                        )
                    )
                else:
                    logger.info("Did this happen? :\\")
                end_two = datetime.now()
                try:
                    os.remove(download_directory)
                    os.remove(thumb_image_path)
                except:
                    pass
                time_taken_for_download = (end_one -start).seconds
                time_taken_for_upload = (end_two - end_one).seconds
                bot.edit_message_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )
