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

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import *
from resources.lib import web_utils
import resources.lib.cq_utils as cqu

import inputstreamhelper
import json
import re
from bs4 import BeautifulSoup as bs
import urlquick


# TO DO

URL_ROOT = utils.urljoin_partial("http://www.tf1.fr")

URL_VIDEO_STREAM = 'https://delivery.tf1.fr/mytf1-wrd/%s'
# videoId

URL_LICENCE_KEY = 'https://drm-wide.tf1.fr/proxy?id=%s|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=drm-wide.tf1.fr|R{SSM}|'
# videoId


def replay_entry(plugin, item_id):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_ROOT(item_id + '/programmes-tv'))
    root_soup = bs(resp.text, 'html.parser')
    categories_soup = root_soup.find(
        'ul',
        attrs={'class': 'filters_2 contentopen'})
    for category in categories_soup.find_all('a'):
        category_name = category.get_text()
        category_url = category['data-target']

        item = Listitem()
        item.label = category_name
        item.set_callback(
            list_programs,
            item_id=item_id,
            category=category_url
        )
        yield item


@Route.register
def list_programs(plugin, item_id, category):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(URL_ROOT(item_id + '/programmes-tv'))
    root_soup = bs(resp.text, 'html.parser')
    programs_soup = root_soup.find(
        'ul',
        attrs={'id': 'js_filter_el_container'})
    for program in programs_soup.find_all('li'):
        current_category = program['data-type']
        if category == current_category or category == 'all':
            item = Listitem()
            program_url = program.find(
                'div',
                class_='description')
            program_url = program_url.find('a')['href']
            program_name = program.find(
                'p',
                class_='program').get_text()
            img = program.find('img')
            try:
                img = img['data-srcset']
            except Exception:
                img = img['srcset']

            img = 'http:' + img.split(',')[-1].split(' ')[0]

            if 'meteo.tf1.fr/meteo-france' in program_url:
                item.label = program_name
                item.art["thumb"] = img
                item.set_callback(
                    list_videos,
                    item_id=item_id,
                    program_category_url=program_url
                )
                yield item

            else:
                item.label = program_name
                item.art["thumb"] = img
                item.set_callback(
                    list_program_categories,
                    item_id=item_id,
                    program_url=program_url
                )
                yield item


@Route.register
def list_program_categories(plugin, item_id, program_url):
    """
    Build program categories
    - Toutes les vidéos
    - Tous les replay
    - Saison 1
    - ...
    """
    resp = urlquick.get(program_url + '/videos')
    program_categories = resp.parse(
        u"ul", attrs={'class': 'filters_1 contentopen'})

    for li in program_categories.iterfind('.//li'):
        item = Listitem()
        item.label = "".join(li.itertext())
        category_id = li.find('a').get('data-filter')
        item.set_callback(
            list_videos,
            item_id=item_id,
            program_category_url=program_url + '/videos?filter=' + category_id
        )
        yield item


@Route.register
def list_videos(plugin, item_id, program_category_url):

    if 'meteo.tf1.fr/meteo-france' in program_category_url:
        resp = urlquick.get(program_category_url)
        program_soup = bs(resp.text, 'html.parser')

        wat_info = program_soup.find(
            'td',
            class_='textbase')

        title = wat_info.find('h3').get_text()

        program_id = re.compile(
            r'\; src \= \'(.*?)\'').findall(resp.text)[0]

        item = Listitem()
        item.label = title
        item.set_callback(
            get_video_url,
            item_id=item_id,
            program_id=program_id,
            item_dict=cqu.item2dict(item)
        )
        yield item

    else:

        resp = urlquick.get(program_category_url)
        program_soup = bs(resp.text, 'html.parser')

        grid = program_soup.find(
            'ul',
            class_='grid')

        if grid is not None:
            for li in grid.find_all('li'):
                video_type_string = li.find(
                    'div', class_='description'
                ).find('a')['data-xiti-libelle']
                video_type_string = video_type_string.split('-')[0]

                if 'Playlist' not in video_type_string:
                    item = Listitem()

                    item.label = li.find(
                        'p',
                        class_='title').get_text()

                    try:
                        stitle = li.find(
                            'p',
                            class_='stitle').get_text()
                        item.info['plot'] = stitle
                    except Exception:
                        pass

                    try:
                        duration_soup = li.find(
                            'p',
                            class_='uptitle').find(
                                'span',
                                class_='momentDate')
                        duration = int(
                            duration_soup.get_text())
                        item.info['duration'] = duration
                    except Exception:
                        pass

                    img = li.find('img')
                    try:
                        img = img['data-srcset']
                    except Exception:
                        img = img['srcset']

                    item.art["thumb"] = 'http:' + \
                        img.split(',')[-1].split(' ')[0]

                    try:
                        date_soup = li.find(
                            'div',
                            class_='text').find(
                            'p',
                            class_='uptitle').find('span')

                        aired = date_soup['data-date'].split('T')[0]
                        item.info.date(aired, '%Y-%m-%d')
                    except Exception:
                        pass

                    program_id = li.find('a')['href']


                    item.set_callback(
                        get_video_url,
                        item_id=item_id,
                        program_id=program_id,
                        item_dict=cqu.item2dict(item)
                    )
                    yield item

            # Check for any next page
            pagination = resp.parse(
                u"div", attrs={'class': 'clearfix list_pagination'})

            ol = pagination.find('ol')
            if ol is not None:
                li_list = ol.findall('li')

                for i in range(len(li_list) - 1):
                    li = li_list[i]
                    if 'selected' in li.find('.//a').get('class') and \
                            i < len(li_list):
                        next_li = li_list[i + 1]
                        yield Listitem.next_page(
                            item_id=item_id,
                            program_category_url=next_li.find('.//a').get('href'))


@Resolver.register
def get_video_url(plugin, item_id, program_id, item_dict):
    if 'www.wat.tv/embedframe' in program_id:
        url = 'http:' + program_id
    elif "http" not in program_id:
        if program_id[0] == '/':
            program_id = program_id[1:]
        url = URL_ROOT(program_id)
    else:
        url = program_id

    video_html = urlquick.get(url).text

    if 'www.wat.tv/embedframe' in program_id:
        video_id = re.compile('UVID=(.*?)&').findall(video_html)[0]
    else:
        video_html_soup = bs(video_html, 'html.parser')
        iframe_player_soup = video_html_soup.find(
            'div',
            class_='iframe_player')
        if iframe_player_soup is not None:
            video_id = iframe_player_soup['data-watid']
        else:
            video_id = re.compile(
                r'\"data\"\:\{\"id\"\:\"(.*?)\"').findall(video_html)[0]

    url_json = URL_VIDEO_STREAM % video_id
    htlm_json = urlquick.get(url_json, headers={'User-Agent': web_utils.get_random_ua}, max_age=-1)
    json_parser = json.loads(htlm_json.text)

    is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
    if not is_helper.check_inputstream():
        return False

    item = Listitem()
    item.path = json_parser["url"].split('&max_bitrate=')[0]
    item.label = item_dict['label']
    item.info.update(item_dict['info'])
    item.art.update(item_dict['art'])
    item.property['inputstreamaddon'] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = URL_LICENCE_KEY % video_id

    return item
