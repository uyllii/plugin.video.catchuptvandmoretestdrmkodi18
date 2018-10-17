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
from resources.lib import resolver_proxy


import json
import re
import urlquick


# TO DO
# Replay protected by SAMPLE-AES (keep code - desactivate channel for the moment)


URL_ROOT = 'https://uktvplay.uktv.co.uk'

URL_SHOWS = URL_ROOT + '/shows/'
# channel_name

URL_BRIGHTCOVE_DATAS = 'https://s3-eu-west-1.amazonaws.com/uktv-static/prod/play/app.%s.js'
# JS_id

URL_BRIGHTCOVE_POLICY_KEY = 'http://players.brightcove.net/%s/%s_default/index.min.js'
# AccountId, PlayerId

URL_BRIGHTCOVE_VIDEO_JSON = 'https://edge.api.brightcove.com/'\
                            'playback/v1/accounts/%s/videos/%s'
# AccountId, VideoId

def replay_entry(plugin, item_id):
    """
    First executed function after replay_bridge
    """
    return list_programs(plugin, item_id)


@Route.register
def list_programs(plugin, item_id):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(URL_SHOWS)
    json_value = re.compile(
        r'window\.\_\_NUXT\_\_\=(.*?)\;\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads(json_value)

    for serie_id in json_parser["state"]["content"]["series"]:
        for program_datas in json_parser["state"]["content"]["series"][serie_id]:
            if item_id == program_datas["channel"]:
                program_title = program_datas["brand_name"]
                item = Listitem()
                item.label = program_title
                item.set_callback(
                    list_videos,
                    item_id=item_id,
                    serie_id=serie_id)
                yield item
                break


@Route.register
def list_videos(plugin, item_id, serie_id):

    resp = urlquick.get(URL_SHOWS)
    json_value = re.compile(
        r'window\.\_\_NUXT\_\_\=(.*?)\;\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads(json_value)

    # Get data_account / data_player
    js_id = re.compile(
        r'uktv\-static\/prod\/play\/app\.(.*?)\.js').findall(resp.text)[0]
    resp2 = urlquick.get(URL_BRIGHTCOVE_DATAS % js_id)
    data_account = re.compile(
        r'VUE_APP_BRIGHTCOVE_ACCOUNT\:\"(.*?)\"').findall(resp2.text)[0]
    data_player = re.compile(
        r'VUE_APP_BRIGHTCOVE_PLAYER\:\"(.*?)\"').findall(resp2.text)[0]
    
    for video_datas in json_parser["state"]["content"]["series"][serie_id]:
                 
        video_title = video_datas["brand_name"] + \
            ' - ' ' S%sE%s' % (video_datas["series_number"], str(video_datas["episode_number"])) + ' - ' + video_datas["name"]
        video_image = video_datas["image"]
        video_plot = video_datas["synopsis"]
        video_duration = video_datas["duration"] * 60
        video_id = video_datas["video_id"]

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image
        item.info['plot'] = video_plot
        item.info['duration'] = video_duration
        item.set_callback(
            get_video_url,
            item_id=item_id,
            data_account=data_account,
            data_player=data_player,
            data_video_id=video_id,
            video_title=video_title,
            video_plot=video_plot,
            video_image=video_image)
        yield item



# BRIGHTCOVE Part
def get_brightcove_policy_key(data_account, data_player):
    """Get policy key"""
    file_js = urlquick.get(
        URL_BRIGHTCOVE_POLICY_KEY % (data_account, data_player))
    return re.compile('policyKey:"(.+?)"').findall(file_js.text)[0]


@Resolver.register
def get_video_url(plugin, item_id, data_account, data_player, data_video_id, video_title, video_plot, video_image):


    # Method to get JSON from 'edge.api.brightcove.com'
    resp = urlquick.get(
        URL_BRIGHTCOVE_VIDEO_JSON % (data_account, data_video_id),
        headers={'User-Agent': web_utils.get_random_ua, 
            'Accept': 'application/json;pk=%s' % (get_brightcove_policy_key(data_account, data_player))})

    json_parser = json.loads(resp.text)

    video_url = ''
    licence_key = ''
    if 'sources' in json_parser:
        for url in json_parser["sources"]:
            if 'src' in url:
                if 'com.widevine.alpha' in url["key_systems"]:
                    video_url = url["src"]
                    licence_key = url["key_systems"]['com.widevine.alpha']['license_url']
    
    item = Listitem()
    item.path = video_url
    item.label = video_title
    item.info['plot'] = video_plot
    item.art["thumb"] = video_image
    item.property['inputstreamaddon'] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = licence_key + '|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=manifest.prod.boltdns.net|R{SSM}|'

    return item
