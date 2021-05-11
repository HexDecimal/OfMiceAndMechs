import src

class SwarmIntegrator(src.items.Item):
    type = "SwarmIntegrator"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.floor_node,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False
        self.faction = "swarm"

    def getLongInfo(self):
        return """
item: SwarmIntegrator

description:
You can use it to create paths
"""

    def apply(self,character):
        command = "aopR.$a*13.$w*13.$s*13.$d*13.$=aa$=ww$=ss$=dd"
        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

src.items.addType(SwarmIntegrator)
