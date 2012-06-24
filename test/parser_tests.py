import htmlparser

class login_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LoginParser()
                page = open("test/login.html")
                self.parser.parse(page.read())

        def test_login_fields(self):
                login_info = self.parser.get_login_info()
                assert("/shared/login/" == login_info['form']['action'])
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == login_info['inputs']['csrfmiddlewaretoken']['value'])
                assert('password' in login_info['inputs'].keys())
                assert('username' in login_info['inputs'].keys())

class throne_parser_tests(object):
        def setup(self):
                pass

	def test_throne(self):
                pass
