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

    log.info("Get five random kds")


    islandlist=[]
    island=random.randint(0,41)
    for _ in range(1,10):
        log.info(islandlist)
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

    print "DONE"

if __name__ == "__main__":
    main()
