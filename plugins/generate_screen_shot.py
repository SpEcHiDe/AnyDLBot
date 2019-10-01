#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import shutil
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
from helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots
from helper_funcs.display_progress import progress_for_pyrogram


@pyrogram.Client.on_message(pyrogram.Filters.command(["generatescss"]))
async def generate_screen_shot(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    TRChatBase(update.from_user.id, update.text, "generatescss")
    if update.reply_to_message is not None:
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                a,
                c_time
            )
        )
        if the_real_download_location is not None:
            await bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.chat.id,
                message_id=a.message_id
            )
            tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
            if not os.path.isdir(tmp_directory_for_each_user):
                os.makedirs(tmp_directory_for_each_user)
            images = await generate_screen_shots(
                the_real_download_location,
                tmp_directory_for_each_user,
                False,
                Config.DEF_WATER_MARK_FILE,
                5,
                9
            )
            logger.info(images)
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=a.message_id
            )
            media_album_p = []
            if images is not None:
                i = 0
                caption = "© @AnyDLBot"
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                pyrogram.InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode="html"
                                )
                            )
                        else:
                            media_album_p.append(
                                pyrogram.InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await bot.send_media_group(
                chat_id=update.chat.id,
                disable_notification=True,
                reply_to_message_id=a.message_id,
                media=media_album_p
            )
            #
            try:
                shutil.rmtree(tmp_directory_for_each_user)
                os.remove(the_real_download_location)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_FOR_SCSS,
            reply_to_message_id=update.message_id
        )
