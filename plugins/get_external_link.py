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
import requests
import subprocess
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
from helper_funcs.display_progress import progress_for_pyrogram


@pyrogram.Client.on_message(pyrogram.Filters.command(["getlink"]))
async def get_link(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    TRChatBase(update.from_user.id, update.text, "getlink")
    logger.info(update.from_user)
    if update.reply_to_message is not None:
        reply_message = update.reply_to_message
        download_location = Config.DOWNLOAD_LOCATION + "/"
        start = datetime.now()
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        after_download_file_name = await bot.download_media(
            message=reply_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                a,
                c_time
            )
        )
        download_extension = after_download_file_name.rsplit(".", 1)[-1]
        await bot.edit_message_text(
            text=Translation.SAVED_RECVD_DOC_FILE,
            chat_id=update.chat.id,
            message_id=a.message_id
        )
        end_one = datetime.now()
        url = "https://transfer.sh/{}.{}".format(str(update.from_user.id), str(download_extension))
        max_days = "5"
        command_to_exec = [
            "curl",
            # "-H", 'Max-Downloads: 1',
            "-H", 'Max-Days: 5', # + max_days + '',
            "--upload-file", after_download_file_name,
            url
        ]
        await bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.chat.id,
            message_id=a.message_id
        )
        try:
            logger.info(command_to_exec)
            t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logger.info("Status : FAIL", exc.returncode, exc.output)
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=exc.output.decode("UTF-8"),
                message_id=a.message_id
            )
            return False
        else:
            logger.info(t_response)
            t_response_arry = t_response.decode("UTF-8").split("\n")[-1].strip()
            shorten_api_url = "http://ouo.io/api/{}?s={}".format(Config.OUO_IO_API_KEY, t_response_arry)
            adfulurl = requests.get(shorten_api_url).text
        await bot.edit_message_text(
            chat_id=update.chat.id,
            text=Translation.AFTER_GET_DL_LINK.format(adfulurl, max_days),
            parse_mode=pyrogram.ParseMode.HTML,
            message_id=a.message_id,
            disable_web_page_preview=True
        )
        try:
            os.remove(after_download_file_name)
        except:
            pass
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_GET_LINK,
            reply_to_message_id=update.message_id
        )
