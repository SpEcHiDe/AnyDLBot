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

# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_message(pyrogram.Filters.command(["rename"]))
def rename_doc(bot, update):
    TRChatBase(update.from_user.id, update.text, "rename")
    if str(update.from_user.id) not in Config.SUPER3X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    if (" " in update.text) and (update.reply_to_message is not None):
        cmd, file_name = update.text.split(" ", 1)
        description = Translation.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        the_real_download_location = bot.download_media(
            message=update.reply_to_message,
            file_name=download_location
        )
        if the_real_download_location is not None:
            bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            if "IndianMovie" in the_real_download_location:
                bot.edit_message_text(
                    text=Translation.RENAME_403_ERR,
                    chat_id=update.from_user.id,
                    message_id=a.message_id
                )
                return
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.from_user.id,
                message_id=a.message_id
            )
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
            else:
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                new_img = img.resize((90, 90))
                new_img.save(thumb_image_path, "JPEG", optimize=True)
            bot.send_document(
                chat_id=update.from_user.id,
                document=new_file_name,
                thumb=thumb_image_path,
                caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id
            )
            try:
                os.remove(the_real_download_location)
                os.remove(thumb_image_path)
            except:
                pass
            bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.from_user.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
    else:
        bot.send_message(
            chat_id=update.from_user.id,
            text=Translation.REPLY_TO_DOC_FOR_RENAME_FILE,
            reply_to_message_id=update.message_id
        )
