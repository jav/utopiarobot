from utopia_robot.robot import UtopiaRobot, htmlparser
import mock
import urllib2



class player_tests(object):
    def setup(self):
        self.player = UtopiaRobot()

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_resources(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/throne_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        resources = self.player.get_resources()
        print "Resources:", resources
        assert(480594 == resources['Money'])
        assert(10065 == resources['Peasants'])
        assert(78481 == resources['Food'])
        assert(13244 == resources['Runes'])
        assert(213924 == resources['Net Worth'])
        assert(153.021 == resources['Net Worth/Acre'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_plague_false(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/throne_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        plague = self.player.get_plague()
        assert(False == plague)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_plague_true(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/throne_plague.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        plague = self.player.get_plague()
        assert(True == plague)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_mana(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        mana = self.player.get_mana()
        print "Mana:", mana
        assert(68  == mana)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_available_spells(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        available_spells = self.player.get_available_spells()
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


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_active_spells(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/mystic_advisor.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        active_spells = self.player.get_active_spells()
        print "Active spells:", active_spells
        assert(14 == active_spells['Fountain of Knowledge'])
        assert( 3 == active_spells["Nature's Blessing"])
        assert(15 == active_spells['Minor Protection'])
        assert( 1 == active_spells['Love and Peace'])


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_cast_paradise_success(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/spell_paradise.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        print ("assert()")
        assert(5 == self.player.cast_spell('Paradise'))
        mystic_form = self.player.parser.get_mystic_form()
        print mystic_form
        assert('88e2dabb2a8b615561e743d05668d47d' == mystic_form['inputs']['csrfmiddlewaretoken']['value'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_get_troops(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        troops = self.player.get_troops()

        print "troops:", troops
        assert(1530 == troops['o-spec']['home'])
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

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_get_soldiers(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        soldiers = self.player.get_soldiers()

        print "soldiers:", soldiers
        assert(1293 == soldiers)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_get_spec_credits(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        credits = self.player.get_spec_credits()

        print "credits:", credits
        assert(123 == credits)

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_train_troops(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/military_trained.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        military={}
        military['o-spec'] = 44
        military['d-spec'] = 33
        military['elite'] = 22
        military['thief'] = 11

        print "Want to train: %s" % military
        military_result = self.player.train_military(military)
        print "Militarty result: %s" % military_result
        assert(44 == military_result['o-spec'])
        assert(33 == military_result['d-spec'])
        assert(22 == military_result['elite'])
        assert(11 == military_result['thief'])
        print "self.player.get_draft_rate():", self.player.get_draft_rate()
        print "self.player.get_draft_rate()[1]:", self.player.get_draft_rate()[1]
        assert('AGGRESSIVE' == self.player.get_draft_rate()[1])

        military_form = self.player.parser.get_military_form()
        print military_form
        assert('88e2dabb2a8b615561e743d05668d47d' == military_form['inputs']['csrfmiddlewaretoken']['value'])

#train form-data
# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# draft_rate:AGGRESSIVE
# draft_target:66
# wage_rate:200
# unit-quantity_0:1
# unit-quantity_1:2
# unit-quantity_2:3
# unit-quantity_3:4
# train:Train troops

#change recruitlvl
# csrfmiddlewaretoken:88e2dabb2a8b615561e743d05668d47d
# draft_rate:NORMAL
# draft_target:65
# wage_rate:201
# unit-quantity_0:
# unit-quantity_1:
# unit-quantity_2:
# unit-quantity_3:
# train:Train troops

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_get_buildings(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/growth_page.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        buildings = self.player.get_buildings()

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


    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_build(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/growth_built.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        buildings={
            'Homes': 1,
            'Farms': 1,
            'Banks': 1,
            'Guilds': 1,
            'Towers': 1,
            'Stables': 1,
            }

        print "Want to build: %s" % buildings
        buildings_result = self.player.build(buildings)
        print "Build result: %s" % buildings_result
        assert(1 == buildings_result['Homes'])
        assert(1 == buildings_result['Farms'])
        assert(1 == buildings_result['Banks'])
        assert(1 == buildings_result['Guilds'])
        assert(1 == buildings_result['Towers'])
        assert(1 == buildings_result['Stables'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_build_info(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/growth_built.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        buildings={
            'Homes': 1,
            'Farms': 1,
            'Banks': 1,
            'Guilds': 1,
            'Towers': 1,
            'Stables': 1,
            }

        print "Want to build: %s" % buildings
        buildings_result = self.player.build(buildings)
        print "Build result: %s" % buildings_result
        assert(1 == buildings_result['Homes'])
        assert(1 == buildings_result['Farms'])
        assert(1 == buildings_result['Banks'])
        assert(1 == buildings_result['Guilds'])
        assert(1 == buildings_result['Towers'])
        assert(1 == buildings_result['Stables'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_build_multiple(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/growth_built_plural.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        buildings={
            'Homes': 2,
            'Farms': 2,
            'Banks': 2,
            'Training Grounds': 2,
            'Forts': 2,
            'Guilds': 2,
            'Towers': 2,
            'Stables': 2,
            }

        print "Want to build: %s" % buildings
        buildings_result = self.player.build(buildings)
        print "Build result: %s" % buildings_result
        assert(2 == buildings_result['Homes'])
        assert(2 == buildings_result['Farms'])
        assert(2 == buildings_result['Banks'])
        assert(2 == buildings_result['Training Grounds'])
        assert(2 == buildings_result['Forts'])
        assert(2 == buildings_result['Guilds'])
        assert(2 == buildings_result['Towers'])
        assert(2 == buildings_result['Stables'])

    @mock.patch('urllib2.urlopen')
    @mock.patch('urllib2.Request')
    @mock.patch.object(UtopiaRobot,'cache_page')
    @mock.patch.object(UtopiaRobot,'_simulate_wait')
    def test_build_multiple(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
        mock_urlopen.return_value = mock_request
        mock_request.read.return_value = open('test/growth_built_plural.html').read()
        mock_cache_page.return_value = True
        mock_simulate_wait.return_value = True

        buildings={
            'Homes': 2,
            'Farms': 2,
            'Banks': 2,
            'Training Grounds': 2,
            'Forts': 2,
            'Guilds': 2,
            'Towers': 2,
            'Stables': 2,
            }

        print "Want to build: %s" % buildings
        buildings_result = self.player.build(buildings)
        print "Build result: %s" % buildings_result
        assert(2 == buildings_result['Homes'])
        assert(2 == buildings_result['Farms'])
        assert(2 == buildings_result['Banks'])
        assert(2 == buildings_result['Training Grounds'])
        assert(2 == buildings_result['Forts'])
        assert(2 == buildings_result['Guilds'])
        assert(2 == buildings_result['Towers'])
        assert(2 == buildings_result['Stables'])

    # @mock.patch('urllib2.urlopen')
    # @mock.patch('urllib2.Request')
    # @mock.patch.object(UtopiaRobot,'cache_page')
    # @mock.patch.object(UtopiaRobot,'_simulate_wait')
    # def test_get_science(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
    #     mock_urlopen.return_value = mock_request
    #     mock_request.read.return_value = open('test/science_page.html').read()
    #     mock_cache_page.return_value = True
    #     mock_simulate_wait.return_value = True

    #     science = player.get_science()
    #     print "Sience:: %s" % science

    #     assert(21132 == science['Alchemy']['points'])
    #     assert(5.5 == science['Alchemy']['effect'])
    #     assert(0 == science['Alchemy']['incomming'])

    #     assert(73226 == science['Tools']['points'])
    #     assert(7.4 == science['Tools']['effect'])
    #     assert(9996 == science['Tools']['incomming'])

    #     assert(32578 == science['Housing']['points'])
    #     assert(3.2 == science['Housing']['effect'])
    #     assert(0 == science['Housing']['incomming'])

    #     assert(4892 == science['Food']['points'])
    #     assert(15.2 == science['Food']['effect'])
    #     assert(0 == science['Food']['incomming'])

    #     assert(4892 == science['Military']['points'])
    #     assert(2.7 == science['Military']['effect'])
    #     assert(0 == science['Military']['incomming'])

    #     assert(21340['Crime']['points'])
    #     assert(23.8 == science['Crime']['effect'])
    #     assert(0 == science['Crime']['incomming'])

    #     assert(20860 == science['Channeling']['points'])
    #     assert(23.6 == science['Channeling']['effect'])
    #     assert(0 == science['Channeling']['incomming'])

    # @mock.patch('urllib2.urlopen')
    # @mock.patch('urllib2.Request')
    # @mock.patch.object(UtopiaRobot,'cache_page')
    # @mock.patch.object(UtopiaRobot,'_simulate_wait')
    # def test_science_multiple(self, mock_simulate_wait, mock_cache_page, mock_request, mock_urlopen):
    #     mock_urlopen.return_value = mock_request
    #     mock_request.read.return_value = open('test/sience_bought.html').read()
    #     mock_cache_page.return_value = True
    #     mock_simulate_wait.return_value = True

    #     buildings={
    #         'Homes': 2,
    #         'Farms': 2,
    #         'Banks': 2,
    #         'Training Grounds': 2,
    #         'Forts': 2,
    #         'Guilds': 2,
    #         'Towers': 2,
    #         'Stables': 2,
    #         }

    #     print "Want to build: %s" % buildings
    #     buildings_result = self.player.build(buildings)
    #     print "Build result: %s" % buildings_result
    #     assert(2 == buildings_result['Homes'])
    #     assert(2 == buildings_result['Farms'])
    #     assert(2 == buildings_result['Banks'])
    #     assert(2 == buildings_result['Training Grounds'])
    #     assert(2 == buildings_result['Forts'])
    #     assert(2 == buildings_result['Guilds'])
    #     assert(2 == buildings_result['Towers'])
    #     assert(2 == buildings_result['Stables'])
