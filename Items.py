import ItemSystem
import random
from dataclasses import dataclass, astuple
from collections.abc import Iterable
import copy

@dataclass
class Filter():
    typeFilter: tuple[type[ItemSystem.AItem]]
    isBlackList: bool = True
    pass

def GetRandomItem(weighted: bool = False, rolls: int = 1, filter: Filter | None = None, maxRarity: int = 100, removeItems: list[ItemSystem.AItem] | None = None) -> ItemSystem.AItem | None:
    items = list()
    if filter is not None:
        filterList = list(filter.typeFilter) if type(filter.typeFilter) is Iterable else [filter.typeFilter]
        items = GetListWithBlacklist(filterList) if filter.isBlackList else GetListWithWhitelist(filterList)
    else:
        items = copy.deepcopy(ItemSystem.itemsList)

    for item in reversed(items):
        if item.rarity > maxRarity:
            items.remove(item)
    
    if removeItems is not None:
        for remove in reversed(removeItems):
            if remove in items:
                items.remove(remove)

    if len(items) <= 0:
        return None

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