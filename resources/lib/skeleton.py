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

from resources.lib import common

'''
SKELETON dictionary corresponds to the architecture of each menu of the addon
(elt1, elt2) -->
    elt1: label
    elt2: next function to call
'''
SKELETON = {
    ('root', 'generic_menu'): {

        ('live_tv', 'generic_menu'): {

            ('fr', 'build_live_tv_menu'): [
                ('m6', 'none'),
                ('w9', 'none'),
                ('6ter', 'none'),
                ('fun_radio', 'none'),
                ('rtl2', 'none'),
                # ('teva', 'none'),
                # ('parispremiere', 'none'),
                ('mb', 'none'),
                ('tf1', 'none'),
                ('tmc', 'none'),
                ('tfx', 'none'),
                ('tf1-series-films', 'none')
            ],

            ('be', 'build_live_tv_menu'): [
                ('rtl_tvi', 'none'),
                ('plug_rtl', 'none'),
                ('club_rtl', 'none'),
                ('contact', 'none')
            ]
        },

        ('replay', 'generic_menu'): {

            ('be', 'generic_menu'): [
                ('rtl_tvi', 'replay_entry'),
                ('plug_rtl', 'replay_entry'),
                ('club_rtl', 'replay_entry'),
                ('rtl_info', 'replay_entry'),
                ('bel_rtl', 'replay_entry'),
                ('contact', 'replay_entry'),
                ('rtl_sport', 'replay_entry')
            ],

            ('fr', 'generic_menu'): [
                ('m6', 'replay_entry'),
                ('w9', 'replay_entry'),
                ('6ter', 'replay_entry'),
                ('stories', 'replay_entry'),
                ('comedy', 'replay_entry'),
                ('fun_radio', 'replay_entry'),
                ('rtl2', 'replay_entry'),
                ('teva', 'replay_entry'),
                ('parispremiere', 'replay_entry'),
                ('tf1', 'replay_entry'),
                ('tmc', 'replay_entry'),
                ('tfx', 'replay_entry'),
                ('tf1-series-films', 'replay_entry'),
                ('tfou', 'replay_entry'),
                # ('francetvsport', 'replay_entry')
            ]

        },
        ('websites', 'generic_menu'): [
        ]

    }
}


'''
SKELETON dictionary is the bridge between
the item in Kodi and the real folder location on disk
'''
FOLDERS = {
    'live_tv': 'channels',
    'replay': 'channels'
}


'''
CHANNELS dictionary is the bridge between
the channel name and his corresponding python file
'''
CHANNELS = {
    'm6': '6play',
    'w9': '6play',
    '6ter': '6play',
    'stories': '6play',
    'comedy': '6play',
    'fun_radio': '6play',
    'rtl2': '6play',
    'teva': '6play',
    'parispremiere': '6play',
    'mb': '6play',
    'rtl_tvi': 'rtlplaybe',
    'plug_rtl': 'rtlplaybe',
    'club_rtl': 'rtlplaybe',
    'rtl_info': 'rtlplaybe',
    'bel_rtl': 'rtlplaybe',
    'contact': 'rtlplaybe',
    'rtl_sport': 'rtlplaybe',
    'tf1': 'mytf1',
    'tmc': 'mytf1',
    'tfx': 'mytf1',
    'tf1-series-films': 'mytf1',
    'tfou': 'mytf1',
    'francetvsport': 'francetvsport'
}

'''
LABELS dict is only used to retrieve correct element in english strings.po
'''
LABELS = {

    # root
    'live_tv': 'Live TV',
    'replay': 'Catch-up TV',
    'websites': 'Websites',

    # Countries
    'be': 'Belgium',
    'fr': 'France',

    # Belgium channels / live TV
    'rtl_tvi': 'RTL-TVI',
    'plug_rtl': 'PLUG RTL',
    'club_rtl': 'CLUB RTL',
    'contact': 'Contact',
    'bel_rtl': 'BEL RTL',
    'rtl_info': 'RTL INFO',
    'rtl_sport': 'RTL Sport',

    # French channels / live TV
    'stories': 'Stories (6play)',
    'comedy': 'Comic (6play)',
    'm6': 'M6',
    'w9': 'W9',
    '6ter': '6ter',
    'fun_radio': 'Fun Radio',
    'rtl2': 'RTL 2',
    'teva': 'Teva',
    'parispremiere': 'Paris Première',
    'mb': 'M6 Boutique',
    'tf1': 'TF1',
    'tmc': 'TMC',
    'tfx': 'TFX',
    'tf1-series-films': 'TF1 Séries Films',
    'tfou': 'Tfou (MYTF1)',
    'francetvsport': 'France TV Sport (francetv)'


}
