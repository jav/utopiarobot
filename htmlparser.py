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
    tick_ongoing = False
    nav_links = { 'Throne': '',
                  'Kingdom': '',
                  'News': '',
                  'Explore': '',
                  'Explore': '',
                  'Growth': '',
                  'Sciences': '',
                  'Military': '',
                  'Wizards': '',
                  'Mystics':   '',
                  'Thievery':  '',
                  'War Room':  '',
                  'Aid':       '',
                  'Mail'    :  '',
                  'Forum'   :  '',
                  'Politics':  '',
                  'Rankings':  '',
                  'Preferences': '',
                  'Taunts': ''

                 }
    resource_list = [ 'Money','Peasants','Food', 'Runes', 'Net Worth', 'Land', 'Net Worth/Acre']
    resources = {}

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.current_page="PAGE_NONE"

        self.parser_state['a'] = False
        self.parser_state['a_text_buffer'] = []
        self.parser_state['div'] = 0
        self.parser_state['div_navigation'] = 0
        self.parser_state['resource-bar'] = False
        self.resource_val = 0

    def start_head(self, attributes):
        self.parser_state['head'] = True

    def end_head(self):
        self.parser_state['head'] = False

    def start_title(self, attributes):
         self.parser_state['title'] = True

    def end_title(self):
        self.parser_state['title'] = False

    def start_h2(self, attributes):
        """TODO: Allow nesting, (which should be broken anyway) """
        self.parser_state['h2'] = True

    def end_h2(self):
        self.parser_state['h2'] = False

    def start_a(self, attributes):
        attr = dict(attributes)
        self.parser_state['a'] = attr
        self.parser_state['a_text_buffer'] = []

    def end_a(self):
        ## Collect what we harvested
        if 'div_navigation' in self.parser_state and self.parser_state['div_navigation']:
            # Navigation links
            label = " ".join(self.parser_state['a_text_buffer'])

            if self.parser_state['a']:
                if label in self.nav_links:
                    self.nav_links[label] = self.parser_state['a']['href']
                else:
                    log.debug("%s was not in self.nav_links" % label)


        self.parser_state['a'] = False

    def start_div(self, attributes):
        self.parser_state['div'] += 1
        attr = dict(attributes)
        if 'class' in attr and 'navigation' == attr['class']:
            self.parser_state['div_navigation'] = self.parser_state['div']

    def end_div(self):
        self.parser_state['div'] -= 1
        if self.parser_state['div'] < self.parser_state['div_navigation']:
            self.parser_state['div_navigation'] = False

    def start_table(self, attributes):
        attr = dict(attributes)
        if 'id' in attr and 'resource-bar' == attr['id']:
            self.parser_state['resource-bar'] = 0

    def end_table(self):
        if self.parser_state['resource-bar']:
            self.parser_state['resource-bar'] = False

    def start_th(self, attributes):
        pass

    def end_th(self):
        if self.parser_state['resource-bar'] is not False:
            resource_name = self.resource_list[self.parser_state['resource-bar']]
            val = self.resource_val.replace(",","")
            log.debug("val: %s", val)
            try:
                if "Net Worth/Acre" == resource_name:
                    self.resources[resource_name] = float(val)
                else:
                    self.resources[resource_name] = int(val)
            except ValueError as ex:
                pass
            self.parser_state['resource-bar'] += 1
            self.parser_state['resource-bar'] %= len(self.resource_list)

    def handle_data(self, data):
        if 'head' in self.parser_state and self.parser_state['head']:
            if 'title' in self.parser_state and self.parser_state['title']:
                self.title = data
                log.debug("(%s) : parsing page (title): %s"% (__name__, self.title))

                if( "Home" in self.title ):
                    self.current_page = "PAGE_INIT"
                if( "Lobby" in self.title ):
                    self.current_page="PAGE_LOBBY"
                if( "Age" in self.title ):
                    self.current_page="PAGE_PROV"
                if( "Throne Page" in self.title ):
                    self.current_page="PAGE_THRONE"

        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True


        if self.parser_state['a']:
            self.parser_state['a_text_buffer'].append(data)

        if self.parser_state['resource-bar'] is not False:
            self.resource_val = data

    def get_nav_links(self):
        return self.nav_links

    def get_resources(self):
        return self.resources

class LoginParser(UtopiaParser):
    def __init__(self):
        super(LoginParser, self).__init__()
        self.login_info = {}
        self.current_input = None
        self.parser_state['login_form'] = ""

    def parse(self, s):
        log.debug("%s : parse() - parser_state: %s" % (__name__, self.parser_state))
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

    def get_login_info(self):
        log.debug("get_login_info() - fields: %s" % self.login_info)
        return self.login_info

class LobbyParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(LobbyParser, self).__init__(self)
        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

    def handle_data(self, data):
        super(LobbyParser, self).handle_data(data)
        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

        if 'a' in self.parser_state:
            if'World of Legends' in data:
                self.parser_state['chooser_link'] = self.parser_state['a']['href']
                log.debug("self.parser_state['chooser_link'] = %s" % self.parser_state['chooser_link'])

    def start_h2(self, attributes):
         self.parser_state['h2'] = True

    def end_h2(self):
        self.parser_state['h2'] = False

    def start_a(self, attributes):
        if "PAGE_LOBBY" == self.current_page:
            for (a,b) in attributes:
                if "href" == a:
                    self.parser_state['a'] = {'href': b}
                    log.debug("self.parser_state['a']['href'] = %s" % self.parser_state['a']['href'] )

    def end_a(self):
        pass

    def get_lobby_fields(self):
        log.debug("get_lobby_fields() - fields: %d" % len( self.parser_state))
        return self.parser_state

class ProvSelectParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(ProvSelectParser, self).__init__()
        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.last_page="PAGE_NONE"

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

    def handle_data(self, data):
        super(ProvSelectParser, self).handle_data(data)

    def start_a(self, attributes):
        #super(ProvSelectParser, self).start_a(attributes)
        for (a,b) in attributes:
            if "href" == a:
                if b.endswith('throne'):
                    self.parser_state['chooser_link'] = b
                    log.debug("self.parser_state['prov_chooser']['chooser_link']= %s" % self.parser_state['chooser_link'] )

    def end_a(self):
        #super(ProvSelectParser, self).end_a()
        pass

    def get_choose_province_fields(self):
        log.debug("get_choose_provincefields() - fields: %d" % len( self.parser_state))
        return self.parser_state

class ThroneParser(UtopiaParser):
    parser_state = {}

    def __init__(self, verbose=0):
        super(ThroneParser, self).__init__()
        sgmllib.SGMLParser.__init__(self, verbose)
        self.last_page="PAGE_NONE"

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

