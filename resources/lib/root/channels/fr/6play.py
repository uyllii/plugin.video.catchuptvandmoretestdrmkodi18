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


import json
import re
from resources.lib import utils
from resources.lib import common

# TO DO
# LIVE TV protected by #EXT-X-FAXS-CM
# Playlists (cas les blagues de TOTO)
# Get vtt subtitle
# Some videos not MDP (find )
# Rework the code (ask sy6sy2)
# Some DRM (m3u8) not working old videos (Kamelot)

# Thank you (https://github.com/peak3d/plugin.video.simple)


# Url to get channel's categories
# e.g. Info, Divertissement, Séries, ...
# We get an id by category
URL_ROOT = 'http://pc.middleware.6play.fr/6play/v2/platforms/' \
           'm6group_web/services/%s/folders?limit=999&offset=0'

# Url to get catgory's programs
# e.g. Le meilleur patissier, La france à un incroyable talent, ...
# We get an id by program
URL_CATEGORY = 'http://pc.middleware.6play.fr/6play/v2/platforms/' \
               'm6group_web/services/6play/folders/%s/programs' \
               '?limit=999&offset=0&csa=6&with=parentcontext'

# Url to get program's subfolders
# e.g. Saison 5, Les meilleurs moments, les recettes pas à pas, ...
# We get an id by subfolder
URL_SUBCATEGORY = 'http://pc.middleware.6play.fr/6play/v2/platforms/' \
                  'm6group_web/services/6play/programs/%s' \
                  '?with=links,subcats,rights'


# Url to get shows list
# e.g. Episode 1, Episode 2, ...
URL_VIDEOS = 'http://pc.middleware.6play.fr/6play/v2/platforms/' \
             'm6group_web/services/6play/programs/%s/videos?' \
             'csa=6&with=clips,freemiumpacks&type=vi,vc,playlist&limit=999'\
             '&offset=0&subcat=%s&sort=subcat'

URL_VIDEOS2 = 'https://pc.middleware.6play.fr/6play/v2/platforms/' \
              'm6group_web/services/6play/programs/%s/videos?' \
              'csa=6&with=clips,freemiumpacks&type=vi&limit=999&offset=0'


URL_JSON_VIDEO = 'https://pc.middleware.6play.fr/6play/v2/platforms/' \
                 'm6group_web/services/6play/videos/%s'\
                 '?csa=6&with=clips,freemiumpacks'


URL_IMG = 'https://images.6play.fr/v1/images/%s/raw'


URL_COMPTE_LOGIN = 'https://login.6play.fr/accounts.login'
# https://login.6play.fr/accounts.login?loginID=*****&password=*******&targetEnv=mobile&format=jsonp&apiKey=3_hH5KBv25qZTd_sURpixbQW6a4OsiIzIEF2Ei_2H7TXTGLJb_1Hr4THKZianCQhWK&callback=jsonp_3bbusffr388pem4
# TODO get value Callback
# callback: jsonp_3bbusffr388pem4

URL_GET_JS_ID_API_KEY = 'https://www.6play.fr/connexion'

URL_API_KEY = 'https://www.6play.fr/client-%s.bundle.js'
# Id

URL_TOKEN_DRM = 'https://6play-users.6play.fr/v2/platforms/m6group_web/services/6play/users/%s/videos/%s/upfront-token'

URL_LICENCE_KEY = 'https://lic.drmtoday.com/license-proxy-widevine/cenc/|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=lic.drmtoday.com&x-dt-auth-token=%s|R{SSM}|JBlicense'
# Token

URL_LIVE_JSON = 'https://pc.middleware.6play.fr/6play/v2/platforms/m6group_web/services/6play/live?channel=%s&with=service_display_images,nextdiffusion,extra_data'
# Chaine

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':

        url_root_site = ''
        if params.channel_name == 'stories' or \
                params.channel_name == 'comedy' or \
                params.channel_name == 'rtl2' or \
                params.channel_name == 'fun_radio':
            url_root_site = URL_ROOT % params.channel_name
        else:
            url_root_site = URL_ROOT % (params.channel_name + 'replay')

        file_path = utils.download_catalog(
            url_root_site,
            '%s.json' % (params.channel_name),
            random_ua=True)
        file_prgm = open(file_path).read()
        json_parser = json.loads(file_prgm)

        # do not cache failed catalog fetch
        # the error format is:
        #   {"error":{"code":403,"message":"Forbidden"}}
        if isinstance(json_parser, dict) and \
                'error' in json_parser.keys():
            utils.os.remove(file_path)
            raise Exception('Failed to fetch the 6play catalog')

        for array in json_parser:
            category_id = str(array['id'])
            category_name = array['name'].encode('utf-8')

            shows.append({
                'label': category_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    category_id=category_id,
                    next='list_shows_2',
                    title=category_name,
                    window_title=category_name
                )
            })

    elif params.next == 'list_shows_2':
        file_prgm = utils.get_webcontent(
            URL_CATEGORY % (params.category_id),
            random_ua=True)
        json_parser = json.loads(file_prgm)

        for array in json_parser:
            program_title = array['title'].encode('utf-8')
            program_id = str(array['id'])
            program_desc = array['description'].encode('utf-8')
            program_imgs = array['images']
            program_img = ''
            program_fanart = ''
            for img in program_imgs:
                if img['role'].encode('utf-8') == 'vignette':
                    external_key = img['external_key'].encode('utf-8')
                    program_img = URL_IMG % (external_key)
                elif img['role'].encode('utf-8') == 'carousel':
                    external_key = img['external_key'].encode('utf-8')
                    program_fanart = URL_IMG % (external_key)

            info = {
                'video': {
                    'title': program_title,
                    'plot': program_desc
                }
            }

            shows.append({
                'label': program_title,
                'thumb': program_img,
                'fanart': program_fanart,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_shows_3',
                    program_id=program_id,
                    program_img=program_img,
                    program_fanart=program_fanart,
                    program_desc=program_desc,
                    title=program_title,
                    window_title=program_title
                ),
                'info': info
            })

    elif params.next == 'list_shows_3':
        program_json = utils.get_webcontent(
            URL_SUBCATEGORY % (params.program_id),
            random_ua=True)

        json_parser = json.loads(program_json)

        try:
            program_fanart = params.program_fanart
        except Exception:
            program_fanart = ''

        for sub_category in json_parser['program_subcats']:
            sub_category_id = str(sub_category['id'])
            sub_category_title = sub_category['title'].encode('utf-8')

            info = {
                'video': {
                    'title': sub_category_title,
                    'plot': params.program_desc
                }
            }

            shows.append({
                'label': sub_category_title,
                'thumb': params.program_img,
                'fanart': program_fanart,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos',
                    program_id=params.program_id,
                    sub_category_id=sub_category_id,
                    window_title=sub_category_title
                ),
                'info': info
            })

        info = {
            'video': {
                'title': common.ADDON.get_localized_string(30701),
                'plot': params.program_desc
            }
        }

        shows.append({
            'label': common.ADDON.get_localized_string(30701),
            'thumb': params.program_img,
            'fanart': program_fanart,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_videos',
                program_id=params.program_id,
                sub_category_id='null',
                window_title=params.window_title

            ),
            'info': info
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
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.sub_category_id == 'null':
        url = URL_VIDEOS2 % params.program_id
    else:
        url = URL_VIDEOS % (params.program_id, params.sub_category_id)
    program_json = utils.get_webcontent(
        url,
        random_ua=True)
    json_parser = json.loads(program_json)

    # TO DO Playlist More one 'clips'

    result_js_id = re.compile(
        r'client\-(.*?)\.bundle\.js').findall(
            utils.get_webcontent(URL_GET_JS_ID_API_KEY))[0]

    result = utils.get_webcontent(URL_API_KEY % result_js_id)

    api_key = re.compile(
            r'\"login.6play.fr\"\,key\:\"(.*?)\"'
        ).findall(result)[0]

    module_name = eval(params.module_path)[-1]

    # Build PAYLOAD
    payload = {
        "loginID": common.PLUGIN.get_setting(
            module_name + '.login'),
        "password": common.PLUGIN.get_setting(
            module_name + '.password'),
        "apiKey": api_key,
        "format": "jsonp",
        "callback": "jsonp_3bbusffr388pem4"
    }

    # LOGIN
    result_2_json = utils.get_webcontent(
        URL_COMPTE_LOGIN, request_type='post', post_dic=payload, specific_headers={'referer':'https://www.6play.fr/connexion'})
    result_2_jsonparser = json.loads(result_2_json.replace('jsonp_3bbusffr388pem4(', '').replace(');',''))
    if "UID" not in result_2_jsonparser:
        utils.send_notification(
            params.channel_name + ' : ' + common.ADDON.get_localized_string(30711))
        return None
    account_id = result_2_jsonparser["UID"]
    account_timestamp = result_2_jsonparser["signatureTimestamp"]
    account_signature = result_2_jsonparser["UIDSignature"]

    for video in json_parser:
        video_id = str(video['id'])

        title = video['title'].encode('utf-8')
        duration = video['clips'][0]['duration']
        description = video['description'].encode('utf-8')
        try:
            aired = video['clips'][0]['product']['last_diffusion']
            aired = aired.encode('utf-8')
            aired = aired[:10]
            year = aired[:4]
            # date : string (%d.%m.%Y / 01.01.2009)
            # aired : string (2008-12-07)
            day = aired.split('-')[2]
            mounth = aired.split('-')[1]
            year = aired.split('-')[0]
            date = '.'.join((day, mounth, year))

        except Exception:
            aired = ''
            year = ''
            date = ''
        img = ''

        program_imgs = video['clips'][0]['images']
        program_img = ''
        for img in program_imgs:
                if img['role'].encode('utf-8') == 'vignette':
                    external_key = img['external_key'].encode('utf-8')
                    program_img = URL_IMG % (external_key)

        info = {
            'video': {
                'title': title,
                'plot': description,
                'aired': aired,
                'date': date,
                'duration': duration,
                'year': year,
                'mediatype': 'tvshow'
            }
        }

        download_video = (
            common.GETTEXT('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                module_path=params.module_path,
                module_name=params.module_name,
                video_id=video_id) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        is_drm = False
        all_datas_videos_path = []
        if video['clips'][0]['assets'] is not None:
            for asset in video['clips'][0]['assets']:
                if 'http_h264' in asset["type"]:
                    all_datas_videos_path.append(
                        asset['full_physical_path'].encode('utf-8'))
                    break
                elif 'h264' in asset["type"]:
                    manifest = utils.get_webcontent(
                        asset['full_physical_path'].encode('utf-8'),
                            random_ua=True)
                    if 'drm' not in manifest:
                        all_datas_videos_path.append(
                            asset['full_physical_path'].encode('utf-8'))
                        break

        if len(all_datas_videos_path) == 0:
            is_drm = True

        if is_drm:
            # Build PAYLOAD headers
            payload_headers = {
                'x-auth-gigya-signature': account_signature,
                'x-auth-gigya-signature-timestamp': account_timestamp,
                'x-auth-gigya-uid': account_id,
            }
            token_json = utils.get_webcontent(
                URL_TOKEN_DRM % (account_id, video_id), specific_headers=payload_headers)
            token_jsonparser = json.loads(token_json)
            token = token_jsonparser["token"]

            videos.append({
                'label': title,
                'thumb': program_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    video_id=video_id,
                ),
                'is_playable': True,
                'info': info,
                'properties': {
                    'inputstreamaddon': 'inputstream.adaptive',
                    'inputstream.adaptive.manifest_type': 'mpd',
                    'inputstream.adaptive.license_type': 'com.widevine.alpha',
                    'inputstream.adaptive.license_key': URL_LICENCE_KEY % token
                },
                'context_menu': context_menu
            })

        else:
            videos.append({
                'label': title,
                'thumb': program_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    video_id=video_id,
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
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
        category=common.get_window_title(params)
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)

def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r':
        video_json = utils.get_webcontent(
            URL_JSON_VIDEO % (params.video_id),
            random_ua=True)
        json_parser = json.loads(video_json)


        video_assets = json_parser['clips'][0]['assets']
        if video_assets is None:
            utils.send_notification(common.ADDON.get_localized_string(30712))
            return ''

        # "type":"primetime_phls_h264" => Video protected by DRM (m3u8)
        # "type":"usp_hls_h264" => Video not protected by DRM (m3u8)
        # "type":"usp_dashcenc_h264" => No supported by Kodi (MDP)
        # "type":"usp_hlsfp_h264" => Video protected by DRM (m3u8)
        # "type":"http_h264" => Video not proted by DRM (mp4) (Quality SD "video_quality":"sd", HD "video_quality":"hq", HD "video_quality":"hd", HD "video_quality":"lq", 3G) 
        # "type":"http_subtitle_vtt_sm" => Subtitle (in English TVShows)

        # desired_quality = common.PLUGIN.get_setting('quality')
        url_stream = ''

        all_datas_videos_path = []
        for asset in video_assets:
            if 'http_h264' in asset["type"]:
                all_datas_videos_path.append(
                    asset['full_physical_path'].encode('utf-8'))
            elif 'h264' in asset["type"]:
                manifest = utils.get_webcontent(
                    asset['full_physical_path'].encode('utf-8'),
                        random_ua=True)
                if 'drm' not in manifest:
                    all_datas_videos_path.append(
                        asset['full_physical_path'].encode('utf-8'))
        if len(all_datas_videos_path) > 0:
            url_stream = all_datas_videos_path[0]
        else:
            for asset in video_assets:
                if 'usp_dashcenc_h264' in asset["type"]:
                    url_stream = asset['full_physical_path'].encode('utf-8')
        return url_stream
    elif params.next == 'play_l':
        if params.channel_name == 'fun_radio' or \
            params.channel_name == 'rtl2':
            video_json = utils.get_webcontent(
                URL_LIVE_JSON % (params.channel_name),
                random_ua=True)
            json_parser = json.loads(video_json)
            video_assets = json_parser[params.channel_name][0]['live']['assets']
        elif params.channel_name == '6ter':
            video_json = utils.get_webcontent(
                URL_LIVE_JSON % '6T',
                random_ua=True)
            json_parser = json.loads(video_json)
            video_assets = json_parser[ '6T'][0]['live']['assets']
        # elif params.channel_name == 'teva':
        #     video_json = utils.get_webcontent(
        #         URL_LIVE_JSON % 'TE',
        #         random_ua=True)
        #     json_parser = json.loads(video_json)
        #     video_assets = json_parser[ 'TE'][0]['live']['assets']
        # elif params.channel_name == 'parispremiere':
        #     video_json = utils.get_webcontent(
        #         URL_LIVE_JSON % 'PP',
        #         random_ua=True)
        #     json_parser = json.loads(video_json)
        #     video_assets = json_parser[ 'PP'][0]['live']['assets']
        else:
            video_json = utils.get_webcontent(
                URL_LIVE_JSON % (params.channel_name.upper()),
                random_ua=True)
            json_parser = json.loads(video_json)
            video_assets = json_parser[params.channel_name.upper()][0]['live']['assets']
        if video_assets is None:
            utils.send_notification(common.ADDON.get_localized_string(30712))
            return ''

        # "type":"primetime_phls_h264" => Video protected by DRM (m3u8)
        # "type":"usp_hls_h264" => Video not protected by DRM (m3u8)
        # "type":"usp_dashcenc_h264" => No supported by Kodi (MDP)
        # "type":"usp_hlsfp_h264" => Video protected by DRM (m3u8)
        # "type":"http_h264" => Video not proted by DRM (mp4) (Quality SD "video_quality":"sd", HD "video_quality":"hq", HD "video_quality":"hd", HD "video_quality":"lq", 3G) 
        # "type":"http_subtitle_vtt_sm" => Subtitle (in English TVShows)

        # desired_quality = common.PLUGIN.get_setting('quality')
        url_stream = ''

        if params.channel_name == 'fun_radio' or \
            params.channel_name == 'rtl2':
            for asset in video_assets:
                if 'delta_hls_h264' in asset["type"]:
                    url_stream = asset['full_physical_path'].encode('utf-8')
        else:
            for asset in video_assets:
                if 'delta_dashcenc_h264' in asset["type"]:
                    url_stream = asset['full_physical_path'].encode('utf-8')
        return url_stream
