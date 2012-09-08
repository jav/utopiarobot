#!/usr/bin/env python

import json
import logging
from optparse import OptionParser
import random
import sys
import time
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


    spells = ['Minor Protection', 'Fertile Lands', 'Love and Peace', "Patriotism"]
    ensure_spells_are_cast(spells, active_spells, player)

    if "Nature's Blessing" in available_spells:
        while player.get_plague() and resources['Runes'] > available_spells["Nature's Blessing"][1] and 15 < player.get_mana():
            if player.cast_spell("Nature's Blessing") is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()


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

#    counter = 0
#    resources = player.get_resources()
#    troops_home = player.get_troops()
    # thief_tot = troops_home['thief']['home'] + troops_home['thief']['training']
    # thief_target = resources['Land'] * 2
    # if thief_target > thief_tot:
    #     player.train_military({'thief': thief_target-thief_tot})

    # resources = player.get_resources()
    # while resources['Money'] > 500 and player.get_soldiers() > 0:
    #     counter +=1
    #     if counter > 4:
    #         break
    #     spec_count = min(player.get_soldiers(), resources['Money'] / 500)

    #     troops={'elite': (spec_count) }

    #     trained_troops = player.train_military(troops)

    #     log.info("train_military(%s): %s" % (troops, trained_troops))



    # SCIENCE!!!
    available_books = player.get_science_info()['Books to Allocate']
    if 3 < available_books:
        buy_sci = {
	    "Alchemy": int(round(available_books)),
            #"Tools": int(round(available_books/7)),
            #"Housing": int(round(available_books/7)),
            #"Food": int(round(available_books/7)),
            #"Military": int(round(available_books/7)),
            #"Crime": int(round(available_books/7)),
            #"Channeling": int(round(available_books/7)),
            }
        result = player.buy_science(buy_sci)
        info_msg="Bought science: %s"%result
    else:
        info_msg = "Less than 3 books (have: %s)"%available_books
    log.info("Buying science DONE: %s", info_msg)

    print "DONE"

    # Dice cost *2 gives enough margin to cast all spels next cycle.
    # So, if we have dice cost *3, spend one dice
    if 'Paradise' in available_spells:
        while resources['Runes'] > available_spells['Paradise'][1]*3 and 20 < player.get_mana():
            if player.cast_spell('Paradise') is not None:
                log.info("Cast Paradise: Success")
                break
            log.info("Cast Paradise: Failed")
            resources = player.get_resources()

    log.info("Cast Paradise: Done")

    #everything is looking good.
    # Lets fetch a few KDs and we 'target search'

    islandlist=[]
    island=random.randint(0,41)
    iterations = random.randint(3,10)
    for _ in range(iterations+1):
        log.info("Islandlist: %s" % islandlist)
        while island in islandlist:
            island = random.randint(1,41)
        islandlist.append(island)
        for kd in range(1,10):
            log.info("Fetching kd:%d, island:%d" % (kd, island))
            kd_info = player.get_kd_info(kd,island)
            kd_json = json.dumps(kd_info).replace("'",'"')

            with open("%d-%d.txt"%(kd,island),'w') as f:
                f.write(kd_json)
            # post to db
            values={"textarea": kd_json}
            data = urllib.urlencode(values)
            headers={}
            log.debug("Posting %s to 127.0.0.1.", kd_json)
            req = urllib2.Request("http://127.0.0.1:5006/post_kd/", data, headers)
            urllib2.urlopen(req)
            time.sleep(random.randint(4,10))

if __name__ == "__main__":
    main()
