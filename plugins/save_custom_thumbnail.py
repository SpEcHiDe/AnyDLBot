#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

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


@pyrogram.Client.on_message(pyrogram.Filters.photo & pyrogram.Filters.private)
def save_photo(bot, update):
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
