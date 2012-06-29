#!/usr/bin/env python

import cookielib
import inspect
#from ipdb import set_trace
import logging
from optparse import OptionParser
import os
import urllib
import urllib2
import re
import zlib

import htmlparser

log = logging.getLogger(__name__)

URL_BASE = "http://utopia-game.com"
URL_LOGIN = "%s/shared" % URL_BASE

class UPlayer(object):

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
        if self.page_cache:
            file_name = str(zlib.crc32(page))
            fh = open(self.page_cache + "/"+ file_name + ".html", 'w+')
            log.debug("Saving page to: %s" % file_name )
            fh.write(res)
            fh.close()

    def _do_login(self, parser):
        log.debug("do_login")

        # OK! Assert that we're on the login page!
        assert('PAGE_INIT' == self.parser.current_page)

        def _login(self):
            if 'PAGE_INIT' != self.parser.current_page:
                values= {}
                data = urllib.urlencode(values)
                log.debug("Loading page: %s" % URL_LOGIN)
                req = urllib2.Request(URL_LOGIN, data, self.headers)
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
        log.debug("_get_throne()")
        data = None
        req = urllib2.Request(URL_BASE + self.nav_links['Throne'], data, self.headers)
        res = urllib2.urlopen(req)
        self.result = res.read()

        self.parser = htmlparser.ThroneParser()
        self.parser.parse(self.result)
        self.cache_page(self.parser.current_page, self.result)

        if 'PAGE_INIT' == self.parser.current_page:
            log.info("Not logged in, -> do_login()")
            self._do_login(self)
            self.parser = htmlparser.ThroneParser()
            self.parser.parse(self.result)

        assert('PAGE_THRONE' == self.parser.current_page)
        if self.parser.get_nav_links():
            self.nav_links = self.parser.get_nav_links()

    def _get_mystics(self):
        log.debug("_get_mystics()")
        assert(0 < len(self.nav_links['Mystics']))
        data = None
        req = urllib2.Request(URL_BASE + self.nav_links['Mystics'], data, self.headers)
        res = urllib2.urlopen(req)
        self.result = res.read()
        self.parser = htmlparser.MysticParser()
        self.parser.parse(self.result)
        self.cache_page(self.parser.current_page, self.result)
        log.debug("Page loaded, self.parser.current_page: %s" % self.parser.current_page)
        if 'PAGE_INIT' == self.parser.current_page:
            log.info("Not logged in, -> do_login()")
            self._do_login(self)
            self.parser = htmlparser.MysticsParser()
            self.parser.parse(self.result)

        assert('PAGE_MYSTIC' == self.parser.current_page)
        if self.parser.get_nav_links():
            self.nav_links = self.parser.get_nav_links()

    def _check_login(self):
        log.debug("_check_login()")
        return self.is_loggedin

    def get_resources(self):
        log.debug("get_resources()")
        if self.parser is None or self.parser.get_resources() is None:
            self._get_throne()
        return self.parser.get_resources()

    def get_available_spells(self):
        log.debug("get_available_spells()")
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC':
            self._get_mystics()
        assert('PAGE_MYSTIC' == self.parser.current_page)
        self.parser.get_available_spells()

    def cast_spell(self, spell):
        log.debug("cast_spell()")
        #Ensure we are on the mystics page
        if self.parser is None or self.parser.current_page != 'PAGE_MYSTIC':
            self._get_mystics()
        assert('PAGE_MYSTIC' == self.parser.current_page)
        mystic_form = self.parser.get_mystic_form()
        #Cast the spell (send POST)
        data = urllib.urlencode( mystic_form['inputs'] )
        req = urllib2.Request(URL_BASE + self.nav_links['Mystics'] + mystic_form['form']['action'])
        res = urllib2.urlopen(req)
        self.result = res.read()
        #Check the result
        self.parser = htmlparser.MysticParser()
        self.parser.parse(self.result)
        self.cache_page(self.parser.current_page, self.result)
        #Return the result
        return self.parser.get_spell_result()


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
        player = UPlayer()

        if(options.page_cache):
            player.page_cache = options.page_cache

        player.username = options.username
        log.debug("set username = %s" % player.username)

        player.password = options.password
        log.debug("set password = %s (masked)" % "".join(["*" for c in player.password]))

        log.info("Log in player (%s)...", player.username)

        print player.get_resources()
        print player.get_resources()

        print player.get_available_spells()
        print player.get_active_spells()
