#!/usr/bin/env python

import logging
from optparse import OptionParser

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
    log.debug("Instanciating player")
    player = UtopiaRobot()

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
        player.cast_spell('Minor Protection')
        spells = player.get_available_spells()

    resources = player.get_resources()

    if player.get_soldiers() > 0:
        troops={"d-spec": 1}
        print "train_military(%s): %s" % (troops, player.train_military(troops))
        # troops = get_troops()
        # if (troops['d-specs']['Home'] + troops['elite']['Home'])*3 < resouces['Acres'] :
        #     #Safe assumption, both have 5 def
        #     # leave 150 raw dpa
        #     pass

    print "DONE"

if __name__ == "__main__":
    main()
