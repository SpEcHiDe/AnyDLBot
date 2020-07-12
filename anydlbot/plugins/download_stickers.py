#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
import os
import time
from PIL import Image
from pyrogram import (
    Client,
    Filters
)
from anydlbot import (
    AUTH_USERS,
    DOWNLOAD_LOCATION
)
from anydlbot.helper_funcs.display_progress import progress_for_pyrogram
# the Strings used for this "thing"
from translation import Translation

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(Filters.sticker)
async def DownloadStickersBot(bot, update):
    if update.from_user.id not in AUTH_USERS:
        await update.delete()
        return

    if update.sticker.is_animated:
        await update.delete()
        return

    LOGGER.info(update.from_user)
    download_location = os.path.join(
        DOWNLOAD_LOCATION,
        (
            str(update.from_user.id),
            "_DownloadStickersBot_",
            str(update.from_user.id),
            ".png"
        )
    )
    a = await update.reply_text(
        text=Translation.DOWNLOAD_START
    )
    try:
        c_time = time.time()
        the_real_download_location = await update.download(
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                a,
                c_time
            )
        )
    except (ValueError) as e:
        await a.edit_text(
            text=str(e)
        )
        return False
    await a.edit_text(
        text=Translation.SAVED_RECVD_DOC_FILE
    )
    # https://stackoverflow.com/a/21669827/4723940
    Image.open(the_real_download_location).convert(
        "RGB"
    ).save(the_real_download_location)
    #
    c_time = time.time()
    await a.reply_document(
        document=the_real_download_location,
        # thumb=thumb_image_path,
        # caption=description,
        # reply_markup=reply_markup,
        # reply_to_message_id=a.message_id,
        progress=progress_for_pyrogram,
        progress_args=(
            Translation.UPLOAD_START,
            a,
            c_time
        )
    )
    await a.reply_photo(
        photo=the_real_download_location,
        # thumb=thumb_image_path,
        # caption=description,
        # reply_markup=reply_markup,
        # reply_to_message_id=a.message_id,
        progress=progress_for_pyrogram,
        progress_args=(
            Translation.UPLOAD_START,
            a,
            c_time
        )
    )
    os.remove(the_real_download_location)
    await a.delete()
