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

        def test_login_fields(self):
                login_info = self.parser.get_login_info()
                assert("/shared/login/" == login_info['form']['action'])
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == login_info['inputs']['csrfmiddlewaretoken']['value'])
                assert('password' in login_info['inputs'].keys())
                assert('username' in login_info['inputs'].keys())


class lobby_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LobbyParser()
                page = open("test/lobby.html")

class throne_parser_tests(object):
        def setup(self):
                pass

	def test_throne(self):
                pass
