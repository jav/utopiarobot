import logging
import sgmllib

log = logging.getLogger(__name__)

PAGE_NONE=0
PAGE_LOGIN=1
PAGE_CHOOSE_WORLD=2
PAGE_CHOOSE_ACCOUNT=3
PATE_THRONE=4

class Parser(sgmllib.SGMLParser):
    "A simple parser class."

    parserState = {}
    parserState['form_depth'] = 0

    login_info = {}

    currentPage = PAGE_NONE

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()

    def start_form(self, attributes):
        log.debug("start_form(%s)"%attributes)
        self.parserState['form_depth'] += 1
        for name, value in attributes:
            if name == "action":
                print "start_form(%s)"% attributes, value
                self.parserState['login_form'] = self.parserState['form_depth']
                log.debug(attributes)
                self.login_info['form'] = dict(attributes)
                log.debug( self.login_info['form'])

    def end_form(self):
        if 'login_form' in self.parserState.keys():
            if self.parserState['login_form'] <= self.parserState['form_depth']:
                self.parserState['login_form'] = -1

        self.parserState['form_depth'] -= 1

    def start_input(self, attributes):
        if self.parserState['login_form'] > 0:
            item = {}
            for k, v in attributes:
                item[k] = v
            if 'name' in item.keys():
                self.login_info[item['name']] = item
            else:
                if not 'other' in self.login_info or not isinstance( self.login_info['other'], list):
                    self.login_info['other'] = []
                self.login_info['other'].append(dict(item))



    def get_login_fields(self):
        return self.login_info
