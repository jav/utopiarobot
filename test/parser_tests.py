import htmlparser
import mock
import urllib2

class login_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LoginParser()
                in_file = "test/login.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "For this test to work, you need to link %s to a copy of the expected page (typically found in the page_cache dir). In the future, I'll provide some (correclty formatted) premade template." % in_file

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
                        print "For this test to work, you need to link %s to a copy of the expected page (typically found in the page_cache dir). In the future, I'll provide some (correclty formatted) premade template." % in_file

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
                        print "For this test to work, you need to link %s to a copy of the expected page (typically found in the page_cache dir). In the future, I'll provide some (correclty formatted) premade template." % in_file

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
                        print "For this test to work, you need to link %s to a copy of the expected page (typically found in the page_cache dir). In the future, I'll provide some (correclty formatted) premade template." % in_file

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
                        print "For this test to work, you need to link %s to a copy of the expected page (typically found in the page_cache dir). In the future, I'll provide some (correclty formatted) premade template." % in_file

        def test_page_enum(self):
                assert("PAGE_MYSTIC" == self.parser.current_page)

        def test_form_inputs(self):
                print self.parser.mystic_form
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == self.parser.mystic_form['inputs']['csrfmiddlewaretoken']['value'])

        @mock.patch('htmlparser.MysticParser')
        def test_available_spells(self):
                available_spells = self.parser.get_available_spells()
                print "available_spells:", available_spells
                assert('Fertile Lands' in available_spells)
                assert(('FERTILE_LANDS',815) == available_spells['Fertile Lands'])

        def test_get_mana(self):
                #assert(68 == self.parser.get_mana())
                pass

        @mock.patch('htmlparser.MysticParser')
        @mock.patch('urllib2.Request')
        def test_cast_paradise(self, mock_request, mock_mysticparser):
                mock_mysticparser.test_handle("FOOBAR")
                pass

