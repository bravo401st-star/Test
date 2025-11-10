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


def GetItemByIndex(index: int):
    if (index >= len(ItemSystem.itemsList) or index < 0):
        return None
    return ItemSystem.itemsList[index]
    

def GetItemsByTag(tag: str):
    items = []
    for item in ItemSystem.itemsList:
        if (item.tag.upper() == tag.upper()):
            items.append(item)

    return items