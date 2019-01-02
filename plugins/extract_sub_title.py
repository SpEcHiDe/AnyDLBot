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

from plugins.helper_funcs.chat_base import TRChatBase


def extractsubtitle(video_file, output_directory):
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".srt"
    command_to_execute = " ".join([
        "ffmpeg",
        "-i ", "\"" + video_file + "\"",
        out_put_file_name
    ])
    t_response = os.system(command_to_execute)
    return out_put_file_name


@pyrogram.Client.on_message(pyrogram.Filters.command(["extractsubtitle"]))
def extract_sub_title(bot, update):
    TRChatBase(update.from_user.id, update.text, "extract_sub_title")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    download_location = Config.DOWNLOAD_LOCATION + "/"
    if update.reply_to_message is not None:
        text = update.reply_to_message.text
        if text.startswith("http"):
            a = bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.UPLOAD_START,
                reply_to_message_id=update.message_id
            )
            sub_title_file_name = extractsubtitle(text, download_location)
            bot.send_document(
                chat_id=update.from_user.id,
                document=sub_title_file_name,
                # thumb=thumb_image_path,
                # caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id
            )
            os.remove(sub_title_file_name)
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
        else:
            bot.send_message(
                chat_id=update.from_user.id,
                text=Translation.REPLY_TO_DOC_OR_LINK_FOR_RARX_SRT,
                reply_to_message_id=update.message_id
            )
    else:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.REPLY_TO_DOC_OR_LINK_FOR_RARX_SRT,
            reply_to_message_id=update.message_id
        )
