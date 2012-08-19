#!/usr/bin/env python

import json
import logging
from optparse import OptionParser
import random
import sys
import urllib
import urllib2

from utopia_robot.robot import UtopiaRobot

log = logging.getLogger(__name__)

def main():
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
    log.info("Instanciating player")
    player = UtopiaRobot()

    if(options.page_cache):
        player.page_cache = options.page_cache

    player.username = options.username
    log.info("set username = %s" % player.username)

    player.password = options.password
    log.info("set password = %s (masked)" % "".join(["*" for c in player.password]))

    log.info("Log in player (%s)...", player.username)

    counter = 0
    resources = player.get_resources()
    troops_home = player.get_troops()
    thief_tot = troops_home['thief']['home'] + troops_home['thief']['training']
    if 500 > thief_tot:
        player.train_military({'thief': 500-thief_tot}, "EMERGENCY")

    resources = player.get_resources()
    while resources['Money'] > 250 and player.get_soldiers() > 0:
        counter +=1
        if counter > 4:
            break
        spec_count = resources['Money'] / 250
        troops={'d-spec': spec_count/3, 'o-spec': 2*(spec_count/3)}
        trained_troops = player.train_military(troops, "EMERGENCY")
        log.info("train_military(%s): %s" % (troops, trained_troops))

if __name__ == "__main__":
    main()
