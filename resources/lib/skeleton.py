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
                ('canalplus', 'none'),
                ('c8', 'none'),
                ('cstar', 'none'),
                ('infosportplus', '')
            ]
        },

        ('replay', 'generic_menu'): {

            ('fr', 'generic_menu'): [
                # ('canalplus', 'replay_entry'),
                # ('c8', 'replay_entry'),
                # ('cstar', 'replay_entry'),
                # ('seasons', 'replay_entry'),
                # ('comedie', 'replay_entry'),
                # ('les-chaines-planete', 'replay_entry'),
                # ('golfplus', 'replay_entry'),
                # ('cineplus', 'replay_entry'),
                # ('infosportplus', 'replay_entry'),
                # ('polar-plus', 'replay_entry'),
                # ('m6', 'replay_entry'),
                # ('w9', 'replay_entry'),
                # ('6ter', 'replay_entry'),
                # ('stories', 'replay_entry'),
                # ('bruce', 'replay_entry'),
                # ('crazy_kitchen', 'replay_entry'),
                # ('home', 'replay_entry'),
                # ('styles', 'replay_entry'),
                # ('comedy', 'replay_entry'),
                # ('fun_radio', 'replay_entry')
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
    'canalplus': 'mycanal',
    'c8': 'mycanal',
    'cstar': 'mycanal',
    'seasons': 'mycanal',
    'comedie': 'mycanal',
    'les-chaines-planete': 'mycanal',
    'golfplus': 'mycanal',
    'cineplus': 'mycanal',
    'infosportplus': 'mycanal',
    'polar-plus': 'mycanal',
    'm6': '6play',
    'w9': '6play',
    '6ter': '6play',
    'stories': '6play',
    'bruce': '6play',
    'crazy_kitchen': '6play',
    'home': '6play',
    'styles': '6play',
    'comedy': '6play',
    'fun_radio': '6play'
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
    'canalplus': 'Canal +',
    'c8': 'C8',
    'cstar': 'CStar',
    'seasons': 'Seasons',
    'comedie': 'Comédie +',
    'les-chaines-planete': 'Les chaînes planètes +',
    'golfplus': 'Golf +',
    'cineplus': 'Ciné +',
    'infosportplus': 'INFOSPORT+',
    'polar-plus': 'Polar+',
    'stories': 'Stories (6play)',
    'bruce': 'Bruce (6play)',
    'crazy_kitchen': 'Crazy Kitchen (6play)',
    'home': 'Home Time (6play)',
    'styles': 'Sixième Style (6play)',
    'comedy': 'Comic (6play)',
    'm6': 'M6',
    'w9': 'W9',
    '6ter': '6ter',
    'fun_radio': 'Fun Radio'


}
