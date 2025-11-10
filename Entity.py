import copy
import EventSystem
import ItemSystem
from abc import ABC
import GameCore as gc
import LevelHandler
import random
from colorama import Fore, Back, Style

class Entity(ABC):
    def __init__(self):
        self.health = 100
        self.name = "Unnamed Entity"
        self.level = 1
        self.maxHealth = self.health

    def SetName(self, name: str):
        self.name = name
        return self
    
    def SetLevel(self, level: int):
        self.level = level
        return self
    
    def SetMaxHealth(self, max: int):
        self.maxHealth = max
        return self
    
    def SetHealth(self, hp: int):
        self.health = hp
        return self
    
    def Kill(self):
        global e_EntityDeath
        e_EntityDeath.Trigger(self)

    def Damage(self, amount: int):
        global e_EntityDeath
        self.health -= amount
        print(self.name + " took " + str(amount) + " damage!")
        if (self.health <= 0):
            self.Kill()
        pass

    def Heal(self, amount: int):
        if (self.health >= self.maxHealth):
            return False
        
        self.health += amount
        if (self.health > self.maxHealth):
            self.health = self.maxHealth

        print(self.name + " healed for " + str(amount) + " health!")
        return True
    


class BasicEnemy(Entity):
    def __init__(self):
        super().__init__()
        self.exp = range(1, 2)

    def SetDropExp(self, xp: range):
        self.exp = xp
        return self
    
    def Kill(self):
        gc.playerCharacter.level.GrantExperience(self.level + random.randrange(self.exp.start, self.exp.stop))
        return super().Kill()


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.items = []
        self.maxStamina = 5
        self.stamina = self.maxStamina
        self.level = LevelHandler.LevelHandler()

    def GiveItem(self, item: ItemSystem.Item):
        if item is None:
            return

        self.items.append(copy.copy(item))
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + item.name + Style.RESET_ALL + " given to " + self.name + Style.RESET_ALL)


e_EntityDeath = EventSystem.Event(Entity)
