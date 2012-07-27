#!/usr/bin/env python

import cookielib
import inspect
#from ipdb import set_trace
import logging
import random
import time

import os
import urllib
import urllib2
import re
import zlib

import htmlparser
from utopia_robot.lists import RACE_PROP, BUILDINGS

log = logging.getLogger(__name__)

URL_BASE = "http://utopia-game.com"
URL_LOGIN = "%s/shared" % URL_BASE

class UtopiaRobot(object):

    password = ""
    username = ""
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
    cookie_file = "cookie_file.txt"
    cj = False
    page_cache = False
    headers = { 'User-Agent' : user_agent }

    parser = None
    page = "PAGE_NONE"

    #Bootstrap throne-url
    nav_links = {
        'Throne': '/wol/game/throne',
        'Mystics': '/wol/game/enchantment',
        'Military': '/wol/game/train_army',
        'Growth': '/wol/game/build',
        'Sciences': '/wol/game/science',
        }

    advisor_links = {
        'Mystics': '/wol/game/council_spells'
        }

    #properties
    resources = None

    def __init__(self):
        self.cj = cookielib.LWPCookieJar()
        if os.path.isfile(self.cookie_file):
            self.cj.load(self.cookie_file)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)

    def cache_page(self, page, res):
        """Save a copy of the page. Currently implemented using the
           'PAGE_SOMETHING' identifier as key."""
        if self.page_cache:
            file_name = str(zlib.crc32(page))
            fh = open(self.page_cache + "/"+ file_name + ".html", 'w+')
            log.debug("Saving page to: %s" % file_name )
            fh.write(res)
            fh.close()

    def _simulate_wait(self):
        """Wait rand(seconds). Expected to be used before we load a page."""
        time.sleep(random.randrange(3,20))

    def _get_page(self, url, data, headers, parser):
        log.debug("get_page( url: %s, data: %s, headers: %s )" % (url, data, headers))
        req = urllib2.Request(url, data, headers)
        self._simulate_wait()
        res = urllib2.urlopen(req)
        self.result = res.read()
        self.parser = parser
        self.parser.parse(self.result)

        if self.parser.tick_ongoing:
            #Tick detected, sleep, retry and abort this instance
            sleep(random.randrange(30,60))
            return self._get_page(url, data, headers,parser)

        self.cache_page(self.parser.current_page, self.result)

        log.debug("Page loaded, self.parser.current_page: %s" % self.parser.current_page)

        if 'PAGE_INIT' == self.parser.current_page:
            log.info("Not logged in, -> do_login()")
            self._do_login(self)
            return self._get_page(url,data,headers,parser) #Risk of infinite recursion

        if self.parser.get_nav_links():
            self.nav_links = self.parser.get_nav_links()


    def _do_login(self, parser):
        """Perform login (from the login page through province selection
        and onwards until we're in the game. (internal function)"""
        log.debug("do_login")

        # OK! Assert that we're on the login page!
        assert('PAGE_INIT' == self.parser.current_page)

        def _login(self):
            if 'PAGE_INIT' != self.parser.current_page:
                values= {}
                data = urllib.urlencode(values)
                log.debug("Loading page: %s" % URL_LOGIN)
                req = urllib2.Request(URL_LOGIN, data, self.headers)
                _simulate_wait()
                res = urllib2.urlopen(req)
                self.result = res.read()

            assert( self.parser.current_page == "PAGE_INIT")

            self.parser = htmlparser.LoginParser()
            self.parser.parse(self.result)
            self.cache_page("PAGE_INIT", self.result)

            login_info = self.parser.get_login_info()
            log.debug( "login_info %s" % login_info )

            post = {}
            for k,v in login_info['inputs'].items():
                if 'name' in v:
                    if 'password' == v['name']:
                        v['value'] = self.password
                        login_info['inputs'][k]['value'] = v['value']
                    if 'username' == v['name']:
                        v['value'] = self.username
                        login_info['inputs'][k]['value'] = v['value']
                post[k] = v


            values = {}
            for k,v in login_info['inputs'].items():
                if isinstance(v, dict) and 'name' in v:
                    values[v['name']] = v['value']

            log.debug( "values %s", values )

            data = urllib.urlencode(values)

            URL_TAKE_LOGIN = "%s%s" % (URL_BASE, login_info['form']['action'])
            log.debug("accessing %s POST:%s" % (URL_TAKE_LOGIN, data) )
            req = urllib2.Request(URL_TAKE_LOGIN, data, self.headers)
            self._simulate_wait()
            res = urllib2.urlopen(req)
            self.result = res.read()
            self.cache_page(self.parser.current_page, self.result)

        def _lobby(self):
            #pick server
            self.parser = htmlparser.LobbyParser()
            self.parser.parse(self.result)
            assert( self.parser.current_page == "PAGE_LOBBY")
            self.cache_page("PAGE_LOBBY", self.result)

            lobby_fields = self.parser.get_lobby_fields()
            URL_TAKE_WORLD_CHOICE = "%s%s" % (URL_BASE, lobby_fields['chooser_link'])
            data = None
            log.debug("accessing %s POST:%s" % (URL_TAKE_WORLD_CHOICE, data) )
            req = urllib2.Request(URL_TAKE_WORLD_CHOICE, data, self.headers)
            self._simulate_wait()
            res = urllib2.urlopen(req)
            self.result = res.read()
            log.debug(self.result)
            self.cache_page(self.parser.current_page, self.result)

        def _pick_prov(self):
            self.parser = htmlparser.ProvSelectParser()
            self.parser.parse(self.result)
            assert( self.parser.current_page == "PAGE_PROV")
            self.cache_page("PAGE_PROV", self.result)

            prov_fields = self.parser.get_choose_province_fields()
            URL_TAKE_PROV_CHOICE = "%s%s" % (URL_BASE, prov_fields['chooser_link'])
            data = None
            log.debug("accessing %s POST:%s" % (URL_TAKE_PROV_CHOICE, data) )
            req = urllib2.Request(URL_TAKE_PROV_CHOICE, data, self.headers)
            self._simulate_wait()
            res = urllib2.urlopen(req)
            self.result = res.read()
            log.debug(self.result)
            self.cache_page(self.parser.current_page, self.result)

        _login(self)
        if 'PAGE_NONE' != self.parser.current_page and 'PAGE_LOBBY' != self.parser.current_page:
            return True
        _lobby(self)
        _pick_prov(self)


    def _get_throne(self):
        """Load the throne page (internal function)"""
        log.debug("_get_throne()")
        data = None
        url = URL_BASE + self.nav_links['Throne']
        self._get_page(url, data, self.headers, htmlparser.ThroneParser())

        assert('PAGE_THRONE' == self.parser.current_page)

    def _get_growth(self):
        """Load the Growth page (internal function)"""
        log.debug("_get_growth()")
        log.debug("nav: %s" % self.nav_links)
        assert(0 < len(self.nav_links['Growth']))
        data = None
        url = URL_BASE + self.nav_links['Growth']
        self._get_page(url, data, self.headers, htmlparser.GrowthParser() )

        assert('PAGE_GROWTH' == self.parser.current_page)

    def _get_mystics(self):
        """Load the mystics page (internal function)"""
        log.debug("_get_mystics()")
        assert(0 < len(self.nav_links['Mystics']))
        data = None
        url = URL_BASE + self.nav_links['Mystics']
        self._get_page(url, data, self.headers, htmlparser.MysticParser() )

        assert('PAGE_MYSTIC' == self.parser.current_page)

    def _get_mystic_advisor(self):
        """Get the mystics council/advisor page (internal function) """
        log.debug("_get_mystic_advisor()")
        assert(0 < len(self.advisor_links['Mystics']))
        data = None
        url = URL_BASE + self.advisor_links['Mystics']
        self._get_page(url, data, self.headers, htmlparser.MysticAdvisorParser() )

        assert('PAGE_MYSTIC_ADVISOR' == self.parser.current_page)

    def _get_military(self):
        """Get the military page (internal function)"""
        log.debug("_get_military()")
        assert(0 < len(self.nav_links['Military']))
        data = None
        url = URL_BASE + self.nav_links['Military']
        self._get_page(url, data, self.headers, htmlparser.MilitaryParser() )

        assert('PAGE_MILITARY' == self.parser.current_page)

    def _get_science(self):
        """Load the Science page (internal function)"""
        log.debug("_get_science()")
        log.debug("nav: %s" % self.nav_links)
        assert(0 < len(self.nav_links['Sciences']))
        data = None
        url = URL_BASE + self.nav_links['Sciences']
        self._get_page(url, data, self.headers, htmlparser.ScienceParser() )

        assert('PAGE_SCIENCE' == self.parser.current_page)

    def _check_login(self):
        """Check if we're logged in or not (NOT IMPLEMENTED)"""
        log.debug("_check_login()")
        return self.is_loggedin

    def get_resources(self):
        """Get the players resources (from the top of the page)
           This is implemented in the UtopiaParser baseclass, so it
           should always be available (with the exception of login-pages)"""
        log.debug("get_resources()")
        if self.parser is None or self.parser.get_resources() is None:
            self._get_throne()
        return self.parser.get_resources()

    def get_plague(self):
        """Get the players plague status.
           If we are not on the Throne page, we will load it."""
        log.debug("get_plague()")
        if self.parser is None or self.parser.current_page != 'PAGE_THRONE':
            self._get_throne()
        assert('PAGE_THRONE' == self.parser.current_page)
        return self.parser.get_plague()

    def get_available_spells(self):
        """Get which spells are available to be cast.
           The return is a dict( (tuple) )
           'in-game-spell-name' = ('SPELL_CODE', int(cost))
           If we are not on the mystics page, we will load it."""
        log.debug("get_available_spells()")
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC':
            self._get_mystics()
        assert('PAGE_MYSTIC' == self.parser.current_page)
        return self.parser.get_available_spells()

    def get_active_spells(self):
        """Get which spells are active.
           If we are not on the mystics_council/advisor page, we will load it.
           Only a few spells are implemented so far.
           """
        log.debug("get_active_spells()")
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC_ADVISOR':
            self._get_mystic_advisor()
        assert('PAGE_MYSTIC_ADVISOR' == self.parser.current_page)
        return self.parser.get_active_spells()

    def get_mana(self):
        """Get player mana
           If we are not on the mystics page, we will load it.
           """
        log.debug("get_mana()")
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC':
            self._get_mystics()
        assert('PAGE_MYSTIC' == self.parser.current_page)
        return self.parser.get_mana()

    def cast_spell(self, spell):
        """Cast a spell
           If we are not on the mystics page, we will load it.
           Returns the result (if successfull, unsucessfull is not yet implemented).
           """
        log.debug("cast_spell()")
        #Ensure we are on the mystics page
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC':
            self._get_mystics()
        assert('PAGE_MYSTIC' == self.parser.current_page)
        mystic_form = self.parser.get_mystic_form()
        #Cast the spell (send POST)
        log.debug("mystic_form['inputs']: %s" % mystic_form['inputs'])

        data = {}
        for k,v in mystic_form['inputs'].items():
            data[k] = v['value']
        log.debug("self.parser.get_available_spells(): %s" % self.parser.get_available_spells())
        data['spell'] = self.parser.get_available_spells()[spell][0]
        data = urllib.urlencode(data)
        log.debug("cast_spell form data: %s" % data)

        url = URL_BASE + self.nav_links['Mystics'] + mystic_form['form']['action']
        self._get_page(url, data, self.headers, htmlparser.MysticParser() )

        #Return the result
        return self.parser.get_spell_result()

    def get_troops(self):
        """Get the players troops.
        Will load the military page (if not already loaded)
        TODO: Get the troops also from the Throne page
        """
        log.debug("get_troops()")
        if self.parser is None or self.parser.current_page != 'PAGE_MILITARY':
            self._get_military()
        assert('PAGE_MILITARY' == self.parser.current_page)
        return self.parser.get_troops()

    def get_soldiers(self):
        """Get the players untrained soldiers.
        Will load the military page (if not already loaded)
        TODO: Get the troops also from the Throne page
        """
        log.debug("get_soldiers()")
        if self.parser is None or self.parser.current_page != 'PAGE_MILITARY':
            self._get_military()
        assert('PAGE_MILITARY' == self.parser.current_page)
        return self.parser.get_soldiers()

    def get_spec_credits(self):
        """Get the players unused free specialist credits. soldiers.
        Will load the military page (if not already loaded)
        TODO: Get the troops also from the Throne page
        """
        log.debug("get_spec_credits()")
        if self.parser is None or self.parser.current_page != 'PAGE_MILITARY':
            self._get_military()
        assert('PAGE_MILITARY' == self.parser.current_page)
        return self.parser.get_spec_credits()

    def get_draft_rate(self):
        """Get the players draftrate.
        Will load the military page (if not already loaded)
        TODO: Get the troops also from the Throne page
        """
        log.debug("get_draft_rate()")
        if self.parser is None or self.parser.current_page != 'PAGE_MILITARY':
            self._get_military()
        assert('PAGE_MILITARY' == self.parser.current_page)
        return self.parser.get_draft_rate()


    def train_military(self, troops_dict):
        """Trains a set of troops.
        Input is expected as a dict with the following structure
        {
            "o-spec": <int to be trained>
            "d-spec": <int to be trained>
            "elite": <int to be trained>
            "thief": <int to be trained>
        }
        Will load the military page (if not already loaded)
        TODO: Get the troops also from the Throne page
        """
        log.debug("train_troops( %s )" % troops_dict)
        if self.parser is None or self.parser.current_page != 'PAGE_MILITARY':
            self._get_military()
        assert('PAGE_MILITARY' == self.parser.current_page)
        military_form = self.parser.get_military_form()

        log.debug("military_form['inputs']: %s" % military_form['inputs'])

        for (troop, field) in zip(['o-spec','d-spec','elite', 'thief'],['unit-quantity_0', 'unit-quantity_1', 'unit-quantity_2', 'unit-quantity_3']):
            if troop in troops_dict:
                military_form['inputs'][field]['value'] = troops_dict[troop]
            else:
                military_form['inputs'][field]['value'] = ""

        log.debug("military_form['inputs']: %s" % military_form['inputs'])
        values = {}
        for k,v in military_form['inputs'].items():
            if 'value' in v:
                values[k] = v['value']

        values['draft_rate'] = self.parser.get_draft_rate()[1]
        log.debug("values: %s" % values)

        data = urllib.urlencode(values)
        url = URL_BASE + self.nav_links['Military'] + military_form['form']['action']
        self._get_page(url, data, self.headers, htmlparser.MilitaryParser() )
        #Return the result
        return self.parser.get_train_result()

    def get_buildings(self):
        """Get the players buildings.
        Will load the growth page (if not already loaded)
        """
        log.debug("get_buildings()")
        if self.parser is None or self.parser.current_page != 'PAGE_GROWTH':
            self._get_growth()
        assert('PAGE_GROWTH' == self.parser.current_page)
        return self.parser.get_buildings()

    def build(self, buildings_dict):
        """Build stuff!
        Expects a dict with keys from lists.BUILDINGS (the plural case-sensitive version)
        Will load the growth page.
        """
        log.debug("build(): %s"%buildings_dict)
        if self.parser is None or self.parser.current_page != 'PAGE_GROWTH':
            self._get_growth()
        assert('PAGE_GROWTH' == self.parser.current_page)
        growth_form = self.parser.get_build_form()
        log.debug("growth_form: %s"%self.parser.get_build_form())

        log.debug("BUILDINGS: %s"%BUILDINGS)
        for building in BUILDINGS:
            log.debug("building: %s"% building[1])
            if building[1] in buildings_dict:
                log.debug("growth_form['inputs']['%s]['value'] = %d" % ('quantity_%d'%BUILDINGS.index(building), buildings_dict[building[1]] ))
                growth_form['inputs']['quantity_%d'%BUILDINGS.index(building)]['value'] = buildings_dict[building[1]]

        log.debug("ABOUT TO BUILD: %s"%growth_form['inputs'])

        values = {}
        for k,v in growth_form['inputs'].items():
            if 'value' in v:
                values[k] = v['value']

        data = urllib.urlencode(values)
        url = URL_BASE + self.nav_links['Growth'] + growth_form['form']['action']
        self._get_page(url, data, self.headers, htmlparser.GrowthParser() )

        #Return the result
        return self.parser.get_building_result()

    def get_build_info(self):
        """Get the build_info.
        Will load the growth page (if not already loaded)
        """
        log.debug("get_build_info()")
        if self.parser is None or self.parser.current_page != 'PAGE_GROWTH':
            self._get_growth()
        assert('PAGE_GROWTH' == self.parser.current_page)
        return self.parser.get_build_info()

    def get_science(self):
        """Get info from the science page (not the advisor).
        Will load the science page (if not already loaded)
        """
        log.debug("get_science()")
        if self.parser is None or self.parser.current_page != 'PAGE_SCIENCE':
            self._get_science()
        assert('PAGE_SCIENCE' == self.parser.current_page)
        return self.parser.get_science()

    def buy_science(self, sci_dict):
        """Buy a dict of science.
        Input is expected as a dict with the following structure
        {
            "Alchemy": <int to be bounght>
            "Tools": <int to be bounght>
            "Housing": <int to be bounght>
            "Food": <int to be bounght>
            "Military": <int to be bounght>
            "Crime": <int to be bounght>
            "Channeling": <int to be bounght>
        }
        Will load the science page (if not already loaded)
        """
        log.debug("buy_science( %s )" % sci_dict)
        if self.parser is None or self.parser.current_page != 'PAGE_SCIENCE':
            self._get_science()
        assert('PAGE_SCIENCE' == self.parser.current_page)
        science_form = self.parser.get_science_form()

        log.debug("science_form['inputs']: %s" % science_form['inputs'])

        for (sci, field) in zip(['Alchemy','Tools','Housing', 'Food', 'Military', 'Crime', 'Channeling'],['quantity_%d'%i for i in range(0,7)]):
            if sci in sci_dict:
                science_form['inputs'][field]['value'] = sci_dict[sci]
            else:
                science_form['inputs'][field]['value'] = ""

        log.debug("science_form['inputs']: %s" % science_form['inputs'])
        values = {}
        for k,v in science_form['inputs'].items():
            if 'value' in v:
                values[k] = int(v['value'])

        values['learn_rate'] = self.parser.get_learn_rate()[1]
        log.debug("values: %s" % values)

        data = urllib.urlencode(values)
        url = URL_BASE + self.nav_links['Sciences'] + science_form['form']['action']
        self._get_page(url, data, self.headers, htmlparser.ScienceParser() )

        #Return the result
        return self.parser.get_science_result()

    def get_science_info(self):
        """Get the science_info.
        Will load the science page (if not already loaded)
        """
        log.debug("get_science_info()")
        if self.parser is None or self.parser.current_page != 'PAGE_SCIENCE':
            self._get_science()
        assert('PAGE_SCIENCE' == self.parser.current_page)
        return self.parser.get_science_info()


if __name__ == "__main__":

        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename",
                          help="Insturctions file (not yet implemented)")
        parser.add_option("-d", "--debug", action="store_true", dest="debug",
                          default=False, help="Print lots of debug logging")
        parser.add_option("-l", "--log-level", dest="log_level", default=logging.WARN)
        parser.add_option("-c", "--config", help="Config file to read from (not implemented).")
        parser.add_option( "--page-cache", help="Directory to dump pages to (for debugging only).")
        parser.add_option("-u", "--username", help="Username for player.")
        parser.add_option("-p", "--password", help="Password for player. (can be defined in conf too)")
        (options, args) = parser.parse_args()

        if(options.debug):
            options.log_level = 10

        logging.basicConfig(level=int(options.log_level))
        logging.basicConfig(level=logging.WARN)

        #Actual logic
        log.debug("Instanciating player")
        player = Player()

        if(options.page_cache):
            player.page_cache = options.page_cache

        player.username = options.username
        log.debug("set username = %s" % player.username)

        player.password = options.password
        log.debug("set password = %s (masked)" % "".join(["*" for c in player.password]))

        log.info("Log in player (%s)...", player.username)


        mana = player.get_mana()
        spells = player.get_available_spells()

        while spells['Minor Protection'] <= 1:
            self.cast_spell('Minor Protection')
            spells = player.get_available_spells()


        resources = player.get_resources()

        if self.get_soldiers() > 0:
            troops = get_troops()
            if (troops['d-specs']['Home'] + troops['elite']['Home'])*3 < resouces['Acres'] :
                #Safe assumption, both have 5 def
                # leave 150 raw dpa
                pass
