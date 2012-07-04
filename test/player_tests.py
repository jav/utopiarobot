import htmlparser
import mock
import urllib2

import utopia

class player_tests(object):
    def setup(self):
        self.player = utopia.UPlayer()

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(htmlparser.MysticParser, 'get_nav_links')
    @mock.patch.object(utopia.UPlayer,'cache_page')
    def test_cast_paradise_success(self, mock_cache_page, mock_mysticparser_nav, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/spell_paradise.html').read()
        mock_mysticparser_nav.return_value = {'Mystics': '/wol/game/enchantment'}
        mock_cache_page.return_value = True

        print ("assert()")
        assert(5 == self.player.cast_spell('Paradise'))
        mystic_form = self.player.parser.get_mystic_form()
        print mystic_form
        assert('88e2dabb2a8b615561e743d05668d47d' == mystic_form['inputs']['csrfmiddlewaretoken']['value'])
