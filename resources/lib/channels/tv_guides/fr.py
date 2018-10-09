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

# Source: https://github.com/melmorabity/tv_grab_fr_telerama


class TeleramaXMLTVGrabber:
    """Implements grabbing and processing functionalities required to generate XMLTV data from
    Télérama mobile API.
    """

    _API_URL = 'https://api.telerama.fr'
    _API_USER_AGENT = 'okhttp/3.2.0'
    _API_KEY = 'apitel-5304b49c90511'
    _API_SECRET = 'Eufea9cuweuHeif'
    _API_DEVICE = 'android_tablette'
    _API_ENCODING = 'UTF-8'
    _TELERAMA_PROGRAM_URL = 'http://www.telerama.fr'
    _RATING_ICON_URL_TEMPLATE = 'http://television.telerama.fr/sites/tr_master/themes/tr/html/' \
                                'images/tv/-{}.png'

    _TELERAMA_TIMEZONE = pytz.timezone('Europe/Paris')
    _TELERAMA_START_TIME = datetime.time(6, 0)
    _TELERAMA_DATE_FORMAT = '%Y-%m-%d'
    _TELERAMA_TIME_FORMAT = '{} %H:%M:%S'.format(_TELERAMA_DATE_FORMAT)
    _XMLTV_DATETIME_FORMAT = '%Y%m%d%H%M%S %z'

    _MAX_PROGRAMS_PER_PAGE = 100
    _MAX_DAYS = 13

    _XMLTV_CREDIT_ROLES = {
        'Acteur': 'actor',
        'Auteur': 'writer',
        'Autre Invité': 'guest',
        'Autre présentateur': 'presenter',
        'Compositeur': 'composer',
        'Créateur': 'writer',
        'Dialogue': 'writer',
        'Guest star': 'guest',
        'Interprète': 'actor',
        'Invité vedette': 'guest',
        'Invité': 'guest',
        'Metteur en scène': 'director',
        'Musique': 'composer',
        'Origine Scénario': 'presenter',
        'Présentateur vedette': 'presenter',
        'Présentateur': 'presenter',
        'Réalisateur': 'director',
        'Scénario': 'writer',
        'Scénariste': 'writer',
        'Voix Off VF': 'actor',
        'Voix Off VO': 'actor'
    }

    _ETSI_PROGRAM_CATEGORIES = {
        'Divertissement': 'Variety show',
        'Documentaire': 'Documentary',
        'Film': 'Movie / Drama',
        'Jeunesse': "Children's / Youth programmes",
        'Magazine': 'Magazines / Reports / Documentary',
        'Musique': 'Music / Ballet / Dance',
        'Sport': 'Sports',
        'Série': 'Movie / Drama',
        'Téléfilm': 'Movie / Drama'
    }

    # http://www.microsoft.com/typography/unicode/1252.htm
    _WINDOWS_1252_UTF_8 = {
        u"\x80": u"\u20AC",  # EURO SIGN
        u"\x82": u"\u201A",  # SINGLE LOW-9 QUOTATION MARK
        u"\x83": u"\u0192",  # LATIN SMALL LETTER F WITH HOOK
        u"\x84": u"\u201E",  # DOUBLE LOW-9 QUOTATION MARK
        u"\x85": u"\u2026",  # HORIZONTAL ELLIPSIS
        u"\x86": u"\u2020",  # DAGGER
        u"\x87": u"\u2021",  # DOUBLE DAGGER
        u"\x88": u"\u02C6",  # MODIFIER LETTER CIRCUMFLEX ACCENT
        u"\x89": u"\u2030",  # PER MILLE SIGN
        u"\x8A": u"\u0160",  # LATIN CAPITAL LETTER S WITH CARON
        u"\x8B": u"\u2039",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        u"\x8C": u"\u0152",  # LATIN CAPITAL LIGATURE OE
        u"\x8E": u"\u017D",  # LATIN CAPITAL LETTER Z WITH CARON
        u"\x91": u"\u2018",  # LEFT SINGLE QUOTATION MARK
        u"\x92": u"\u2019",  # RIGHT SINGLE QUOTATION MARK
        u"\x93": u"\u201C",  # LEFT DOUBLE QUOTATION MARK
        u"\x94": u"\u201D",  # RIGHT DOUBLE QUOTATION MARK
        u"\x95": u"\u2022",  # BULLET
        u"\x96": u"\u2013",  # EN DASH
        u"\x97": u"\u2014",  # EM DASH
        u"\x98": u"\u02DC",  # SMALL TILDE
        u"\x99": u"\u2122",  # TRADE MARK SIGN
        u"\x9A": u"\u0161",  # LATIN SMALL LETTER S WITH CARON
        u"\x9B": u"\u203A",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        u"\x9C": u"\u0153",  # LATIN SMALL LIGATURE OE
        u"\x9E": u"\u017E",  # LATIN SMALL LETTER Z WITH CARON
        u"\x9F": u"\u0178",  # LATIN CAPITAL LETTER Y WITH DIAERESIS
    }

    def __init__(self, generator=None, generator_url=None, logger=None):
        self._logger = logger or logging.getLogger(__name__)

        initialization_data = self._get_initialization_data()
        self._channels = {self._telerama_to_xmltv_id(c['id']): {'display_name': c['nom'],
                                                                'url': c['link'],
                                                                'icon': c['logo'],
                                                                'telerama_id': c['id']}
                          for c in initialization_data['donnees']['chaines']}
        self._categories = {c['id']: c['libelle'] for c in initialization_data['donnees']['genres']}

        self._generator = generator
        self._generator_url = generator_url

    def _query_telerama_api(self, procedure, **query):
        """Query the Télérama API."""

        # Authentication method taken from https://github.com/zubrick/tv_grab_fr_telerama
        updated_query = dict(query)
        updated_query['appareil'] = self._API_DEVICE
        signing_string = procedure + ''.join(sorted([k + str(v) for k, v in updated_query.items()]))
        signature = hmac.new(self._API_SECRET.encode(), signing_string.encode(),
                             hashlib.sha1).hexdigest()
        updated_query['api_signature'] = signature
        updated_query['api_cle'] = self._API_KEY

        url = '{}{}?{}'.format(self._API_URL, procedure, urllib.parse.urlencode(updated_query))

        self._logger.debug('Retrieving URL %s', url)

        with requests.Session() as session:
            response = session.get(url, headers={'User-agent': self._API_USER_AGENT})
            return response

    @staticmethod
    def _telerama_to_xmltv_id(telerama_id):
        """Convert a Télérama channel ID to a valid XMLTV channel ID."""

        return '{}.tv.telerama.fr'.format(telerama_id)

    def _get_initialization_data(self):
        """Retrieve Télérama initalization data, such as predefined program categories and available
        channels.
        """

        self._logger.debug('Getting available channels')
        response = self._query_telerama_api('/v1/application/initialisation')
        if response.status_code != 200:
            self._logger.error('Unable to retrieve initialisation data')
            response.raise_for_status()
        return response.json()

    def get_available_channels(self):
        """Return the list of all available channels from Télérama, as a dictionary."""

        return self._channels

    def _get_programs(self, xmltv_ids, date):
        """Get Télérama programs for a given channel and a given day."""

        self._logger.debug('Getting Télérama programs on %s', date)

        telerama_ids = [self._channels[xmltv_id]['telerama_id'] for xmltv_id in xmltv_ids]
        page = 1
        programs = []
        while True:
            response = self._query_telerama_api(
                '/v1/programmes/telechargement',
                dates=datetime.datetime.strftime(date, self._TELERAMA_DATE_FORMAT),
                id_chaines=','.join(str(i) for i in telerama_ids), page=page,
                nb_par_page=self._MAX_PROGRAMS_PER_PAGE
            )
            try:
                data = response.json()
                if response.status_code == 200:
                    programs += data.get('donnees', [])
                    page += 1
                    continue
                else:
                    data = response.json()
                    if response.status_code == 404 and data.get('error') and \
                       data.get('msg') == "Il n'y a pas de programmes.":
                        # No more program page available
                        break
            except ValueError:
                pass

            self._logger.error('Unable to retrieve program data for date %s', str(date))
            response.raise_for_status()

        return programs

    def _etsi_category(self, category):
        """Translate Télérama program category to ETSI EN 300 468 category."""

        etsi_category = self._ETSI_PROGRAM_CATEGORIES.get(category)
        if etsi_category is None:
            self._logger.warning('Télérama category "%s" has no defined ETSI equivalent', category)

        return etsi_category

    def _fix_xml_unicode_string(self, text):
        """Replace in a string all Windows-1252 specific chars to UTF-8 and delete non
        XML-compatible characters.
        """

        fixed_text = ''.join([self._WINDOWS_1252_UTF_8.get(c, c) for c in text])
        fixed_text = re.sub(r'[\x00-\x08\x0b\x0E-\x1F\x7F]', '', fixed_text)

        return fixed_text

    @staticmethod
    def _html_to_text(text):
        html_format = html2text.HTML2Text()
        html_format.ignore_emphasis = True
        html_format.body_width = False
        html_format.ignore_links = True
        return html_format.handle(text)

    def _parse_channel_xmltv(self, xmltv_id):
        """Convert a channel identified by its XMLTV ID to a XMLTV Element object."""

        display_name = self._channels[xmltv_id]['display_name']
        icon = self._channels[xmltv_id].get('icon')
        url = self._channels[xmltv_id].get('url')

        channel_xml = Element('channel', id=xmltv_id)
        display_name_xml = SubElement(channel_xml, 'display-name')
        display_name_xml.text = display_name
        if icon is not None:
            channel_xml.append(Element('icon', src=icon))
        if url is not None:
            url_xml = SubElement(channel_xml, 'url')
            url_xml.text = url

        return channel_xml

    def _parse_program_xmltv(self, program):
        """Convert a Télérama program entry to a XMLTV Element object."""

        program_xml = Element('programme')

        # Channel ID
        program_xml.set('channel', self._telerama_to_xmltv_id(program['id_chaine']))

        # Showview
        if program['showview']:
            program_xml.set('showview', program['showview'])

        # Start and stop time, for the current timezone
        start = self._TELERAMA_TIMEZONE.localize(
            datetime.datetime.strptime(program['horaire']['debut'], self._TELERAMA_TIME_FORMAT)
        )
        stop = self._TELERAMA_TIMEZONE.localize(
            datetime.datetime.strptime(program['horaire']['fin'], self._TELERAMA_TIME_FORMAT)
        )

        program_xml.set('start', datetime.datetime.strftime(start, self._XMLTV_DATETIME_FORMAT))
        program_xml.set('stop', datetime.datetime.strftime(stop, self._XMLTV_DATETIME_FORMAT))

        # Title
        title_xml = SubElement(program_xml, 'title')
        title_xml.text = program['titre']
        if program['titre_original']:
            title_xml.set('lang', 'fr')
            original_title_xml = SubElement(program_xml, 'title')
            original_title_xml.text = program['titre_original']

        # Sub-title
        if program['soustitre']:
            sub_title_xml = SubElement(program_xml, 'sub-title')
            sub_title_xml.text = program['soustitre']

        # Desc
        if program['resume']:
            desc_xml = SubElement(program_xml, 'desc', lang='fr')
            desc_xml.text = self._html_to_text(self._fix_xml_unicode_string(program['resume']))

        # Credits
        if 'intervenants' in program:
            credits_xml = Element('credits')

            directors = set()
            actors = set()
            writers = set()
            composers = set()
            presenters = set()
            guests = set()

            for credit in program['intervenants']:
                role = self._XMLTV_CREDIT_ROLES.get(credit['libelle'])
                if role is None:
                    if credit['libelle']:
                        self._logger.warning('Télérama role "%s" has no XMLTV equivalent',
                                             credit['libelle'])
                    continue
                name = credit['nom']
                if credit['prenom']:
                    name = '{} {}'.format(credit['prenom'], name)
                credit_xml = Element(role)
                credit_xml.text = name

                if role == 'director':
                    directors.add(credit_xml)
                elif role == 'actor':
                    actors.add(credit_xml)
                    if credit['role']:
                        credit_xml.set('role', credit['role'])
                elif role == 'writer':
                    writers.add(credit_xml)
                elif role == 'composer':
                    composers.add(credit_xml)
                elif role == 'presenter':
                    presenters.add(credit_xml)
                elif role == 'guests':
                    guests.add(credit_xml)

                for role_xml_list in directors, actors, writers, composers, presenters, guests:
                    for credit_xml in sorted(role_xml_list, key=lambda n: n.text):
                        credits_xml.append(credit_xml)

                if list(credits_xml):
                    program_xml.append(credits_xml)

        # Year
        if program['annee_realisation']:
            date_xml = SubElement(program_xml, 'date')
            date_xml.text = program['annee_realisation']

        # Categories
        category = self._categories.get(program['id_genre'])
        if program['id_genre'] is not None:
            etsi_category = self._etsi_category(category)
            if etsi_category is not None:
                category_xml = SubElement(program_xml, 'category')
                category_xml.text = etsi_category
            # Keep original category in French
            category_xml = SubElement(program_xml, 'category', lang='fr')
            category_xml.text = category
            # Add specific category
            if program['genre_specifique'] and category != program['genre_specifique']:
                category_xml = SubElement(program_xml, 'category', lang='fr')
                category_xml.text = program['genre_specifique']

        # Icon
        if 'vignettes' in program:
            program_xml.append(Element('icon', src=program['vignettes']['grande']))

        # URL
        if program['url']:
            url_xml = SubElement(program_xml, 'url')
            url_xml.text = '{}/{}'.format(self._TELERAMA_PROGRAM_URL, program['url'])

        # Episode/season
        if program['serie'] and program['serie']['numero_episode']:
            season = (program['serie'].get('saison', 1) or 1) - 1
            episode = program['serie']['numero_episode'] - 1

            episode_num_xml = SubElement(program_xml, 'episode-num', system='xmltv_ns')
            episode_num_xml.text = '{}.{}'.format(season, episode)
            if program['serie'].get('nombre_episode'):
                episode_num_xml.text += '/{}'.format(program['serie']['nombre_episode'])
            episode_num_xml.text += '.0/1'

        # Video format
        video_xml = Element('video')
        aspect = None
        if program['flags']['est_ar16x9']:
            aspect = '16:9'
        elif program['flags']['est_ar4x3']:
            aspect = '4:3'
        if aspect is not None:
            aspect_xml = SubElement(video_xml, 'aspect')
            aspect_xml.text = aspect
        if program['flags']['est_hd']:
            quality_xml = SubElement(video_xml, 'quality')
            quality_xml.text = 'HDTV'
        if list(video_xml):
            program_xml.append(video_xml)

        # Audio format
        stereo = None
        if program['flags']['est_dolby']:
            stereo = 'dolby'
        elif program['flags']['est_stereoar16x9'] or program['flags']['est_stereo']:
            stereo = 'stereo'
        elif program['flags']['est_vm']:
            stereo = 'bilingual'
        if stereo is not None:
            audio_xml = SubElement(program_xml, 'audio')
            stereo_xml = SubElement(audio_xml, 'stereo')
            stereo_xml.text = stereo

        # Check whether the program was previously shown
        if program['flags']['est_premdif'] or program['flags']['est_inedit']:
            program_xml.append(Element('premiere'))
        elif program['flags']['est_redif']:
            program_xml.append(Element('previously-shown'))
        elif program['flags']['est_derdif']:
            program_xml.append(Element('last-chance'))

        # Subtitles
        if program['flags']['est_stm']:
            program_xml.append(Element('subtitles', type='deaf-signed'))
        elif program['flags']['est_vost']:
            program_xml.append(Element('subtitles', type='onscreen'))

        # Rating
        if program['csa_full']:
            rating_xml = SubElement(program_xml, 'rating', system='CSA')
            rating_value_xml = SubElement(rating_xml, 'value')
            rating_value_xml.text = program['csa_full'][0]['nom_long']
            if program['csa_full'][0]['nom_court'] != 'TP':
                rating_icon = self._RATING_ICON_URL_TEMPLATE.format(
                    program['csa_full'][0]['nom_court']
                )
                rating_xml.append(Element('icon', src=rating_icon))

        # Star rating
        if program['note_telerama'] > 0:
            star_rating_xml = SubElement(program_xml, 'star-rating', system='Télérama')
            star_rating_value_xml = SubElement(star_rating_xml, 'value')
            star_rating_value_xml.text = '{}/5'.format(program['note_telerama'])

        # Review
        review = ''
        if program['critique']:
            review = self._html_to_text(program['critique'])
        if program['notule']:
            notule = self._html_to_text(self._fix_xml_unicode_string(program['notule']))
            if review:
                review = '{}\n\n{}'.format(notule, review)
            else:
                review = notule
        if review:
            review_xml = SubElement(program_xml, 'review', type='text', lang='fr')
            review_xml.text = review.strip()

        return program_xml

    def _get_xmltv_data(self, xmltv_ids, days=1, offset=0):
        """Get Télérama programs in XMLTV format as XML ElementTree object."""

        if days + offset > self._MAX_DAYS:
            self._logger.warning(
                'Grabber can only fetch programs up to %i days in the future',
                self._MAX_DAYS
            )
            days = min(self._MAX_DAYS - offset, self._MAX_DAYS)

        root_xml = Element('tv', attrib={'source-info-name': 'Télérama',
                                         'source-info-url': 'http://www.telerama.fr/',
                                         'source-data-url': self._API_URL})
        if self._generator is not None:
            root_xml.set('generator-info-name', self._generator)
        if self._generator_url is not None:
            root_xml.set('generator-info-url', self._generator_url)

        start = datetime.datetime.combine(datetime.date.today(), datetime.time(0),
                                          tzinfo=pytz.reference.LocalTimezone())
        start = start + datetime.timedelta(days=offset)
        stop = start + datetime.timedelta(days=days)

        # Dates to fetch from the Télérama API
        telerama_fetch_dates = [start.date() + datetime.timedelta(days=d) for d in range(days)]
        # Télérama data for a given day contain programs starting between 6:00 AM and 6:00 AM the
        # next day (Paris time)
        if start < self._TELERAMA_TIMEZONE.localize(
                datetime.datetime.combine(start, self._TELERAMA_START_TIME)
        ):
            telerama_fetch_dates.insert(0, start.date() - datetime.timedelta(days=1))
        elif stop > self._TELERAMA_TIMEZONE.localize(
                datetime.datetime.combine(stop, self._TELERAMA_START_TIME)
        ):
            telerama_fetch_dates.append(stop.date())

        programs_xml = []
        valid_xmltv_ids = set()
        for date in telerama_fetch_dates:
            for program in self._get_programs(xmltv_ids, date):
                program_xml = self._parse_program_xmltv(program)
                program_start = datetime.datetime.strptime(program_xml.get('start'),
                                                           self._XMLTV_DATETIME_FORMAT)
                program_stop = datetime.datetime.strptime(program_xml.get('stop'),
                                                          self._XMLTV_DATETIME_FORMAT)

                # Skip programs outside the fetch period
                if program_stop < start or program_start >= stop:
                    continue

                # Skip programs starting after 6:AM (Paris time) the next day to avoid duplicates
                if program_start >= self._TELERAMA_TIMEZONE.localize(
                        datetime.datetime.combine(date + datetime.timedelta(days=1),
                                                  self._TELERAMA_START_TIME)
                ):
                    continue

                xmltv_id = program_xml.get('channel')
                valid_xmltv_ids.add(xmltv_id)

                programs_xml.append(program_xml)

        # Keep only channels which have programs actually in the XMLTV result
        for xmltv_id in valid_xmltv_ids:
            root_xml.append(self._parse_channel_xmltv(xmltv_id))

        root_xml.extend(programs_xml)

        return ElementTree(root_xml)

    def write_xmltv(self, xmltv_ids, output_file, days=1, offset=0):
        """Grab Télérama programs in XMLTV format and write them to file."""

        self._logger.debug('Writing XMLTV program to file %s', output_file)

        xmltv_data = self._get_xmltv_data(xmltv_ids, days, offset)
        xmltv_data.write(output_file, encoding='UTF-8', xml_declaration=True, pretty_print=True)


_PROGRAM = 'tv_grab_fr_telerama'
__version__ = '2.2'
__url__ = 'https://github.com/melmorabity/tv_grab_fr_telerama'

_DESCRIPTION = 'France (Télérama)'
_CAPABILITIES = ['baseline', 'manualconfig']

_DEFAULT_DAYS = 1
_DEFAULT_OFFSET = 0

_DEFAULT_CONFIG_FILE = os.path.join(os.environ['HOME'], '.xmltv', _PROGRAM + '.conf')

_DEFAULT_OUTPUT = '/dev/stdout'


def _print_description():
    """Print the description for the grabber."""

    print(_DESCRIPTION)


def _print_version():
    """Print the grabber version."""

    print('This is {} version {}'.format(_PROGRAM, __version__))


def _print_capabilities():
    """Print the capabilities for the grabber."""

    print('\n'.join(_CAPABILITIES))


def _parse_cli_args():
    """Command line argument processing."""

    parser = argparse.ArgumentParser(
        description='get French television listings using Télérama mobile API in XMLTV format'
    )
    parser.add_argument('--description', action='store_true',
                        help='print the description for this grabber')
    parser.add_argument('--version', action='store_true', help='show the version of this grabber')
    parser.add_argument('--capabilities', action='store_true',
                        help='show the capabilities this grabber supports')
    parser.add_argument(
        '--configure', action='store_true',
        help='generate the configuration file by asking the users which channels to grab'
    )
    parser.add_argument(
        '--days', type=int, default=_DEFAULT_DAYS,
        help='grab DAYS days of TV data (default: %(default)s)'
    )
    parser.add_argument(
        '--offset', type=int, default=_DEFAULT_OFFSET,
        help='grab TV data starting at OFFSET days in the future (default: %(default)s)'
    )
    parser.add_argument(
        '--output', default=_DEFAULT_OUTPUT,
        help='write the XML data to OUTPUT instead of the standard output'
    )
    parser.add_argument(
        '--config-file', default=_DEFAULT_CONFIG_FILE,
        help='file name to write/load the configuration to/from (default: %(default)s)'
    )

    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument('--quiet', action='store_true',
                                 help='only print error-messages on STDERR')
    log_level_group.add_argument(
        '--debug', action='store_true',
        help='provide more information on progress to stderr to help in debugging'
    )

    return parser.parse_args()


def _read_configuration(config_file=_DEFAULT_CONFIG_FILE):
    """Load channel XMLTV IDs from the configuration file."""

    xmltv_ids = []
    with open(config_file, 'r') as config:
        for line in config:
            match = re.search(r'^\s*channel\s*=\s*(.+)\s*$', line)
            if match is not None:
                xmltv_ids.append(match.group(1))

    return xmltv_ids


def _write_configuration(xmltv_ids, config_file=_DEFAULT_CONFIG_FILE):
    """Write specified channels to the specified configuration file."""

    config_dir = os.path.dirname(os.path.abspath(config_file))
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    with open(config_file, 'w') as config:
        for xmltv_id in xmltv_ids:
            print('channel={}'.format(xmltv_id), file=config)


def _configure(available_channels, config_file=_DEFAULT_CONFIG_FILE):
    """Prompt channels to configure and write them into the configuration file."""

    xmltv_ids = []
    answers = ['yes', 'no', 'all', 'none']
    select_all = False
    select_none = False
    print('Select the channels that you want to receive data for.',
          file=sys.stderr)
    for xmltv_id, channel_data in available_channels.items():
        if not select_all and not select_none:
            while True:
                prompt = '{} [{} (default=no)] '.format(channel_data['display_name'],
                                                        ','.join(answers))
                answer = input(prompt).strip()
                if answer in answers or answer == '':
                    break
                print('invalid response, please choose one of {}'.format(','.join(answers)),
                      file=sys.stderr)
            select_all = answer == 'all'
            select_none = answer == 'none'
        if select_all or answer == 'yes':
            xmltv_ids.append(xmltv_id)
        if select_all:
            print('{} yes'.format(channel_data['display_name']), file=sys.stderr)
        elif select_none:
            print('{} no'.format(channel_data['display_name']), file=sys.stderr)

    _write_configuration(xmltv_ids, config_file)


def _main():
    """Main execution path."""

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())

    args = _parse_cli_args()

    if args.version:
        _print_version()
        sys.exit()

    if args.description:
        _print_description()
        sys.exit()

    if args.capabilities:
        _print_capabilities()
        sys.exit()

    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)

    telerama = TeleramaXMLTVGrabber(generator=_PROGRAM, generator_url=__url__, logger=logger)
    available_channels = telerama.get_available_channels()

    logger.info('Using configuration file %s', args.config_file)

    if args.configure:
        _configure(available_channels, args.config_file)
        sys.exit()

    if not os.path.isfile(args.config_file):
        logger.error('You need to configure the grabber by running it with --configure')
        sys.exit(1)

    xmltv_ids = _read_configuration(args.config_file)
    if not xmltv_ids:
        logger.error('Configuration file %s is empty, delete and run with --configure',
                     args.config_file)

    telerama.write_xmltv(xmltv_ids, args.output, days=args.days, offset=args.offset)