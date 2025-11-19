import GameCore as gc
import StatusEffect

class Item():
    tag = "ITEM"

    def __init__(self):
        self.name = "Unnamed Item"
        self.rarity = 100
        pass
    
    def GetDesc(self):
        return self.name
    
    def SetName(self, name: str):
        self.name = name
        return self

    def SetRarity(self, rarity: int):
        self.rarity = rarity
        return self
    
    def GetGoldCost(self) -> int:
        baseCost = 10
        cost = int(baseCost * (100 / self.rarity))
        return cost
    
class LevelableItem():
    def __init__(self):
        self.itemLevel = 1
        self.maxLevel = 10

    def Upgrade(self, amount: int = 1):
        self.itemLevel = min(self.itemLevel + amount, self.maxLevel)

    def SetMaxLevel(self, max: int):
        self.maxLevel = max
        return self


class UseableItem(Item):
    def __init__(self):
        super().__init__()
        self.useCost = 1
        self.useCount = -1
        self.effectToApply: None | type = None

    def GetDesc(self):
        return super().GetDesc() + " - COST: " + str(self.useCost)

    def Use(self, target):
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        stamina = gc.playerCharacter.stamina
        if (stamina < self.useCost):
            print("Not enough stamina to use item! Need " + str(self.useCost) + " stamina, has " + str(stamina) + " stamina.")
            return False
        
        gc.playerCharacter.stamina -= self.useCost
        print("Using " + self.name + " on " + target.name)
        
        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()

        self.OnUse(target)

    def OnUse(self, target):
        if (self.effectToApply != None):
            StatusEffect.Apply(target, self.effectToApply)
        pass

    def SetEffectToApply(self, effectType: type):
        if not issubclass(effectType, StatusEffect.AEffect):
            return self
        
        self.effectToApply = effectType
        return self

    def RemoveSelfFromInventory(self):
        if (self in gc.playerCharacter.items):
            gc.playerCharacter.items.remove(self)

    def SetUses(self, uses: int):
        self.useCount = uses
        return self
    
    def SetUseCost(self, cost: int):
        self.useCost = cost
        return self


class Weapon(UseableItem, LevelableItem):
    tag = "WEAPON"
    DAMAGE_MULT_PER_LEVEL = 0.12

    def __init__(self):
        super().__init__()
        LevelableItem.__init__(self)

        self.baseDamage = 1

    def GetDesc(self):
        from colorama import Fore, Style
        return f"[{Fore.YELLOW}{Style.BRIGHT}{self.itemLevel}{Style.RESET_ALL}] " + super().GetDesc() + f" - Damage: {self.baseDamage}{f' + {self.CalculateAdditionalLevelDamage()}'}"

    def OnUse(self, target):
        target.Damage(self.GetDamage())
        super().OnUse(target)

    def SetDamage(self, damage: int):
        self.baseDamage = damage
        return self
    
    def GetDamage(self) -> int:
        return self.baseDamage + self.CalculateAdditionalLevelDamage()
    
    def CalculateAdditionalLevelDamage(self) -> int:
        return round(self.baseDamage * ((self.itemLevel - 1) * Weapon.DAMAGE_MULT_PER_LEVEL))
    
class VampireDagger(Weapon):
    def GetDesc(self):
        return super().GetDesc() + " - Heals for half damage dealt."

    def OnUse(self, target):
        gc.playerCharacter.Heal(self.GetDamage() // 2)
        super().OnUse(target)

class RapidfireWeapon(Weapon):
    def __init__(self):
        super().__init__()
        self.attackCount = 3

    def GetDesc(self):
        return super().GetDesc() + f" - Attacks {self.attackCount} times."
    
    def OnUse(self, target):
        import time
        for i in range(self.attackCount):
            super().OnUse(target)
            time.sleep(0.1)

    def SetAttackCount(self, count: int):
        self.attackCount = count
        return self

class HolyPotion(UseableItem):
    tag = "POTION"

    def GetDesc(self):
        return super().GetDesc() + " - Removes negative status effects and protects from future effects"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.BlessedEffect, 5)
        target.ClearStatusEffects(True)
        super().OnUse(target)
        return True


class HealthPotion(UseableItem):
    tag = "POTION"

    def __init__(self):
        super().__init__()
        self.healing = 0

    def GetDesc(self):
        return super().GetDesc() + " - Healing: " + str(self.healing)
    
    def Use(self, target):
        if (target.health >= target.maxHealth):
            print(f"{target.name} is already full health!")
            return False
        return super().Use(target)

    def OnUse(self, target):
        target.Heal(self.healing)
        super().OnUse(target)

    def SetHealing(self, healing: int):
        self.healing = healing
        return self
    
class EnergyPotion(UseableItem):
    tag = "POTION"

    def __init__(self):
        super().__init__()
        self.energy = 0

    def GetDesc(self):
        return super().GetDesc() + f" - Stamina Recovery: {self.energy}"

    def OnUse(self, target):
        gc.playerCharacter.stamina += self.energy
        if (gc.playerCharacter.stamina > gc.playerCharacter.maxStamina):
            print("You feel even more energized than normal!")
        super().OnUse(target)
    
    def SetEnergy(self, energy: int):
        self.energy = energy
        return self


itemsList = [
    # Weapons
    Weapon().SetName("Rusty Sword").SetRarity(100).SetUseCost(2).SetDamage(15),
    Weapon().SetName("Excalibur").SetRarity(1).SetUseCost(2).SetDamage(50),
    Weapon().SetName("Adventurers Sword").SetRarity(40).SetUseCost(2).SetDamage(25),
    Weapon().SetName("Mace").SetRarity(50).SetUseCost(3).SetDamage(40),
    Weapon().SetName("Dagger").SetRarity(45).SetUseCost(1).SetDamage(7),
    VampireDagger().SetName("Vampire Dagger").SetRarity(20).SetUseCost(1).SetDamage(10),
    Weapon().SetName("Poison Dagger").SetRarity(30).SetUseCost(1).SetDamage(8).SetEffectToApply(StatusEffect.PoisonEffect),
    RapidfireWeapon().SetName("Shank").SetRarity(46).SetUseCost(1).SetDamage(2).SetAttackCount(4).SetEffectToApply(StatusEffect.BleedEffect),

    # Potions
    HealthPotion().SetName("Lesser Health Potion").SetRarity(75).SetUseCost(1).SetUses(3).SetHealing(20),
    HealthPotion().SetName("Greater Health Potion").SetRarity(30).SetUseCost(1).SetUses(1).SetHealing(50),
    EnergyPotion().SetName("Energy Potion").SetRarity(35).SetUseCost(1).SetUses(2).SetEnergy(3),
    HolyPotion().SetName("Holy Potion").SetRarity(37).SetUseCost(1).SetUses(1),

    # Basic Items
    Item().SetName("Cloth Fragment").SetRarity(90),
    Item().SetName("Golden Chalice").SetRarity(4),
    Item().SetName("Silver Nugget").SetRarity(15),
    Item().SetName("Gravel Piece").SetRarity(96),
    Item().SetName("Wooden Log").SetRarity(92),
    Item().SetName("Silverware").SetRarity(35),
    Item().SetName("Random Jewel").SetRarity(12)
]