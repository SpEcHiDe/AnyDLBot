#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import os

from anydlbot import AUTH_USERS


from pyrogram import Client
logging.getLogger("pyrogram").setLevel(logging.WARNING)


from anydlbot.plugins.youtube_dl_button import youtube_dl_call_back
from anydlbot.plugins.dl_button import ddl_call_back


@Client.on_callback_query()
async def button(bot, update):
    if update.from_user.id not in AUTH_USERS:
        await update.message.delete()
        return
    # LOGGER.info(update)
    cb_data = update.data
    if "|" in cb_data:
        await youtube_dl_call_back(bot, update)
    elif "=" in cb_data:
        await ddl_call_back(bot, update)
