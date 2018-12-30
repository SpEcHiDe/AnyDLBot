import os

class Config(object):
    # get a token from https://chatbase.com
    CHAT_BASE_TOKEN = os.environ.get("CHAT_BASE_TOKEN", "")
    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    # your domain to show when download file is greater than MAX_FILE_SIZE
    HTTP_DOMAIN = os.environ.get("HTTP_DOMAIN", "https://example.com/")
    # for running on Heroku.com
    PORT = int(os.environ.get('PORT', 5000))
    # The Telegram API things
    APP_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH")
    # Get these values from my.telegram.org
    # Array to store users who are authorized to use the bot
    AUTH_USERS = set(str(x) for x in os.environ.get("AUTH_USERS", "").split())
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    # Telegram maximum file upload size
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 14000000000
    # chunk size that should be used with requests
    CHUNK_SIZE = 128
    # default thumbnail to be used in the videos
    DEF_THUMB_NAIL_VID_S = "https://placehold.it/90x90"
