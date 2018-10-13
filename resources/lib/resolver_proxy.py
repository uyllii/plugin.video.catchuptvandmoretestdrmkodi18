# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import *
from resources.lib import web_utils

import json
import re
import urlquick
import xbmcgui

# TO DO
# Quality VIMEO
# Download Mode with Facebook (the video has no audio)


DESIRED_QUALITY = Script.setting['quality']

URL_DAILYMOTION_EMBED = 'http://www.dailymotion.com/embed/video/%s'
URL_DAILYMOTION_EMBED_2 = 'https://www.dailymotion.com/player/metadata/video/%s?integration=inline&GK_PV5_NEON=1'
# Video_id

URL_VIMEO_BY_ID = 'https://player.vimeo.com/video/%s?byline=0&portrait=0&autoplay=1'
# Video_id

URL_FACEBOOK_BY_ID = 'https://www.facebook.com/allocine/videos/%s'
# Video_id

URL_YOUTUBE = 'https://www.youtube.com/embed/%s?&autoplay=0'
# Video_id

URL_BRIGHTCOVE_POLICY_KEY = 'http://players.brightcove.net/%s/%s_default/index.min.js'
# AccountId, PlayerId

URL_BRIGHTCOVE_VIDEO_JSON = 'https://edge.api.brightcove.com/'\
                            'playback/v1/accounts/%s/videos/%s'
# AccountId, VideoId

URL_MTVNSERVICES_STREAM = 'https://media-utils.mtvnservices.com/services/' \
                          'MediaGenerator/%s?&format=json&acceptMethods=hls'
# videoURI

def ytdl_resolver(plugin, url_stream):
    
    # TODO REWRITE this part to use codequick ?

    YDStreamExtractor = __import__('YDStreamExtractor')

    # TO FIX
    # quality = 0
    # if DESIRED_QUALITY == "DIALOG":
    #     all_quality = ['SD', '720p', '1080p', 'Highest available']
    #     seleted_item = xbmcgui.Dialog().select(
    #         LABELS['Choose video quality'],
    #         all_quality)

    #     if seleted_item > -1:
    #         selected_quality_string = all_quality[seleted_item]
    #         quality_string = {
    #             'SD': 0,
    #             '720p': 1,
    #             '1080p': 2,
    #             'Highest available': 3
    #         }
    #         quality = quality_string[selected_quality_string]
    #     else:
    #         return None
    # elif DESIRED_QUALITY == "BEST":
    #     quality = 3

    quality = 3

    vid = YDStreamExtractor.getVideoInfo(
        url_stream,
        quality=quality,
        resolve_redirects=True
    )
    if vid is None:
        # TODO catch the error (geo-blocked, deleted, etc ...)
        plugin.notify('ERROR', plugin.localize(30716))
        return False
    else:
        return vid.streamURL()
    

# Kaltura Part
def get_stream_kaltura(plugin, video_url, isDownloadVideo):

    if isDownloadVideo == True:
        # TODO add download feature
        return None
    return ytdl_resolver(plugin, video_url)

# DailyMotion Part
def get_stream_dailymotion(plugin, video_id, isDownloadVideo):

    url_dmotion = URL_DAILYMOTION_EMBED % (video_id)

    if isDownloadVideo == True:
        # TODO add download feature
        return None
    url_dmotion = URL_DAILYMOTION_EMBED_2 % (video_id)
    dmotion_json = urlquick.get(url_dmotion)
    dmotion_jsonparser = json.loads(dmotion_json.text)
    all_datas_videos_quality = []
    all_datas_videos_path = []
    if "qualities" not in dmotion_jsonparser:
        plugin.notify('ERROR', plugin.localize(30716))
        return None
    if "auto" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('auto')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["auto"][0]["url"])
    if "144" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('144')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["144"][1]["url"])
    if "240" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('240')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["240"][1]["url"])
    if "380" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('380')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["380"][1]["url"])
    if "480" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('480')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["480"][1]["url"])
    if "720" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('720')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["720"][1]["url"])
    if "1080" in dmotion_jsonparser["qualities"]:
        all_datas_videos_quality.append('1080')
        all_datas_videos_path.append(dmotion_jsonparser["qualities"]["1080"][1]["url"])
    if DESIRED_QUALITY == "DIALOG":
        selected_item = xbmcgui.Dialog().select(
            LABELS['Choose video quality'],
                all_datas_videos_quality)
        if selected_item > -1:
            return all_datas_videos_path[selected_item]
        else:
            return None
    elif DESIRED_QUALITY == 'BEST':
        url_stream = ''
        for video_path in all_datas_videos_path:
            url_stream = video_path
        return url_stream
    else:
        if len(all_datas_videos_path) == 1:
            return all_datas_videos_path[0]
        else:
            return all_datas_videos_path[1]
    # return ytdl_resolver(url_dmotion)

# Vimeo Part
def get_stream_vimeo(plugin, video_id, isDownloadVideo):

    url_vimeo = URL_VIMEO_BY_ID % (video_id)

    if isDownloadVideo == True:
        # TODO add download feature
        return None

    html_vimeo = urlquick.get(url_vimeo, headers={'User-Agent': web_utils.get_random_ua}, max_age=-1)
    json_vimeo = json.loads('{' + re.compile('var config \= \{(.*?)\}\;').findall(
        html_vimeo.text)[0] + '}')
    hls_json = json_vimeo["request"]["files"]["hls"]
    default_cdn = hls_json["default_cdn"]
    return hls_json["cdns"][default_cdn]["url"]

# Facebook Part
def get_stream_facebook(plugin, video_id, isDownloadVideo):

    url_facebook = URL_FACEBOOK_BY_ID % (video_id)

    if isDownloadVideo == True:
        # TODO add download feature
        return None

    html_facebook = urlquick.get(url_facebook)

    if len(re.compile(
        r'hd_src_no_ratelimit:"(.*?)"').findall(
        html_facebook.text)) > 0:
        if DESIRED_QUALITY == "DIALOG":
            all_datas_videos_quality = []
            all_datas_videos_path = []
            all_datas_videos_quality.append('SD')
            all_datas_videos_path.append(re.compile(
                r'sd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook.text)[0])
            all_datas_videos_quality.append('HD')
            all_datas_videos_path.append(re.compile(
                r'hd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook.text)[0])
            selected_item = xbmcgui.Dialog().select(
                LABELS['Choose video quality'],
                all_datas_videos_quality)
            if selected_item > -1:
                return all_datas_videos_path[selected_item].encode(
                    'utf-8')
            else:
                return None
        elif DESIRED_QUALITY == 'BEST':
            return re.compile(
                r'hd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook.text)[0]
        else:
            return re.compile(
                r'sd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook.text)[0]
    else:
        return re.compile(
            r'sd_src_no_ratelimit:"(.*?)"').findall(
            html_facebook.text)[0]


# Youtube Part
def get_stream_youtube(plugin, video_id, isDownloadVideo):
    url_youtube = URL_YOUTUBE % video_id

    if isDownloadVideo is True:
        # TODO add download feature
        return None

    return ytdl_resolver(plugin, url_youtube)


# BRIGHTCOVE Part
def get_brightcove_policy_key(data_account, data_player):
    """Get policy key"""
    file_js = urlquick.get(
        URL_BRIGHTCOVE_POLICY_KEY % (data_account, data_player))
    return re.compile('policyKey:"(.+?)"').findall(file_js.text)[0]


def get_brightcove_video_json(plugin, data_account, data_player, data_video_id):

    # Method to get JSON from 'edge.api.brightcove.com'
    resp = urlquick.get(
        URL_BRIGHTCOVE_VIDEO_JSON % (data_account, data_video_id),
        headers={'User-Agent': web_utils.get_random_ua, 
            'Accept': 'application/json;pk=%s' % (get_brightcove_policy_key(data_account, data_player))})
    json_parser = json.loads(resp.text)

    video_url = ''
    if 'sources' in json_parser:
        for url in json_parser["sources"]:
            if 'src' in url:
                if 'm3u8' in url["src"]:
                    video_url = url["src"]
    else:
        if json_parser[0]['error_code'] == "ACCESS_DENIED":
            plugin.notify('ERROR', plugin.localize(30713))
            return None
    return video_url

# MTVN Services Part
def get_mtvnservices_stream(plugin, video_uri):
    json_video_stream = urlquick.get(
        URL_MTVNSERVICES_STREAM % video_uri)
    json_video_stream_parser = json.loads(json_video_stream.text)
    if 'redition' not in json_video_stream_parser["package"]["video"]["item"][0]:
        plugin.notify('ERROR', plugin.localize(30716))
        return None
    return json_video_stream_parser["package"]["video"]["item"][0]["rendition"][0]["src"]
