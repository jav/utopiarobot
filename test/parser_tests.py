from utopia_robot import htmlparser
import mock
import urllib2

class login_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LoginParser()
                in_file = "test/login.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. sFor this test to work, you need a copy of the tested page atlink %s to a copy of the expected page. Missing file: %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_INIT" == self.parser.current_page)

        def test_login_fields(self):
                login_info = self.parser.get_login_info()
                assert("/shared/login/" == login_info['form']['action'])
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == login_info['inputs']['csrfmiddlewaretoken']['value'])
                assert('password' in login_info['inputs'])
                assert('username' in login_info['inputs'])


class lobby_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.LobbyParser()
                in_file = "test/lobby.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_LOBBY" == self.parser.current_page)

        def test_lobby_fields(self):
                lobby_fields = self.parser.get_lobby_fields()
                assert("/wol/chooser/" == lobby_fields['chooser_link'])


class choose_prov_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ProvSelectParser()
                in_file = "test/prov_select.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)
        def test_page_enum(self):
                print("self.parser.current_page: %s" % self.parser.current_page)
                assert("PAGE_PROV" == self.parser.current_page)

        def test_choose_province_fields(self):
                chooser_fields = self.parser.get_choose_province_fields()
                assert("/wol/game/throne" == chooser_fields['chooser_link'])


class throne_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ThroneParser()
                in_file = "test/throne_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print("self.parser.current_page: %s" % self.parser.current_page)
                assert("PAGE_THRONE" == self.parser.current_page)

	def test_navigation(self):
                nav_links = self.parser.get_nav_links()

                links = { 'Throne'  :  '/wol/game/throne',
                          'Kingdom' :  '/wol/game/kingdom_details',
                          'News'    :  '/wol/game/province_news',
                          'Explore' :  '/wol/game/explore',
                          'Growth'  :  '/wol/game/build',
                          'Sciences':  '/wol/game/science',
                          'Military':  '/wol/game/train_army',
                          'Wizards' :  '/wol/game/wizards',
                          'Mystics' :  '/wol/game/enchantment',
                          'Thievery':  '/wol/game/thievery',
                          'War Room':  '/wol/game/send_armies',
                          'Aid'     :  '/wol/game/aid',
                          'Mail'    :  '/wol/mail/inbox/',
                          'Forum'   :  '/wol/kingdom_forum/topics/',
                          'Politics':  '/wol/game/vote',
                          'Rankings':  '/wol/game/ranking',
                          'Preferences': '/wol/game/preferences/',
                          'Taunts': '/wol/game/taunts'
                        }
                print nav_links
                for (title, link) in links.items():
                        print "%s == nav_links[%s] (%s)" % (link, title, nav_links[title])
                        assert(link == nav_links[title])

        def test_resources(self):
                resources = self.parser.get_resources()

                print resources
                assert(480594 == resources['Money'])
                assert(10065  == resources['Peasants'])
                assert(78481  == resources['Food'])
                assert(13244  == resources['Runes'])
                assert(213924 == resources['Net Worth'])
                assert(1398   == resources['Land'])
                assert(153.021   == resources['Net Worth/Acre'])

        def test_plague(self):
                plague = self.parser.get_plague()
                print "plague:", plague
                assert(False == plague)

class throne_parser_tests_plague(object):
        def setup(self):
                self.parser = htmlparser.ThroneParser()
                in_file = "test/throne_plague.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_plague(self):
                plague = self.parser.get_plague()
                print "plague:", plague
                assert(True == plague)



class mystics_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MysticParser()
                in_file = "test/mystic_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_MYSTIC" == self.parser.current_page)

        def test_form_inputs(self):
                print self.parser.mystic_form
                assert('48d2f5a8ed943a16e37423a1c320f1dd' == self.parser.mystic_form['inputs']['csrfmiddlewaretoken']['value'])

        def test_available_spells(self):
                available_spells = self.parser.get_available_spells()
                print "available_spells:", available_spells
                print "Paradise:", available_spells['Paradise']
                print "Paradise:", available_spells['Paradise'][0]
                assert('Fertile Lands' in available_spells)
                print "Available spells:", available_spells
                assert(('FERTILE_LANDS',815) == available_spells['Fertile Lands'])
                assert(('PARADISE', 4891) == available_spells['Paradise'])
                assert(('LOVE_AND_PEACE', 1141) == available_spells['Love and Peace'])
                assert(('SHADOW_LIGHT', 3098) == available_spells['Shadow Light'])
                assert(('NATURES_BLESSING', 978) == available_spells["Nature's Blessing"])
                assert(('INSPIRE_ARMY', 1793) == available_spells['Inspire Army'])
                assert(('FOUNTAIN_OF_KNOWLEDGE', 2527) == available_spells['Fountain of Knowledge'])
                assert(('TREE_OF_GOLD', 1304) == available_spells['Tree of Gold'])
                assert(('FERTILE_LANDS', 815) == available_spells['Fertile Lands'])
                assert(('WAR_SPOILS', 2364) == available_spells['War Spoils'])
                assert(('PARADISE', 4891) == available_spells['Paradise'])
                assert(('MAGIC_SHIELD', 815) == available_spells['Magic Shield'])
                assert(('ANONYMITY', 2119) == available_spells['Anonymity'])
                assert(('BUILDERS_BOON', 1630) == available_spells['Builders Boon'])
                assert(('MINOR_PROTECTION', 570) == available_spells['Minor Protection'])


        def test_get_mana(self):
                assert(68 == self.parser.get_mana())

        def test_cast_paradise_success(self):
                parser = htmlparser.MysticParser()
                in_file = 'test/spell_paradise.html'
                try:
                        with open(in_file) as page:
                                parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)


                parser.parse(in_file)
                paradise_result = parser.get_spell_result()
                print "paradise_result: %s" % paradise_result
                assert(5 == paradise_result)
                mystic_form = parser.get_mystic_form()
                print mystic_form
                assert('88e2dabb2a8b615561e743d05668d47d' == mystic_form['inputs']['csrfmiddlewaretoken']['value'])

class mystics_advisor_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MysticAdvisorParser()
                in_file = "test/mystic_advisor.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                assert("PAGE_MYSTIC_ADVISOR" == self.parser.current_page)

        def test_get_active_spells(self):
                active_spells = self.parser.get_active_spells()
                print active_spells
                assert(15 == active_spells['Minor Protection'])
                assert(3 == active_spells["Nature's Blessing"])
                assert(1 == active_spells["Love and Peace"])
                assert(14 == active_spells["Fountain of Knowledge"])


class military_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.MilitaryParser()
                in_file = "test/military_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_MILITARY" == self.parser.current_page)

        def test_get_soldiers(self):
                soldiers = self.parser.get_soldiers()
                print soldiers
                assert(1293 == soldiers)

        def test_get_troops(self):
                troops = self.parser.get_troops()
                print "troops:", troops

                assert(1530 == troops['o-spec']['home'])
                assert(807 == troops['o-spec']['training'])
                assert(350 == troops['o-spec']['cost'])
                assert(806 == troops['o-spec']['max'])

                assert(839 == troops['d-spec']['home'])
                assert(165 == troops['d-spec']['training'])
                assert(350 == troops['d-spec']['cost'])
                assert(806 == troops['d-spec']['max'])

                assert(11184 == troops['elite']['home'])
                assert(53 == troops['elite']['training'])
                assert(500 == troops['elite']['cost'])
                assert(564 == troops['elite']['max'])

                assert(2222 == troops['thief']['home'])
                assert(0 == troops['thief']['training'])
                assert(500 == troops['thief']['cost'])
                assert(564 == troops['thief']['max'])

        def test_get_spec_credits(self):
                credits = self.parser.get_spec_credits()
                print "credits:", credits
                assert(123 == credits)

class growth_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.GrowthParser()
                in_file = "test/growth_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_GROWTH" == self.parser.current_page)

        def test_get_buildings(self):
                buildings = self.parser.get_buildings()
                print "buildings:", buildings

                assert(228 == buildings['Homes']['built'])
                assert( 36 == buildings['Homes']['incoming'])
                assert(167 == buildings['Farms']['built'])
                assert( 18 == buildings['Farms']['incoming'])
                assert(  0 == buildings['Mills']['built'])
                assert(  0 == buildings['Mills']['incoming'])
                assert(486 == buildings['Banks']['built'])
                assert( 50 == buildings['Banks']['incoming'])
                assert(106 == buildings['Training Grounds']['built'])
                assert(  0 == buildings['Training Grounds']['incoming'])
                assert(  0 == buildings['Armouries']['built'])
                assert(  0 == buildings['Armouries']['incoming'])
                assert(  0 == buildings['Military Barracks']['built'])
                assert(  0 == buildings['Military Barracks']['incoming'])
                assert( 98 == buildings['Forts']['built'])
                assert(  0 == buildings['Forts']['incoming'])
                assert(  0 == buildings['Guard Stations']['built'])
                assert(  0 == buildings['Guard Stations']['incoming'])
                assert(  0 == buildings['Hospitals']['built'])
                assert(  0 == buildings['Hospitals']['incoming'])
                assert(248 == buildings['Guilds']['built'])
                assert( 15 == buildings['Guilds']['incoming'])
                assert(196 == buildings['Towers']['built'])
                assert( 32 == buildings['Towers']['incoming'])
                assert( 28 == buildings["Thieves' Dens"]['built'])
                assert(  0 == buildings["Thieves' Dens"]['incoming'])
                assert(  0 == buildings['Watch Towers']['built'])
                assert(  0 == buildings['Watch Towers']['incoming'])
                assert(  0 == buildings['Libraries']['built'])
                assert(  0 == buildings['Libraries']['incoming'])
                assert(  0 == buildings['Schools']['built'])
                assert(  0 == buildings['Schools']['incoming'])
                assert( 96 == buildings['Stables']['built'])
                assert(  0 == buildings['Stables']['incoming'])
                assert(  0 == buildings['Dungeons']['built'])
                assert(  0 == buildings['Dungeons']['incoming'])


        def test_get_form_fields(self):
                build_form = self.parser.get_build_form()
                print "build_form:", build_form
                assert("88e2dabb2a8b615561e743d05668d47d" == build_form['inputs']['csrfmiddlewaretoken']['value'])
                assert("Order Construction" == build_form['inputs']['build']['value'])
                for i in range(0, 18):
                        field = 'quantity_%d'%i
                        print field
                        assert( field in build_form['inputs'] )

        def test_get_build_info(self):
                build_info = self.parser.get_build_info()
                print "build_info:", build_info

                assert(1814 == build_info['Total Land'])
                assert( 865 == build_info['Construction Cost'])
                assert(  10 == build_info['Total Undeveloped land'])
                assert(  10 == build_info['Maximum Buildable Now'])
                assert(  16 == build_info['Construction Time'])
                assert( 463 == build_info['Raze Cost'])
                assert(  32 == build_info['Free Building Credits'])
                assert( 143 == build_info['Maximum Razeable Now'])


class science_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ScienceParser()
                in_file = "test/science_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_SCIENCE" == self.parser.current_page)


        def test_get_science(self):
                science = self.parser.get_science()
                print "science:", science

                assert(21132 == science['Alchemy']['points'])
                assert(5.5 == science['Alchemy']['effect'])
                assert(0 == science['Alchemy']['incomming'])

                assert(73226 == science['Tools']['points'])
                assert(7.4 == science['Tools']['effect'])
                assert(9996 == science['Tools']['incomming'])

                assert(32578 == science['Housing']['points'])
                assert(3.2 == science['Housing']['effect'])
                assert(0 == science['Housing']['incomming'])

                assert(4892 == science['Food']['points'])
                assert(15.2 == science['Food']['effect'])
                assert(0 == science['Food']['incomming'])

                assert(4892 == science['Military']['points'])
                assert(2.7 == science['Military']['effect'])
                assert(0 == science['Military']['incomming'])

                assert(21340 == science['Crime']['points'])
                assert(23.8 == science['Crime']['effect'])
                assert(0 == science['Crime']['incomming'])

                assert(20860 == science['Channeling']['points'])
                assert(23.6 == science['Channeling']['effect'])
                assert(0 == science['Channeling']['incomming'])


        def test_get_form_fields(self):
                science_form = self.parser.get_science_form()
                print "science_form:", science_form
                assert("896adc6656e44910f20c4265cec55f0d" == science_form['inputs']['csrfmiddlewaretoken']['value'])
                learn_rate = self.parser.get_learn_rate()
                print "learn_rate:", learn_rate
                assert(("Limited", "LIMITED") == learn_rate)
                assert(500 == science_form['inputs']['learn_min_income']['value'])
                for i in range(0, 7):
                        field = 'quantity_%d'%i
                        print field
                        assert( field in science_form['inputs'] )

# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# learn_rate:ACTIVE
# learn_min_income:500
# quantity_0:1
# quantity_1:2
# quantity_2:3
# quantity_3:4
# quantity_4:5
# quantity_5:6
# quantity_6:7
        def test_get_science_info(self):
                info = self.parser.get_science_info()
                print "science_info:", info
                assert(42055 == info['Total Money'])
                assert((3794, 5) == info['Estimated Research Cost'])
                assert(69514 == info['Daily Income'])
                assert(0 == info['Books to Allocate'])



class explore_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.ExploreParser()
                in_file = "test/explore_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_EXPLORE" == self.parser.current_page)

        def test_get_explore_info(self):
                explore_info = self.parser.get_explore_info()
                print "Explore_info:", explore_info
                assert(   50 == explore_info['Exploration Costs (Soldiers)'])
                assert(   50 == explore_info['soldiers'])
                assert(23264 == explore_info['Exploration Costs (Gold)'])
                assert(23264 == explore_info['gold'])
                assert( 8080 == explore_info['Available Uncharted Acres'])
                assert( 8080 == explore_info['available'])
                assert(    0 == explore_info['Currently Exploring'])
                assert(    5 == explore_info['Maximum Explorable Now'])

        def test_get_form_fields(self):
                explore_form = self.parser.get_explore_form()
                print "explore_form:", explore_form
                assert('88e2dabb2a8b615561e743d05668d47d' == explore_form['inputs']['csrfmiddlewaretoken']['value'])
                assert('num_acres' in explore_form['inputs'] )

        def test_get_explore_result(self):
                #Not implemented
                pass

class kingdom_parser_tests(object):
        def setup(self):
                self.parser = htmlparser.KingdomParser()
                in_file = "test/kingdom_page.html"
                try:
                        with open(in_file) as page:
                                self.parser.parse(page.read())
                except IOError as e:
                        print "CANNOT OPEN FILE %s. For this test to work, you need a copy of the tested page at %s" % (in_file, in_file)

        def test_page_enum(self):
                print self.parser.current_page
                assert("PAGE_KINGDOM" == self.parser.current_page)

        def test_get_kd_info(self):
                kd = self.parser.get_kd_info()
                print "kd:", kd
                assert(1 == kd['kd'])
                assert(17 == kd['island'])
                assert(20 == kd['Total Provinces'])
                assert('normal' == kd['Stance'])
                assert(3077180 == kd['Total Networth'])
                assert(153859 == kd['Average Networth'])
                assert(0 == kd['Wars Won'])
                assert(2 == kd['Concluded Wars'])
                assert(18629 == kd['Total Land'])
                assert(103 == kd['Average Opponent Relative Size'])
                assert('normal' == kd['Their Attitude To Us'])
                assert('normal' == kd['Our Attitude To Them'])

                assert(True == kd['provinces']['house 1']['protected'])
                assert(False == kd['provinces']['house 1']['online'])
                assert(False == kd['provinces']['house 1']['monarch'])
                assert(1 == kd['provinces']['house 1']['Slot'])
                assert('house 1' == kd['provinces']['house 1']['Province'])
                assert('Avian' == kd['provinces']['house 1']['Race'])
                assert(354 == kd['provinces']['house 1']['Land'])
                assert(19272 == kd['provinces']['house 1']['Net Worth'])
                assert(54== kd['provinces']['house 1']['Net Worth/Acre'])
                assert('Lord' == kd['provinces']['house 1']['Nobility'])

                assert(True == kd['provinces']['house 1']['protected'])
                assert(1 == kd['provinces']['house 1']['Slot'])
                assert('house 1' == kd['provinces']['house 1']['Province'])
                assert('Avian' == kd['provinces']['house 1']['Race'])
                assert(354 == kd['provinces']['house 1']['Land'])
                assert(19272 == kd['provinces']['house 1']['Net Worth'])
                assert(54== kd['provinces']['house 1']['Net Worth/Acre'])
                assert('Lord' == kd['provinces']['house 1']['Nobility'])
