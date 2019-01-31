#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import math
import os
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation


def progress_for_pyrogram(client, current, total, ud_type, message_id, chat_id):
    """if round(current / total * 100, 0) % 10 == 0:
        try:
            client.edit_message_text(
                chat_id,
                message_id,
                text="{}: {} of {}".format(
                    ud_type,
                    humanbytes(current),
                    humanbytes(total)
                )
            )
        except:
            pass"""
    # logger.info("{}: {} of {}".format(ud_type, humanbytes(current), humanbytes(total)))
    pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(math.floor(size)) + " " + Dic_powerN[n] + 'B'
