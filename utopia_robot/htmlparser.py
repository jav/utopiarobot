import logging
import re
import sgmllib
import string
from utopia_robot.lists import RACE_PROP, BUILDINGS
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
        self.parser_state['resource-bar'] = {}
        self.parser_state['resource-bar']['index'] = -1
        self.resource_val = 0

    def parse(self, s):
        pass

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

    def start_p(self, attributes):
        pass

    def end_p(self):
        pass

    def start_table(self, attributes):
        attr = dict(attributes)
        if 'id' in attr and 'resource-bar' == attr['id']:
            self.parser_state['resource-bar']['index'] = 0

    def end_table(self):
        if 0 <= self.parser_state['resource-bar']['index']:
            self.parser_state['resource-bar']['index'] = -1

    def start_thead(self, attributes):
        pass

    def end_thead(self):
        pass

    def start_tbody(self, attributes):
        pass

    def end_tbody(self):
        pass

    def start_tr(self, attributes):
        pass

    def end_tr(self):
        pass

    def start_th(self, attributes):
        pass

    def end_th(self):
        if 0 <= self.parser_state['resource-bar']['index']:
            resource_name = self.resource_list[self.parser_state['resource-bar']['index']]
            val = self.resource_val.replace(",","")
            try:
                if "Net Worth/Acre" == resource_name:
                    self.resources[resource_name] = float(val)
                else:
                    self.resources[resource_name] = int(val)
            except ValueError as ex:
                pass
            self.parser_state['resource-bar']['index'] += 1
            self.parser_state['resource-bar']['index'] %= len(self.resource_list)

    def start_td(self, attributes):
        pass

    def end_td(self):
        pass

    def start_form(self, attributes):
        pass

    def end_form(self):
        pass

    def start_input(self, attributes):
        pass

    def end_input(self):
        pass

    def start_select(self, attributes):
        pass

    def end_select(self):
        pass

    def start_option(self, attributes):
        pass

    def end_option(self):
        pass

    def handle_data(self, data):
        if 'head' in self.parser_state and self.parser_state['head']:
            if 'title' in self.parser_state and self.parser_state['title']:
                self.title = data
                log.debug("(%s) : parsing page (title): %s"% (__name__, self.title))

                if "Home" in self.title:
                    self.current_page = "PAGE_INIT"
                if "Lobby" in self.title:
                    self.current_page="PAGE_LOBBY"
                if "Age" in self.title:
                    self.current_page="PAGE_PROV"
                if "Throne Page" in self.title:
                    #THRONE will be overriden if any link in 'navigation' is <h1>
                    self.current_page="PAGE_THRONE"
                if "Mystic Circle" in self.title:
                    self.current_page="PAGE_MYSTIC"
                if "Army" in self.title:
                    self.current_page="PAGE_MILITARY"
                if "Buildings" in self.title:
                    self.current_page="PAGE_GROWTH"
                if "Science Research" in self.title:
                    self.current_page="PAGE_SCIENCE"
                if "Explore Page" in self.title:
                    self.current_page="PAGE_EXPLORE"
                if "Kingdom Details" in self.title:
                    self.current_page="PAGE_KINGDOM"
                log.debug("DETECTED PAGE: %s" % self.current_page)
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

        if 0 <= self.parser_state['resource-bar']['index']:
            self.resource_val = data

    def get_nav_links(self):
        log.debug("get_nav_links(): %s" % self.nav_links)
        return self.nav_links

    def get_resources(self):
        log.debug("get_resources(): %s" % self.resources)
        return self.resources

class LoginParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(LoginParser, self).__init__(verbose)
        self.login_info = {}
        self.current_input = None
        self.parser_state['login_form'] = ""

    def parse(self, s):
        super(LoginParser, self).parse(s)
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
        super(LobbyParser, self).__init__(verbose)
        self.hyperlinks = []

    def parse(self, s):
        super(LobbyParser, self).parse(s)
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
        super(ProvSelectParser, self).__init__(verbose)
        self.hyperlinks = []
        self.current_page="PAGE_NONE"

    def parse(self, s):
        super(ProvSelectParser, self).parse(s)
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
        super(ThroneParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['ThroneParser'] = {}
        self.parser_state['ThroneParser']['plague'] = False

        self.plague = False

    def parse(self, s):
        super(ThroneParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_p(self, attributes):
        super(ThroneParser, self).start_p(attributes)
        attr = dict(attributes)
        if 'class' in attr and 'advice-message'== attr['class']:
            self.parser_state['ThroneParser']['plague'] = True

    def end_p(self):
        super(ThroneParser, self).end_p()
        self.parser_state['ThroneParser']['plague'] = False

    def handle_data(self, data):
        super(ThroneParser, self).handle_data(data)
        if self.parser_state['ThroneParser']['plague']:
            if "The Plague has spread" in data:
                self.plague = True

    def get_plague(self):
        log.debug("get_plague(): %s" % self.plague)
        return self.plague

class MysticParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(MysticParser, self).__init__(verbose)
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
        super(MysticParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_form(self, attributes):
        attr = dict(attributes)
        if 'action' in attr and 'method' in attr and "" == attr['action'] and 'name' not in attr and "POST" == attr['method']:
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
        log.debug("get_mystic_form(): %s" % self.mystic_form)
        return self.mystic_form

    def get_available_spells(self):
        log.debug("get_available_spells(): %s" % self.available_spells)
        return self.available_spells

    def get_mana(self):
        log.debug("get_mana(): %s" % self.mana)
        return self.mana

    def get_spell_result(self):
        log.debug("get_spell_result: %s" % self.spell_result)
        return self.spell_result


class MysticAdvisorParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(MysticAdvisorParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['MysticAdvisorParser'] = {}
        self.parser_state['MysticAdvisorParser']['th'] = False
        self.parser_state['MysticAdvisorParser']['td'] = False
        self.parser_state['MysticAdvisorParser']['div'] = False
        self.parser_state['MysticAdvisorParser']['div_depth'] = 0
        self.current_spell = {}
        self.active_spells = {}

    def parse(self, s):
        super(MysticAdvisorParser, self).parse(s)
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
                if "days" in data:
                    data = data.replace("days","").strip()
                if "day" in data:
                    data = data.replace("day","").strip()
                try:
                    self.current_spell['duration'] = int(data)
                    self.active_spells[self.current_spell['name']] = self.current_spell['duration']
                    log.debug("Spell: %s: %s"% (self.current_spell['name'], self.current_spell['duration']))
                except:
                    pass

    def get_active_spells(self):
        log.debug("get_active_spells(): %s" % self.active_spells)
        return self.active_spells


class MilitaryParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(MilitaryParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['MilitaryParser'] = {}
        self.parser_state['MilitaryParser']['th'] = False
        self.parser_state['MilitaryParser']['td'] = False
        self.parser_state['MilitaryParser']['div'] = False
        self.parser_state['MilitaryParser']['div_depth'] = 0
        self.parser_state['MilitaryParser']['troops'] = False
        self.parser_state['MilitaryParser']['current_troop'] = -1
        self.parser_state['MilitaryParser']['current_val'] = 0
        self.parser_state['MilitaryParser']['soldier_mark'] = False
        self.parser_state['MilitaryParser']['form'] = False
        self.parser_state['MilitaryParser']['inputs'] = False
        self.parser_state['MilitaryParser']['select'] = False
        self.parser_state['MilitaryParser']['option'] = False
        self.parser_state['MilitaryParser']['selected_draft_val'] = False
        self.parser_state['MilitaryParser']['last_draft_level'] = False
        self.parser_state['MilitaryParser']['last_draft_label'] = False
        self.parser_state['MilitaryParser']['select_draft_rate'] = False
        self.parser_state['MilitaryParser']['spec_credits'] = False

        self.military_form = {}
        self.troops = {}
        self.soldier = 0
        self.troops_list = ['o-spec', 'd-spec', 'elite', 'thief']
        self.vals_list = ['home', 'training', 'cost', 'max']
        self.train_result = None
        self.draft_levels = {}
        self.selected_draft_rate = None
        self.spec_credits = 0

    def parse(self, s):
        super(MilitaryParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_tr(self, attributes):
        super(MilitaryParser, self).start_tr(attributes)
        self.parser_state['MilitaryParser']['tr'] = True

    def end_tr(self):
        super(MilitaryParser, self).end_tr()
        self.parser_state['MilitaryParser']['tr'] = False
        if self.parser_state['MilitaryParser']['troops']:
            self.parser_state['MilitaryParser']['current_troop'] += 1
            self.parser_state['MilitaryParser']['current_val'] = 0

    def start_th(self, attributes):
        super(MilitaryParser, self).start_th(attributes)
        self.parser_state['MilitaryParser']['th'] = True

    def end_th(self):
        super(MilitaryParser, self).end_th()
        self.parser_state['MilitaryParser']['th'] = False

    def start_td(self, attributes):
        super(MilitaryParser, self).start_td(attributes)
        self.parser_state['MilitaryParser']['td'] = True

    def end_td(self):
        super(MilitaryParser, self).end_td()
        self.parser_state['MilitaryParser']['td'] = False
        self.parser_state['MilitaryParser']['current_val'] += 1

    def end_table(self):
        super(MilitaryParser, self).end_table()
        self.parser_state['MilitaryParser']['troops'] = False

    def start_div(self, attributes):
        super(MilitaryParser, self).start_div(attributes)
        attr=dict(attributes)
        self.parser_state['MilitaryParser']['div'] = attr
        self.parser_state['MilitaryParser']['div_depth'] += 1

    def end_div(self):
        super(MilitaryParser, self).end_div()
        self.parser_state['MilitaryParser']['div'] = False
        self.parser_state['MilitaryParser']['div_depth'] -= 1

    def start_form(self, attributes):
        super(MilitaryParser, self).start_form(attributes)
        attr=dict(attributes)
        self.parser_state['MilitaryParser']['form'] = attr
        self.parser_state['MilitaryParser']['inputs'] = {}
        self.parser_state['MilitaryParser']['other_inputs'] = []
        log.debug("starting form: %s" % self.parser_state['MilitaryParser']['form'] )

    def end_form(self):
        super(MilitaryParser, self).end_form()
        if self.parser_state['MilitaryParser']['inputs'] and 'csrfmiddlewaretoken' in self.parser_state['MilitaryParser']['inputs']:
            self.military_form = {}
            self.military_form['form'] = self.parser_state['MilitaryParser']['form']
            self.military_form['inputs'] = self.parser_state['MilitaryParser']['inputs']
            self.military_form['other_inputs'] = self.parser_state['MilitaryParser']['other_inputs']
            log.debug("self.military_form: %s" % self.military_form)

    def start_input(self, attributes):
        super(MilitaryParser, self).start_input(attributes)
        attr=dict(attributes)
        #self.parser_state['MilitaryParser']['input']
        if self.parser_state['MilitaryParser']['form']:
            if 'name' in attr:
                self.parser_state['MilitaryParser']['inputs'][attr['name']] = attr
            else:
                self.parser_state['MilitaryParser']['other_inputs'].append(attr)

    def start_select(self, attributes):
        super(MilitaryParser, self).start_select(attributes)
        attr=dict(attributes)
        self.parser_state['MilitaryParser']['select'] = attr
        if 'name' in attr and 'draft_rate' == attr['name']:
            self.parser_state['MilitaryParser']['select_draft_rate'] = True


    def end_select(self):
        super(MilitaryParser, self).end_select()
        self.parser_state['MilitaryParser']['select'] = False

    def start_option(self, attributes):
        super(MilitaryParser, self).start_option(attributes)
        attr=dict(attributes)
        self.parser_state['MilitaryParser']['option'] = attr
        if self.parser_state['MilitaryParser']['select_draft_rate']:
            self.parser_state['MilitaryParser']['last_draft_level'] = attr['value']
            if 'selected' in attr and 'selected' == attr['selected']:
                self.parser_state['MilitaryParser']['selected_draft_val'] = attr['value']

    def end_option(self):
        super(MilitaryParser, self).end_option()
        self.parser_state['MilitaryParser']['option'] = False
        self.draft_levels[self.parser_state['MilitaryParser']['last_draft_label']] = self.parser_state['MilitaryParser']['last_draft_level']
        if self.parser_state['MilitaryParser']['selected_draft_val']:
            self.selected_draft_rate = {self.parser_state['MilitaryParser']['last_draft_label']: self.parser_state['MilitaryParser']['last_draft_level']}
            self.parser_state['MilitaryParser']['selected_draft_val'] = False

    def handle_data(self, data):
        super(MilitaryParser, self).handle_data(data)
        if self.parser_state['MilitaryParser']['th']:
            if "Unit (Off/Def)" in data:
                self.parser_state['MilitaryParser']['troops'] = True
                self.parser_state['MilitaryParser']['troops_count'] = 0
            if "Number of soldiers" in data:
                self.parser_state['MilitaryParser']['soldier_mark'] = True
            if "Free specialist credits left" in data:
                self.parser_state['MilitaryParser']['spec_credits'] = True

        if self.parser_state['MilitaryParser']['td']:
            if self.parser_state['MilitaryParser']['soldier_mark']:
                self.soldiers = int(data.replace(",",""))
                self.parser_state['MilitaryParser']['soldier_mark'] = False
            if self.parser_state['MilitaryParser']['troops']:
                data = data.replace(",","")
                data = data.replace("gc","")
                try:
                    if 0 == self.parser_state['MilitaryParser']['current_val']:
                        self.troops[self.troops_list[self.parser_state['MilitaryParser']['current_troop']]] = {}
                    self.troops[self.troops_list[self.parser_state['MilitaryParser']['current_troop']]][self.vals_list[self.parser_state['MilitaryParser']['current_val']]] = int(data)
                except:
                    pass
            if self.parser_state['MilitaryParser']['spec_credits']:
                self.spec_credits = int(data)
                self.parser_state['MilitaryParser']['spec_credits'] = False

        if self.parser_state['MilitaryParser']['div']:
            if 'class' in self.parser_state['MilitaryParser']['div'] and 'good message' == self.parser_state['MilitaryParser']['div']['class']:
                log.debug("RACE_PROP %s", RACE_PROP)
                self.train_result={}
                for race_troop, troop in zip(RACE_PROP['human']['troops']+[("thief", "thieves")], ['o-spec', 'd-spec', 'elite', 'thief']): # TODO: Make race a variable!
                    log.debug("Parsing 'good message' - data: %s", data)
                    match = re.search("([0-9]+) (%s|%s)" % race_troop, data, re.IGNORECASE)
                    if match is not None:
                        log.debug("train_result[%s] = %s" % (troop, match.group(1)))
                        trained = int(match.group(1))
                    else:
                        trained = 0
                    self.train_result[troop] =trained
        #if self.parser_state['MilitaryParser']['inputs']

        if self.parser_state['MilitaryParser']['select_draft_rate']:
            self.parser_state['MilitaryParser']['last_draft_label'] = data.strip()

    def get_military_form(self):
        log.debug("get_military_form(): %s" % self.military_form)
        return self.military_form

    def get_troops(self):
        log.debug("get_troops(): %s" % self.troops)
        return self.troops

    def get_soldiers(self):
        log.debug("get_soldiers(): %s" % self.soldiers)
        return self.soldiers

    def get_train_result(self):
        log.debug("get_train_result(): %s" % self.train_result)
        return self.train_result

    def get_draft_rate(self):
        log.debug("get_draft_rate(): %s" % self.selected_draft_rate)
        if self.selected_draft_rate is None:
            return self.selected_draft_rate
        return self.selected_draft_rate.items()[0]

    def get_spec_credits(self):
        log.debug("get_spec_credits(): %s" % self.spec_credits)
        return self.spec_credits

class GrowthParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(GrowthParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['GrowthParser'] = {}
        self.parser_state['GrowthParser']['th'] = False
        self.parser_state['GrowthParser']['tbody'] = False
        self.parser_state['GrowthParser']['td'] = False
        self.parser_state['GrowthParser']['buildings_list_started'] = False
        self.parser_state['GrowthParser']['building_index'] = 0
        self.parser_state['GrowthParser']['building_val_index'] = 0
        self.parser_state['GrowthParser']['current_building'] = None
        self.parser_state['GrowthParser']['inputs'] = {}
        self.parser_state['GrowthParser']['other_inputs'] = []
        self.parser_state['GrowthParser']['div'] = False
        self.parser_state['GrowthParser']['building_results'] = False
        self.parser_state['GrowthParser']['building_info'] = False
        self.parser_state['GrowthParser']['building_info_current'] = None

        self.buildings_list = [building[1] for building in BUILDINGS]
# ['Homes', 'Farms', 'Mills', 'Banks', 'Training Grounds', 'Armouries', 'Military Barracks', 'Forts', 'Guard Stations', 'Hospitals', 'Guilds', 'Towers', "Thieves' Dens", 'Watch Towers', 'Libraries', 'Schools', 'Stables', 'Dungeons']

        self.build_form = {}
        self.build_result = {}
        self.buildings = {}
        self.build_info = {}

    def parse(self, s):
        super(GrowthParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_table(self, attributes):
        super(GrowthParser, self).start_table(attributes)
        attr = dict(attributes)

        if 'class' in attr and 'two-column-stats' == attr['class']:
            self.parser_state['GrowthParser']['building_info'] = True
            log.debug("self.parser_state['GrowthParser']['building_info'] = True")

    def end_table(self):
        super(GrowthParser, self).end_table()
        if self.parser_state['GrowthParser']['building_info']:
            self.parser_state['GrowthParser']['building_info'] = False
            log.debug("self.parser_state['GrowthParser']['building_info'] = False")

    def start_th(self, attributes):
        super(GrowthParser, self).start_th(attributes)
        self.parser_state['GrowthParser']['th'] = True

    def end_th(self):
        super(GrowthParser, self).end_th()
        self.parser_state['GrowthParser']['th'] = False

    def start_tbody(self, attributes):
        super(GrowthParser, self).start_tbody(attributes)
        self.parser_state['GrowthParser']['tbody'] = True

    def end_tbody(self):
        super(GrowthParser, self).end_tbody()
        self.parser_state['GrowthParser']['tbody'] = False

    def start_td(self, attributes):
        super(GrowthParser, self).start_td(attributes)
        self.parser_state['GrowthParser']['td'] = True

    def end_td(self):
        super(GrowthParser, self).end_td()
        self.parser_state['GrowthParser']['td'] = False

    def start_form(self, attributes):
        super(GrowthParser, self).start_form(attributes)
        attr = dict(attributes)
        self.parser_state['GrowthParser']['form'] = True
        self.parser_state['GrowthParser']['current_form'] = attr

    def end_form(self):
        super(GrowthParser, self).end_form()
        self.parser_state['GrowthParser']['form'] = False
        if self.parser_state['GrowthParser']['buildings_list_started']:
            self.build_form['form'] = self.parser_state['GrowthParser']['current_form']
            self.build_form['inputs'] = self.parser_state['GrowthParser']['inputs']
            self.build_form['other_inputs'] = self.parser_state['GrowthParser']['other_inputs']
            self.parser_state['GrowthParser']['buildings_list_started'] = False
        log.debug("Nulling form-state.")
        self.parser_state['GrowthParser']['inputs'] = {}
        self.parser_state['GrowthParser']['other_inputs'] = []

    def start_input(self, attributes):
        super(GrowthParser, self).start_input(attributes)
        attr = dict(attributes)
        self.parser_state['GrowthParser']['input'] = True
        if 'name' in attr:
            self.parser_state['GrowthParser']['inputs'][attr['name']] = attr
        else:
            self.parser_state['GrowthParser']['other_inputs'].append(attr)

    def end_input(self):
        super(GrowthParser, self).end_input()
        self.parser_state['GrowthParser']['input'] = False

    def start_div(self, attributes):
        super(GrowthParser, self).start_div(attributes)
        attr = dict(attributes)
        self.parser_state['GrowthParser']['div'] = True
        if 'class' in attr and 'good message' == attr['class']:
            log.debug("BUIILDING RESULTS: TRUE")
            self.parser_state['GrowthParser']['building_results'] = True

    def end_div(self):
        super(GrowthParser, self).end_div()
        self.parser_state['GrowthParser']['div'] = False
        if self.parser_state['GrowthParser']['building_results']:
            log.debug("BUIILDING RESULTS: FALSE")
        self.parser_state['GrowthParser']['building_results'] = False

    def handle_data(self, data):
        super(GrowthParser, self).handle_data(data)
        if "You Own" == data:
            self.parser_state['GrowthParser']['buildings_list_started'] = True
        if self.parser_state['GrowthParser']['tbody'] and self.parser_state['GrowthParser']['buildings_list_started']:
            if self.parser_state['GrowthParser']['th']:
                self.parser_state['GrowthParser']['current_building'] = self.buildings_list[self.parser_state['GrowthParser']['building_index']]
                self.buildings[self.parser_state['GrowthParser']['current_building']] = {}
                self.parser_state['GrowthParser']['building_val_index'] = 0
                self.parser_state['GrowthParser']['building_index'] += 1
            if self.parser_state['GrowthParser']['td'] and 2 > self.parser_state['GrowthParser']['building_val_index']:
                if self.parser_state['GrowthParser']['building_val_index'] == 0:
                    self.buildings[self.parser_state['GrowthParser']['current_building']]['built'] = int(data.replace(',',''))
                else:
                    self.buildings[self.parser_state['GrowthParser']['current_building']]['incoming'] = int(data.replace(',',''))
                self.parser_state['GrowthParser']['building_val_index'] += 1

        if self.parser_state['GrowthParser']['building_results']:
            for singular, plural in BUILDINGS:
                log.debug("Regexp: %s"% "([0-9]+) (%s|%s)" % (singular, plural))
                match = re.search("([0-9]+) (%s|%s)" % (singular, plural), data, re.IGNORECASE)
                if match is not None:
                    built = int(match.group(1))
                    log.debug("Building result[%s] = %s" % (plural, match.group(1)))
                else:
                    built = 0
                    log.debug("Building result[%s] = 0" % plural)
                self.build_result[plural] = built

        if self.parser_state['GrowthParser']['building_info']:
            if self.parser_state['GrowthParser']['th']:
                self.parser_state['GrowthParser']['building_info_current'] = data
            if self.parser_state['GrowthParser']['td']:
                label = self.parser_state['GrowthParser']['building_info_current']
                val = data
                if "Total Land" == label:
                    val = val.replace(',','')
                    val = val.replace('acres','').replace(' acre','')
                    self.build_info[label] = int(val.strip())
                if "Construction Cost" == label:
                    val = val.replace(',','')
                    val = val.replace('gc per acre','')
                    self.build_info[label] = int(val.strip())
                elif "Total Undeveloped land" == label:
                    val = val.replace(',','')
                    val = val.replace('acres','').replace(' acre','')
                    self.build_info[label] = int(val.strip())
                elif "Maximum Buildable Now" == label:
                    val = val.replace(',','')
                    val = val.replace('acres','').replace(' acre','')
                    self.build_info[label] = int(val.strip())
                elif "Construction Time" == label:
                    val = val.replace(',','')
                    val = val.replace(' days','')
                    self.build_info[label] = int(val.strip())
                elif "Raze Cost" == label:
                    val = val.replace(',','')
                    val = val.replace('gc per acre','')
                    self.build_info[label] = int(val.strip())
                elif "Free Building Credits" == label:
                    val = val.replace(',','')
                    self.build_info[label] = int(val.strip())
                elif "Maximum Razeable Now" == label:
                    val = val.replace(',','')
                    val = val.replace('acres','').replace(' acre','')
                    self.build_info[label] = int(val.strip())

    def get_buildings(self):
        log.debug("get_buildings(): %s" % self.buildings)
        return self.buildings

    def get_build_form(self):
        log.debug("get_growth_form_fields(): %s" % self.build_form)
        return self.build_form

    def get_building_result(self):
        log.debug("get_building_result(): %s"% self.build_result)
        return self.build_result

    def get_build_info(self):
        log.debug("get_build_info(): %s"% self.build_info)
        return self.build_info

class ScienceParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(ScienceParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['ScienceParser'] = {}
        self.parser_state['ScienceParser']['h2'] = False
        self.parser_state['ScienceParser']['table'] = False
        self.parser_state['ScienceParser']['th'] = False
        self.parser_state['ScienceParser']['td'] = False
        self.parser_state['ScienceParser']['sci_form'] = False
        self.parser_state['ScienceParser']['input'] = False
        self.parser_state['ScienceParser']['inputs'] = {}
        self.parser_state['ScienceParser']['other_inputs'] = []
        self.parser_state['ScienceParser']['current_sci'] = None
        self.parser_state['ScienceParser']['current_sci_index'] = 0
        self.parser_state['ScienceParser']['rate_selector'] = False
        self.parser_state['ScienceParser']['current_option'] = None
        self.parser_state['ScienceParser']['curr_form'] = None
        self.parser_state['ScienceParser']['good-message'] = False
        self.parser_state['ScienceParser']['sci_info'] = False
        self.parser_state['ScienceParser']['curr_sci_info_name'] = None

        self.science = {}
        self.result={}
        self.science_info = {}
        self.science_info_labels = ['Total Money', 'Estimated Research Cost', 'Daily Income', 'Books to Allocate']
        self.science_options = {}
        self.selected_option = None
        self.sci_list = ['Alchemy', 'Tools', 'Housing', 'Food', 'Military', 'Crime','Channeling']
        for science in self.sci_list:
            self.science[science] = {'points': None, 'effect': None, 'incomming':None}

    def parse(self, s):
        super(ScienceParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_h2(self, attributes):
        super(ScienceParser, self).start_h2(attributes)
        self.parser_state['ScienceParser']['h2'] = True

    def end_h2(self):
        super(ScienceParser, self).end_h2()
        self.parser_state['ScienceParser']['h2'] = False

    def start_div(self, attributes):
        super(ScienceParser, self).start_div(attributes)
        attr = dict(attributes)
        if 'class' in attr and 'selector' == attr['class']:
            self.parser_state['ScienceParser']['rate_selector'] = True
        if 'class' in attr and 'good message' == attr['class']:
            self.parser_state['ScienceParser']['good-message'] = True

    def end_div(self):
        super(ScienceParser, self).end_div()
        self.parser_state['ScienceParser']['good-message'] = False

    def start_table(self, attributes):
        super(ScienceParser, self).start_table(attributes)
        attr = dict(attributes)
        self.parser_state['ScienceParser']['table'] = True
        if 'class' in attr and 'two-column-stats' == attr['class']:
            self.parser_state['ScienceParser']['sci_info'] = True

    def end_table(self):
        super(ScienceParser, self).end_table()
        self.parser_state['ScienceParser']['table'] = False
        self.parser_state['ScienceParser']['sci_info'] = False

    def start_th(self, attributes):
        super(ScienceParser, self).start_th(attributes)
        self.parser_state['ScienceParser']['th'] = True

    def end_th(self):
        super(ScienceParser, self).end_th()
        self.parser_state['ScienceParser']['th'] = False
        self.parser_state['ScienceParser']['current_sci_index'] = 0

    def start_td(self, attributes):
        super(ScienceParser, self).start_td(attributes)
        self.parser_state['ScienceParser']['td'] = True

    def end_td(self):
        super(ScienceParser, self).end_td()
        self.parser_state['ScienceParser']['td'] = False
        self.parser_state['ScienceParser']['current_sci_index'] += 1

    def start_form(self, attributes):
        super(ScienceParser, self).start_form(attributes)
        attr = dict(attributes)
        self.parser_state['ScienceParser']['curr_form'] = attr

    def end_form(self):
        super(ScienceParser, self).end_form()
        self.parser_state['ScienceParser']['sci_form'] = False
        self.parser_state['ScienceParser']['curr_form'] = None

    def start_input(self, attributes):
        super(ScienceParser, self).start_input(attributes)
        attr = dict(attributes)
        if self.parser_state['ScienceParser']['sci_form']:
            if 'name' in attr:
                if 'learn_min_income' in attr['name']:
                    attr['value'] = int(attr['value'])
                self.parser_state['ScienceParser']['inputs'][attr['name']] = attr
            else:
                self.parser_state['ScienceParser']['other_inputs'].append(attr)

    def start_select(self, attributes):
        super(ScienceParser, self).start_select(attributes)

    def end_select(self):
        super(ScienceParser, self).end_select()
        self.parser_state['ScienceParser']['rate_selector'] = False
        self.parser_state['ScienceParser']['current_option'] = None

    def start_option(self, attributes):
        super(ScienceParser, self).start_option(attributes)
        attr = dict(attributes)
        assert('value' in attr)
        self.parser_state['ScienceParser']['current_option'] = attr

    def end_option(self):
        super(ScienceParser, self).end_option()

    def handle_data(self, data):
        super(ScienceParser, self).handle_data(data)
        if self.parser_state['ScienceParser']['sci_info']:
            if self.parser_state['ScienceParser']['th']:
                if data in self.science_info_labels:
                    self.parser_state['ScienceParser']['curr_sci_info_name'] = data
            if self.parser_state['ScienceParser']['td']:
                if self.parser_state['ScienceParser']['curr_sci_info_name']:
                    curr_sci_info_name = self.parser_state['ScienceParser']['curr_sci_info_name']
                    if 'Estimated Research Cost' == curr_sci_info_name :
                        (cost,_,percent) = data.partition("gc")
                        cost = cost.replace(',','').strip()
                        percent = percent.replace('(','').replace(')','').replace('%','').strip()
                        val = (int(cost), float(percent))
                    else:
                        val = int(data.replace(',','').replace('gc','').replace('book','').replace('s',''))
                    self.science_info[curr_sci_info_name] = val

                self.parser_state['ScienceParser']['curr_sci_info_name'] = None

        if self.parser_state['ScienceParser']['good-message']:
            log.debug("GOOD MESSAGE")
            if 'of' in data:
                (_,_,msg) = data.partition('study')
                (val,_,msg) = msg.partition('book')
                (_,_,msg) = msg.partition('of')
                val = int(val.replace(',','').strip())
                sci_name = msg.replace('.','').strip().title()
                self.result[sci_name] = val

        if self.parser_state['ScienceParser']['current_option'] is not None:
            curr_opt = self.parser_state['ScienceParser']['current_option']
            log.debug("data: %s" % data)
            (name, _,booksandcost) = data.partition("-")
            name = name.strip()
            (books,_,cost) = booksandcost.partition('for')
            books = books.replace('books','').strip()
            cost = cost[:cost.index('(')]
            cost = cost.replace(',','').replace('gc','')
            log.debug("name: %s, books: %s, cost: %s" % (name, books, cost))
            self.science_options[data] = curr_opt['value']
            if 'selected' in curr_opt and 'selected' == curr_opt['selected']:
                self.selected_option = (name, curr_opt['value'])
            self.parser_state['ScienceParser']['current_option'] = None
        if self.parser_state['ScienceParser']['h2']:
            log.debug("H2: %s" % data)
            if "Daily Science Research Rate" in data:
                self.parser_state['ScienceParser']['sci_form'] = True
                self.parser_state['ScienceParser']['form'] = self.parser_state['ScienceParser']['curr_form']
                log.debug("Sci_form: %s" % self.parser_state['ScienceParser']['form'])
        if self.parser_state['ScienceParser']['th']:
            if data in self.sci_list:
                self.parser_state['ScienceParser']['current_sci'] = data
            else:
                self.parser_state['ScienceParser']['current_sci'] = None

        if self.parser_state['ScienceParser']['td']:
            assert( 0 <= self.parser_state['ScienceParser']['current_sci_index'])
            if self.parser_state['ScienceParser']['current_sci'] is not None:

                curr_sci = self.parser_state['ScienceParser']['current_sci']

                if  0 == self.parser_state['ScienceParser']['current_sci_index'] and self.science[curr_sci]['points'] is None:
                    self.science[curr_sci]['points'] = int(data.replace(',',''))
                elif 1 == self.parser_state['ScienceParser']['current_sci_index'] and self.science[curr_sci]['effect'] is None:
                    data = data[:data.index('%')]
                    self.science[curr_sci]['effect'] = float(data.replace(',','').replace('+',''))
                elif 2 == self.parser_state['ScienceParser']['current_sci_index'] and self.science[curr_sci]['incomming'] is None:
                    self.science[curr_sci]['incomming'] = int(data.replace(',',''))
                elif 3 == self.parser_state['ScienceParser']['current_sci_index']:
                    self.parser_state['ScienceParser']['current_sci'] = None

    def get_science_form(self):
        return {'form': self.parser_state['ScienceParser']['form'],'inputs': self.parser_state['ScienceParser']['inputs']}

    def get_science(self):
        return self.science

    def get_learn_rate(self):
        return self.selected_option

    def get_science_result(self):
        return self.result

    def get_science_info(self):
        log.debug("get_sience_info(): %s"% self.science_info)
        return self.science_info


class ExploreParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(ExploreParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['ExploreParser'] = {}
        self.parser_state['ExploreParser']['table'] = False
        self.parser_state['ExploreParser']['th'] = False
        self.parser_state['ExploreParser']['td'] = False
        self.parser_state['ExploreParser']['expl_form'] = False
        self.parser_state['ExploreParser']['input'] = False
        self.parser_state['ExploreParser']['inputs'] = {}
        self.parser_state['ExploreParser']['other_inputs'] = []

        self.parser_state['ExploreParser']['explore_info'] = None
        self.parser_state['ExploreParser']['curr_info'] = None

        self.explore_info = {}
        self.explore_form = {'form':{}, 'inputs':{}, 'other_inputs':[]}

    def parse(self, s):
        super(ExploreParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_table(self, attributes):
        super(ExploreParser, self).start_table(attributes)
        attr = dict(attributes)
        self.parser_state['ExploreParser']['table'] = True
        if 'class' in attr and 'two-column-stats' == attr['class']:
            self.parser_state['ExploreParser']['explore_info'] = True

    def end_table(self):
        super(ExploreParser, self).end_table()
        self.parser_state['ExploreParser']['table'] = False
        self.parser_state['ExploreParser']['explore_info'] = False

    def start_th(self, attributes):
        super(ExploreParser, self).start_th(attributes)
        self.parser_state['ExploreParser']['th'] = True

    def end_th(self):
        super(ExploreParser, self).end_th()
        self.parser_state['ExploreParser']['th'] = False

    def start_td(self, attributes):
        super(ExploreParser, self).start_td(attributes)
        self.parser_state['ExploreParser']['td'] = True

    def end_td(self):
        super(ExploreParser, self).end_td()
        self.parser_state['ExploreParser']['td'] = False

    def start_form(self, attributes):
        super(ExploreParser, self).start_form(attributes)
        attr = dict(attributes)
        if 'action' in attr and "" == attr['action']:
            self.parser_state['ExploreParser']['expl_form'] = True
            self.explore_form['form'] = self.parser_state['ExploreParser']['expl_form'] = attr

    def end_form(self):
        super(ExploreParser, self).end_form()
        self.parser_state['ExploreParser']['expl_form'] = False

    def start_input(self, attributes):
        super(ExploreParser, self).start_input(attributes)
        attr = dict(attributes)
        if self.parser_state['ExploreParser']['expl_form']:
            if 'name' in attr:
                if 'value' not in attr:
                    attr['value'] = ""
                self.explore_form['inputs'][attr['name']] = attr
            else:
                self.explore_form['other_inputs'].append(attr)

    def handle_data(self, data):
        super(ExploreParser, self).handle_data(data)
        if self.parser_state['ExploreParser']['explore_info']:
            if self.parser_state['ExploreParser']['th']:
                self.parser_state['ExploreParser']['curr_info'] = data
            elif self.parser_state['ExploreParser']['td'] and self.parser_state['ExploreParser']['curr_info'] is not None:
                curr_info = self.parser_state['ExploreParser']['curr_info']
                (value,_,_) = data.partition(' ')
                print data
                self.explore_info[curr_info] = int(value.replace(',','').replace('gc',''))
                # self.parser_state['ExploreParser']['explore_info'] = None
                # self.parser_state['ExploreParser']['curr_info'] = None
                log.debug("self.explore_info: %s" % self.explore_info)

    def get_explore_info(self):
        log.debug("get_explore_info(): %s" % self.explore_info)
        self.explore_info.update({'soldiers': self.explore_info['Exploration Costs (Soldiers)']})
        self.explore_info.update({'gold': self.explore_info['Exploration Costs (Gold)']})
        self.explore_info.update({'available': self.explore_info['Available Uncharted Acres']})
        return self.explore_info

    
# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# num_acres:1
# explore:Send Expedition

    def get_explore_form(self):
        log.debug("get_explore_form(): %s", self.explore_form)
        return self.explore_form

    def get_explore_result(self):
        log.debug("get_explore_results(): NaN")
        #not yet implemented
        return -1

class KingdomParser(UtopiaParser):
    def __init__(self, verbose=0):
        super(KingdomParser, self).__init__(verbose)
        self.last_page="PAGE_NONE"

        self.parser_state['KingdomParser'] = {}
        self.parser_state['KingdomParser']['table'] = False
        self.parser_state['KingdomParser']['th'] = False
        self.parser_state['KingdomParser']['td'] = False
        self.parser_state['KingdomParser']['kd_form'] = False
        self.parser_state['KingdomParser']['kd_info'] = False
        self.parser_state['KingdomParser']['kd_data'] = False
        self.parser_state['KingdomParser']['kd_data_index'] = 0
        self.parser_state['KingdomParser']['curr_prov'] = {}
        self.parser_state['KingdomParser']['curr_info'] = None
        self.parser_state['KingdomParser']['input'] = False
        self.parser_state['KingdomParser']['inputs'] = {}
        self.parser_state['KingdomParser']['other_inputs'] = []
        self.parser_state['KingdomParser']['collected_data'] = ""

        self.kd_form = {'form':{}, 'inputs':{}, 'other_inputs':[]}
        self.kd_info = {}
        self.kd_info['provinces'] = {}
        self.kd_prov_headers = []


    def parse(self, s):
        super(KingdomParser, self).parse(s)
        self.feed(s)
        self.close()

    def start_table(self, attributes):
        super(KingdomParser, self).start_table(attributes)
        attr = dict(attributes)
        self.parser_state['KingdomParser']['table'] = True
        if 'class' in attr and 'two-column-stats' == attr['class']:
            self.parser_state['KingdomParser']['kd_info'] = True
        elif 'class' in attr and 'tablesorter' == attr['class']:
            self.parser_state['KingdomParser']['kd_data'] = True

    def end_table(self):
        super(KingdomParser, self).end_table()
        self.parser_state['KingdomParser']['table'] = False
        self.parser_state['KingdomParser']['kd_info'] = False
        self.parser_state['KingdomParser']['kd_data'] = False

    def start_tr(self, attributes):
        super(KingdomParser, self).start_tr(attributes)
        self.parser_state['KingdomParser']['tr'] = True
        self.parser_state['KingdomParser']['kd_data_index'] = 0

    def end_tr(self):
        super(KingdomParser, self).end_tr()
        self.parser_state['KingdomParser']['tr'] = False
        curr_prov = self.parser_state['KingdomParser']['curr_prov']
        if 0 < len(curr_prov):
            self.kd_info['provinces'][curr_prov['Province']] = curr_prov
            self.parser_state['KingdomParser']['curr_prov'] = {}

    def start_th(self, attributes):
        super(KingdomParser, self).start_th(attributes)
        self.parser_state['KingdomParser']['th'] = True
        self.parser_state['KingdomParser']['collected_data'] = ""

    def end_th(self):
        super(KingdomParser, self).end_th()
        self.parser_state['KingdomParser']['th'] = False
        if self.parser_state['KingdomParser']['kd_data']:
            data = self.parser_state['KingdomParser']['collected_data']
            self.kd_prov_headers.append(data.strip())

    def start_td(self, attributes):
        super(KingdomParser, self).start_td(attributes)
        self.parser_state['KingdomParser']['td'] = True
        self.parser_state['KingdomParser']['collected_data'] = ""

    def end_td(self):
        super(KingdomParser, self).end_td()
        self.parser_state['KingdomParser']['td'] = False
        if self.parser_state['KingdomParser']['kd_data']:
            data = self.parser_state['KingdomParser']['collected_data'].strip()
            index = self.parser_state['KingdomParser']['kd_data_index']
            header = self.kd_prov_headers[index]
            if 'Province' == header:
                self.parser_state['KingdomParser']['curr_prov']['online'] = True if '*' in data else False
                self.parser_state['KingdomParser']['curr_prov']['protected'] = True if '^' in data else False
                self.parser_state['KingdomParser']['curr_prov']['monarch'] = True if '(M)' in data else False

            data = data.replace('^','').replace('*','').replace('(M)','').replace('gc','').replace('acres','').replace(',','')
            if '-' == data or header not in ['Slot', 'Land', 'Net Worth', 'Net Worth/Acre']:
                self.parser_state['KingdomParser']['curr_prov'][header] = data.strip()
            else:
                self.parser_state['KingdomParser']['curr_prov'][header] = int(data.strip())

            self.parser_state['KingdomParser']['kd_data_index'] += 1

    def start_form(self, attributes):
        super(KingdomParser, self).start_form(attributes)
        attr = dict(attributes)
        if 'class' in attr and "change-kingdom" == attr['class']:
            self.parser_state['KingdomParser']['kd_form'] = True
            self.kd_form['form'] = self.parser_state['KingdomParser']['kd_form'] = attr

    def end_form(self):
        super(KingdomParser, self).end_form()
        self.parser_state['KingdomParser']['kd_form'] = False

    def start_input(self, attributes):
        super(KingdomParser, self).start_input(attributes)
        attr = dict(attributes)

    def handle_data(self, data):
        super(KingdomParser, self).handle_data(data)
        if self.parser_state['KingdomParser']['kd_data']:
            self.parser_state['KingdomParser']['collected_data'] += data
        if self.parser_state['KingdomParser']['kd_info']:
            if self.parser_state['KingdomParser']['th']:
                if self.parser_state['KingdomParser']['curr_info'] is None:
                    self.parser_state['KingdomParser']['curr_info'] = data
                else:
                    self.parser_state['KingdomParser']['curr_info'] += data
            if self.parser_state['KingdomParser']['td']:
                name = self.parser_state['KingdomParser']['curr_info']
                if name in ['Stance', 'Their Attitude To Us', 'Our Attitude To Them']:
                    self.kd_info[name] = data.strip().lower()
                elif 'Wars Won / Concluded Wars' == name:
                    (won,_,concluded) = data.partition('/')
                    self.kd_info['Wars Won'] = int(won.strip())
                    self.kd_info['Concluded Wars'] = int(concluded.strip())
                elif name in ['Total Land', 'Total Networth']:
                    total_str = name
                    avg_str = name.replace('Total', 'Average')
                    data = data.replace('gc','').replace(',','').replace('acres','').replace('avg:','')
                    (total,_,avg) = data.partition("(")
                    self.kd_info[total_str] = int(total.strip())
                    avg = avg.replace(')','')
                    self.kd_info[avg_str] = int(avg.strip())
                elif 'Total Provinces' == name:
                    self.kd_info[name] = int(data.strip())
                elif 'Average Opponent Relative Size' == name:
                    self.kd_info[name] = int(data.replace('%','').strip())

                self.parser_state['KingdomParser']['curr_info'] = None

    def get_kd_form(self):
        log.debug("get_kd_form(): %s", self.kd_form)
        return self.kd_form

    def get_kd_info(self):
        log.debug("get_kd_info(): %s", self.kd_info)
        return self.kd_info
