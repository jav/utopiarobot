#!/usr/bin/env python

import cookielib
import inspect
import logging
from optparse import OptionParser
import os
import urllib
import urllib2
import re

import htmlparser

log = logging.getLogger(__name__)

URL_BASE = "http://utopia-game.com"
URL_LOGIN = "%s/shared" % URL_BASE

PAGE_LOGIN=1
PAGE_CHOOSE_WORLD=2
PAGE_CHOOSE_ACCOUNT=3
PATE_THRONE=4

class uplayer(object):

    password = ""
    username = ""
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
    cookie_file = "cookie_file.txt"
    cj = False

    def __init__(self):
        self.cj = cookielib.LWPCookieJar()
        if os.path.isfile(self.cookie_file):
            self.cj.load(self.cookie_file)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)

    def do_login(self):
        log.debug("do_login")
        headers = { 'User-Agent' : self.user_agent }
        values= {}
        data = urllib.urlencode(values)
        log.debug("Loading page: %s" % URL_LOGIN)
        req = urllib2.Request(URL_LOGIN, data, headers)
        res = urllib2.urlopen(req)

        if log.level <= 10 and self.cj:
            log.debug("Cookies")
            for index, cookie in enumerate(self.cj):
                log.debug("%d: %s" % (index, cookie))
        self.cj.save(self.cookie_file)

        myparser = htmlparser.Parser()
        myparser.parse(res.read())

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
        log.debug(res.read())


if __name__ == "__main__":

        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename",
                          help="Insturctions file (not yet implemented)")
        parser.add_option("-d", "--debug", action="store_true", dest="debug",
                          default=False, help="Print lots of debug logging")
        parser.add_option("-l", "--log-level", dest="log_level", default=logging.WARN)
        parser.add_option("-c", "--config", help="Config file to read from (not implemented).")
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

        player.username = options.username
        log.debug("set username = %s" % player.username)

        player.password = options.password
        log.debug("set password = %s (masked)" % "".join(["*" for c in player.password]))

        log.info("Log in player (%s)...", player.username)
        player.do_login()

