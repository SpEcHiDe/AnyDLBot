#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


import ffmpeg
import os
import subprocess
import time


def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".jpg"
    # width = "90"
    o = (
        ffmpeg
        .input(video_file, ss=ttl)
        # .filter("scale", width, -1)
        .output(out_put_file_name, vframes=1)
    )
    logger.info(o.get_args())
    o.run()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

# https://github.com/Nekmo/telegram-upload/blob/master/telegram_upload/video.py#L26

def cult_small_video(video_file, output_directory, start_time, end_time):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".mp4"
    in1 = ffmpeg.input(video_file, ss=start_time)
    v1 = in1["v"]
    a1 = in1["a"]
    joined = ffmpeg.concat(v1, a1, v=1, a=1).node
    v3 = joined[0]
    a3 = joined[1]
    o = ffmpeg.output(v3, a3, out_put_file_name, strict="-2", to=end_time, format="mp4")
    logger.info(o.get_args())
    o.run()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
