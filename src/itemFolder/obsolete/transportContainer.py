import src

class TransportContainer(Item):
    type = "TransportContainer"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport Container",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        options = [("addItems","load item"),
                   ("transportItem","transport item"),
                   ("getJobOrder","set transport command")
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        # add item
        # remove item
        # transport item
        # set transport command
        pass

src.items.addType(TransportContainer)
