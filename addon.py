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

from codequick import Route, Resolver, Listitem, run, Script, utils

from resources.lib.skeleton import *
from resources.lib.labels import *
from resources.lib import common


def get_sorted_menu(item_id):
    # The current menu to build contains
    # all the items present in the 'item_id'
    # dictionnary of the skeleton.py file
    current_menu = eval(item_id.upper())

    # First, we have to sort the current menu
    # according to each item order and we have
    # to hide each disabled item
    menu = []
    for item_id, item_infos in current_menu.items():

        # If the item is enable
        if Script.setting.get_boolean(item_id):

            # Get order value in settings file
            item_order = Script.setting.get_int(item_id + '.order')

            item = (
                item_order,
                item_id,
                item_infos
            )

            menu.append(item)

    # We sort the menu according to the item_order values
    return sorted(menu, key=lambda x: x[0])


@Route.register
def root(plugin):
    """
    root is the entry point
    of Catch-up TV & More
    """
    # First menu to build is the root menu
    # (see ROOT dictionnary in skeleton.py)
    return generic_menu(plugin, 'ROOT', '')


@Route.register
def generic_menu(plugin, item_id, item_thumb):
    """
    Build a generic addon menu
    with all not hidden items
    """
    menu = get_sorted_menu(item_id)

    for index, (item_order,
                item_id,
                item_infos
                ) in enumerate(menu):

        item = Listitem()

        item.params['item_id'] = item_id

        label = LABELS[item_id]
        if isinstance(label, int):
            item.label = plugin.localize(label)
        else:
            item.label = label

        # Get item path of icon and fanart
        item.params['item_thumb'] = ''
        if 'thumb' in item_infos:
            item.art["thumb"] = common.get_item_media_path(
                item_infos['thumb'])
            item.params['item_thumb'] = item.art["thumb"]

        if 'fanart' in item_infos:
            item.art["fanart"] = common.get_item_media_path(
                item_infos['fanart'])

        # If this item requires a module to work, get
        # the module path to be loaded
        if 'module' in item_infos:
            item.params['item_module'] = item_infos['module']

        # Get the next action to trigger if this
        # item will be selected by the user
        item.set_callback(eval(item_infos['callback']))

        yield item


@Route.register
def tv_guide_menu(plugin, item_id, item_thumb):
    menu = get_sorted_menu(item_id)
    channels_id = []
    for index, (channel_order,
                channel_id,
                channel_infos
                ) in enumerate(menu):
        channels_id.append(channel_id)

    # Load the graber module accroding to the country (e.g. resources.lib.channels.tv_guides.fr_live)
    tv_guide_module_path = 'resources.lib.channels.tv_guides.' + item_id
    tv_guide_module = importlib.import_module(tv_guide_module_path)

    # For each channel grab the current program according to the current time
    tv_guide = tv_guide_module.grab_tv_guide(channels_id)

    for index, (item_order,
                item_id,
                item_infos
                ) in enumerate(menu):

        item = Listitem()

        item.params['item_id'] = item_id

        label = LABELS[item_id]
        if isinstance(label, int):
            item.label = plugin.localize(label)
        else:
            item.label = label
        item.label = utils.color(item.label, 'blue')

        # Get item path of icon and fanart
        item.params['item_thumb'] = ''
        if 'thumb' in item_infos:
            item.art["thumb"] = common.get_item_media_path(
                item_infos['thumb'])
            item.params['item_thumb'] = item.art["thumb"]

        if 'fanart' in item_infos:
            item.art["fanart"] = common.get_item_media_path(
                item_infos['fanart'])

        # If this item requires a module to work, get
        # the module path to be loaded
        if 'module' in item_infos:
            item.params['item_module'] = item_infos['module']

        # If we have program infos from the grabber
        if item_id in tv_guide:
            channel_infos = tv_guide[item_id]

            if 'title' in channel_infos:
                item.label = item.label + ' — ' + utils.italic(channel_infos['title'])

            if 'originaltitle' in channel_infos:
                item.info['originaltitle'] = channel_infos['originaltitle']

            if 'genre' in channel_infos:
                item.info['genre'] = channel_infos['genre']

            plot = ''
            if 'soustitre' in channel_infos:
                plot = channel_infos['soustitre']

            if 'plot' in channel_infos:
                plot = plot + '\n' + channel_infos['plot']
            item.info['plot'] = plot

            if 'director' in channel_infos:
                item.info['director'] = channel_infos['director']

            if 'cast' in channel_infos:
                item.info['cast'] = channel_infos['cast']

            if 'writer' in channel_infos:
                item.info['writer'] = channel_infos['writer']

            if 'year' in channel_infos:
                item.info['year'] = channel_infos['year']

            if 'episode' in channel_infos:
                item.info['episode'] = channel_infos['episode']

            if 'season' in channel_infos:
                item.info['season'] = channel_infos['season']

            if 'image' in channel_infos:
                item.art["fanart"] = channel_infos['image']

            if 'rating' in channel_infos:
                item.info["rating"] = channel_infos['rating']

        # Get the next action to trigger if this
        # item will be selected by the user
        item.set_callback(eval(item_infos['callback']))

        yield item


@Route.register
def replay_bridge(plugin, item_id, item_thumb, item_module):
    """
    replay_bridge is the bridge between the
    addon.py file and each channel modules files.
    Because each time the user enter in a new
    menu level the PLUGIN.run() function is
    executed.
    So we have to load on the fly the corresponding
    module of the channel.
    """
    plugin.setting['module_to_load'] = item_module

    # Let's go to the module file ...
    item_module = importlib.import_module(item_module)
    return item_module.replay_entry(plugin, item_id)


@Route.register
def website_bridge(plugin, item_id, item_thumb, item_module):
    """
    Like replay_bridge
    """
    plugin.setting['module_to_load'] = item_module

    # Let's go to the module file ...
    item_module = importlib.import_module(item_module)
    return item_module.website_entry(plugin, item_id)


@Resolver.register
def live_bridge(plugin, item_id, item_thumb, item_module):
    """
    Like replay_bridge
    """
    plugin.setting['module_to_load'] = item_module

    # Let's go to the module file ...
    item_module = importlib.import_module(item_module)
    return item_module.live_entry(plugin, item_id, item_thumb)


def main():
    """
    Before running the plugin we need
    to check if there is any module
    to load on the fly
    """
    module_to_load = Script.setting['module_to_load']
    if module_to_load != '':
        try:
            importlib.import_module(module_to_load)
        except Exception:
            pass

    run()


if __name__ == '__main__':
    main()
