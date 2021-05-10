#!/usr/bin/env python3

#####################################################################################################################
###
##      load environment and start the games main loop
#       basically nothing to see here
#       if you are a first time visitor, interaction.py, story.py and gamestate.py are probably better files to start with
#
#####################################################################################################################

# import basic libs
import sys
import json
import time

# import basic internal libs
import src.items as items
items.setup()
import src.quests as quests
import src.rooms as rooms
import src.characters as characters
import src.terrains as terrains
import src.cinematics as cinematics
import src.story as story
import src.gameMath as gameMath
import src.interaction as interaction
import src.gamestate as gamestate
import src.events as events
import src.chats as chats
import src.saveing as saveing

# import configs
import config.commandChars as commandChars
import config.names as names

# parse arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--phase", type=str, help="the phase to start in")
parser.add_argument("--unicode", action="store_true", help="force fallback encoding")
parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
parser.add_argument("-m", "--music", action="store_true", help="enable music (downloads stuff and runs mplayer!)")
parser.add_argument("-t", "--tiles", action="store_true", help="spawn a tile based view of the map (requires pygame)")
parser.add_argument("--nourwid", action="store_true", help="do not show shell based")
parser.add_argument("-ts", "--tileSize", type=int, help="the base size of tiles")
parser.add_argument("-T", "--terrain", type=str, help="select the terrain")
parser.add_argument("-s", "--seed", type=str, help="select the seed of a new game")
parser.add_argument("--multiplayer", action="store_true", help="activate multiplayer")
parser.add_argument("--load", action="store_true", help="load")
parser.add_argument("-S", "--speed", type=int, help="set the speed of the game to a fixed speed")
parser.add_argument("-sc", "--scenario", type=str, help="set the scenario to run")
args = parser.parse_args()

##################################################################################################################################
###
##        switch scenarios
#
##################################################################################################################################

# load the gamestate
loaded = False
if not args.nourwid:
    if args.load:
        shouldLoad = True
    else:
        load = input("load saved game? (Y/n)")
        if load.lower() == "n":
            shouldLoad = False
        else:
            shouldLoad = True
else:
    shouldLoad = True

if not shouldLoad:
    if not args.scenario:
        scenarios = [
                        ("story1","story mode (old+broken)",),
                        ("story2","story mode (new)",),
                        ("siege","siege",),
                        ("survival","survival",),
                        ("creative","creative mode",),
                        ("dungeon","dungeon",),
                    ]

        text = "\n"
        counter = 0
        for scenario in scenarios:
            text += "%s: %s\n"%(counter,scenario[1],)
            counter += 1

        scenarioNum = input("select scenario (type number)\n\n%s\n\n"%(text,))
        scenario = scenarios[int(scenarioNum)][0]
    else:
        scenario = args.scenario

    print(scenario)

    if scenario == "siege":
        args.terrain = "test"
        args.phase = "BuildBase"
    elif scenario == "survival":
        args.terrain = "desert"
        args.phase = "DesertSurvival"
    elif scenario == "creative":
        args.terrain = "nothingness"
        args.phase = "CreativeMode"
    elif scenario == "dungeon":
        args.terrain = "nothingness"
        args.phase = "Dungeon"

print(args.terrain)

import src.canvas as canvas

# set rendering mode
if not args.nourwid:
    if args.unicode:
        displayChars = canvas.DisplayMapping("unicode")
    else:
        displayChars = canvas.DisplayMapping("pureASCII")
else:
    displayChars = canvas.TileMapping("testTiles")

if args.speed:
    interaction.speed = args.speed

if args.seed:
    seed = int(args.seed)
else:
    import random
    seed = random.randint(1,100000)

if args.nourwid:
    interaction.nourwid = True

    import src.pseudoUrwid
    interaction.urwid = src.pseudoUrwid
    items.urwid = src.pseudoUrwid
    chats.urwid = src.pseudoUrwid
    canvas.urwid = src.pseudoUrwid
    cinematics.urwid = src.pseudoUrwid

    interaction.setUpNoUrwid()

else:
    interaction.nourwid = False

    import urwid
    interaction.urwid = urwid
    items.urwid = urwid
    chats.urwid = urwid
    canvas.urwid = urwid
    cinematics.urwid = urwid

    interaction.setUpUrwid()

# bad code: common variables with modules
void = saveing.Void()
characters.void = void
rooms.void = void
items.void = void
terrains.void = void
gamestate.void = void
story.void = void
interaction.void = void
quests.void = void
cinematics.void = void
events.void = void
chats.void = void

# bad code: common variables with modules
items.characters = characters
rooms.characters = characters
story.characters = characters
terrains.characters = characters

# bad code: common variables with modules
story.names = names
characters.names = names
gamestate.names = names
items.names = names
rooms.names = names

gamestate.macros = interaction.macros

# bad code: common variables with modules
phasesByName = {}
gamestate.phasesByName = phasesByName
story.phasesByName = phasesByName
story.registerPhases()

# create and load the gamestate
gameStateObj = gamestate.GameState()

terrain = None
gamestate.terrain = terrain

# set up debugging
if args.debug:
    '''
    logger object for logging to file
    '''
    class debugToFile(object):
        '''
        clear file
        '''
        def __init__(self):
            logfile = open("debug.log","w")
            logfile.close()
        '''
        add log message to file
        '''
        def append(self,message):
            logfile = open("debug.log","a")
            logfile.write(str(message)+"\n")
            logfile.close()
    
    # set debug mode
    debugMessages = debugToFile()
    interaction.debug = True
    characters.debug = True
    quests.debug = True
    canvas.debug = True
    gameMath.debug = True

# set dummies to replace dummy objects
else:
    '''
    dummy logger
    '''
    class FakeLogger(object):
        '''
        discard input
        '''
        def append(self,message):
            pass

    # set debug mode
    debugMessages = FakeLogger()
    interaction.debug = False
    characters.debug = False
    quests.debug = False
    canvas.debug = False
    gameMath.debug = False

# bad code: common variables with modules
items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars
story.displayChars = displayChars
gamestate.displayChars = displayChars
interaction.displayChars = displayChars
cinematics.displayChars = displayChars
characters.displayChars = displayChars
events.displayChars = displayChars
chats.displayChars = displayChars
canvas.displayChars = displayChars

# bad code: common variables with modules
items.debugMessages = debugMessages
quests.debugMessages = debugMessages
rooms.debugMessages = debugMessages
characters.debugMessages = debugMessages
terrains.debugMessages = debugMessages
cinematics.debugMessages = debugMessages
story.debugMessages = debugMessages
interaction.debugMessages = debugMessages
events.debugMessages = debugMessages
canvas.debugMessages = debugMessages
gamestate.debugMessages = debugMessages

# bad code: common variables with modules
story.cinematics = cinematics
interaction.cinematics = cinematics
events.cinematics = cinematics
rooms.cinematics = cinematics
gamestate.cinematics = cinematics

if shouldLoad:
    try:
        # load the game
        loaded = gameStateObj.load()
        seed = gameStateObj.initialSeed
    except Exception as e:
        ignore = input("error in gamestate, could not load gamestate completely. Abort and show error message? (Y/n)")
        if not ignore.lower() == "n":
            raise e
mainChar = gameStateObj.mainChar

##################################################################################################################################
###
##        background music
#
#################################################################################################################################

# play music
if args.music :
    def playMusic():
        import threading
        thread = threading.currentThread()
        import subprocess
        import os.path

        # download music
        # bad pattern: I didn't ask the people at freemusicarchive about the position on traffic leeching. If you know they don't like it please create an issue
        # bad code: it obviously is an issue, since they knowingly broke this mechanism
        if not os.path.isfile("music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/ece1b96c8f23874bda6ffdda2dd6cf9cd2fcb582","-O","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        if not os.path.isfile("music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/c1a7a0cd0e262469607e26935e69ed1e5bfed538","-O","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        mplayer = subprocess.Popen(["mplayer","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # play music
        while mplayer.stdout.read1(100):
           if thread.stop:
               mplayer.terminate()
               mplayer.kill()
               return
        
    # start music as subprocess
    from threading import Thread
    musicThread = Thread(target=playMusic)
    musicThread.stop = False
    musicThread.start()
else:
    musicThread = None

##################################################################################################################################
###
##        some stuff that is somehow needed but slated for removal
#
#################################################################################################################################

# bad code: common variables with modules
rooms.story = story
chats.story = story

# bad code: common variables with modules
story.chats = chats
characters.chats = chats
rooms.chats = chats
quests.chats = chats

# bad code: common variables with modules
cinematics.quests = quests
story.quests = quests
terrains.quests = quests
characters.quests = quests
items.quests = quests
chats.quests = quests

# bad code: common variables with modules
story.rooms = rooms

# bad code: common variables with modules
items.commandChars = commandChars
story.commandChars = commandChars
characters.commandChars = commandChars
interaction.commandChars = commandChars
chats.commandChars = commandChars

interaction.setFooter()

# bad code: common variables with modules
story.items = items

# bad code: common variables with modules
cinematics.main = interaction.main
cinematics.header = interaction.header

# bad code: common variables with modules
cinematics.loop = interaction.loop
quests.loop = interaction.loop
story.loop = interaction.loop
events.loop = interaction.loop

# bad code: common variables with modules
story.events = events
items.events = events
rooms.events = events
quests.events = events
characters.events = events
terrains.events = events

# bad code: common variables with modules
cinematics.callShow_or_exit = interaction.callShow_or_exit
quests.callShow_or_exit = interaction.callShow_or_exit
story.callShow_or_exit = interaction.callShow_or_exit
events.callShow_or_exit = interaction.callShow_or_exit
chats.callShow_or_exit = interaction.callShow_or_exit

# bad code: common variables with modules
rooms.calculatePath = gameMath.calculatePath
quests.calculatePath = gameMath.calculatePath
characters.calculatePath = gameMath.calculatePath
terrains.calculatePath = gameMath.calculatePath

# bad code: common variables with modules
rooms.Character = characters.Character
        
# bad code: common variables with modules
messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages
story.messages = messages
interaction.messages = messages
events.messages = messages
chats.messages = messages
canvas.messages = messages

# bad code: common variables with modules
cinematics.interaction = interaction
characters.interaction = interaction
story.interaction = interaction
rooms.interaction = interaction
items.interaction = interaction
quests.interaction = interaction
chats.interaction = interaction

# bad code: common variables with modules
quests.showCinematic = cinematics.showCinematic

##########################################
###
## set up the terrain
#
##########################################

if not loaded:
    # spawn selected terrain
    if args.terrain and args.terrain == "scrapField":
        gameStateObj.terrainType = terrains.ScrapField
    elif args.terrain and args.terrain == "nothingness":
        gameStateObj.terrainType = terrains.Nothingness
    elif args.terrain and args.terrain == "test":
        gameStateObj.terrainType = terrains.GameplayTest
    elif args.terrain and args.terrain == "tutorial":
        gameStateObj.terrainType = terrains.TutorialTerrain
    elif args.terrain and args.terrain == "desert":
        gameStateObj.terrainType = terrains.Desert
    else:
        gameStateObj.terrainType = terrains.GameplayTest
else:
    terrain = gameStateObj.terrain
    interaction.lastTerrain = terrain

# bad code: common variables with modules
cinematics.interaction = interaction

# state that should be contained in the gamestate
mapHidden = True
mainChar = None

if not loaded:
    gameStateObj.setup(phase=args.phase, seed=seed)
    terrain = gameStateObj.terrain
    interaction.lastTerrain = terrain

interaction.macros = gameStateObj.macros

# bad code: common variables with modules
characters.roomsOnMap = terrain.rooms

# bad code: common variables with modules
items.terrain = terrain
story.terrain = terrain
interaction.terrain = terrain
terrains.terrain = terrain
gamestate.terrain = terrain
quests.terrain = terrain
chats.terrain = terrain
characters.terrain = terrain

##################################################################################################################################
###
##        setup the game
#
#################################################################################################################################

# bad code: common variables with modules
story.gamestate = gameStateObj
interaction.gamestate = gameStateObj
quests.gamestate = gameStateObj
characters.gamestate = gameStateObj
items.gamestate = gameStateObj
terrains.gamestate = gameStateObj
rooms.gamestate = gameStateObj
chats.gamestate = gameStateObj

# bad code: common variables with modules
rooms.mainChar = gameStateObj.mainChar
terrains.mainChar = gameStateObj.mainChar
story.mainChar = gameStateObj.mainChar
interaction.mainChar = gameStateObj.mainChar
cinematics.mainChar = gameStateObj.mainChar
quests.mainChar = gameStateObj.mainChar
chats.mainChar = gameStateObj.mainChar
characters.mainChar = gameStateObj.mainChar


##################################################################################################################################
###
##        the main loop
#
#################################################################################################################################

# the game loop
# bad code: either unused or should be contained in terrain
'''
advance the game
'''
def advanceGame():
    for row in gameStateObj.terrainMap:
        for specificTerrain in row:
            for character in specificTerrain.characters:
                character.advance()

            for room in specificTerrain.rooms:
                room.advance()

            while specificTerrain.events and specificTerrain.events[0].tick <= gameStateObj.tick:
                event = specificTerrain.events[0]
                if event.tick < gameStateObj.tick:
                    continue
                event.handleEvent()
                specificTerrain.events.remove(event)

    gameStateObj.tick += 1


# bad code: common variables with modules
cinematics.advanceGame = advanceGame
interaction.advanceGame = advanceGame
story.advanceGame = advanceGame

# set up the splash screen
if not args.debug and not interaction.submenue and not loaded:
    text = """

     OOO FFF          AAA N N DD
     O O FF   mice    AAA NNN D D
     OOO F            A A N N DD



     MMM   MMM  EEEEEE  CCCCCC  HH   HH  SSSSSSS
     MMMM MMMM  EE      CC      HH   HH  SS
     MM MMM MM  EEEE    CC      HHHHHHH  SSSSSSS
     MM  M  MM  EEEE    CC      HHHHHHH  SSSSSSS
     MM     MM  EE      CC      HH   HH        S
     MM     MM  EEEEEE  CCCCCC  HH   HH  SSSSSSS


        - a pipedream


    press space to continue

"""
    openingCinematic = cinematics.TextCinematic(text,rusty=True,scrolling=True,creator=void)
    cinematics.cinematicQueue.insert(0,openingCinematic)
    gameStateObj.openingCinematic = openingCinematic
    gameStateObj.mainChar.macroState["commandKeyQueue"].insert(0,(".",["norecord"]))
    gameStateObj.mainChar.macroState["commandKeyQueue"].insert(0,(".",["norecord"]))
    gameStateObj.mainChar.macroState["commandKeyQueue"].insert(0,(".",["norecord"]))
    gameStateObj.mainChar.macroState["commandKeyQueue"].insert(0,(".",["norecord"]))
else:
    gameStateObj.openingCinematic = None

# set up the current phase
if not loaded:
    gameStateObj.currentPhase.start(seed=seed)

# bad code: loading registry should be cleared

# set up tile based mode
if args.tiles:
    # spawn tile based rendered window
    import pygame
    pygame.init()
    pygame.key.set_repeat(200,20)
    if args.tileSize:
        interaction.tileSize = args.tileSize
    else:
        interaction.tileSize = 10
    pydisplay = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)
    pygame.display.set_caption('Of Mice and Mechs')
    pygame.display.update()
    interaction.pygame = pygame
    interaction.pydisplay = pydisplay
    interaction.useTiles = True
    interaction.tileMapping = canvas.TileMapping("testTiles")
else:
    interaction.useTiles = False
    interaction.tileMapping = None

######################################################################################################
###
##    main loop is started here
#
######################################################################################################

if args.multiplayer:
    interaction.multiplayer = True
    interaction.fixedTicks = 0.1
else:
    interaction.multiplayer = False
    interaction.fixesTicks = False

# start the interaction loop of the underlying library
try:
    if not args.nourwid:
        input("game ready. press enter to start")
        interaction.loop.run()
except:
    if musicThread:
        musicThread.stop = True
    raise

# stop the music
if musicThread:
    musicThread.stop = True

if args.nourwid:
    while 1:
        interaction.gameLoop(None,None)

# print death messages
if gameStateObj.mainChar.dead:
    print("you died.")
    if gameStateObj.mainChar.deathReason:
        print("Cause of death:\n"+gameStateObj.mainChar.deathReason)
