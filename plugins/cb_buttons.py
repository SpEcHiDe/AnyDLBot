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

# the secret configuration specific things
if bool(os.environ.get("ENV", False)):
    from sample_config import Config
else:
    from config import Config


import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


from plugins.youtube_dl_button import youtube_dl_call_back
from plugins.dl_button import ddl_call_back


@pyrogram.Client.on_callback_query()
async def button(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await update.message.delete()
        return
    # LOGGER.info(update)
    cb_data = update.data
    if "|" in cb_data:
        await youtube_dl_call_back(bot, update)
    elif "=" in cb_data:
        await ddl_call_back(bot, update)
