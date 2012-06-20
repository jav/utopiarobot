import logging
import sgmllib
import string

log = logging.getLogger(__name__)

# pages = {
#     "PAGE_NONE": 0,
#     "PAGE_INIT": 1,
#     "PAGE_LOBBY": 2,
#     "PAGE_CHOOSE_ACCOUNT": 3,
#     "PAGE_THRONE": 4
#}

class UtopiaParser(sgmllib.SGMLParser):
    "A simple parser class."

    parserState = {}
    parserState['form_depth'] = 0

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
         self.parserState['title'] = True

    def end_title(self):
        log.debug("handle_endtag()")
        self.parserState['title'] = False

    def handle_data(self, data):
        if 'title' in self.parserState.keys() and self.parserState['title']:
            self.title = data
            #self.title = data.strip().translate(string.maketrans("\n", " ")) 
            log.info("parsing page: %s"%self.title)
            log.debug("parsing page: %s"%self.title)
            if "Home" in self.title:
                self.last_page="PAGE_INIT"
            elif "Lobby" in self.title:
                self.last_page="PAGE_LOBBY"

        if 'h2' in self.parserState.keys() and self.parserState['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

        if 'lobby' in self.parserState.keys() and isinstance( self.parserState['lobby'], dict):
            if 'a' in self.parserState['lobby'].keys():
                if'World of Legends' in data:
                    self.parserState['lobby']['chooser_link'] = self.parserState['lobby']['a']['href']
                    log.debug("self.parserState['lobby']['chooser_link'] = %s" % self.parserState['lobby']['chooser_link'])

    def start_h2(self, attributes):
         self.parserState['h2'] = True

    def end_h2(self):
        self.parserState['h2'] = False

    def start_a(self, attributes):
        if "PAGE_LOBBY" == self.last_page:
            for (a,b) in attributes:
                if "href" == a:
                    if 'lobby' not in self.parserState.keys() or not isinstance(self.parserState['lobby'], dict):
                        self.parserState['lobby'] = {}
                    self.parserState['lobby']['a'] = {'href': b}
                    log.debug("self.parserState['lobby']['a']['href'] = %s" % self.parserState['lobby']['a']['href'] )

    def end_a(self):
        pass

    def start_form(self, attributes):
        log.debug("start_form(%s)"%attributes)
        self.parserState['form_depth'] += 1
        log.debug("form_depth: %s" % self.parserState['form_depth'])
        for name, value in attributes:
            if name == "action":
                print "start_form(%s)"% attributes, value
                self.parserState['login_form'] = self.parserState['form_depth']
                log.debug(attributes)
                self.login_info['form'] = dict(attributes)
                log.debug( self.login_info['form'])

    def end_form(self):
        log.debug("end_form()")
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
        log.debug("get_login_fields() - fields: %d" % len(self.login_info.keys()))
        return self.login_info

    def get_lobby_fields(self):
        log.debug("get_lobby_fields() - fields: %d" % len( self.parserState['lobby']))
        return self.parserState['lobby']
