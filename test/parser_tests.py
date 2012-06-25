import htmlparser

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
                assert('password' in login_info['inputs'].keys())
                assert('username' in login_info['inputs'].keys())


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
                links = self.parser.get_links()

                links = [ ('Throne'  ,  'throne'),
                          ('Kingdom' ,  'kingdom_details'),
                          ('News'    ,  'province_news'),
                          ('Explore' ,  'explore'),
                          ('Growth'  ,  'build'),
                          ('Sciences',  'science'),
                          ('Military',  'train_army'),
                          ('Wizards' ,  'wizards'),
                          ('Mystics' ,  'enchantment'),
                          ('Thievery',  'thievery'),
                          ('War Room',  'send_armies'),
                          ('Aid'     ,  'aid')

                        ]

                for (title, link) in links:
                        assert( '/wol/game/'+ link == links[title])
