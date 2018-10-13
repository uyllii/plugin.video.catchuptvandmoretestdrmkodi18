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
import importlib


def item2dict(item):
    item_dict = {}
    item_dict['art'] = dict(item.art)
    item_dict['info'] = dict(item.info)
    item_dict['stream'] = dict(item.stream)
    item_dict['context'] = dict(item.context)
    item_dict['property'] = item.property
    item_dict['params'] = item.params
    item_dict['label'] = item.label
    return item_dict


#  SYS.ARGV[0]: plugin://plugin.video.catchuptvandmore/resources/lib/websites/culturepub/list_shows
def find_module_in_url(base_url):
    base_url_l = base_url.split('/')
    module_l = []
    addon_name_triggered = False
    for name in base_url_l:
        if addon_name_triggered:
            module_l.append(name)
            continue
        if name == 'plugin.video.catchuptvandmoretestdrmkodi18':
            addon_name_triggered = True
    module_l.pop()  # Pop the function name
    module = '.'.join(module_l)
    # print 'MODULE: ' + module
    return module


def import_needed_module(base_url):
    module_to_import = find_module_in_url(base_url)
    try:
        importlib.import_module(module_to_import)
    except Exception:
        pass
    return module_to_import
