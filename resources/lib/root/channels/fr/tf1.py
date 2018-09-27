# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
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

import ast
import inputstreamhelper
import json
import re
import os
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Quality Mode on LIVE TV
# Replay LCI add More Buttons
# DRM (SAMPLE-AES) for Replay => https://github.com/peak3d/inputstream.adaptive/issues/96
# https://bitmovin.com/demos/drm


URL_ROOT = "http://www.tf1.fr/"
URL_TIME = 'http://www.wat.tv/servertime2/'
URL_TOKEN = 'http://api.wat.tv/services/Delivery'
URL_LIVE_TV = 'https://www.tf1.fr/%s/direct'
URL_LIVE_INFO = 'https://api.mytf1.tf1.fr/live/2/%s'
URL_API_IMAGE = 'http://api.mytf1.tf1.fr/image'

SECRET_KEY = 'W3m0#1mFI'
APP_NAME = 'sdk/Iphone/1.0'
VERSION = '2.1.3'
HOSTING_APPLICATION_NAME = 'com.tf1.applitf1'
HOSTING_APPLICATION_VERSION = '7.0.4'
IMG_WIDTH = 640
IMG_HEIGHT = 360

URL_VIDEO_STREAM = 'https://delivery.tf1.fr/mytf1-wrd/%s'

URL_LICENCE_KEY = 'https://drm-wide.tf1.fr/proxy?id=%s|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=drm-wide.tf1.fr|R{SSM}|'
# videoId

DESIRED_QUALITY = common.PLUGIN.get_setting('quality')


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos_categories' in params.next:
        return list_videos_categories(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    url = ''.join((
        URL_ROOT,
        params.channel_name,
        '/programmes-tv'))
    file_path = utils.download_catalog(
        url,
        params.channel_name + '.html')
    root_html = open(file_path).read()
    root_soup = bs(root_html, 'html.parser')

    if params.next == 'list_shows_1':
        categories_soup = root_soup.find(
            'ul',
            attrs={'class': 'filters_2 contentopen'})
        for category in categories_soup.find_all('a'):
            category_name = category.get_text().encode('utf-8')
            category_url = category['data-target'].encode('utf-8')

            shows.append({
                'label': category_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    category=category_url,
                    next='list_shows_2',
                    window_title=category_name
                )
            })

    elif params.next == 'list_shows_2':
        programs_soup = root_soup.find(
            'ul',
            attrs={'id': 'js_filter_el_container'})
        for program in programs_soup.find_all('li'):
            category = program['data-type'].encode('utf-8')
            if params.category == category or params.category == 'all':
                program_url = program.find(
                    'div',
                    class_='description')
                program_url = program_url.find('a')['href'].encode('utf-8')
                program_name = program.find(
                    'p',
                    class_='program').get_text().encode('utf-8')
                img = program.find('img')
                try:
                    img = img['data-srcset'].encode('utf-8')
                except Exception:
                    img = img['srcset'].encode('utf-8')

                img = 'http:' + img.split(',')[-1].split(' ')[0]

                if 'meteo.tf1.fr/meteo-france' in program_url:
                    shows.append({
                        'label': program_name,
                        'thumb': img,
                        'url': common.PLUGIN.get_url(
                            module_path=params.module_path,
                            module_name=params.module_name,
                            action='replay_entry',
                            program_url=program_url,
                            next='list_videos',
                            window_title=program_name
                        )
                    })
                else:
                    shows.append({
                        'label': program_name,
                        'thumb': img,
                        'url': common.PLUGIN.get_url(
                            module_path=params.module_path,
                            module_name=params.module_name,
                            action='replay_entry',
                            program_url=program_url,
                            next='list_videos_categories',
                            window_title=program_name
                        )
                    })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos_categories(params):
    """Build videos categories listing"""
    videos_categories = []
    url = ''.join((
        params.program_url,
        '/videos'))
    program_html = utils.get_webcontent(url)
    program_soup = bs(program_html, 'html.parser')

    filters_1_soup = program_soup.find(
        'ul',
        class_='filters_1')
    if filters_1_soup is not None:
        for li in filters_1_soup.find_all('li'):
            category_title = li.get_text().encode('utf-8')
            category_id = li.find('a')['data-filter'].encode('utf-8')

            # Get Last Page of each categorie
            # Get First page :
            url_first_page = ''.join((
                params.program_url,
                '/videos',
                '?filter=',
                category_id))
            program_first_page_html = utils.get_webcontent(url_first_page)
            program_first_page_soup = bs(
                program_first_page_html, 'html.parser')
            # Get Last page :
            last_page = '0'
            if program_first_page_soup.find(
                    'a', class_='icon i-chevron-right-double trackXiti'
            ) is not None:
                last_page = program_first_page_soup.find(
                    'a',
                    class_='icon i-chevron-right-double trackXiti'
                ).get('href').rsplit('/')[-1].split('?')[0]

            videos_categories.append({
                'label': category_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    program_url=params.program_url,
                    page='1',
                    last_page=last_page,
                    next='list_videos',
                    window_title=category_title,
                    category_id=category_id
                )
            })
    return common.PLUGIN.create_listing(
        videos_categories,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title(params)
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if 'meteo.tf1.fr/meteo-france' in params.program_url:
        program_html = utils.get_webcontent(params.program_url)
        program_soup = bs(program_html, 'html.parser')

        wat_info = program_soup.find(
            'td',
            class_='textbase')

        title = wat_info.find('h3').get_text()

        program_id = re.compile(
            '; src = \'(.*?)\?').findall(program_html)[0]

        info = {
            'video': {
                'title': title,
                # 'plot': stitle,
                # 'aired': aired,
                # 'date': date,
                # 'duration': duration,
                # 'year': int(aired[:4]),
                'mediatype': 'tvshow'
            }
        }

        download_video = (
            ('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                module_path=params.module_path,
                module_name=params.module_name,
                program_id=program_id) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        videos.append({
            'label': title,
            # 'thumb': img,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_r',
                program_id=program_id,
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })
    else:
        if params.page == '1':
            url = ''.join((
                params.program_url,
                '/videos',
                '?filter=',
                params.category_id))
        else:
            url = ''.join((
                params.program_url,
                '/videos/%s' % params.page,
                '?filter=',
                params.category_id))
        program_html = utils.get_webcontent(url)
        program_soup = bs(program_html, 'html.parser')

        grid = program_soup.find(
            'ul',
            class_='grid')

        is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
        if not is_helper.check_inputstream():
            return False

        if grid is not None:
            for li in grid.find_all('li'):
                video_type_string = li.find(
                    'div', class_='description'
                ).find('a')['data-xiti-libelle'].encode('utf-8')
                video_type_string = video_type_string.split('-')[0]

                if 'Playlist' not in video_type_string:
                    title = li.find(
                        'p',
                        class_='title').get_text().encode('utf-8')

                    try:
                        stitle = li.find(
                            'p',
                            class_='stitle').get_text().encode('utf-8')
                    except Exception:
                        stitle = ''

                    try:
                        duration_soup = li.find(
                            'p',
                            class_='uptitle').find(
                                'span',
                                class_='momentDate')
                        duration = int(
                            duration_soup.get_text().encode('utf-8'))
                    except Exception:
                        duration = 0

                    img = li.find('img')
                    try:
                        img = img['data-srcset'].encode('utf-8')
                    except Exception:
                        img = img['srcset'].encode('utf-8')

                    img = 'http:' + img.split(',')[-1].split(' ')[0]

                    try:
                        date_soup = li.find(
                            'div',
                            class_='text').find(
                                'p',
                                class_='uptitle').find('span')

                        aired = date_soup['data-date'].encode(
                            'utf-8').split('T')[0]
                        day = aired.split('-')[2]
                        mounth = aired.split('-')[1]
                        year = aired.split('-')[0]
                        date = '.'.join((day, mounth, year))
                        # date : string (%d.%m.%Y / 01.01.2009)
                        # aired : string (2008-12-07)

                    except Exception:
                        date = ''
                        aired = ''
                        year = 0

                    program_id = li.find('a')['href'].encode('utf-8')

                    if 'www.wat.tv/embedframe' in program_id:
                        url = 'http:' + program_id
                    elif "http" not in program_id:
                        if program_id[0] == '/':
                            program_id = program_id[1:]
                        url = URL_ROOT + program_id
                    else:
                        url = program_id
                    video_html = utils.get_webcontent(url)

                    if 'www.wat.tv/embedframe' in program_id:
                        video_id = re.compile('UVID=(.*?)&').findall(video_html)[0]
                    else:
                        video_html_soup = bs(video_html, 'html.parser')
                        iframe_player_soup = video_html_soup.find(
                            'div',
                            class_='iframe_player')
                        video_id = iframe_player_soup['data-watid'].encode('utf-8')

                    info = {
                        'video': {
                            'title': title,
                            'plot': stitle,
                            'aired': aired,
                            'date': date,
                            'duration': duration,
                            'year': int(aired[:4]),
                            'mediatype': 'tvshow'
                        }
                    }

                    download_video = (
                        common.GETTEXT('Download'),
                        'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                            action='download_video',
                            module_path=params.module_path,
                            module_name=params.module_name,
                            program_id=program_id) + ')'
                    )
                    context_menu = []
                    context_menu.append(download_video)

                    videos.append({
                        'label': title,
                        'thumb': img,
                        'url': common.PLUGIN.get_url(
                            module_path=params.module_path,
                            module_name=params.module_name,
                            action='replay_entry',
                            next='play_r',
                            program_id=program_id,
                        ),
                        'is_playable': True,
                        'info': info,
                        'properties': {
                            'inputstreamaddon': 'inputstream.adaptive',
                            'inputstream.adaptive.manifest_type': 'mpd',
                            'inputstream.adaptive.license_type': 'com.widevine.alpha',
                            'inputstream.adaptive.license_key': URL_LICENCE_KEY % video_id
                        },
                        'context_menu': context_menu
                    })

        if int(params.page) < int(params.last_page):
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    program_url=params.program_url,
                    category_id=params.category_id,
                    last_page=params.last_page,
                    next='list_videos',
                    page=str(int(params.page) + 1),
                    update_listing=True,
                    previous_listing=str(videos)
                )
            })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""

    if params.next == 'play_r' or params.next == 'download_video':

        if 'www.wat.tv/embedframe' in params.program_id:
            url = 'http:' + params.program_id
        elif "http" not in params.program_id:
            if params.program_id[0] == '/':
                params.program_id = params.program_id[1:]
            url = URL_ROOT + params.program_id
        else:
            url = params.program_id
        video_html = utils.get_webcontent(url)

        if 'www.wat.tv/embedframe' in params.program_id:
            video_id = re.compile('UVID=(.*?)&').findall(video_html)[0]
        else:
            video_html_soup = bs(video_html, 'html.parser')
            iframe_player_soup = video_html_soup.find(
                'div',
                class_='iframe_player')
            video_id = iframe_player_soup['data-watid'].encode('utf-8')

        url_json = URL_VIDEO_STREAM % video_id
        htlm_json = utils.get_webcontent(url_json, random_ua=True)
        json_parser = json.loads(htlm_json)

        return json_parser["url"].split('&max_bitrate=')[0]

    elif params.next == 'play_l':

        # Video_ID 'L_%CHANNEL_NAME%'
        video_id = 'L_%s' % params.channel_name.upper()

        timeserver = str(utils.get_webcontent(URL_TIME))

        auth_key = '%s-%s-%s-%s-%s' % (
            video_id,
            SECRET_KEY,
            APP_NAME,
            SECRET_KEY,
            timeserver
        )

        auth_key = common.sp.md5(auth_key).hexdigest()
        auth_key = auth_key + '/' + timeserver

        post_data = {
            'appName': APP_NAME,
            'method': 'getUrl',
            'mediaId': video_id,
            'authKey': auth_key,
            'version': VERSION,
            'hostingApplicationName': HOSTING_APPLICATION_NAME,
            'hostingApplicationVersion': HOSTING_APPLICATION_VERSION
        }

        url_video = utils.get_webcontent(
            url=URL_TOKEN,
            request_type='post',
            post_dic=post_data)
        url_video = json.loads(url_video)
        url_video = url_video['message'].replace('\\', '')

        return url_video.split('&b=')[0]
