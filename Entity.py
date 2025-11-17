import copy
import EventSystem
import ItemSystem
from abc import ABC
import GameCore as gc
import LevelHandler
import random
from colorama import Fore, Back, Style
import Actions
from EnemyTags import Tags

class Entity(ABC):
    def __init__(self):
        self.health = 100
        self.name = "Unnamed Entity"
        self.level = 1
        self.maxHealth = self.health
        self.additionalDamage = 0

    def OnSpawn(self):
        pass

    def SetName(self, name: str):
        self.name = name
        return self
    
    def SetLevel(self, level: int):
        self.level = level
        return self
    
    def SetMaxHealth(self, max: int, setHealthToo: bool = False):
        self.maxHealth = max
        if setHealthToo:
            self.SetHealth(max)
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
        self.canSpawnInEncounters = True

    def OnSpawn(self):
        if self.actionSet is not None:
            self.actionSet.Setup(self)

        # scale health by level
        self.SetMaxHealth(self.maxHealth + ((self.level - 1) * 10), True)
        return super().OnSpawn()

    def SetDropExp(self, xp: range | int):
        self.exp = xp
        return self
    
    def DisableSpawnPool(self):
        self.canSpawnInEncounters = False
        return self
    
    def Kill(self):
        if self.exp == 0:
            return super().Kill()
        toDrop = self.level + random.randrange(self.exp.start, self.exp.stop) if type(self.exp) is range else self.exp
        gc.playerCharacter.level.GrantExperience(toDrop)
        gc.playerCharacter.GiveGold(toDrop * 2)
        return super().Kill()
    
    def AttachActionSet(self, actionSet: Actions.ActionSet):
        self.actionSet = copy.deepcopy(actionSet)
        return self

    def DoTurn(self):
        if self.actionSet != None:
            self.actionSet.PerformNextAction()

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
    
    def TryToRaiseDead(self, entity: BasicEnemy):
        import Enemies
        if (entity is self):
            return
        if (not issubclass(type(entity), BasicEnemy)):
            return
        if (entity.HasTag(Tags.UNDEAD, Tags.CANT_BE_UNDEAD)):
            return
        undead = Enemies.CreateEnemyByName(entity.name)
        if (undead == None):
            return
        undead.SetName(f"Undead {undead.name}")
        undead.SetMaxHealth(int(undead.maxHealth / 2))
        undead.SetHealth(undead.maxHealth)
        undead.AddTags(Tags.UNDEAD)

        print(f"{self.name} is raising an {undead.name}!!")
        gc.SpawnEnemy(undead)

class TrollEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()

    def DoTurn(self):
        self.Heal(5)
        return super().DoTurn()
    
class TransformOnDeathEnemy(BasicEnemy):
    def __init__(self, transformIndex: int, flavorText: str = ""):
        super().__init__()
        self.transformToIndex: int = transformIndex
        self.flavorText: str = flavorText

    def Kill(self):
        import Enemies
        if (self.flavorText != ""):
            print(f"{self.name} {self.flavorText}")
        gc.SpawnEnemy(Enemies.CreateEnemyByIndex(self.transformToIndex), True)
        return super().Kill()

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.items = []
        self.maxStamina = 5
        self.stamina = self.maxStamina
        self.level = LevelHandler.LevelHandler()
        self.gold = 0

    def GiveItem(self, item: ItemSystem.Item | None):
        if item is None:
            return

        self.items.append(copy.copy(item))
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + item.name + Style.RESET_ALL + " given to " + self.name + Style.RESET_ALL)

    def Damage(self, amount):
        if (gc.godmode):
            print(f"Godly power has blocked {amount} damage.")
            return
        return super().Damage(amount)
    
    def GiveGold(self, amount: int):
        self.gold += amount
        print(f"{self.name} received {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}! Current gold: {Fore.YELLOW}{Style.BRIGHT}{self.gold}{Style.RESET_ALL}")

    def SpendGold(self, amount: int) -> bool:
        if (self.gold < amount):
            print(f"Not enough gold! Need {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}, has {Fore.YELLOW}{Style.BRIGHT}{self.gold} gold{Style.RESET_ALL}.")
            return False
        self.gold -= amount
        print(f"{self.name} spent {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}. Current gold: {Fore.YELLOW}{Style.BRIGHT}{self.gold}{Style.RESET_ALL}")
        return True