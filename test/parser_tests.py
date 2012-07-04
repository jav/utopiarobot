import htmlparser
import mock
import urllib2

import utopia

class login_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LoginParser()
                in_file = "test/login.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. sFor this test to work, you need a copy of the tested page atlink %s to a copy of the expected page. Missing file: %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_INIT" == self.parser.current_page)

        def test_login_fields(self):
                login_info = self.parser.get_login_info()
                assert("/shared/login/" == login_info['form']['action'])
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == login_info['inputs']['csrfmiddlewaretoken']['value'])
                assert('password' in login_info['inputs'])
                assert('username' in login_info['inputs'])


class lobby_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LobbyParser()
                in_file = "test/lobby.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_LOBBY" == self.parser.current_page)

        def test_lobby_fields(self):
                lobby_fields = self.parser.get_lobby_fields()
                assert("/wol/chooser/" == lobby_fields['chooser_link'])


class choose_prov_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ProvSelectParser()
                in_file = "test/prov_select.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)
        def test_page_enum(self):
                print("self.parser.current_page: %s" % self.parser.current_page)
                assert("PAGE_PROV" == self.parser.current_page)

        def test_choose_province_fields(self):
                chooser_fields = self.parser.get_choose_province_fields()
                assert("/wol/game/throne" == chooser_fields['chooser_link'])


class throne_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ThroneParser()
                in_file = "test/throne_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print("self.parser.current_page: %s" % self.parser.current_page)
                assert("PAGE_THRONE" == self.parser.current_page)

	def test_navigation(self):
                nav_links = self.parser.get_nav_links()

                links = { 'Throne'  :  '/wol/game/throne',
                          'Kingdom' :  '/wol/game/kingdom_details',
                          'News'    :  '/wol/game/province_news',
                          'Explore' :  '/wol/game/explore',
                          'Growth'  :  '/wol/game/build',
                          'Sciences':  '/wol/game/science',
                          'Military':  '/wol/game/train_army',
                          'Wizards' :  '/wol/game/wizards',
                          'Mystics' :  '/wol/game/enchantment',
                          'Thievery':  '/wol/game/thievery',
                          'War Room':  '/wol/game/send_armies',
                          'Aid'     :  '/wol/game/aid',
                          'Mail'    :  '/wol/mail/inbox/',
                          'Forum'   :  '/wol/kingdom_forum/topics/',
                          'Politics':  '/wol/game/vote',
                          'Rankings':  '/wol/game/ranking',
                          'Preferences': '/wol/game/preferences/',
                          'Taunts': '/wol/game/taunts'
                        }
                print nav_links
                for (title, link) in links.items():
                        print "%s == nav_links[%s] (%s)" % (link, title, nav_links[title])
                        assert(link == nav_links[title])

        def test_resources(self):
                resources = self.parser.get_resources()

                print resources
                assert(480594 == resources['Money'])
                assert(10065  == resources['Peasants'])
                assert(78481  == resources['Food'])
                assert(13244  == resources['Runes'])
                assert(213924 == resources['Net Worth'])
                assert(1398   == resources['Land'])
                assert(153.021   == resources['Net Worth/Acre'])


class mystics_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MysticParser()
                in_file = "test/mystic_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_MYSTIC" == self.parser.current_page)

        def test_form_inputs(self):
                print self.parser.mystic_form
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == self.parser.mystic_form['inputs']['csrfmiddlewaretoken']['value'])

        def test_available_spells(self):
                available_spells = self.parser.get_available_spells()
                print "available_spells:", available_spells
                print "Paradise:", available_spells['Paradise']
                print "Paradise:", available_spells['Paradise'][0]
                assert('Fertile Lands' in available_spells)
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


        def test_get_mana(self):
                assert(68 == self.parser.get_mana())

        def test_cast_paradise_success(self):
                parser = htmlparser.MysticParser()
                in_file = 'test/spell_paradise.html'
                try:
                        with open(in_file) as page:
                                parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)


                parser.parse(in_file)
                paradise_result = parser.get_spell_result()
                print "paradise_result: %s" % paradise_result
                assert(5 == paradise_result)
                mystic_form = parser.get_mystic_form()
                print mystic_form
                assert('88e2dabb2a8b615561e743d05668d47d' == mystic_form['inputs']['csrfmiddlewaretoken']['value'])

class mystics_advisor_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MysticAdvisorParser()
                in_file = "test/mystic_advisor.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_MYSTIC_ADVISOR" == self.parser.current_page)

        def test_get_active_spells(self):
                active_spells = self.parser.get_active_spells()
                print active_spells
                assert(15 == active_spells['Minor Protection'])
                assert(3 == active_spells["Nature's Blessing"])
                assert(1 == active_spells["Love and Peace"])
                assert(14 == active_spells["Fountain of Knowledge"])


class military_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MilitaryParser()
                in_file = "test/military_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_MILITARY" == self.parser.current_page)

        def test_get_soldiers(self):
                soldiers = self.parser.get_soldiers()
                print soldiers
                assert(1293 == soldiers)

        def test_get_troops(self):
                troops = self.parser.get_troops()
                print "troops:", troops

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
