import htmlparser
import mock
import urllib2

import utopia

class player_tests(object):
    def setup(self):
        self.player = utopia.UPlayer()

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    def test_resources(self, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/throne_page.html').read()
        resources = self.player.get_resources()
        print "Resources:", resources
        assert(480594 == resources['Money'])
        assert(10065 == resources['Peasants'])
        assert(78481 == resources['Food'])
        assert(13244 == resources['Runes'])
        assert(213924 == resources['Net Worth'])
        assert(153.021 == resources['Net Worth/Acre'])


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    def test_available_spells(self, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_page.html').read()
        available_spells = self.player.get_available_spells()
        print "Available spells:", available_spells
        assert(('FERTILE_LANDS',815) == available_spells['Fertile Lands'])
        assert(('PARADISE', 4891) == available_spells['Paradise'])
        assert(('LOVE_AND_PEACE', 1141) == available_spells['Love and Peace'])
        assert(('SHADOW_LIGHT', 3098) == available_spells['Shadow Light'])
        assert(('NATURES_BLESSING', 978) == available_spells["Nature's Blessing"])
        assert(('INSPIRE_ARMY', 1793) == available_spells['Inspire Army'])
        assert(('FOUNTAIN_OF_KNOWLEDGE', 2527) == available_spells['Fountain of Knowledge'])
        assert(('TREE_OF_GOLD', 1304) == available_spells['Tree of Gold'])
        assert(('FERTILE_LANDS', 815) == available_spells['Fertile Lands'])
        assert(('WAR_SPOILS', 2364) == available_spells['War Spoils'])
        assert(('PARADISE', 4891) == available_spells['Paradise'])
        assert(('MAGIC_SHIELD', 815) == available_spells['Magic Shield'])
        assert(('ANONYMITY', 2119) == available_spells['Anonymity'])
        assert(('BUILDERS_BOON', 1630) == available_spells['Builders Boon'])
        assert(('MINOR_PROTECTION', 570) == available_spells['Minor Protection'])


    # @mock.patch('urllib2.urlopen')
    # @mock.patch('urllib2.Request')
    # def test_active_spells(self, mock_request, mock_urlopen):
    #     mock_urlopen.return_value = mock_request
    #     mock_request.read.return_value = open('test/mystic_advisor.html').read()
    #     available_spells = self.player.get_available_spells()
    #     print "Available spells:", available_spells
    #     assert(1==2)

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

