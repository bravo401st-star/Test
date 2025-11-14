import copy
import EventSystem
import ItemSystem
from abc import ABC
import GameCore as gc
import LevelHandler
import random
from colorama import Fore, Back, Style
import EnemyAttackPattern

class Entity(ABC):
    def __init__(self):
        self.health = 100
        self.name = "Unnamed Entity"
        self.level = 1
        self.maxHealth = self.health

    def OnSpawn(self):
        pass

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
e_EntityDeath = EventSystem.Event(Entity)

class BasicEnemy(Entity):
    def __init__(self):
        super().__init__()
        self.exp = range(1, 2)
        self.actionSet = None
        self.tags = []

    def SetDropExp(self, xp: range):
        self.exp = xp
        return self
    
    def Kill(self):
        if self.exp == 0:
            return super().Kill()
        gc.playerCharacter.level.GrantExperience(self.level + random.randrange(self.exp.start, self.exp.stop))
        return super().Kill()
    
    def AttachActionSet(self, actionSet: EnemyAttackPattern.ActionSet):
        self.actionSet = copy.deepcopy(actionSet)
        return self

    def DoTurn(self):
        self.actionSet.PerformNextAction(self)

    def SetTags(self, *tags: str):
        self.tags = list(tags)
        return self

    def AddTags(self, *tags: str):
        for tag in tags:
            self.tags.append(tag)
        return self
    
    def HasTag(self, *tags: str):
        for tagInList in tags:
            for t in self.tags:
                if t == tagInList:
                    return True
        return False
    
class NecromancerEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()

    def OnSpawn(self):
        global e_EntityDeath
        e_EntityDeath.Subscribe(self.TryToRaiseDead)
        return super().OnSpawn()

    def Kill(self):
        global e_EntityDeath
        e_EntityDeath.Unsubscribe(self.TryToRaiseDead)
        return super().Kill()
    
    def TryToRaiseDead(self, entity):
        import Enemies
        if (entity is self):
            return
        if (not issubclass(type(entity), BasicEnemy)):
            return
        if (entity.HasTag("Undead", "Cant_Be_Undead")):
            return
        undead = Enemies.CreateEnemyByName(entity.name)
        if (undead == None):
            return
        undead.SetName(f"Undead {undead.name}")
        undead.SetMaxHealth(undead.maxHealth / 2)
        undead.SetHealth(undead.maxHealth)
        undead.AddTags("Undead")

        print(f"{self.name} is raising an {undead.name}!!")
        gc.SpawnEnemy(undead)


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

    def Damage(self, amount):
        if (gc.godmode):
            print(f"Godly power has blocked {amount} damage.")
            return
        return super().Damage(amount)