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


@pyrogram.Client.on_message(pyrogram.Filters.command(["help", "about"]))
def help_user(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/help")
    bot.send_message(
        chat_id=update.from_user.id,
        text=Translation.HELP_USER,
        parse_mode=pyrogram.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.Filters.command(["start"]))
def start(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/start")
    bot.send_message(
        chat_id=update.from_user.id,
        text=Translation.START_TEXT,
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.Filters.command(["upgrade"]))
def upgrade(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/upgrade")
    bot.send_message(
        chat_id=update.from_user.id,
        text=Translation.UPGRADE_TEXT,
        parse_mode=pyrogram.ParseMode.HTML,
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )
