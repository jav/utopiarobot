#!/usr/bin/env python

import inspect
import logging
from optparse import OptionParser
import urllib
import urllib2
import re
import sgmllib


log = logging.getLogger(__name__)

class MyParser(sgmllib.SGMLParser):
    "A simple parser class."

    parserState = {}
    parserState['form_depth'] = 0

    login_info = {}

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
        log.debug("start_input()")
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

class uplayer(object):

    password = ""
    username = ""
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"

    def __init__(self):
        pass

    def do_login(self):
        headers = { 'User-Agent' : self.user_agent }
        values= {}
        data = urllib.urlencode(values)
        req = urllib2.Request("http://utopia-game.com/shared", data, headers)
        res = urllib2.urlopen(req)

        myparser = MyParser()
        myparser.parse(res.read())

        login_fields = myparser.get_login_fields()


        post = {}
        for k,v in login_fields.items():
            print "login_fields - k:%s, v:%s" % (k,v)
            if 'other' == k:
                pass
            elif 'name' in v.keys():
                print "TYPE", v['type']
                if 'password' == v['type']:
                    v['value'] = '123'
                    login_fields[k]['value'] = v['value']
                if 'username' == v['type']:
                    v['value'] = 'jav'
                    login_fields[k]['value'] = v['value']
            post[k] = v

        log.debug( "login_fields", login_fields )

        value = {}
        for k,v in login_fields.items():
            if 'name' == k:
                value[k] = v

        log.debug( "value", value )

        data = urllib.urlencode(values)
        req = urllib2.Request(login_fields['form']['action'], data, headers)
        res = urllib2.urlopen(req)
        log.debug(res.read())


if __name__ == "__main__":

        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename",
                          help="Insturctions file (not yet implemented)")
        parser.add_option("-d", "--debug",
                          action="store_true", dest="debug", default=False,
                          help="Print lots of debug logging")
        parser.add_option("-l", "--log-level", dest="log_level", default=logging.WARN)
        parser.add_option("-c", "--config", help="Config file to read from.")
        parser.add-option("-u", "--username", help="Username for player.")
        parser.add-option("-p", "--password", help="Password for player. (can be defined in conf too)")
        (options, args) = parser.parse_args()

        if(options.debug):
            options.log_level = 10

        logging.basicConfig(level=int(options.log_level))
        logging.basicConfig(level=logging.WARN)

        #Actual logic
        log.debug("Instanciating player")
        player = uplayer()
        log.info("Log in player")
        player.do_login()

