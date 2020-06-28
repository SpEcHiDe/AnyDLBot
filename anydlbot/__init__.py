#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import os

# the secret configuration specific things
if bool(os.environ.get("ENV", False)):
    from anydlbot.sample_config import Config
else:
    from anydlbot.config import Config


# TODO: is there a better way?
TG_BOT_TOKEN = Config.TG_BOT_TOKEN
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
AUTH_USERS = Config.AUTH_USERS
DOWNLOAD_LOCATION = Config.DOWNLOAD_LOCATION
MAX_FILE_SIZE = Config.MAX_FILE_SIZE
TG_MAX_FILE_SIZE = Config.TG_MAX_FILE_SIZE
CHUNK_SIZE = Config.CHUNK_SIZE
DEF_THUMB_NAIL_VID_S = Config.DEF_THUMB_NAIL_VID_S
MAX_MESSAGE_LENGTH = Config.MAX_MESSAGE_LENGTH
PROCESS_MAX_TIMEOUT = Config.PROCESS_MAX_TIMEOUT
HTTP_PROXY = Config.HTTP_PROXY
FINISHED_PROGRESS_STR = Config.FINISHED_PROGRESS_STR
UN_FINISHED_PROGRESS_STR = Config.UN_FINISHED_PROGRESS_STR
