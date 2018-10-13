# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2016  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals
from codequick import Script


def download_video(video_url):
    #  print('URL Video to download ' + video_url)

    #  Now that we have video URL we can try to download this one
    YDStreamUtils = __import__('YDStreamUtils')
    YDStreamExtractor = __import__('YDStreamExtractor')

    quality_string = {
        'SD': 0,
        '720p': 1,
        '1080p': 2,
        'Highest available': 3
    }

    vid = YDStreamExtractor.getVideoInfo(
        video_url,
        quality=quality_string[Script.setting.get_string('dl_quality')],
        resolve_redirects=True
    )

    path = Script.setting.get_string('dl_folder')
    #  path = path.decode("utf-8").encode(common.FILESYSTEM_CODING)

    with YDStreamUtils.DownloadProgress() as prog:
        try:
            YDStreamExtractor.setOutputCallback(prog)
            YDStreamExtractor.handleDownload(
                vid,
                bg=Script.setting.get_boolean('dl_background'),
                path=path
            )
        finally:
            YDStreamExtractor.setOutputCallback(None)
    return False
