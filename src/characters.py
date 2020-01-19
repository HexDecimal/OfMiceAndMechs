########################################################################################################
###
##     the code for the characters belongs here
#
########################################################################################################

# import basic libs
import json

# import the other internal libs
import src.items
import src.saveing
import src.quests
import src.chats

# bad code: containers for global state
characters = None
calculatePath = None
roomsOnMap = None

"""
this is the class for characters meaning both npc and pcs. 
all characters except the pcs always have automated = True to
make them to things on their own
"""
class Character(src.saveing.Saveable):

    def setDefaultMacroState(self):
        import time
        self.macroState = {
            "commandKeyQueue":[],
            "state":[],
            "recording":False,
            "recordingTo":None,
            "replay":[],
            "loop":[],
            "number":None,
            "doNumber":False,
            "macros":{},
            "shownStarvationWarning":False,
            "lastLagDetection":time.time(),
            "lastRedraw":time.time(),
            "idleCounter":0,
            "submenue":None,
            "ignoreNextAutomated": False,
            "ticksSinceDeath": None,
            "footerPosition":0,
            #"footerLength":len(footerText),
            "footerSkipCounter":20,
            "itemMarkedLast":None,
            "lastMoveAutomated":False,
            "stealKey":{},
                }

    '''
    sets basic info AND adds default behaviour/items
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,quests=[],automated=True,name=None,creator=None,characterId=None,seed=None):
        super().__init__()

        if name == None and seed:
            name = names.characterFirstNames[(seed)%len(names.characterFirstNames)]+" "+names.characterLastNames[(seed*10)%len(names.characterLastNames)]

        if display == None and not name == None:
            display = displayChars.staffCharactersByLetter[name[0].lower()]

        if name == None:
            name = "Person"
        if display == None:
            display = "＠"

        self.setDefaultMacroState()

        self.macroStateBackup = None

        # set basic state
        self.specialRender = False
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = {"default":[]}
        self.path = []
        self.subordinates = []
        self.reputation = 0
        self.events = []
        self.room = None
        self.terrain = None
        self.xPosition = 0
        self.yPosition = 0
        self.satiation = 1000
        self.dead = False
        self.deathReason = None
        self.questsToDelegate = []
        self.unconcious = False
        self.displayOriginal = display
        self.isMilitary = False
        self.hasFloorPermit = True
        # bad code: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []
        self.questsDone = []
        self.solvers = []
        self.aliances = []
        self.stasis = False
        self.registers = {}

        # generate the id for this object
        if characterId:
            self.id = characterId
        else:
            self.id = {
                   "other":"character",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
            self.id["creator"] = creator.id
            self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # mark attributes for saving
        self.attributesToStore.extend([
               "gotBasicSchooling","gotMovementSchooling","gotInteractionSchooling","gotExamineSchooling",
               "xPosition","yPosition","name","satiation","unconcious","reputation","tutorialStart",
               "isMilitary","hasFloorPermit","dead","deathReason","automated","watched","solvers","questsDone",
               "stasis","registers",])
        self.objectsToStore.append("serveQuest")
        self.objectsToStore.append("room")

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        # add default quests
        self.assignQuest(src.quests.SurviveQuest(creator=self))
        for quest in quests:
            self.assignQuest(quest)

        self.silent = False

        self.messages = []

        # save state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

        self.xPosition = xPosition
        self.yPosition = yPosition

    """
    proxy render method to display attribute
    """
    @property
    def display(self):
        return self.render()

    """
    render the character
    """
    def render(self):
        if self.unconcious:
            return displayChars.unconciousBody
        else:
            return self.displayOriginal

    """
    the object the character is in. Either room or terrain
    """
    @property
    def container(self):
        if self.room:
            return self.room
        else:
            return self.terrain

    '''
    get a quest from the character (proxies room quest queue)
    '''
    def getQuest(self):
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    '''
    almost straightforward adding of events to the characters event queue
    ensures that the events are added in proper order
    '''
    def addEvent(self,event):
        # get the position for this event
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1

        # add event at proper position
        self.events.insert(index,event)

    '''
    reset the path to the current quest
    bad code: is only needed because path is contained in character instead of quest
    '''
    def recalculatePath(self):
        # log impossible state
        if not self.quests:
            debugMessages.append("reacalculate path called without quests")
            self.path = []
            return

        # reset path
        self.setPathToQuest(self.quests[0])

    '''
    straightforward removing of events from the characters event queue
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    almost straightforward getter for chat options
    # bad code: adds default chat options
    '''
    def getChatOptions(self,partner):
        # get the usual chat options
        chatOptions = self.basicChatOptions[:]

        if not self.silent:
            # add chat for recruitment
            if not self in partner.subordinates:
                chatOptions.append(src.chats.RecruitChat)
                pass
            if not partner in self.subordinates:
                chatOptions.append({"dialogName":"may i serve you?","chat":chats.RoomDutyChat,"params":{
                "superior":self
                }})
            else:
                chatOptions.append({"dialogName":"can i do something for you?","chat":chats.RoomDutyChat2,"params":{
                "superior":self
                }})
            if self.isMilitary:
                chatOptions.append({"dialogName":"I want to join the military","chat":chats.JoinMilitaryChat,"params":{
                "superior":self
                }})

        return chatOptions

    '''
    get the changes in state since creation
    '''
    def getDiffState(self):
        # fetch the basic result
        result = super().getDiffState()

        # save path
        if not self.path == self.initialState["path"]:
            result["path"] = self.path

        result["questsDone"] = self.questsDone
        result["solvers"] = self.solvers

        # save inventory
        # bad code: should be abstracted
        (itemStates,changedItems,newItems,removedItems) = self.getDiffList(self.inventory,self.initialState["inventory"]["inventoryIds"])
        inventory = {}
        if changedItems:
            inventory["changed"] = changedItems
        if newItems:
            inventory["new"] = newItems
        if removedItems:
            inventory["removed"] = removedItems
        if itemStates:
            inventory["states"] = itemStates
        if itemStates or removedItems:
            result["inventory"] = inventory

        # save quests
        # bad code: should be abstracted
        (questStates,changedQuests,newQuests,removedQuests) = self.getDiffList(self.quests,self.initialState["quests"]["questIds"])
        quests = {}
        if changedQuests:
            quests["changed"] = changedQuests
        if newQuests:
            quests["new"] = newQuests
        if removedQuests:
            quests["removed"] = removedQuests
        if questStates:
            quests["states"] = questStates
        if questStates or removedQuests:
            result["quests"] = quests

        # store events diff
        # bad code: should be abstracted
        (eventStates,changedEvents,newEvents,removedEvents) = self.getDiffList(self.events,self.initialState["eventIds"])
        if changedEvents:
            result["changedEvents"] = changedEvents
        if newEvents:
            result["newEvents"] = newEvents
        if removedEvents:
            result["removedEvents"] = removedEvents
        if eventStates:
            result["eventStates"] = eventStates

        # save chat options
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                chatOptions.append(option)
        result["chatOptions"] = chatOptions

        import copy
        result["macroState"] = copy.deepcopy(self.macroState)
        if not result["macroState"]["itemMarkedLast"] == None:
            result["macroState"]["itemMarkedLast"] = result["macroState"]["itemMarkedLast"].id

        return result

    '''
    getter for the players state
    '''
    def getState(self):
        # fetch base state
        state = super().getState()

        import copy
        state["macroState"] = copy.deepcopy(self.macroState)
        if not state["macroState"]["itemMarkedLast"] == None:
            state["macroState"]["itemMarkedLast"] = state["macroState"]["itemMarkedLast"].id

        # add simple structures
        state.update({ 
                 "inventory": {},
                 "quests": {},
                 "path":self.path,
               })
                 
        # store inventory
        inventory = []
        for item in self.inventory:
            inventory.append(item.id)
        state["inventory"]["inventoryIds"] = inventory

        # store quests
        questIds = []
        questStates = {}
        for quest in self.quests:
            questIds.append(quest.id)
            questStates[quest.id] = quest.getState()
        state["quests"]["questIds"] = questIds
        state["quests"]["states"] = questStates

        # store events
        (eventIds,eventStates) = self.storeStateList(self.events)
        state["eventIds"] = eventIds

        # store serve quest
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    chatOptions.append(option)
        state["chatOptions"] = chatOptions

        return state

    '''
    setter for the players state
    '''
    def setState(self,state):
        # set basic state
        super().setState(state)

        if not "loop" in state["macroState"]:
            state["macroState"]["loop"] = []

        self.macroState = state["macroState"]

        if not self.macroState["itemMarkedLast"] == None:
            def setParam(instance):
                self.macroState["itemMarkedLast"] = instance
            loadingRegistry.callWhenAvailable(self.macroState["itemMarkedLast"],setParam)

        # set unconcious state
        if "unconcious" in state:
            if self.unconcious:
                self.fallUnconcious()

        # set path
        if "path" in state:
            self.path = state["path"]
        
        # set inventory
        if "inventory" in state:
            self.loadFromList(state["inventory"],self.inventory,src.items.getItemFromState)

        # set quests
        if "quests" in state:

            # deactivate the quest that will be removed later
            if "removed" in state["quests"]:
                for quest in self.quests[:]:
                    if quest.id in state["quests"]["removed"]:
                        quest.deactivate()
                        quest.completed = True
                
            # load quests using the saving class
            self.loadFromList(state["quests"],self.quests,src.quests.getQuestFromState)

            # load a fixed set of quests
            if "questIds" in state["quests"]:

                # tear down current quests
                for quest in self.quests[:]:
                    quest.deactivate()
                    quest.completed = True
                    self.quests.remove(quest)

                # add new quests
                for questId in state["quests"]["questIds"]:
                    quest = src.quests.getQuestFromState(state["quests"]["states"][questId])
                    self.quests.append(quest)

        # set chat options
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                if not isinstance(chatType,dict):
                    chatOptions.append(chats.chatMap[chatType])
                else:
                    option = {}
                    option["chat"] = chats.chatMap[chatType["chat"]]
                    option["dialogName"] = chatType["dialogName"]
                    if "params" in chatType:
                        params = {}
                        for (key,value) in chatType["params"].items():
                            '''
                            set value
                            '''
                            def setParam(instance):
                                params[key] = instance
                            loadingRegistry.callWhenAvailable(value,setParam)
                        option["params"] = params
                    chatOptions.append(option)
            self.basicChatOptions = chatOptions

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        return state

    def awardReputation(self,amount=0,fraction=0, reason=None):
        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation//fraction
        self.reputation += totalAmount
        if self.watched:
            text = "you were rewarded %i reputation"%totalAmount
            if reason:
                text += " for "+reason
            self.messages.append(text)

    def revokeReputation(self,amount=0,fraction=0, reason=None):
        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation//fraction
        self.reputation -= totalAmount
        if self.watched:
            text = "you lost %i reputation"%totalAmount
            if reason:
                text += " for "+reason
            self.messages.append(text)

    '''
    starts the next quest in the quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def startNextQuest(self):
        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                debugMessages.append("setting path to quest failed")
                pass

    '''
    straightforward getting a string with detailed info about the character
    '''
    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoordinate: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubordinates: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)

    '''
    adds a quest to the characters quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def assignQuest(self,quest,active=False):
            if active:
                self.quests.insert(0,quest)
            else:
                self.quests.append(quest)
            quest.assignToCharacter(self)
            quest.activate()
            if (active or len(self.quests) == 1):
                try:
                    if self.quests[0] == quest:
                        self.setPathToQuest(quest)
                except:
                    # bad pattern: exceptions should be logged
                    pass

    '''
    set the path to a quest
    bad pattern: path should be determined by a quests solver
    bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    '''
    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY") and self.container:
            self.path = self.container.findPath((self.xPosition,self.yPosition),(quest.dstX,quest.dstY))
        else:
            self.path = []

    '''
    straightforward adding to inventory
    '''
    def addToInventory(self,item):
        self.inventory.append(item)

    '''
    this wrapper converts a character centered call to a solver centered call
    bad code: should be handled in quest
    '''
    def applysolver(self,solver):
        if not self.unconcious and not self.dead:
            solver(self)

    '''
    set state and display to unconcious
    '''
    def fallUnconcious(self):
        self.unconcious = True
        if self.watched:
            self.messages.append("*thump,snort*")
        self.changed("fallen unconcious",self)

    '''
    set state and display to not unconcious
    '''
    def wakeUp(self):
        self.unconcious = False
        if self.watched:
            self.messages.append("*grown*")
        self.changed("woke up",self)

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None):
        self.lastRoom = self.room
        self.lastTerrain = self.terrain

        # replace character with corpse
        if self.container:
            container = self.container
            container.removeCharacter(self)
            corpse = src.items.Corpse(self.xPosition,self.yPosition,creator=self)
            container.addItems([corpse])
        # log impossible state
        else:
            debugMessages.append("this should not happen, character died without beeing somewhere ("+str(self)+")")

        # set attributes
        self.dead = True
        if reason:
            self.deathReason = reason
        self.path = []

        # notify listeners
        self.changed("died",{"character":self,"corpse":corpse,"reason":reason})

        # notify listeners
        self.changed()

    '''
    walk the predetermined path
    return:
        True when done
        False when not done

    bad pattern: should be contained in quest solver
    '''
    def walkPath(self):
        # smooth over impossible state
        if self.dead:
            debugMessages.append("dead men walking")
            return
        if not self.path:
            self.setPathToQuest(self.quests[0])
            debugMessages.append("walking without path")

        # move along the predetermined path
        currentPosition = (self.xPosition,self.yPosition)
        if not (self.path and not self.path == [currentPosition]):
            return True

        # get next step
        nextPosition = self.path[0]

        item = None
        # try to move within a room
        if self.room:
            # move naively within a room
            if (nextPosition[0] == currentPosition[0] and nextPosition[1] == currentPosition[1]-1):
                item = self.room.moveCharacterDirection(self,"north")
            if (nextPosition[0] == currentPosition[0] and nextPosition[1] == currentPosition[1]+1):
                item = self.room.moveCharacterDirection(self,"south")
            elif nextPosition[0] == currentPosition[0]-1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"west")
            elif nextPosition[0] == currentPosition[0]+1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"east")
            else:
                # smooth over impossible state
                if not debug:
                    # resorting to teleport
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                    self.changed()
                else:
                    debugMessages.append("character moved on non continious path")
        # try to move within a terrain
        else:
            # check if a room was entered
            # basically checks if a walkable space/door is within a room on the coordinate the character walks on. If there is something in the way, an item it will be saved for interaction.
            # bad pattern: collision detection and room teleportation should be done in terrain

            for room in self.terrain.rooms:
                """
                helper function to move a character into a direction
                """
                def moveCharacter(localisedEntry,direction):
                    if localisedEntry in room.walkingAccess:

                        # check whether the character walked into something
                        if localisedEntry in room.itemByCoordinates:
                            for listItem in room.itemByCoordinates[localisedEntry]:
                                if not listItem.walkable:
                                    return listItem

                        # teleport the chracter into the room
                        room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                        self.terrain.characters.remove(self)
                        self.terrain = None
                        self.changed()
                        return
                    else:
                        # show message the character bumped into a wall
                        # bad pattern: why restrict the player to standard entry points?
                        self.messages.append("you cannot move there ("+direction+")")
                        return

                # handle the character moving into the rooms boundaries
                # bad code: repetitive, confusing code
                # check north
                if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        # try to move character
                        localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                        item = moveCharacter(localisedEntry,"north")
                        break
                # check south
                if room.yPosition*15+room.offsetY == nextPosition[1]:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        # try to move character
                        localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                        item = moveCharacter(localisedEntry,"south")
                        break
                # check east
                if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        # try to move character
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"east")
                        break
                # check west
                if room.xPosition*15+room.offsetX == nextPosition[0]:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        # try to move character
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"west")
                        break
            else:
                # move the char to the next position on path
                self.xPosition = nextPosition[0]
                self.yPosition = nextPosition[1]
                self.changed()
            
        # handle bumping into an item
        if item:
            # open doors
            # bad pattern: this should not happen here
            if isinstance(item,src.items.Door):
                item.apply(self)
            return False

        # smooth over impossible state
        else:
            if not debug:
                if not self.path or not nextPosition == self.path[0]:
                    return False

            # remove last step from path
            if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
                self.path = self.path[1:]
        return False

    """
    almost straightforward dropping of items
    """
    def drop(self,item):
        # remove item from inventory
        self.inventory.remove(item)

        # add item to floor
        item.xPosition = self.xPosition
        item.yPosition = self.yPosition
        self.container.addItems([item])

        # notify listener
        item.changed()
        self.changed()

    """
    examine an item
    """
    def examine(self,item):
        # print info
        self.messages.append(item.description)
        if item.description != item.getDetailedInfo():
            self.messages.append(item.getDetailedInfo())
        if item.getLongInfo():
            self.submenue = interaction.TextMenu(item.getLongInfo())
            self.macroState["submenue"] = self.submenue

        # notify listeners
        self.changed("examine",item)

    """
    advance the character one tick
    """
    def advance(self):
        if self.stasis:
            return

        # smooth over impossible state
        while self.events and gamestate.tick > self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)

        # handle events
        while self.events and gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            if not event in self.events:
                debugMessages.append("impossible state with events")
                continue
            self.events.remove(event)

        # handle satiation
        self.satiation -= 1
        self.changed()
        if self.satiation < 0:
            self.die(reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "+commandChars.drink+" key")
            return

        if self == mainChar and self.satiation < 30 and self.satiation > -1:
            self.messages.append("you'll starve in "+str(mainChar.satiation)+" ticks!")

        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()

    '''
    register for notifications
    '''
    def addListener(self,listenFunction,tag="default"):
        # create container if container doesn't exist
        # bad performace: string comparison, should use enums. Is this slow in python?
        if not tag in self.listeners:
            self.listeners[tag] = []

        # added listener function
        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregister for notifications
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clear up dict
        # bad performance: probably better to not clean up and recreate
        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    '''
    def changed(self,tag="default",info=None):
        # do nothing if nobody listens
        if not tag in self.listeners:
            return

        # call each listener
        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

"""
the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
bad code: animals should not be characters. This means it is possible to chat with a mouse 
"""
class Mouse(Character):
    '''
    basic state setting
    '''
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator)
        self.vanished = False

    '''
    disapear
    '''
    def vanish(self):
        # remove self from map
        self.container.removeCharacter(self)
        self.vanished = True
