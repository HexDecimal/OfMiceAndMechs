import src

class PoisonBloom(src.items.Item):
    """
    a poisonous plant
    """

    type = "PoisonBloom"

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.poisonBloom)

        self.name = "poison bloom"
        self.description = "Its spore sacks shriveled and are covered in green slime"
        self.usageInfo = """
You can eat it to die.
"""
        self.walkable = True
        self.dead = False
        self.bolted = False
        self.attributesToStore.extend(["dead"])

    def apply(self, character):
        """
        handle a character trying to use this item
        by killing the character

        Parameters:
            character: the character trying to use the item
        """

        if not self.terrain:
            self.dead = True

        character.die()

        if not self.dead:
            new = itemMap["PoisonBush"]()
            self.container.addItem(new,self.getPosition())

        character.addMessage("you eat the poison bloom and die")

        self.destroy(generateSrcap=False)

    def pickUp(self, character):
        """
        handle getting picked up by a character

        Parameters:
            character: the character picking up the item
        """

        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def destroy(self, generateSrcap=True):
        """
        destroy the item without leaving residue
        """

        super().destroy(generateSrcap=False)

src.items.addType(PoisonBloom)
