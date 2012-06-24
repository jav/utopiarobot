import logging
import sgmllib
import string

log = logging.getLogger(__name__)

# pages = {
#     "PAGE_NONE": 0,
#     "PAGE_INIT": 1,
#     "PAGE_LOBBY": 2,
#     "PAGE_PROV": 3,
#     "PAGE_THRONE": 4
#}




class UtopiaParser(sgmllib.SGMLParser, object):
    parser_state = {}

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.last_page="PAGE_NONE"

    def start_head(self, attributes):
        self.parser_state['head'] = True

    def end_head(self):
        self.parser_state['head'] = False

    def start_title(self, attributes):
         self.parser_state['title'] = True

    def end_title(self):
        self.parser_state['title'] = False

    def handle_data(self, data):
        if 'head' in self.parser_state and self.parser_state['head']:
            if 'title' in self.parser_state and self.parser_state['title']:
                self.title = data
                log.debug("parsing page (title): %s"%self.title)

                if( "Home" in self.title ):
                    self.current_page = "PAGE_INIT"


class LoginParser(UtopiaParser):
    def __init__(self):
        super(LoginParser, self).__init__()
        self.login_info = {}
        self.current_input = None
        self.parser_state['login_form'] = ""

    def parse(self, s):
        "Parse the given string 's'."
        log.debug("parse()")
        self.feed(s)
        self.close()

    def start_div(self, attributes):
        for (name, val) in attributes:
            if 'id' == name and 'login' == val:
                self.login_info = {}
                self.parser_state['login_form'] = "DIV"

    def start_form(self, attributes):
        if "DIV" == self.parser_state['login_form']:
            self.parser_state['login_form'] = "FORM"
            log.debug("start_form(%s)"%attributes)
            self.login_info['form'] = dict(attributes)

    def end_form(self):
        self.parser_state['login_form'] = ""

    def start_input(self, attributes):
        if "FORM" == self.parser_state['login_form']:
            if 'inputs' not in self.login_info:
                self.login_info['inputs'] = {}

            attr_dict = dict(attributes)
            log.debug("Attr_dict: %s" % attr_dict)
            if 'name' in attr_dict:
                self.login_info['inputs'][attr_dict['name']] = attr_dict;
                self.current_input = self.login_info['inputs'][attr_dict['name']]
                log.debug("Appended: %s: %s" %( attr_dict['name'], self.current_input ))
            else:
                if not 'other_inputs' in self.login_info:
                    self.login_info['other_inputs'] = []
                self.login_info['other_inputs'].append(attr_dict)
                self.current_input = self.login_info['other_inputs'][-1]

    def end_input(self):
        self.current_input = None

    def handle_data(self, data):
        super(LoginParser, self).handle_data(data)
        # if "FORM" == self.parser_state['login_form']:
        #     if self.current_input is not None:
        #         self.current_input['value'] = data
        #         log.debug("%s: value: %s" % (self.current_input['name']  , self.current_input['value']   ))

    def get_login_info(self):
        log.debug("get_login_info() - fields: %s" % self.login_info)
        return self.login_info

class LobbyParser(UtopiaParser):
    parser_state = {}
    parser_state['form_depth'] = 0

    login_info = {}

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.last_page="PAGE_NONE"

    def parse(self, s):
        "Parse the given string 's'."
        log.debug("parse()")
        self.feed(s)
        self.close()

    def start_title(self, attributes):
         log.debug("handle_starttag()")
         self.parser_state['title'] = True

    def end_title(self):
        log.debug("handle_endtag()")
        self.parser_state['title'] = False

    def handle_data(self, data):
        if 'title' in self.parser_state and self.parser_state['title']:
            self.title = data
            log.debug("parsing page: %s"%self.title)
            #if the following breaks, you've used the wrong parser (or the page has changed format)
            assert("Lobby" in self.title)
            self.last_page="PAGE_LOBBY"

        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

        if 'lobby' in self.parser_state and isinstance( self.parser_state['lobby'], dict):
            if 'a' in self.parser_state['lobby']:
                if'World of Legends' in data:
                    self.parser_state['lobby']['chooser_link'] = self.parser_state['lobby']['a']['href']
                    log.debug("self.parser_state['lobby']['chooser_link'] = %s" % self.parser_state['lobby']['chooser_link'])

    def start_h2(self, attributes):
         self.parser_state['h2'] = True

    def end_h2(self):
        self.parser_state['h2'] = False

    def start_a(self, attributes):
        if "PAGE_LOBBY" == self.last_page:
            for (a,b) in attributes:
                if "href" == a:
                    if 'lobby' not in self.parser_state or not isinstance(self.parser_state['lobby'], dict):
                        self.parser_state['lobby'] = {}
                    self.parser_state['lobby']['a'] = {'href': b}
                    log.debug("self.parser_state['lobby']['a']['href'] = %s" % self.parser_state['lobby']['a']['href'] )

    def end_a(self):
        pass

    def get_lobby_fields(self):
        log.debug("get_lobby_fields() - fields: %d" % len( self.parser_state['lobby']))
        return self.parser_state['lobby']

class ProvSelectParser(UtopiaParser):
    parser_state = {}
    parser_state['form_depth'] = 0

    login_info = {}

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.last_page="PAGE_NONE"

    def parse(self, s):
        "Parse the given string 's'."
        log.debug("parse()")
        self.feed(s)
        self.close()

    def start_title(self, attributes):
         log.debug("handle_starttag()")
         self.parser_state['title'] = True

    def end_title(self):
        log.debug("handle_endtag()")
        self.parser_state['title'] = False

    def handle_data(self, data):
        if 'title' in self.parser_state and self.parser_state['title']:
            self.title = data
            log.debug("parsing page: %s"%self.title)
            #if the following breaks, you've used the wrong parser (or the page has changed format)
            assert("Age" in self.title)
            self.last_page="PAGE_PROV"

        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

    def start_h2(self, attributes):
         self.parser_state['h2'] = True

    def end_h2(self):
        self.parser_state['h2'] = False

    def start_a(self, attributes):
        if "PAGE_PROV" == self.last_page:
            for (a,b) in attributes:
                if "href" == a:
                    if 'choose_prov' not in self.parser_state or not isinstance(self.parser_state['choose_prov'], dict):
                        self.parser_state['choose_prov'] = {}
                    if b.endswith('throne'):
                        self.parser_state['choose_prov']['chooser_link'] = b
                        log.debug("self.parser_state['prov_chooser']['chooser_link']= %s" % self.parser_state['choose_prov']['chooser_link'] )

    def end_a(self):
        pass

    def get_choose_province_fields(self):
        log.debug("get_choose_provincefields() - fields: %d" % len( self.parser_state['choose_prov']))
        return self.parser_state['choose_prov']

class ThroneParserParser(UtopiaParser):
    parser_state = {}

    def __init__(self, verbose=0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.last_page="PAGE_NONE"

    def parse(self, s):
        "Parse the given string 's'."
        log.debug("parse()")
        self.feed(s)
        self.close()

    def start_title(self, attributes):
         log.debug("handle_starttag()")
         self.parser_state['title'] = True

    def end_title(self):
        log.debug("handle_endtag()")
        self.parser_state['title'] = False

    def handle_data(self, data):
        if 'title' in self.parser_state and self.parser_state['title']:
            self.title = data
            log.debug("parsing page: %s"%self.title)
            #if the following breaks, you've used the wrong parser (or the page has changed format)
            assert("Age" in self.title)
            self.last_page="PAGE_PROV"

        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

    def start_h2(self, attributes):
         self.parser_state['h2'] = True

    def end_h2(self):
        self.parser_state['h2'] = False

    def start_a(self, attributes):
        if "PAGE_PROV" == self.last_page:
            for (a,b) in attributes:
                if "href" == a:
                    if 'choose_prov' not in self.parser_state or not isinstance(self.parser_state['choose_prov'], dict):
                        self.parser_state['choose_prov'] = {}
                    if b.endswith('throne'):
                        self.parser_state['choose_prov']['chooser_link'] = b
                        log.debug("self.parser_state['prov_chooser']['chooser_link']= %s" % self.parser_state['choose_prov']['chooser_link'] )

    def end_a(self):
        pass

    def get_choose_province_fields(self):
        log.debug("get_choose_provincefields() - fields: %d" % len( self.parser_state['choose_prov']))
        return self.parser_state['choose_prov']
