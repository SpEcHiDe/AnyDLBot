#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
import json
from pyrogram import (
    Client,
    Filters,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
from anydlbot import (
    AUTH_USERS,
    HTTP_PROXY,
    DOWNLOAD_LOCATION,
    DEF_THUMB_NAIL_VID_S
)
from anydlbot.helper_funcs.display_progress import humanbytes
from anydlbot.helper_funcs.help_uploadbot import DownLoadFile
from anydlbot.helper_funcs.extract_link import get_link
from anydlbot.helper_funcs.run_cmnd import run_shell_command
# the Strings used for this "thing"
from translation import Translation


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(Filters.regex(pattern=".*http.*"))
async def echo(bot, update: Message):
    if update.from_user.id not in AUTH_USERS:
        await update.delete()
        return
    # LOGGER.info(update)
    # await bot.send_chat_action(
    #     chat_id=update.chat.id,
    #     action="typing"
    # )
    LOGGER.info(update.from_user)
    url, _, youtube_dl_username, youtube_dl_password = get_link(update)
    if HTTP_PROXY is not None:
        command_to_exec = [
            "youtube-dl",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--proxy", HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "youtube-dl",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url
        ]
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    # logger.info(command_to_exec)
    t_response, e_response = await run_shell_command(command_to_exec)
    # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
    if e_response and "nonnumeric port" not in e_response:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = e_response.replace(
            Translation.YTDL_ERROR_MESSAGE,
            ""
        )
        if Translation.ISOAYD_PREMIUM_VIDEOS in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        await update.reply_text(
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            quote=True,
            parse_mode="html",
            disable_web_page_preview=True
        )
        return False
    if t_response:
        # logger.info(t_response)
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        save_ytdl_json_path = DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")
                approx_file_size = ""
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                cb_string_file = "{}|{}|{}".format(
                    "file", format_id, format_ext)
                if format_string and "audio only" not in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            f"S {format_string} video  {format_ext} ",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            f"D {format_string} video  {approx_file_size} ",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                else:
                    # special weird case :\
                    ikeyboard = [
                        InlineKeyboardButton(
                            "SVideo [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "DFile [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "64 kbps" + ")",
                        callback_data=cb_string_64.encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "MP3 " + "(" + "128 kbps" + ")",
                        callback_data=cb_string_128.encode("UTF-8")
                    )
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "320 kbps" + ")",
                        callback_data=cb_string.encode("UTF-8")
                    )
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}|{}|{}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "SVideo",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "DFile",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
            cb_string_file = "{}={}={}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}={}={}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "video",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "file",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        # logger.info(reply_markup)
        thumbnail = DEF_THUMB_NAIL_VID_S
        thumbnail_image = DEF_THUMB_NAIL_VID_S
        if "thumbnail" in response_json:
            if response_json["thumbnail"] is not None:
                thumbnail = response_json["thumbnail"]
                thumbnail_image = response_json["thumbnail"]
        thumb_image_path = DownLoadFile(
            thumbnail_image,
            DOWNLOAD_LOCATION + "/" +
            str(update.from_user.id) + ".jpg",
            128,
            None,  # bot,
            Translation.DOWNLOAD_START,
            update.message_id,
            update.chat.id
        )
        await update.reply_photo(
            photo=thumb_image_path,
            quote=True,
            caption=Translation.FORMAT_SELECTION.format(
                thumbnail
            ) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            parse_mode="html"
        )
    else:
        # fallback for nonnumeric port a.k.a seedbox.io
        inline_keyboard = []
        cb_string_file = "{}={}={}".format(
            "file", "LFO", "NONE")
        cb_string_video = "{}={}={}".format(
            "video", "OFL", "ENON")
        inline_keyboard.append([
            InlineKeyboardButton(
                "SVideo",
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "DFile",
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await update.reply_photo(
            photo=DEF_THUMB_NAIL_VID_S,
            quote=True,
            caption=Translation.FORMAT_SELECTION.format(""),
            reply_markup=reply_markup,
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
