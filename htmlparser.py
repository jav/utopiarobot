import  logging
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
        self.parser_state['div'] = {}
        self.parser_state['div_depth'] = 0
        self.parser_state['div_navigation'] = {}
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

    def start_h1(self, attributes):
        self.parser_state['h1'] = True

    def end_h1(self):
        self.parser_state['h1'] = False

    def start_h2(self, attributes):
        self.parser_state['h2'] = dict(attributes)

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
                    #log.debug("%s was not in self.nav_links" % label)
                    pass

        self.parser_state['a'] = False

    def start_div(self, attributes):
        self.parser_state['div_depth'] += 1
        self.parser_state['div'] = dict(attributes)
        self.parser_state['div']['depth'] = self.parser_state['div_depth']
        attr = dict(attributes)
        if 'class' in attr and 'navigation' == attr['class']:
            self.parser_state['div_navigation'] = self.parser_state['div']


    def end_div(self):
        self.parser_state['div'] = {}
        self.parser_state['div_depth'] -= 1
        if 'depth' in self.parser_state['div_navigation'] and self.parser_state['div_depth'] < self.parser_state['div_navigation']['depth']:
            self.parser_state['div_navigation'] = {}

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
            try:
                if "Net Worth/Acre" == resource_name:
                    self.resources[resource_name] = float(val)
                else:
                    self.resources[resource_name] = int(val)
            except ValueError as ex:
                pass
            self.parser_state['resource-bar'] += 1
            self.parser_state['resource-bar'] %= len(self.resource_list)

    def start_td(self, attributes):
        pass

    def end_td(self):
        pass

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
                    #THRONE will be overriden if any link in 'navigation' is <h1>
                    self.current_page="PAGE_THRONE"
                if( "Mystic Circle" in self.title ):
                    self.current_page="PAGE_MYSTIC"
                log.debug("SAVED PAGE: %s" % self.current_page)
        if 'h2' in self.parser_state and self.parser_state['h2']:
            if 'The game is currently ticking. Please wait a few moments' in  data:
                self.tick_ongoing = True

        if 'div' in self.parser_state and 'class' in self.parser_state['div'] and 'game-header' in self.parser_state['div']['class']:
            if 'a' not in self.parser_state or not self.parser_state['a']:
                if 'h1' in self.parser_state and self.parser_state['h1']:
                    if 'PAGE_THRONE' == self.current_page:
                        if 'Throne' == data:
                            self.current_page = 'PAGE_THRONE'
                        elif 'State' == data:
                            self.current_page = 'PAGE_STATE_ADVISOR'
                        elif 'Military' == data:
                            self.current_page = 'PAGE_MILITARY_ADVISOR'
                        elif 'Buildings' == data:
                            self.current_page = 'PAGE_GROWTH_ADVISOR'
                        elif 'Science' == data:
                            self.current_page = 'PAGE_SCIENCE_ADVISOR'
                        elif 'Mystics' == data:
                            self.current_page = 'PAGE_MYSTIC_ADVISOR'
                        elif 'History' == data:
                            self.current_page = 'PAGE_HISTORY_ADVISOR'

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
        super(LoginParser, self).start_div(attributes)
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
        self.current_page="PAGE_NONE"

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

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
    def __init__(self, verbose=0):
        super(ThroneParser, self).__init__()
        sgmllib.SGMLParser.__init__(self, verbose)
        self.last_page="PAGE_NONE"

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()


class MysticParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(MysticParser, self).__init__()
        sgmllib.SGMLParser.__init__(self, verbose)
        self.last_page="PAGE_NONE"
        self.available_spells = {}
        self.spell_result = [None, None]
        self.parser_state['mystic_form'] = False
        self.parser_state['select_spell'] = False
        self.parser_state['available_spells'] = []
        self.parser_state['current_spell'] = None
        self.parser_state['spell_success'] = False
        self.parser_state['spell_fail'] = False
        self.parser_state['th'] = False
        self.parser_state['td'] = False
        self.parser_state['mana'] = False

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

    def start_form(self, attributes):
        attr = dict(attributes)
        if "" == attr['action'] and "POST" == attr['method'] and 'name' not in attr:
            self.parser_state['mystic_form'] = True
            self.mystic_form = {}
            self.mystic_form['form'] = attr
            self.mystic_form['inputs'] = {}
            self.mystic_form['other_inputs'] = []

    def end_form(self):
        # collect all the info in the form
        if self.parser_state['mystic_form']:
            for spell in self.parser_state['available_spells']:
                spell_str = " ".join(spell[0])
                (spell_name, _, cost) = spell_str.partition("(")
                (cost, _, _) = cost.partition(")")
                cost = cost.strip().replace(",","").replace("runes","")
                spell_name = spell_name.strip()
                spell_code = spell[1].replace(",","")
                if '----' in spell_name:
                    continue
                #log.debug(" available_spells[ %s ] = ( %s, %s)" % (spell_name, spell[1], cost))
                self.available_spells[ spell_name ] = (spell_code, int(cost))
            self.parser_state['mystic_form'] = False

    def start_input(self, attributes):
        attr = dict(attributes)
        if self.parser_state['mystic_form']:
            if 'name' not in attr:
                self.mystic_form['other_inputs'].append(attr)
            else:
                self.mystic_form['inputs'][attr['name']] = attr

    def start_select(self, attributes):
        attr = dict(attributes)
        if 'name' in attr and 'spell' == attr['name']:
            self.parser_state['select_spell'] = True

    def end_select(self):
        if self.parser_state['select_spell']:
            self.parser_state['select_spell'] = False

    def start_option(self, attributes):
        attr = dict(attributes)
        if self.parser_state['select_spell']:
            if self.parser_state['current_spell'] is not None:
                self.parser_state['available_spells'].append(self.parser_state['current_spell'] )
            self.parser_state['current_spell'] = ( [], attr['value'])


    def start_div(self, attributes):
        super(MysticParser, self).start_div(attributes)
        attr = dict(attributes)
        if 'class' in attr and 'good message' == attr['class']:
            self.parser_state['spell_success'] = True

    def end_div(self):
        super(MysticParser, self).end_div()
        if self.parser_state['spell_success']:
            log.debug("end_div(): spell_success-collect")
            #collect string
            vals = []
            for word in self.parser_state['spell_success'].split(" "):
                #If it's a number, runes or result
                word = word.replace(",","")
                try:
                    val = int(word)
                    vals.append(val)
                except:
                    pass
            self.spell_result = vals[1]
            log.debug("self.spell_result: %s" % self.spell_result)
            self.parser_state['spell_success'] = False

    def start_th(self,attributes):
        super(MysticParser, self).start_th(attributes)
        self.parser_state['th'] = True

    def end_th(self, attributes):
        super(MysticParser, self).end_th()
        if self.parser_state['th']:
            self.parser_state['th'] = False

    def start_td(self, attributes):
        super(MysticParser, self).start_td(attributes)
        self.parser_state['td'] = True

    def end_th(self):
        super(MysticParser, self).end_th()
        if self.parser_state['td']:
            self.parser_state['td'] = False

    def handle_data(self, data):
        super(MysticParser, self).handle_data(data)
        if self.parser_state['select_spell'] and self.parser_state['current_spell'] is not None:
            self.parser_state['current_spell'][0].append(data)
        if self.parser_state['spell_success'] is not False:
            self.parser_state['spell_success'] = data
        if self.parser_state['th'] and self.parser_state['td']:
            if self.parser_state['mana']:
                self.mana = int(data.replace('%',''))
                self.parser_state['mana'] = False
            if "Mana" == data:
                self.parser_state['mana'] = True


    def get_mystic_form(self):
        return self.mystic_form

    def get_available_spells(self):
        log.debug("get_available_spells()")
        return self.available_spells

    def get_mana(self):
        return self.mana

    def get_spell_result(self):
        log.debug("get_spell_result: %s" % self.spell_result)
        return self.spell_result


class MysticAdvisorParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(MysticAdvisorParser, self).__init__()
        sgmllib.SGMLParser.__init__(self, verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['MysticAdvisorParser'] = {}
        self.parser_state['MysticAdvisorParser']['th'] = False
        self.parser_state['MysticAdvisorParser']['td'] = False
        self.parser_state['MysticAdvisorParser']['div'] = False
        self.parser_state['MysticAdvisorParser']['div_depth'] = 0
        self.current_spell = {}
        self.active_spells = {}

    def parse(self, s):
        log.debug("%s : parse() - state: %s"% (__name__, self.parser_state))
        self.feed(s)
        self.close()

    def start_div(self, attributes):
        super(MysticAdvisorParser, self).start_div(attributes)
        self.parser_state['div_depth'] += 1
        self.parser_state['MysticAdvisorParser']['div'] = dict(attributes)
        self.parser_state['MysticAdvisorParser']['div']['depth'] =  self.parser_state['MysticAdvisorParser']['div_depth']
        if 'class' in self.parser_state['MysticAdvisorParser']['div'] and 'good' == self.parser_state['MysticAdvisorParser']['div']['class']:
            if 'good' == self.parser_state['MysticAdvisorParser']['div']['class']:
                self.parser_state['MysticAdvisorParser']['good'] = True

    def end_div(self):
        super(MysticAdvisorParser, self).end_div()
        self.parser_state['div_depth'] -= 1
        self.parser_state['MysticAdvisorParser']['div'] = False

    def start_th(self, attributes):
        super(MysticAdvisorParser, self).start_th(attributes)
        self.parser_state['MysticAdvisorParser']['th'] = True

    def end_th(self):
        super(MysticAdvisorParser, self).end_th()
        self.parser_state['MysticAdvisorParser']['th'] = False

    def start_td(self, attributes):
        super(MysticAdvisorParser, self).start_td(attributes)
        self.parser_state['MysticAdvisorParser']['td'] = True

    def end_td(self):
        super(MysticAdvisorParser, self).end_td()
        self.parser_state['MysticAdvisorParser']['td'] = False

    def handle_data(self, data):
        super(MysticAdvisorParser, self).handle_data(data)
        if 'good' in self.parser_state['MysticAdvisorParser'] and  self.parser_state['MysticAdvisorParser']['good']:
            if self.parser_state['MysticAdvisorParser']['th']:
                if 0 < len(data.strip()):
                    self.current_spell = {}
                    self.current_spell['name'] = data.strip()
                    log.debug("Current spell: %s", self.current_spell['name'])
        if self.current_spell and self.parser_state['MysticAdvisorParser']['td']:
            if 0 < len(data.strip()):
                data = data.replace("days","").strip()
                try:
                    self.current_spell['duration'] = int(data)
                    self.active_spells[self.current_spell['name']] = self.current_spell['duration']
                    log.debug("Spell: %s: %s"% (self.current_spell['name'], self.current_spell['duration']))
                except:
                    pass


    def get_active_spells(self):
        return self.active_spells
