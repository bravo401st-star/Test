import ItemSystem
import random

def GetRandomItem(weighted: bool = False, rolls: int = 1, filter: list[type] | None = None) -> ItemSystem.AItem:
    items = GetListWithBlacklist(filter) if filter is not None else ItemSystem.itemsList

    if weighted:
        totalWeight = 0
        for item in items:
            totalWeight += item.rarity

        roll = random.uniform(1, totalWeight)
        rollCount = 1
        while rollCount < rolls:
            newRoll = random.uniform(1, totalWeight)
            if roll < newRoll:
                roll = newRoll
            rollCount += 1

        currentWeight = 0
        for item in items:
            currentWeight += item.rarity
            if roll <= currentWeight:
                return item
            
    rand = random.randint(0, len(items) - 1)
    return items[rand]

def GetItemByName(name: str) -> ItemSystem.AItem | None:
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

def GetListWithBlacklist(filter: list[type]) -> list[ItemSystem.AItem]:
    items = []
    for item in ItemSystem.itemsList:
        for f in filter:
            if type(item) is not f:
                items.append(item)
                break
    return items

def GetListWithWhitelist(filter: list[type]) -> list[ItemSystem.AItem]:
    items = []
    for item in ItemSystem.itemsList:
        for f in filter:
            if issubclass(type(item), f):
                items.append(item)
                break
    return items