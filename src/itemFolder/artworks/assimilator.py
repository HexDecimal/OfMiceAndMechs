import src
import random
import copy
import json

class Assimilator(src.items.Item):
    """
    """


    type = "Assimilator"

    def __init__(self, name="Assimilator", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="AS", name=name)

        self.usageInfo = """
Use it by activating it."""

    def apply(self,character):
        if character.registers.get("gotMostBasicTraining") == None:
            character.registers["gotMostBasicTraining"] = True
            self.implantIntroduction({"character":character,"step":0})
            return
        
        if character.rank == None:
            self.shortIntroduction({"character":character})
            return
        
        if character.rank == 6:
            if character.reputation < 300:
                text = """

you need 300 reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""
            else:
                text = """

you are hereby rank 5.

Continue to be useful.

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20, health +50)

"""
                character.rank = 5

                character.baseDamage += 2
                character.addMessage("your base damage increased by 2")
                character.maxHealth += 20
                character.heal(50)
                character.addMessage("your max heath increased by 20")

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return

        if character.rank == 5:
            if character.reputation < 600:
                text = """

you need 600 reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""
            else:
                text = """

you are hereby rank 4.

Continue to be useful.

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20, health +50)

"""
                character.rank = 4

                character.baseDamage += 2
                character.addMessage("your base damage increased by 2")
                character.maxHealth += 20
                character.heal(50)
                character.addMessage("your max heath increased by 20")

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return

        if character.rank == 4:
            if character.reputation < 1000:
                text = """

you need 1000 reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""
            else:
                text = """

you are hereby rank 3.
This means you are the commander of this base now.

Continue to be useful.

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20, health +50)

"""
                character.rank = 3

                character.baseDamage += 2
                character.addMessage("your base damage increased by 2")
                character.maxHealth += 20
                character.heal(50)
                character.addMessage("your max heath increased by 20")

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return
        
        if character.rank == 3:
                text = """

you this bases commander.
you can not increase your rank.

"""

        super().apply(character)

    def shortIntroduction(self,extraParams):
        text = """
Showing short introduction.
"""

        character = extraParams["character"]
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration1","params":params}

    def implantIntroduction(self,extraParams):
        character = extraParams["character"]
        step = extraParams["step"]

        if step == 0:
            text = """
You have no records on this base.

Showing full introduction.
"""
        elif step == 1:
            text = """
You are a clone and serve in faction %s.

After assimilation you will serve on this base.
All clones on this base work together.
Ranks on this base are 3,4,5,6 and it supports ghuls.
You will have rank 6 the lowest rank beside ghuls.

---

The green @3, @4, @5, @6 and @x are your allies.
Try to work with them.

"""%(character.faction,)
        elif step == 2:
            text = """

Most coordination is done by the implants.
No clone is complete without it.
It stores your tasks and can direct your steps.
Most day to day tasks can be solved completely by the implant.

Ghuls don't have implants and can only execute simple commands.

---

Try pressing "+", if you are lost or a quest doesn't complete correctly.

The Implant is represented by the quests in your UI.
Press "+" to autosolve a step of your quest.

This can result in 2 effects:
* The quest splits into subquests
* The character will move some steps to solve the deepest subquest.

If you want to stop your character from moving automatically press "ctrl-d".
Alternatively click the red "*" in the upper part of your UI to stop.
"""
        else:
            self.basicIntegration1({"character":character})
            return

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character,"step":step+1}
        character.macroState["submenue"].followUp = {"container":self,"method":"implantIntroduction","params":params}


    def basicIntegration1(self,extraParams):
        character = extraParams["character"]
        text = """
This base is primarily organised by a job system.
That means you just will told to be useful.
What you will be doing exactly will be decided by your duties.
The implant will guide you through the steps.

Main duties that have to be taken care of on this base are:

* Hauling:
Carry resources between stockpiles
* Clearing:
Pick up items from the walkways
* Resource fetching:
Transport resources between rooms 
* Resource gathering:
Go outside and collect resources
* Trap reloading:
Reloading the trap rooms

To find tasks to complete just walk around until you find somewhere to be useful.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration2","params":params}

    def basicIntegration2(self,extraParams):
        character = extraParams["character"]
        if not "fighting" in character.skills: 
            text = """

You need to retrain your skills for this base.

You have no skills retrained.

Retrain a skill and return to integrate into the bases systems

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.TrainSkill()
            quest.assignToCharacter(character)
            quest.activate()
            quest.generateSubquests(character)
            character.quests.insert(0,quest)

        else:
            text = """
You hereby have a rank of 6.

Your duties are:

Questing:
Go to the QuestArtwork and complete the quests given.

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20, health +50)

---

your stats were increased and you got healing.
This happens when you complete a story section.

"""
            character.rank = 6
            character.registers["HOMEx"] = 7
            character.registers["HOMEy"] = 7

            character.baseDamage += 2
            character.addMessage("your base damage increased by 2")
            character.maxHealth += 20
            character.heal(50)
            character.addMessage("your max heath increased by 20")

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration3","params":extraParams}

    def basicIntegration3(self,extraParams):
        character = extraParams["character"]
        text = """
Now go on and be useful

----
You were assigned the "be useful" quest.
Initially it will show up as one line only.
When you press "+" that quest generates sub quests.
"""

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.duties = ["Questing"]

        for quest in character.quests:
            quest.postHandler()

        character.quests = []
        character.quests.append(src.quests.BeUsefull())

src.items.addType(Assimilator)
