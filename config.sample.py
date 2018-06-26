
class Config(object):
    # get a token from http://botan.io
    BOTAN_IO_TOKEN = ""
    # get a token from @BotFather
    TG_BOT_TOKEN = ""
    # your domain to show when download file is greater than MAX_FILE_SIZE
    HTTP_DOMAIN = "https://example.com/"
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    # Telegram maximum file upload size
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 14000000000
    # The Telegram API things
    APP_ID = 12345
    API_HASH = ""
    # Get these values from my.telegram.org
    # for storing the Telethon session
    TL_SESSION = "AnyDLBot.session"

