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


from pyrogram import (
    Client,
    CallbackQuery
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


from anydlbot.plugins.youtube_dl_button import youtube_dl_call_back
from anydlbot.plugins.dl_button import ddl_call_back


@Client.on_callback_query()
async def button(bot, update: CallbackQuery):
    if update.from_user.id not in AUTH_USERS:
        await update.message.delete()
        return
    # LOGGER.info(update)
    # NOTE: You should always answer,
    # but we want different conditionals to
    # be able to answer to differnetly
    # (and we can only answer once),
    # so we don't always answer here.
    await update.answer()

    cb_data = update.data
    if "|" in cb_data:
        await youtube_dl_call_back(bot, update)
    elif "=" in cb_data:
        await ddl_call_back(bot, update)
