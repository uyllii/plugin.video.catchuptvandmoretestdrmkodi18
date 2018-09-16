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
            ]
        },

        ('replay', 'generic_menu'): {

            ('fr', 'generic_menu'): [
                ('m6', 'replay_entry'),
                ('w9', 'replay_entry'),
                ('6ter', 'replay_entry'),
                ('stories', 'replay_entry'),
                ('comedy', 'replay_entry'),
                ('fun_radio', 'replay_entry'),
                ('rtl2', 'replay_entry'),
                ('teva', 'replay_entry'),
                ('parispremiere', 'replay_entry')
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
    'parispremiere': '6play'
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
    'fr': 'France',

    # French channels / live TV
    'stories': 'Stories (6play)',
    'comedy': 'Comic (6play)',
    'm6': 'M6',
    'w9': 'W9',
    '6ter': '6ter',
    'fun_radio': 'Fun Radio',
    'rtl2': 'RTL 2',
    'teva': 'Teva',
    'parispremiere': 'Paris Première'


}
