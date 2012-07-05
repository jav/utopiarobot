from utopia_robot.robot import UtopiaRobot, htmlparser
import mock
import urllib2



class player_tests(object):
    def setup(self):
        self.player = UtopiaRobot()

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_resources(self, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/throne_page.html').read()
        mock_cache_page.return_value = True
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
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_mana(self, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_page.html').read()
        mock_cache_page.return_value = True

        mana = self.player.get_mana()
        print "Mana:", mana
        assert(68  == mana)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_available_spells(self, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_page.html').read()
        mock_cache_page.return_value = True
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


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    def test_active_spells(self, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_advisor.html').read()
        active_spells = self.player.get_active_spells()
        print "Active spells:", active_spells
        assert(14 == active_spells['Fountain of Knowledge'])
        assert( 3 == active_spells["Nature's Blessing"])
        assert(15 == active_spells['Minor Protection'])
        assert( 1 == active_spells['Love and Peace'])


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(htmlparser.MysticParser, 'get_nav_links')
    @mock.patch.object(UtopiaRobot,'cache_page')
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

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_get_troops(self, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_page.html').read()
        mock_cache_page.return_value = True

        troops = self.player.get_troops()

        print "troops:", troops
        assert(1530 == troops['o-spec']['home'])
        assert(1530 == troops['o-spec']['home'])
        assert(807 == troops['o-spec']['training'])
        assert(350 == troops['o-spec']['cost'])
        assert(806 == troops['o-spec']['max'])

        assert(839 == troops['d-spec']['home'])
        assert(165 == troops['d-spec']['training'])
        assert(350 == troops['d-spec']['cost'])
        assert(806 == troops['d-spec']['max'])

        assert(11184 == troops['elite']['home'])
        assert(53 == troops['elite']['training'])
        assert(500 == troops['elite']['cost'])
        assert(564 == troops['elite']['max'])

        assert(2222 == troops['thief']['home'])
        assert(0 == troops['thief']['training'])
        assert(500 == troops['thief']['cost'])
        assert(564 == troops['thief']['max'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_get_soldiers(self, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_page.html').read()
        mock_cache_page.return_value = True

        soldiers = self.player.get_soldiers()

        print "soldiers:", soldiers
        assert(1293 == soldiers)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(htmlparser.MilitaryParser, 'get_nav_links')
    @mock.patch.object(UtopiaRobot,'cache_page')
    def test_train_troops(self, mock_cache_page, mock_militaryparser_nav, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_trained.html').read()
        mock_militaryparser_nav.return_value = {'Military': '/wol/game/train_army'}
        mock_cache_page.return_value = True

        military={}
        military['o-spec'] = 44
        military['d-spec'] = 33
        military['elite'] = 22
        military['thief'] = 11

        print "Want to train: %s" % military
        military_result = self.player.train_military(military)
        print "Militarty result: %s" % military_result
        assert(44 == military_result['o-spec'])
        assert(33 == military_result['d-spec'])
        assert(22 == military_result['elite'])
        assert(11 == military_result['thief'])
        print "self.player.get_draft_rate():", self.player.get_draft_rate()
        print "self.player.get_draft_rate()[1]:", self.player.get_draft_rate()[1]
        assert('AGGRESSIVE' == self.player.get_draft_rate()[1])

        military_form = self.player.parser.get_military_form()
        print military_form
        assert('88e2dabb2a8b615561e743d05668d47d' == military_form['inputs']['csrfmiddlewaretoken']['value'])

#train form-data
# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# draft_rate:AGGRESSIVE
# draft_target:66
# wage_rate:200
# unit-quantity_0:1
# unit-quantity_1:2
# unit-quantity_2:3
# unit-quantity_3:4
# train:Train troops

#change recruitlvl
# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# draft_rate:NORMAL
# draft_target:65
# wage_rate:201
# unit-quantity_0:
# unit-quantity_1:
# unit-quantity_2:
# unit-quantity_3:
# train:Train troops
