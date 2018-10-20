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
from codequick import Script


"""
The following dictionaries describe
the addon's tree architecture.
* Key: item id
* Value: item infos
    - callback: Callback function to run once this item is selected
    - thumb: Item thumb path relative to "media" folder
    - fanart: Item fanart path relative to "meia" folder
    - module: Item module to load in order to work (like 6play.py)
"""

ROOT = {
    'live_tv': {
        'callback': 'generic_menu',
        'thumb': ['live_tv.png']
    },
    'replay': {
        'callback': 'generic_menu',
        'thumb': ['replay.png']
    },
    'websites': {
        'callback': 'generic_menu',
        'thumb': ['websites.png']
    }
}


LIVE_TV = {
    'fr_live': {
        'callback': 'tv_guide_menu' if Script.setting.get_boolean('tv_guide') else 'generic_menu',
        'thumb': ['channels', 'fr.png']
    },
    'uk_live': {
        'callback': 'generic_menu',
        'thumb': ['channels', 'uk.png']
    }
}


REPLAY = {
    'fr_replay': {
        'callback': 'generic_menu',
        'thumb': ['channels', 'fr.png']
    },
    'be_replay': {
        'callback': 'generic_menu',
        'thumb': ['channels', 'be.png']
    },
    'uk_replay': {
        'callback': 'generic_menu',
        'thumb': ['channels', 'uk.png']
    }
}


FR_LIVE = {
    'm6': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', 'm6.png'],
        'fanart': ['channels', 'fr', 'm6_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'w9': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', 'w9.png'],
        'fanart': ['channels', 'fr', 'w9_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    '6ter': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', '6ter.png'],
        'fanart': ['channels', 'fr', '6ter_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'rtl2': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', 'rtl2.png'],
        'fanart': ['channels', 'fr', 'rtl2_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'fun_radio': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', 'fun_radio.png'],
        'fanart': ['channels', 'fr', 'fun_radio_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'mb': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'fr', 'mb.png'],
        'fanart': ['channels', 'fr', 'mb_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    }
}


UK_LIVE = {
    'questtv': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'uk', 'questtv.png'],
        'fanart': ['channels', 'uk', 'questtv_fanart.jpg'],
        'module': 'resources.lib.channels.uk.questod'
    },
    'questred': {
        'callback': 'live_bridge',
        'thumb': ['channels', 'uk', 'questred.png'],
        'fanart': ['channels', 'uk', 'questred_fanart.jpg'],
        'module': 'resources.lib.channels.uk.questod'
    }
}


FR_REPLAY = {
    'tf1': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'tf1.png'],
        'fanart': ['channels', 'fr', 'tf1_fanart.jpg'],
        'module': 'resources.lib.channels.fr.mytf1'
    },
    'tmc': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'tmc.png'],
        'fanart': ['channels', 'fr', 'tmc_fanart.jpg'],
        'module': 'resources.lib.channels.fr.mytf1'
    },
    'tf1-series-films': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'tf1-series-films.png'],
        'fanart': ['channels', 'fr', 'tf1-series-films_fanart.jpg'],
        'module': 'resources.lib.channels.fr.mytf1'
    },
    'tfx': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'tfx.png'],
        'fanart': ['channels', 'fr', 'tfx_fanart.jpg'],
        'module': 'resources.lib.channels.fr.mytf1'
    },
    'tfou': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'tfou.png'],
        'fanart': ['channels', 'fr', 'tfou_fanart.jpg'],
        'module': 'resources.lib.channels.fr.mytf1'
    },
    'm6': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'm6.png'],
        'fanart': ['channels', 'fr', 'm6_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'w9': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'w9.png'],
        'fanart': ['channels', 'fr', 'w9_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    '6ter': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', '6ter.png'],
        'fanart': ['channels', 'fr', '6ter_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'stories': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'stories.png'],
        'fanart': ['channels', 'fr', 'stories_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'comedy': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'comedy.png'],
        'fanart': ['channels', 'fr', 'comedy_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'rtl2': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'rtl2.png'],
        'fanart': ['channels', 'fr', 'rtl2_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    },
    'fun_radio': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'fr', 'fun_radio.png'],
        'fanart': ['channels', 'fr', 'fun_radio_fanart.jpg'],
        'module': 'resources.lib.channels.fr.6play'
    }
}

BE_REPLAY = {
    'rtl_tvi': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'rtl_tvi.png'],
        'fanart': ['channels', 'be', 'rtl_tvi_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'plug_rtl': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'plug_rtl.png'],
        'fanart': ['channels', 'be', 'plug_rtl_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'club_rtl': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'club_rtl.png'],
        'fanart': ['channels', 'be', 'club_rtl_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'rtl_info': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'rtl_info.png'],
        'fanart': ['channels', 'be', 'rtl_info_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'bel_rtl': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'bel_rtl.png'],
        'fanart': ['channels', 'be', 'bel_rtl_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'contact': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'contact.png'],
        'fanart': ['channels', 'be', 'contact_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    },
    'rtl_sport': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'be', 'rtl_sport.png'],
        'fanart': ['channels', 'be', 'rtl_sport_fanart.jpg'],
        'module': 'resources.lib.channels.be.rtlplaybe'
    }
}

UK_REPLAY = {
    'questod': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'uk', 'questod.png'],
        'fanart': ['channels', 'uk', 'questod_fanart.jpg'],
        'module': 'resources.lib.channels.uk.questod'
    },
    'dave': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'uk', 'dave.png'],
        'fanart': ['channels', 'uk', 'dave_fanart.jpg'],
        'module': 'resources.lib.channels.uk.uktvplay'
    },
    'really': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'uk', 'really.png'],
        'fanart': ['channels', 'uk', 'really_fanart.jpg'],
        'module': 'resources.lib.channels.uk.uktvplay'
    },
    'drama': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'uk', 'drama.png'],
        'fanart': ['channels', 'uk', 'drama_fanart.jpg'],
        'module': 'resources.lib.channels.uk.uktvplay'
    },
    'yesterday': {
        'callback': 'replay_bridge',
        'thumb': ['channels', 'uk', 'yesterday.png'],
        'fanart': ['channels', 'uk', 'yesterday_fanart.jpg'],
        'module': 'resources.lib.channels.uk.uktvplay'
    }
}

WEBSITES = {

}
