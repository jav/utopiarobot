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
    parser.add_option("-c", "--config", help="Config file to read from (not implemented).")
    parser.add_option( "--page-cache", help="Directory to dump pages to (for debugging only).")
    parser.add_option("-u", "--username", help="Username for player.")
    parser.add_option("-p", "--password", help="Password for player. (can be defined in conf too)")
    (options, args) = parser.parse_args()

    if(options.debug):
        options.log_level = 10


    print '''This script will
Train 75dpa (d-specs)
Train 2tpa
Train number of d-specs * 0.2 as leets
Train everything else as o-specs.

If it does not have enough gc, and ToG is available, it will ToG on demand
and stop when mana is <25% (or out of runes)
'''



    print "Instanciating player"
    player = UtopiaRobot()

    if options.page_cache is not None:
        player.page_cache = options.page_cache

    assert(options.username is not None)
    assert(options.password is not None)

    player.username = options.username
    player.password = options.password
    print "Log in player (%s, %s)...", (player.username,"".join(["*" for c in player.password]))

    #We'll need to know which spells are available lateron, this info dosen't change much.
    available_spells = player.get_available_spells()

    # Check our military status
    resources = player.get_resources()
    troops = player.get_troops()

    # Right now, we are not accounting for armories, we should.
    # also, we're not accounting for different race-leets.
    # So, assume standard cost, and human leets (5/5)
    def need_more_def(troops):
        total_spec_def = (troops['d-spec']['home'] + troops['d-spec']['training'] + troops['elite']['home'] + troops['elite']['training']) * 5
        return 75 > (total_spec_def / resources['Land'])

    while need_more_def(troops) and 0 < player.get_soldiers():
        print "Need more def, lets train some."
        
        if  350 > resources['Money']:
            print "I'm short on money, lets ToG!"
            #cast Tog
            if 'Tree of Gold' in available_spells and resources['Runes'] > available_spells['Tree of Gold'] and 20 < player.get_mana():
                player.cast_spell('Tree of Gold')
                print "ToG done, let's try to trian some troops!"
            else:
                print "Oh, I don't have ToG. Breaking loop"
                break
        # Train d-specs please
        train_target = (75*resources['Land']/5) - (troops['d-spec']['home']+troops['d-spec']['training'] + troops['elite']['home']+troops['elite']['training'])
        print "Trying to train %d d-specs" % train_target
        train_result = player.train_military({'d-spec': train_target})
        print "Train result: %s" % train_result
        troops = player.get_troops()
        print "Home + in training  = %d specs, %d leets " % (troops['d-spec']['training']+troops['d-spec']['training'],troops['elite']['training']+troops['elite']['training'])
        resources = player.get_resources()

    tot_def = (troops['d-spec']['home'] + troops['d-spec']['training'] + troops['elite']['home']+troops['elite']['training']) * 5
    land = resources['Land']
    print "Total (incomming) def: %d, dpa: %f" % (tot_def, tot_def/land)

if __name__ == "__main__":
    main()
