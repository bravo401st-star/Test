import ItemSystem
import copy
from abc import ABC

class Entity(ABC):
    def __init__(self, name: str, health: int):
        self.health = health
        self.name = name

    
    def Damage(self, amount: int):
        self.health -= amount
        print(self.name + " took " + str(amount) + " damage!")
        pass


class BasicEnemy(Entity):
    def __init__(self, name, health):
        super().__init__(name, health)


class Player(Entity):
    def __init__(self, name, health):
        super().__init__(name, health)
        self.items = []
        self.maxStamina = 5
        self.stamina = self.maxStamina


    def GiveItem(self, item: ItemSystem.Item):
        if item is None:
            return

        self.items.append(copy.copy(item))
        print(item.name + " given to " + self.name)


def SpawnEnemy(enemy: Entity):
    global enemiesInScene
    enemiesInScene.append(enemy)
    print("A " + enemy.name + " has appeared!")
    pass


def GetEntity(index: int):
    global enemiesInScene

    if (index < 0 or index > len(enemiesInScene)):
        return None

    if (index == 0):
        return playerCharacter
    else:
        return enemiesInScene[index - 1]


playerCharacter = Player("Player", health=100)
enemiesInScene = []
gameRunning = True