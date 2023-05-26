import src

class BuildRoom(src.quests.MetaQuestSequence):
    type = "BuildRoom"

    def __init__(self, description="build room", creator=None, command=None, lifetime=None, targetPosition=None,tryHard=False, reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shortCode = "M"
        self.targetPosition = targetPosition
        self.tryHard = tryHard
        self.reason = reason

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def generateTextDescription(self):
        roombuilder = src.items.itemMap["RoomBuilder"]()
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        out = ["""
Build a room on the tile %s%s."""%(self.targetPosition,reason,),"""

Rooms are build using the RoomBuilder (""",roombuilder.render(),""").
The RoomBuilder needs to be placed in the middle of a tile.
Walls and doors have to be placed in a room shaped pattern around that.
When all of that is done, the Roombuilder can be activated to build a room.
"""]

        if self.tryHard:
            out.append("""
Try as hard as you can to achieve this.
If something is missing, produce it.
If something disturbs you, destroy it.
""")

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append("""
Follow this quests sub quests. They will guide you and try to explain how to build a base.""")
            out.append("""
Press d to move the cursor and show the subquests description.
""")

        out.append("""
Press a to move back to the main quest.
""")
        return out

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit submenu"))

            items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0))
            if not items or not items[-1].type == "RoomBuilder":
                quest = src.quests.questMap["PlaceItem"](targetPosition=(7,7,0),targetPositionBig=self.targetPosition,itemType="RoomBuilder",reason="start building the room")
                return ([quest],None)
            
            wallPositions = [(1,1,0),(1,13,0),(13,1,0),(13,13,0)]
            wallPositions.extend([(2,1,0),(3,1,0),(4,1,0),(5,1,0),(6,1,0)])
            wallPositions.extend([(8,1,0),(9,1,0),(10,1,0),(11,1,0),(12,1,0)])
            wallPositions.extend([(2,13,0),(3,13,0),(4,13,0),(5,13,0),(6,13,0)])
            wallPositions.extend([(8,13,0),(9,13,0),(10,13,0),(11,13,0),(12,13,0)])
            wallPositions.extend([(1,2,0),(1,3,0),(1,4,0),(1,5,0),(1,6,0)])
            wallPositions.extend([(13,2,0),(13,3,0),(13,4,0),(13,5,0),(13,6,0)])
            wallPositions.extend([(1,8,0),(1,9,0),(1,10,0),(1,11,0),(1,12,0)])
            wallPositions.extend([(13,8,0),(13,9,0),(13,10,0),(13,11,0),(13,12,0)])
            missingWallPositions = []
            for wallPos in wallPositions:
                items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+wallPos[0],15*self.targetPosition[1]+wallPos[1],0))
                if items and items[-1].type == "Wall":
                    continue
                missingWallPositions.append(wallPos)

            if missingWallPositions:
                if not character.inventory or not character.inventory[-1].type == "Wall":
                    amount = None
                    if len(missingWallPositions) < 10:
                        amount = len(missingWallPositions)
                    quest = src.quests.questMap["FetchItems"](toCollect="Wall",takeAnyUnbolted=True,tryHard=self.tryHard,amount=amount,reason="have walls for the rooms outline")
                    return ([quest],None)

                quests = []
                counter = 0
                for missingWallPos in missingWallPositions:
                    if not (len(character.inventory) > counter and character.inventory[-1-counter].type == "Wall"):
                        break
                    quest = src.quests.questMap["PlaceItem"](targetPosition=missingWallPos,targetPositionBig=self.targetPosition,itemType="Wall",tryHard=self.tryHard,reason="build the outline of the room")
                    quests.append(quest)
                    counter += 1
                return (list(reversed(quests)),None)
            
            doorPositions = [(7,1,0),(1,7,0),(7,13,0),(13,7,0)]
            missingDoorPositions = []
            for doorPos in doorPositions:
                items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+doorPos[0],15*self.targetPosition[1]+doorPos[1],0))
                if items:
                    continue
                missingDoorPositions.append(doorPos)

            if missingDoorPositions:
                numDoors = 0
                for item in character.inventory:
                    if item.type == "Door":
                        numDoors += 1

                if not numDoors:
                    amount = len(missingDoorPositions)
                    quest = src.quests.questMap["FetchItems"](toCollect="Door",takeAnyUnbolted=True,tryHard=self.tryHard,amount=amount,reason="have doors to place")
                    return ([quest],None)

                quests = []
                counter = 0
                for missingDoorPos in missingDoorPositions:
                    if not numDoors:
                        break
                    numDoors -= 1
                    quest = src.quests.questMap["PlaceItem"](targetPosition=missingDoorPos,targetPositionBig=self.targetPosition,itemType="Door",tryHard=self.tryHard,reason="add doors to the room")
                    quests.append(quest)
                    counter += 1
                return (list(reversed(quests)),None)
            
            roomBuilderPos = (7,7,0)
            if character.getDistance((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=roomBuilderPos,ignoreEndBlocked=True,reason="get next to the RoomBuilder")
                return ([quest], None)

            offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
            for (offset,command) in offsets.items():
                if character.getPosition(offset=offset) == (15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0):
                    return (None, (command,"activate the RoomBuilder"))
            1/0
        return (None,None)
    
    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if character.getTerrain().getRoomByPosition(self.targetPosition):
            self.postHandler()
            return True
        return False

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.targetPosition,"target"))
        return result

src.quests.addType(BuildRoom)
