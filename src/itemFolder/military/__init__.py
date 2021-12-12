"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.military." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.military.armor
import src.itemFolder.military.bomb
import src.itemFolder.military.mortar
import src.itemFolder.military.landmine
import src.itemFolder.military.sword

