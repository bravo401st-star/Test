import copy
import EventSystem
import ItemSystem
from abc import ABC
import GameCore as gc
import LevelHandler
import random
from colorama import Fore, Back, Style
import Actions
from EnemyTags import ElementTag
import Relics

class AEntity(ABC):
    def __init__(self):
        self.health = 100
        self.name = "Unnamed Entity"
        self.level = 1
        self.maxHealth = self.health
        self.additionalRawDamage = 0
        self.damageMultiplier = 1.0
        self.effects = []
        self.evasion = 0.0
        self.damageResistance = 0.0
        self.shield = 0

    def OnSpawn(self):
        pass

    def DoTurn(self):
        effectsToRemove = []
        for effect in self.effects:
            effect.OnEffectTick()
            if effect.stacks <= 0:
                effectsToRemove.append(effect)

        for effect in effectsToRemove:
            self.RemoveEffect(effect)
        pass

    def RemoveEffect(self, effect):
        self.effects.remove(effect)
        effect.OnEffectRemove()

    def ClearStatusEffects(self, ignorePositive = False):
        for effect in reversed(self.effects):
            if ignorePositive and effect.positive:
                continue
            self.RemoveEffect(effect)

    def HasEffect(self, effectType: type) -> bool:
        for effect in self.effects:
            if type(effect) is effectType:
                return True
        return False
    
    def Cleanup(self):
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
        if (self.health <= 0):
            return
        if self.CheckEvasion():
            return
        amount -= int(amount * min(self.damageResistance, 0.9))

        if self.shield > 0:
            if amount <= self.shield:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0

        self.health -= amount
        print(self.name + " took " + str(amount) + " damage!")
        if (self.health <= 0):
            self.Kill()
        pass

    def CheckEvasion(self) -> bool:
        if (self.evasion <= 0.0):
            return False
        roll = random.uniform(0.0, 1.0)
        if (roll < self.evasion):
            print(f"{self.name} evaded the attack!")
            return True
        return False

    def Heal(self, amount: int):
        if (self.health >= self.maxHealth):
            return False
        
        self.health += amount
        if (self.health > self.maxHealth):
            self.health = self.maxHealth

        print(self.name + " healed for " + str(amount) + " health!")
        return True
    
    def GetEffectListText(self) -> str | None:
        if len(self.effects) <= 0:
            return None
        effectList = "["

        for effect in self.effects:
            effectList += f"{effect.GetName()} ({effect.stacks}), "

        return effectList[:-2] + "]"

e_EntityDeath = EventSystem.Event(AEntity)

class BasicEnemy(AEntity):
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
        self.SetMaxHealth(round(self.maxHealth * (1 + 0.03 * (self.level - 1))), True)
        return super().OnSpawn()

    def SetDropExp(self, xp: range | int):
        self.exp = xp
        return self
    
    def DisableSpawnPool(self):
        self.canSpawnInEncounters = False
        return self
    
    def Kill(self):
        import Relics
        import Commands
        if self.exp == 0:
            return super().Kill()
        toDrop = self.level + random.randrange(self.exp.start, self.exp.stop) if type(self.exp) is range else self.exp
        gc.playerCharacter.level.GrantExperience(round(toDrop * gc.experienceMultiplier))
        gc.playerCharacter.GiveGold(round(toDrop * 2 * gc.goldMultiplier))

        if (gc.playerCharacter.HasRelic(Relics.SoulbinderCharm)):
            if (random.randrange(0, 100) < int(Relics.SoulbinderCharm.RELIC_DROP_CHANCE * 100)):
                gc.GiveRelicReward(Commands)

        if gc.playerCharacter.HasRelic(Relics.SoulvesselJar):
            Relics.soulvesselJarKillsNeeded -= 1
            if Relics.soulvesselJarKillsNeeded <= 0:
                Relics.soulvesselJarKillsNeeded = 20
                print(f"{Fore.CYAN}Your {Style.BRIGHT}Soulvessel Jar{Style.RESET_ALL}{Fore.CYAN} has filled and grants you a their energy!{Style.RESET_ALL}")
                gc.playerCharacter.maxStamina += 1

        return super().Kill()
    
    def AttachActionSet(self, actionSet: Actions.ActionSet):
        self.actionSet = copy.deepcopy(actionSet)
        return self

    def DoTurn(self):
        if (self.health <= 0):
            return
        if self.actionSet != None:
            self.actionSet.PerformNextAction()
        return super().DoTurn()

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
    
    def TryToRaiseDead(self, entity: BasicEnemy):
        import Enemies
        if (entity is self):
            return
        if (not issubclass(type(entity), BasicEnemy)):
            return
        if (entity.HasTag(ElementTag.UNDEAD, ElementTag.CANT_BE_UNDEAD)):
            return
        undead = Enemies.CreateEnemyByName(entity.name)
        if (undead == None):
            return
        undead.SetName(f"Undead {undead.name}")
        undead.SetMaxHealth(int(undead.maxHealth / 2))
        undead.SetHealth(undead.maxHealth)
        undead.AddTags(ElementTag.UNDEAD)

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

class Player(AEntity):
    def __init__(self):
        super().__init__()
        self.items = []
        self.maxStamina = 5
        self.stamina = self.maxStamina
        self.level = LevelHandler.LevelHandler()
        self.gold = 0
        self.relics: list[Relics.ARelic] = []
        self.critialHitChance = 0.05 # 5% base crit chance

    def GiveRelic(self, relic: Relics.ARelic | None):
        if relic is None:
            return

        self.relics.append(relic)
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + relic.name + Style.RESET_ALL + " acquired by " + self.name + Style.RESET_ALL)
        relic.OnAcquire()

    def RemoveRelic(self, relicType: type):
        for relic in self.relics:
            if type(relic) is relicType:
                self.relics.remove(relic)
                print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + relic.name + Style.RESET_ALL + " removed from " + self.name + Style.RESET_ALL)
                return

    def GiveItem(self, item: ItemSystem.AItem | None):
        if item is None:
            return

        self.items.append(copy.copy(item))
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + item.name + Style.RESET_ALL + " given to " + self.name + Style.RESET_ALL)

    def HasRelic(self, relicType: type) -> bool:
        for relic in self.relics:
            if type(relic) is relicType:
                return True
        return False
    
    def HasItem(self, itemName: str) -> bool:
        for item in self.items:
            if item.name == itemName:
                return True
        return False
    
    def GetItemCount(self, itemName: str) -> int:
        count = 0
        for item in self.items:
            if item.name == itemName:
                count += 1
        
        return count
    
    def RemoveItem(self, itemName: str) -> bool:
        for i, item in enumerate(self.items):
            if item.name == itemName:
                self.items.pop(i)
                return True
        return False
    
    def GetRelicCount(self, relicType: type) -> int:
        count = 0
        for relic in self.relics:
            if type(relic) is relicType:
                count += 1
        return count
    
    def Heal(self, amount: int):
        if self.HasRelic(Relics.CelestialOrb):
            amount = round(amount * (1 + Relics.CelestialOrb.HEALING_MULT))
            print(f"{self.name}'s Life Spring Amulet increases healing to {amount}!")

        if self.HasRelic(Relics.ShadowboundMark):
            amount = round(amount * Relics.ShadowboundMark.HEALING_REDUCTION_PERCENT)
            print(f"{self.name}'s Shadowbound Mark reduces healing to {amount}!")

        return super().Heal(amount)

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
    
    def Kill(self):
        if self.HasRelic(Relics.PhoenixFeather):
            print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}Phoenix Feather{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX} glows brightly, resurrecting {self.name}!{Style.RESET_ALL}")
            self.SetHealth(round(self.maxHealth * Relics.PhoenixFeather.REVIVE_HEALTH_PERCENT))
            self.RemoveRelic(Relics.PhoenixFeather)
            return
        return super().Kill()
    
    def GetGold(self) -> int:
        return self.gold
    
    def CanAfford(self, amount: int) -> bool:
        return self.gold >= amount
    
    def DoTurn(self):
        if self.HasRelic(Relics.CelestialOrb):
            self.Heal(round(self.maxHealth * Relics.CelestialOrb.HEAL_START_COMBAT_PERCENT)) # heal 10% max health each turn

        bloodOathCount = self.GetRelicCount(Relics.BloodOathPendant)
        if bloodOathCount > 0:
            self.Damage(Relics.BloodOathPendant.HEALTH_LOST_PER_TURN * bloodOathCount)
        return super().DoTurn()