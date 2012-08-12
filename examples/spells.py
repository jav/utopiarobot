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

    available_spells = player.get_available_spells()
    log.debug("available_spells: %s" % available_spells)
    active_spells = player.get_active_spells()
    resources = player.get_resources()

    if 'Patriotism' in available_spells: #Check for presence in available spells (to avoid a future KeyError exception)
        if 'Patriotism' not in active_spells: # If the spell is not active, set it to -1 (again, to avoid KeyError exeptions)
            active_spells['Patriotism'] = -1
        while active_spells['Patriotism'] <= 1 and  resources['Runes'] > available_spells['Patriotism'][1] and 20 < player.get_mana():
            if player.cast_spell('Patriotism') is not None:
                log.info("Cast Patriotism: Success")
                break
            log.info("Cast Patriotism: Failed")
            resources = player.get_resources()

    log.info("Cast Patriotism: Done")
    resources = player.get_resources()

    if 'Fertile Lands' in available_spells:
        if 'Fertile Lands' not in spells:
            active_spells['Fertile Lands'] = -1
        while active_spells['Fertile Lands'] <= 1 and resources['Food'] < 20000 and resources['Runes'] > available_spells['Fertile Lands'][1] and 20 < player.get_mana():
            if player.cast_spell('Fertile Lands') is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()

    log.info("Cast Fertile Lands: Done")
    resources = player.get_resources()

    if 'Love and Peace' in available_spells:
        if 'Love and Peace' not in active_spells:
            active_spells['Love and Peace'] = -1
        while active_spells['Love and Peace'] <= 1 and resources['Runes'] > available_spells['Love and Peace'][1] and 20 < player.get_mana():
            if player.cast_spell('Love and Peace') is not None:
                log.info("Cast Love and Peace: Success")
                break
            log.info("Cast Love and Peace: Failed")
            resources = player.get_resources()

    log.info("Cast Love and Peace: Done")
    resources = player.get_resources()

    print "DONE"

if __name__ == "__main__":
    main()
