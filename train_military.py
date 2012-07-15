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
        while spells['Minor Protection'] <= 2 and  resources['Runes'] > available_spells['Minor Protection'][1] and 20 < player.get_mana():
            if player.cast_spell('Minor Protection') is not None:
                break
            spells = player.get_active_spells()
            resources = player.get_resources()

    resources = player.get_resources()

    # If we are low on food, make sure we cast Fertile lands.
    if 'Fertile Lands' in available_spells:
        if 'Fertile Lands' not in spells:
            spells['Fertile Lands'] = 0
        while spells['Fertile Lands'] <= 2 and resources['Food'] < 30000 and resources['Runes'] > available_spells['Fertile Lands'][1] and 20 < player.get_mana():
            if player.cast_spell('Fertile Lands') is not None:
                break
            spells = player.get_active_spells()
            resources = player.get_resources()

    # If we are low on food, make sure we cast Fertile lands.
    if 'Patriotism' in available_spells:
        if 'Patritoism' not in spells:
            spells['Patriotism'] = 0
        while spells['Patriotism'] <= 2 and resources['Runes'] > available_spells['Patriotism'][1] and 20 < player.get_mana():
            if player.cast_spell('Patriotism') is not None:
                break
            spells = player.get_active_spells()
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
            troops={'d-spec': spec_count}
            if 1 > spec_count:
                break
        else:
            troops={'elite': leet_count}

        print "train_military(%s): %s" % (troops, player.train_military(troops))

    # if 'Paradise' in available_spells:
    #     while resources['Runes'] > available_spells['Paradise'][1] and 10 < player.get_mana():
    #         player.cast_spell('Paradise')
    #         resources = player.get_resources()

    #log.debug("build_result: %s" % player.build({"Farms": 1}))

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
        if 0.15 < buildings['Guilds']['total'] / build_info['Total Land']:
            to_build['Guilds'] = int((0.15 - (buildings['Guilds']['total'] / build_info['Total Land'])) * build_info['Total Land'])
        if 0.12 < buildings['Towers']['total'] / build_info['Total Land']:
            to_build['Towers'] = int((0.12 - (buildings['Guilds']['total'] / build_info['Total Land'])) * build_info['Total Land'])

        player.build(to_build)
    log.info("build_info: %s" ,player.get_build_info())
    log.info("buildings: %s", player.get_buildings())


    print "DONE"

if __name__ == "__main__":
    main()
