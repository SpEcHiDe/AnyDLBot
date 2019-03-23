#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime
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

from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import humanbytes


from pydrive.auth import GoogleAuth


@pyrogram.Client.on_message(pyrogram.Filters.command(["gauth"]))
def g_auth(bot, update):
    TRChatBase(update.from_user.id, update.text, "gauth")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)] = GoogleAuth()
    auth_url = Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)].GetAuthUrl()
    # Create authentication url user needs to visit
    bot.send_message(
        chat_id=update.chat.id,
        text=Translation.G_DRIVE_GIVE_URL_TO_LOGIN.format(auth_url),
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.Filters.command(["gsetup"]))
def g_setup(bot, update):
    TRChatBase(update.from_user.id, update.text, "gsetup")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    recvd_commands = update.command
    if len(recvd_commands) == 2:
        cmnd, auth_code = recvd_commands
        Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)].Auth(auth_code)
        # Authorize and build service from the code
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.G_DRIVE_SETUP_COMPLETE,
            reply_to_message_id=update.message_id
        )
    else:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.G_DRIVE_SETUP_IN_VALID_FORMAT,
            reply_to_message_id=update.message_id
        )
