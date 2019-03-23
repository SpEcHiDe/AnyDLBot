#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
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
from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.help_Nekmo_ffmpeg import take_screen_shot, cult_small_video

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


@pyrogram.Client.on_message(pyrogram.Filters.command(["ffmpegrobot"]))
def ffmpegrobot_ad(bot, update):
    TRChatBase(update.from_user.id, update.text, "ffmpegrobot")
    bot.send_message(
        chat_id=update.chat.id,
        text=Translation.FF_MPEG_RO_BOT_AD_VER_TISE_MENT,
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.Filters.command(["trim"]))
def trim(bot, update):
    TRChatBase(update.from_user.id, update.text, "trim")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".FFMpegRoBot.mkv"
    if os.path.exists(saved_file_path):
        a = bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        commands = update.command
        if len(commands) == 3:
            # output should be video
            cmd, start_time, end_time = commands
            o = cult_small_video(saved_file_path, Config.DOWNLOAD_LOCATION, start_time, end_time)
            logger.info(o)
            if o is not None:
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.UPLOAD_START,
                    message_id=a.message_id
                )
                c_time = time.time()
                bot.send_video(
                    chat_id=update.chat.id,
                    video=o,
                    # caption=description,
                    # duration=duration,
                    # width=width,
                    # height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    # thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, a.message_id, update.chat.id, c_time
                    )
                )
                os.remove(o)
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    disable_web_page_preview=True,
                    message_id=a.message_id
                )
        elif len(commands) == 2:
            # output should be screenshot
            cmd, start_time = commands
            o = take_screen_shot(saved_file_path, Config.DOWNLOAD_LOCATION, start_time)
            logger.info(o)
            if o is not None:
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.UPLOAD_START,
                    message_id=a.message_id
                )
                c_time = time.time()
                bot.send_document(
                    chat_id=update.chat.id,
                    document=o,
                    # thumb=thumb_image_path,
                    # caption=description,
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, a.message_id, update.chat.id, c_time
                    )
                )
                c_time = time.time()
                bot.send_photo(
                    chat_id=update.chat.id,
                    photo=o,
                    # caption=Translation.CUSTOM_CAPTION_UL_FILE,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START, a.message_id, update.chat.id, c_time
                    )
                )
                os.remove(o)
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    disable_web_page_preview=True,
                    message_id=a.message_id
                )
        else:
            bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.FF_MPEG_RO_BOT_RE_SURRECT_ED,
                message_id=a.message_id
            )
    else:
        # reply help message
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FF_MPEG_RO_BOT_STEP_TWO_TO_ONE,
            reply_to_message_id=update.message_id
        )


@pyrogram.Client.on_message(pyrogram.Filters.command(["storageinfo"]))
def storage_info(bot, update):
    TRChatBase(update.from_user.id, update.text, "storageinfo")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".FFMpegRoBot.mkv"
    if os.path.exists(saved_file_path):
        metadata = extractMetadata(createParser(saved_file_path))
        duration = None
        if metadata.has("duration"):
            duration = metadata.get('duration')
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FF_MPEG_RO_BOT_STOR_AGE_INFO.format(duration),
            reply_to_message_id=update.message_id
        )
    else:
        # reply help message
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FF_MPEG_RO_BOT_STEP_TWO_TO_ONE,
            reply_to_message_id=update.message_id
        )


@pyrogram.Client.on_message(pyrogram.Filters.command(["clearffmpegmedia"]))
def clear_media(bot, update):
    TRChatBase(update.from_user.id, update.text, "clearffmpegmedia")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".FFMpegRoBot.mkv"
    if os.path.exists(saved_file_path):
        os.remove(saved_file_path)
    bot.send_message(
        chat_id=update.chat.id,
        text=Translation.FF_MPEG_DEL_ETED_CUSTOM_MEDIA,
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.Filters.command(["downloadmedia"]))
def download_media(bot, update):
    TRChatBase(update.from_user.id, update.text, "downloadmedia")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".FFMpegRoBot.mkv"
    if not os.path.exists(saved_file_path):
        a = bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        try:
            c_time = time.time()
            bot.download_media(
                message=update.reply_to_message,
                file_name=saved_file_path,
                progress=progress_for_pyrogram,
                progress_args=(Translation.DOWNLOAD_START, a.message_id, update.chat.id, c_time)
            )
        except (ValueError) as e:
            bot.edit_message_text(
                chat_id=update.chat.id,
                text=str(e),
                message_id=a.message_id
            )
        else:
            bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.SAVED_RECVD_DOC_FILE,
                message_id=a.message_id
            )
    else:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FF_MPEG_RO_BOT_STOR_AGE_ALREADY_EXISTS,
            reply_to_message_id=update.message_id
        )
