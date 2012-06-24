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

class uplayer(object):

    password = ""
    username = ""
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
    cookie_file = "cookie_file.txt"
    cj = False
    page_cache = False

    def __init__(self):
        self.cj = cookielib.LWPCookieJar()
        if os.path.isfile(self.cookie_file):
            self.cj.load(self.cookie_file)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)

    def cache_page(self, page, res):
        if self.page_cache:
            fh = open(self.page_cache + "/"+ str(zlib.crc32(page)) + ".html", 'w+')
            fh.write(res)
            fh.close()

    def do_login(self):
        log.debug("do_login")
        headers = { 'User-Agent' : self.user_agent }
        values= {}
        data = urllib.urlencode(values)
        log.debug("Loading page: %s" % URL_LOGIN)
        req = urllib2.Request(URL_LOGIN, data, headers)
        res = urllib2.urlopen(req)
        result = res.read()
        log.debug("Downloaded %d bytes" % len(result))
        #self.cache_page(URL_LOGIN, res)

#        if log.level <= 10 and self.cj:
#            log.debug("Cookies")
#            for index, cookie in enumerate(self.cj):
#                log.debug("%d: %s" % (index, cookie))
#        self.cj.save(self.cookie_file)

        myparser = htmlparser.LoginParser()
        myparser.parse(result)
        assert( myparser.last_page == "PAGE_INIT")
        self.cache_page("PAGE_INIT", result)

        login_fields = myparser.get_login_fields()

        post = {}
        for k,v in login_fields.items():
            if 'other' == k:
                pass
            elif 'name' in v.keys():
                print "TYPE", v['type']
                if 'password' == v['name']:
                    v['value'] = self.password
                    login_fields[k]['value'] = v['value']
                if 'username' == v['name']:
                    v['value'] = self.username
                    login_fields[k]['value'] = v['value']
            post[k] = v

        log.debug( "login_fields %s" % login_fields )

        values = {}
        for k,v in login_fields.items():
            log.debug("k: %s, v: %s" %( k,v))
            if isinstance(v, dict) and 'name' in v.keys():
                values[v['name']] = v['value']

        log.debug( "values %s", values )

        data = urllib.urlencode(values)

        URL_TAKE_LOGIN = "%s%s" % (URL_BASE, login_fields['form']['action'])
        log.debug("accessing %s POST:%s" % (URL_TAKE_LOGIN, data) )
        req = urllib2.Request(URL_TAKE_LOGIN, data, headers)
        res = urllib2.urlopen(req)
        result = res.read()

        #pick server
        myparser = htmlparser.LobbyParser()
        myparser.parse(result)
        assert( myparser.last_page == "PAGE_LOBBY")
        self.cache_page("PAGE_LOBBY", result)

        lobby_fields = myparser.get_lobby_fields()
        URL_TAKE_WORLD_CHOICE = "%s%s" % (URL_BASE, lobby_fields['chooser_link'])
        data = None
        log.debug("accessing %s POST:%s" % (URL_TAKE_WORLD_CHOICE, data) )
        req = urllib2.Request(URL_TAKE_WORLD_CHOICE, data, headers)
        res = urllib2.urlopen(req)
        result = res.read()

        log.debug(result)

        myparser = htmlparser.ProvSelectParser()
        myparser.parse(result)
        assert( myparser.last_page == "PAGE_PROV")
        self.cache_page("PAGE_PROV", result)

        prov_fields = myparser.get_choose_province_fields()
        URL_TAKE_PROV_CHOICE = "%s%s" % (URL_BASE, prov_fields['chooser_link'])
        data = None
        log.debug("accessing %s POST:%s" % (URL_TAKE_PROV_CHOICE, data) )
        req = urllib2.Request(URL_TAKE_PROV_CHOICE, data, headers)
        res = urllib2.urlopen(req)
        result = res.read()

        log.debug(result)

        self.cache_page("PAGE_THRONE", result)

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
        player = uplayer()

        if(options.page_cache):
            player.page_cache = options.page_cache

        player.username = options.username
        log.debug("set username = %s" % player.username)

        player.password = options.password
        log.debug("set password = %s (masked)" % "".join(["*" for c in player.password]))

        log.info("Log in player (%s)...", player.username)
        player.do_login()

