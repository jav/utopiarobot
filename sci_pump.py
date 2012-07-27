#!/usr/bin/env python

import logging
from optparse import OptionParser
import random
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
    log.info("Instanciating player")
    player = UtopiaRobot()

    if(options.page_cache):
        player.page_cache = options.page_cache

    player.username = options.username
    log.info("set username = %s" % player.username)

    player.password = options.password
    log.info("set password = %s (masked)" % "".join(["*" for c in player.password]))

    log.info("Log in player (%s)...", player.username)

    mana = player.get_mana()
    available_spells = player.get_available_spells()
    log.debug("available_spells: %s" % available_spells)
    spells = player.get_active_spells()
    resources = player.get_resources()

    # First and foremost, Make sure we have Minor Protection
    if 'Minor Protection' in available_spells:
        if 'Minor Protection' not in spells:
            spells['Minor Protection'] = 0
        while spells['Minor Protection'] <= 1 and  resources['Runes'] > available_spells['Minor Protection'][1] and 20 < player.get_mana():
            if player.cast_spell('Minor Protection') is not None:
                log.info("Cast Minor Protection: Success")
                break
            log.info("Cast Minor Protection: Failed")
            resources = player.get_resources()

    log.info("Cast Minor Protection: Done")
    resources = player.get_resources()

    # if we got plague, remove it.
    # Because we still don't detect plague-removal, we reload the throne page on each iteraton
    if "Nature's Blessing" in available_spells:
        if "Nature's Blessing" not in spells:
            spells["Nature's Blessing"] = 0
        while player.get_plague() and spells["Nature's Blessing"] <= 1 and  resources['Runes'] > available_spells["Nature's Blessing"][1] and 10 < player.get_mana():
            if player.cast_spell("Nature's Blessing") is not None:
                log.info("Cast Nature's Blessing: Success")
                break
            log.info("Cast Nature's Blessing: Failed")
            resources = player.get_resources()

    log.info("Cast Nature's Blessing: Done")
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
    log.info("Cast Fertile Lands: Done")

    # If we are low on food, make sure we cast Fertile lands.
    if 'Fountain of Knowledge' in available_spells:
        if 'Fountain of Knowledge' not in spells:
            spells['Fountain of Knowledge'] = 0
        while spells['Fountain of Knowledge'] <= 1 and resources['Runes'] > available_spells['Fountain of Knowledge'][1] and 20 < player.get_mana():
            if player.cast_spell('Fountain of Knowledge') is not None:
                log.info("Cast Fertile Lands: Success")
                break
            log.info("Cast Fertile Lands: Failed")
            resources = player.get_resources()
    log.info("Cast Fontain of Knowledge: Done")

    resources = player.get_resources()
    while 20 < player.get_mana() and player.get_soldiers() > 0:
        resources = player.get_resources()
        leet_count = resources['Money'] / 500

        while 1 > leet_count and player.get_mana >= 20:
            player.cast_spell("Tree of Gold")
            available_spells = player.get_available_spells()
            resources = player.get_resources()
            #leet_count = resources['Money'] / 500
            spec_count = resources['Money'] / 350
            troops={'o-spec': sec_count}
            trained_troops = player.train_military(troops)
        # if 1 > leet_count:
        #     troops={'o-spec': spec_count}
        #     if 1 > spec_count:
        #         break
        # else:
        #     troops={'elite': leet_count}

        #Bug here: Will only print the train-result from the last loop
        log.info("train_military(%s): %s" % (troops, trained_troops))

    # If we reach this point, and we're out of money. Let's try to spend our spec-credits
    resources = player.get_resources()
    if 350 > resources['Money'] and 0 < player.get_soldiers() and 0 < player.get_spec_credits():
        troops={'o-spec': min(player.get_soldiers(), player.get_spec_credits())}
        print "spec-credits: train_military(%s): %s" % (troops, player.train_military(troops))

    info_msg = ""
    if 'Paradise' in available_spells:
        if resources['Runes'] <= available_spells['Paradise']:
            info_msg = "Not enough runes (have: %s, need: %s)" % (resources['Runes'], available_spells['Paradise'])
        elif 10 >= player.get_mana():
            info_msg = "Not enough mana (%s%)" % player.get_mana()
        else:
            while resources['Runes'] > available_spells['Paradise'][1] and 10 < player.get_mana():
                result = player.cast_spell('Paradise')
                log.info("Cast Paradise - Result: %s" % result)
                resources = player.get_resources()
    else:
        info_msg = "Paradise not available to cast."
    log.info("Paradise done: %s"% info_msg)

    log.info("Prep building.")
    build_info = player.get_build_info()
    buildings = player.get_buildings()
    resources = player.get_resources()

    iterations_counter = 0
    while 6 < iterations_counter and 0 < build_info['Total Undeveloped land'] and build_info['Construction Cost'] < resources['Money']:
        iterations_counter += 1
        for k,v in buildings.items():
            buildings[k]['total'] = v['built'] + v['incoming']

        to_build = {}
        # min 8% farms
        if 0.08 < buildings['Farms']['total'] / build_info['Total Land']:
            to_build['Farms'] = int((0.07 - (buildings['Farms']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Farms'] : %s" % to_build['Farms'])
        if 0.15 < buildings['Guilds']['total'] / build_info['Total Land']:
            to_build['Guilds'] = int((0.15 - (buildings['Guilds']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Guilds'] : %s" % to_build['Guilds'])
        if 0.09 < buildings['Forts']['total'] / build_info['Total Land']:
            to_build['Forts'] = int((0.12 - (buildings['Forts']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Forts'] : %s" % to_build['Forts'])
        if 0.25 < buildings['Banks']['total'] / build_info['Total Land']:
            to_build['Banks'] = int((0.12 - (buildings['Banks']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Banks'] : %s" % to_build['Banks'])
        if 0.14 < buildings['Towers']['total'] / build_info['Total Land']:
            to_build['Towers'] = int((0.15 - (buildings['Towers']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Towers'] : %s" % to_build['Towers'])
        if 0.2 < buildings['Schools']['total'] / build_info['Total Land']:
            to_build['Schools'] = int((0.12 - (buildings['Schools']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Schools'] : %s" % to_build['Schools'])
        if 0.09 < buildings['Training Grounds']['total'] / build_info['Total Land']:
            to_build['Training Grounds'] = int((0.12 - (buildings['Training Grounds']['total'] / build_info['Total Land'])) * build_info['Total Land'])
            log.info("To build['Training Grounds'] : %s" % to_build['Training Grounds'])


        if 0 <= len(to_build):
            log.info("No need to build anything.")
            break

        log.info("Want to build: %s"% to_build)
        player.build(to_build)
        log.info("build_info: %s" ,player.get_build_info())
        log.info("buildings: %s", player.get_buildings())

        build_info = player.get_build_info()
        resources = player.get_resources()
        if 0 < build_info['Total Undeveloped land']:
                # If we are low on food, make sure we cast Fertile lands.
            while 'Tree of Gold' in available_spells and resources['Runes'] > available_spells['Tree of Gold'][1] and 20 < player.get_mana() and player.cast_spell('Tree of Gold') is not None:
                resources = player.get_resources()


    # SCIENCE!!!
    available_books = player.get_science_info()['Books to Allocate']
    if 3 < available_books:
        buy_sci = {
            "Alchemy": int(round(available_books/4)),
            "Tools": int(round(available_books/4)),
            "Housing": int(round(available_books/4)+random.randrange(0,10),
            "Food": int(round(available_books/16)),
            "Military": int(round(available_books/16)),
            "Crime": int(round(available_books/16)),
            "Channeling": int(round(available_books/16)),
            }
        result = player.buy_science(buy_sci)
        info_msg="Bought science: %s"%result
    else:
        info_msg = "Less than 3 books (have: %s)"%available_books
    log.info("Buying science DONE: %s", info_msg)

    print "DONE"

if __name__ == "__main__":
    main()
