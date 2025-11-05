import ItemSystem
import random

def GetRandomItem(weighted: bool = False):
    rand = random.randint(0, len(ItemSystem.itemsList) - 1)
    return ItemSystem.itemsList[rand]


def GetItemByName(name: str):
    for item in ItemSystem.itemsList:
        if item.name == name:
            return item
    print("Unknown item: \"" + name + "\"")
    return None