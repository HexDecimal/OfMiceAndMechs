import src
import random

class SecureTile(src.quests.questMap["GoToTile"]):
    type = "SecureTile"

    def __init__(self, description="secure tile", toSecure=None, endWhenCleared=False, reputationReward=0,rewardText=None,strict=False):
        super().__init__(description=description,targetPosition=toSecure)
        self.metaDescription = description
        self.endWhenCleared = endWhenCleared
        self.reputationReward = reputationReward
        self.rewardText = rewardText
        self.huntdownCooldown = 0
        self.strict = strict

    def generateTextDescription(self):
        text  = """
Secure the tile %s.

This means you should go to the tile and kill all enemies you find."""%(self.targetPosition,)
        if not self.endWhenCleared:
            text = "\n"+text+"\n\nStay there and kill all enemies arriving"
        else:
            text = "\n"+text+"\n\nthe quest will end after you do this"
        text += """

You can attack enemies by walking into them.
But you can use your environment to your advantage, too.
Try luring enemies into landmines or detonating some bombs."""

        return text

    def wrapedTriggerCompletionCheck2(self, extraInfo):
        if not self.active:
            return
        self.triggerCompletionCheck(extraInfo["character"])

    def handleTileChange2(self):
        if not self.active:
            return
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.wrapedTriggerCompletionCheck2, "character died on tile")
        self.startWatching(character,self.handleTileChange2, "changedTile")

        super().assignToCharacter(character)

    def postHandler(self,character=None):
        if self.reputationReward and character:
            if self.rewardText:
                text = self.rewardText
            else:
                text = "securing a tile"
            character.awardReputation(amount=50, reason=text)
        super().postHandler()

    def triggerCompletionCheck(self,character=None):

        if not character:
            return False

        if not self.endWhenCleared:
            return False

        if isinstance(character.container,src.rooms.Room):
            if character.container.xPosition == self.targetPosition[0] and character.container.yPosition == self.targetPosition[1]:
                if not character.getNearbyEnemies():
                    self.postHandler(character)
                    return True
        else:
            if character.xPosition//15 == self.targetPosition[0] and character.yPosition//15 == self.targetPosition[1]:
                if not character.getNearbyEnemies():
                    self.postHandler(character)
                    return True

        return False

    def getSolvingCommandString(self, character, dryRun=True):
        if not self.subQuests:
            if character.getBigPosition() == self.targetPosition:
                enemies = character.getNearbyEnemies()
                if not enemies and not self.endWhenCleared:
                    return "10."
            return super().getSolvingCommandString(character,dryRun=dryRun)

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:
            if character.health < 80 and character.canHeal():
                return (None,"JH","to heal")

            if not self.strict:
                self.huntdownCooldown -= 1
                if self.huntdownCooldown < 0:
                    enemies = character.getNearbyEnemies()
                    if enemies:
                        if not dryRun:
                            self.huntdownCooldown = 100
                        if random.random() < 0.3:
                            quest = src.quests.questMap["Huntdown"](target=random.choice(enemies))
                            return ([quest],None)
                        else:
                            quest = src.quests.questMap["Fight"]()
                            return ([quest],None)

        return super().getNextStep(character=character,ignoreCommands=ignoreCommands)

src.quests.addType(SecureTile)
