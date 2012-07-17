#!/usr/bin/env python

import logging
from optparse import OptionParser
import sys

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
    available_spells = player.get_available_spells()
    log.debug("available_spells: %s" % available_spells)
    spells = player.get_active_spells()
    resources = player.get_resources()

    # First and foremost, make sure we have Minor Protection
    if 'Minor Protection' in available_spells:
        if 'Minor Protection' not in spells:
            spells['Minor Protection'] = 0
        while spells['Minor Protection'] <= 1 and  resources['Runes'] > available_spells['Minor Protection'][1] and 20 < player.get_mana():
            if player.cast_spell('Minor Protection') is not None:
                log.info("Cast Minor Protection: Success")
                break
            log.info("Cast Minor Protection: Failed")
            resources = player.get_resources()

    resources = player.get_resources()

    # If we are low on food, make sure we cast Fertile lands.
    if 'Fertile Lands' in available_spells:
        if 'Fertile Lands' not in spells:
            spells['Fertile Lands'] = 0
        while spells['Fertile Lands'] <= 1 and resources['Food'] < 30000 and resources['Runes'] > available_spells['Fertile Lands'][1] and 20 < player.get_mana():
            if player.cast_spell('Fertile Lands') is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()

    # If we are low on food, make sure we cast Fertile lands.
    if 'Fountain of Knowledge' in available_spells:
        if 'Fountain of Knowledge' not in spells:
            spells['Fountain of Knowledge'] = 0
        while spells['Fountain of Knowledge'] <= 1 and resources['Food'] < 30000 and resources['Runes'] > available_spells['Fountain of Knowledge'][1] and 20 < player.get_mana():
            if player.cast_spell('Fountain of Knowledge') is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()

    resources = player.get_resources()
    while 20 < player.get_mana() and player.get_soldiers() > 0:
        resources = player.get_resources()
        leet_count = resources['Money'] / 500

        while 1 > leet_count and player.get_mana >= 20:
            player.cast_spell("Tree of Gold")
            available_spells = player.get_available_spells()
            resources = player.get_resources()
            leet_count = resources['Money'] / 500

        if 1 > leet_count:
            spec_count = resources['Money'] / 350
            troops={'o-spec': spec_count}
            if 1 > spec_count:
                break
        else:
            troops={'elite': leet_count}

        print "train_military(%s): %s" % (troops, player.train_military(troops))

    # If we reach this point, and we're out of money. Let's try to spend our spec-credits
    resources = player.get_resources()
    if 350 > resources['Money'] and 0 < player.get_soldiers() and 0 < player.get_spec_credits():
        troops={'o-spec': min(player.get_soldiers(), player.get_spec_credits())}
        print "spec-credits: train_military(%s): %s" % (troops, player.train_military(troops))

    if 'Paradise' in available_spells:
        while resources['Runes'] > available_spells['Paradise'][1] and 10 < player.get_mana():
            result = player.cast_spell('Paradise')
            log.info("Cast Paradise - Result: %s" % result)
            resources = player.get_resources()

    build_info = player.get_build_info()
    buildings = player.get_buildings()
    for k,v in buildings.items():
        buildings[k]['total'] = v['built'] + v['incoming']
    resources = player.get_resources()
    to_build = {}
    if 0 < build_info['Total Undeveloped land'] and build_info['Construction Cost'] < resources['Money']:
        # min 8% farms
        if 0.07 < buildings['Farms']['total'] / build_info['Total Land']:
            to_build['Farms'] = int((0.07 - (buildings['Farms']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Farms'] : %s" % to_build['Farms'])
        if 0.15 < buildings['Guilds']['total'] / build_info['Total Land']:
            to_build['Guilds'] = int((0.15 - (buildings['Guilds']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Guilds'] : %s" % to_build['Guilds'])
        if 0.12 < buildings['Towers']['total'] / build_info['Total Land']:
            to_build['Towers'] = int((0.15 - (buildings['Towers']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Towers'] : %s" % to_build['Towers'])
        if 0.12 < buildings['Schools']['total'] / build_info['Total Land']:
            to_build['Schools'] = int((0.12 - (buildings['Schools']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Schools'] : %s" % to_build['Schools'])

        player.build(to_build)
    log.info("build_info: %s" ,player.get_build_info())
    log.info("buildings: %s", player.get_buildings())


    print "DONE"

if __name__ == "__main__":
    main()
