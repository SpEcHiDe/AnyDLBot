#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import subprocess

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


@pyrogram.Client.on_message(pyrogram.Filters.command(["getlink"]))
def get_link(bot, update):
    TRChatBase(update.from_user.id, update.text, "getlink")
    if str(update.from_user.id) not in Config.SUPER3X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    if update.reply_to_message is not None:
        reply_message = update.reply_to_message
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        after_download_file_name = bot.download_media(
            message=reply_message,
            file_name=download_location
        )
        download_extension = after_download_file_name.rsplit(".", 1)[-1]
        bot.edit_message_text(
            text=Translation.SAVED_RECVD_DOC_FILE,
            chat_id=update.from_user.id,
            message_id=a.message_id
        )
        url = "https://transfer.sh/{}.{}".format(str(update.from_user.id), str(download_extension))
        max_days = "5"
        command_to_exec = [
            "curl",
            # "-H", 'Max-Downloads: 1',
            "-H", 'Max-Days: 5', # + max_days + '',
            "--upload-file", after_download_file_name,
            url
        ]
        bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.from_user.id,
            message_id=a.message_id
        )
        try:
            logger.info(command_to_exec)
            t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logger.info("Status : FAIL", exc.returncode, exc.output)
            bot.edit_message_text(
                chat_id=update.from_user.id,
                text=exc.output.decode("UTF-8"),
                message_id=a.message_id
            )
        else:
            t_response_arry = t_response.decode("UTF-8").split("\n")[-1].strip()
            bot.edit_message_text(
                chat_id=update.from_user.id,
                text=Translation.AFTER_GET_DL_LINK.format(t_response_arry, max_days),
                parse_mode=pyrogram.ParseMode.HTML,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
            try:
                os.remove(after_download_file_name)
            except:
                pass
    else:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.REPLY_TO_DOC_GET_LINK,
            reply_to_message_id=update.message_id
        )
