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

    def ensure_spells_are_cast(spells, active_spells, player):
        log.debug("ensure_spells_are_cast: {0}".format(spells))
        resources = player.get_resources()
        for spell in spells:
            log.info("Trying to cast {0}.".format(spell))
            if spell in available_spells:
                if spell not in active_spells:
                    active_spells[spell] = 0
                while active_spells[spell] <= 1 and  resources['Runes'] > available_spells[spell][1] and 20 < player.get_mana():
                    if player.cast_spell(spell) is not None:
                        log.info("Cast {0}: Success".format(spell))
                        break
                    log.info("Cast {0}: Failed".format(spell))
                    resources = player.get_resources()

            log.info("Cast {0}: Done".format(spell))
            resources = player.get_resources()


    spells = ['Minor Protection', 'Patriotism', 'Inspire Army']
    ensure_spells_are_cast(spells, active_spells, player)

    if 'Fertile Lands' in available_spells:
        if 'Fertile Lands' not in active_spells:
            active_spells['Fertile Lands'] = 0
        while active_spells['Fertile Lands'] <= 1 and resources['Food'] < 20000 and resources['Runes'] > available_spells['Fertile Lands'][1] and 20 < player.get_mana():
            if player.cast_spell('Fertile Lands') is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()

    log.info("Cast Fertile Lands: Done")
    resources = player.get_resources()

    counter = 0
    resources = player.get_resources()
    troops_home = player.get_troops()
    thief_tot = troops_home['thief']['home'] + troops_home['thief']['training']
    thief_target = resources['Land'] * 1.1
    if thief_target > thief_tot:
        player.train_military({'thief': thief_target-thief_tot})

    resources = player.get_resources()
    while resources['Money'] > 250 and player.get_soldiers() > 0:
        counter +=1
        if counter > 4:
            break
        spec_count = min(player.get_soldiers(), resources['Money'] / 250)

        troops={'d-spec': (spec_count/2), 'o-spec': (spec_count/2)}

        trained_troops = player.train_military(troops)

        log.info("train_military(%s): %s" % (troops, trained_troops))



    # SCIENCE!!!
    available_books = player.get_science_info()['Books to Allocate']
    if 3 < available_books:
        buy_sci = {
            #"Alchemy": int(round(available_books/3)),
            #"Tools": int(round(available_books/3)),
            #"Housing": int(round(available_books/3)),
            "Food": int(round(available_books/2)),
            #"Military": int(round(available_books/16)),
            #"Crime": int(round(available_books/16)),
            "Channeling": int(round(available_books/2)),
            }
        result = player.buy_science(buy_sci)
        info_msg="Bought science: %s"%result
    else:
        info_msg = "Less than 3 books (have: %s)"%available_books
    log.info("Buying science DONE: %s", info_msg)

    print "DONE"

if __name__ == "__main__":
    main()
