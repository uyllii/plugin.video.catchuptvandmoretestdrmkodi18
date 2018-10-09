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

from codequick import Route, Resolver, Listitem, run, Script

from resources.lib.skeleton import *
from resources.lib.labels import *
from resources.lib import common


@Route.register
def root(plugin):
    """
    root is the entry point
    of Catch-up TV & More
    """
    # First menu to build is the root menu
    # (see ROOT dictionnary in skeleton.py)
    return generic_menu(plugin, 'ROOT')


@Route.register
def generic_menu(plugin, item_id):
    """
    Build a generic addon menu
    with all not hidden items
    """

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
        if plugin.setting.get_boolean(item_id):

            # Get order value in settings file
            item_order = plugin.setting.get_int(item_id + '.order')

            item = (
                item_order,
                item_id,
                item_infos
            )

            menu.append(item)

    # We sort the menu according to the item_order values
    menu = sorted(menu, key=lambda x: x[0])

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
        if 'thumb' in item_infos:
            item.art["thumb"] = common.get_item_media_path(
                item_infos['thumb'])

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
def replay_bridge(plugin, item_id, item_module):
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
def website_bridge(plugin, item_id, item_module):
    """
    Like replay_bridge
    """
    plugin.setting['module_to_load'] = item_module

    # Let's go to the module file ...
    item_module = importlib.import_module(item_module)
    return item_module.website_entry(plugin, item_id)


@Resolver.register
def live_bridge(plugin, item_id, item_module):
    """
    Like replay_bridge
    """
    plugin.setting['module_to_load'] = item_module

    # Let's go to the module file ...
    item_module = importlib.import_module(item_module)
    return item_module.live_entry(plugin, item_id)


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
