import GameCore as gc
import StatusEffect
import Relics

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

    def Use(self) -> bool:
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        if not self.CheckCanUse():
            return False
        
        gc.playerCharacter.stamina -= self.useCost
        print(f"Using {self.name}")
        
        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()

        self.OnUse()
        return True

    def CheckCanUse(self) -> bool:
        stamina = gc.playerCharacter.stamina
        if (stamina < self.useCost):
            print("Not enough stamina to use item! Need " + str(self.useCost) + " stamina, has " + str(stamina) + " stamina.")
            return False
        
        return True

    def OnUse(self):
        if (self.effectToApply != None):
            StatusEffect.Apply(gc.playerCharacter, self.effectToApply)
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


class TargetUseableItem(UseableItem):
    def Use(self, target) -> bool:
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        if not self.CheckCanUse():
            return False
        
        gc.playerCharacter.stamina -= self.useCost
        print("Using " + self.name + " on " + target.name)
        
        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()

        self.OnUse(target)
        return True

    def OnUse(self, target):
        if (self.effectToApply != None):
            StatusEffect.Apply(target, self.effectToApply)
        pass

class Weapon(TargetUseableItem, LevelableItem):
    tag = "WEAPON"
    DAMAGE_MULT_PER_LEVEL = 0.12

    def __init__(self):
        super().__init__()
        LevelableItem.__init__(self)
        self.baseDamage = 1

    def GetDesc(self):
        from colorama import Fore, Style
        return f"[{Fore.YELLOW}{Style.BRIGHT}{self.itemLevel}{Style.NORMAL}{Fore.RESET}] " + super().GetDesc() + f" - Damage: {self.GetDamage()}"

    def OnUse(self, target):
        # get critial hit chance
        import random
        from colorama import Fore, Style
        critChance = gc.playerCharacter.critialHitChance
        isCrit = random.random() < critChance
        if gc.playerHasAttackedThisTurn == False and gc.playerCharacter.HasRelic(Relics.OraclesWhisper):
            isCrit = True
        if isCrit:
            print(Fore.RED + Style.BRIGHT + "Critical Hit!" + Style.RESET_ALL)
            target.Damage(self.GetDamage() * 2)
            if (gc.playerCharacter.HasRelic(Relics.FangoftheRaven)):
                StatusEffect.Apply(target, StatusEffect.BleedEffect, 8)
        else:
            target.Damage(self.GetDamage())
        gc.playerHasAttackedThisTurn = True
        super().OnUse(target)

    def SetDamage(self, damage: int):
        self.baseDamage = damage
        return self
    
    def GetDamage(self) -> int:
        damage = self.baseDamage + self.CalculateAdditionalLevelDamage()
        if (not gc.playerHasAttackedLastTurn) and gc.playerCharacter.HasRelic(Relics.StonehoofTotem):
            damage = round(damage * 1.5)
        damage = round(damage * gc.playerCharacter.damageMultiplier)
        damage += gc.playerCharacter.additionalRawDamage
        return damage
    
    def CalculateAdditionalLevelDamage(self) -> int:
        return round(self.baseDamage * ((self.itemLevel - 1) * Weapon.DAMAGE_MULT_PER_LEVEL))
    
class LifestealWeapon(Weapon):
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

class ElementalWeapon(Weapon):
    """Weapons that deal elemental damage with secondary status effects."""
    def __init__(self):
        super().__init__()
        self.elementType = "fire"  # fire, ice, lightning, nature
        self.effectDuration = 3

    def GetDesc(self):
        return super().GetDesc() + f" - {self.elementType.capitalize()} Element."
    
    def OnUse(self, target):
        super().OnUse(target)
        # Status effects applied via SetEffectToApply

    def SetElement(self, elementType: str):
        self.elementType = elementType
        return self
    
    def SetEffectDuration(self, duration: int):
        self.effectDuration = duration
        return self

class SniperWeapon(Weapon):
    """High damage weapon with lower attack cost but single target focus."""
    def __init__(self):
        super().__init__()
        self.critDamageMultiplier = 2.5

    def GetDesc(self):
        return super().GetDesc() + " - High precision, increased crit damage."
    
    def OnUse(self, target):
        super().OnUse(target)

    def SetCritDamageMultiplier(self, mult: float):
        self.critDamageMultiplier = mult
        return self

class DefensiveWeapon(Weapon):
    """Weapons that provide defensive benefits alongside damage."""
    def __init__(self):
        super().__init__()
        self.damageReduction = 0  # percentage reduction
        self.blockChance = 0  # chance to block incoming damage

    def GetDesc(self):
        defensiveText = f" - Defense: {self.damageReduction}% reduction"
        if self.blockChance > 0:
            defensiveText += f", {int(self.blockChance*100)}% block chance"
        return super().GetDesc() + defensiveText
    
    def OnUse(self, target):
        super().OnUse(target)

    def SetDamageReduction(self, reduction: int):
        self.damageReduction = reduction
        return self
    
    def SetBlockChance(self, chance: float):
        self.blockChance = chance
        return self
    
class Potion(TargetUseableItem):
    tag = "POTION"

class HolyPotion(Potion):
    def GetDesc(self):
        return super().GetDesc() + " - Removes negative status effects and protects from future effects"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.BlessedEffect, 5)
        target.ClearStatusEffects(True)
        super().OnUse(target)
        return True


class HealthPotion(Potion):
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
    
class EnergyPotion(Potion):
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
    
class RegenerationPotion(Potion):
    def __init__(self):
        super().__init__()
        self.duration = 0

    def GetDesc(self):
        return super().GetDesc() + f" - Heals per turn for {self.duration} turns."

    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.RegenerationEffect, self.duration)
        super().OnUse(target)

    def SetDuration(self, duration: int):
        self.duration = duration
        return self
    
class SmokeBomb(UseableItem):
    def GetDesc(self):
        return super().GetDesc() + f" - Escapes combat"
    
    def Use(self) -> bool:
        import Commands
        if (not Commands.PromptYesNoQuestion("Are you sure you want to escape combat? (You recieve no rewards!)", False)):
            return False
        return super().Use()
    
    def OnUse(self):
        # clear enemies from scene
        for enemy in reversed(gc.enemiesInScene):
            gc.RemoveEnemyFromScene(enemy, False)
        gc.CheckEncounterStatus(False)

        return super().OnUse()
    
class Antidote(Potion):
    def Use(self, target) -> bool:
        if (not target.HasEffect(StatusEffect.PoisonEffect)):
            print(f"{target.name} does not have any poison effect!")
            return False
        return super().Use(target)

    def OnUse(self, target):
        target.RemoveEffect(StatusEffect.PoisonEffect)
        return super().OnUse(target)

class RegenerationExtendPotion(Potion):
    """Extends existing regeneration or applies new regeneration."""
    def __init__(self):
        super().__init__()
        self.duration = 5

    def GetDesc(self):
        return super().GetDesc() + f" - Grants regeneration for {self.duration} turns"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.RegenerationEffect, self.duration)
        super().OnUse(target)

    def SetDuration(self, duration: int):
        self.duration = duration
        return self

class PoisonApplyPotion(Potion):
    """Offensive potion that poisons enemies."""
    def __init__(self):
        super().__init__()
        self.potency = 2

    def GetDesc(self):
        return super().GetDesc() + f" - Poisons target with strength {self.potency}"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.PoisonEffect, self.potency)
        super().OnUse(target)

    def SetPotency(self, potency: int):
        self.potency = potency
        return self

class BleedApplyPotion(Potion):
    """Offensive potion that causes bleeding."""
    def __init__(self):
        super().__init__()
        self.severity = 3

    def GetDesc(self):
        return super().GetDesc() + f" - Inflicts bleeding on target"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.BleedEffect, self.severity)
        super().OnUse(target)

    def SetSeverity(self, severity: int):
        self.severity = severity
        return self

class SlowingPotion(Potion):
    """Slows the target by applying the bogged effect."""
    def __init__(self):
        super().__init__()
        self.duration = 4

    def GetDesc(self):
        return super().GetDesc() + f" - Slows target for {self.duration} turns"
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.BoggedEffect, self.duration)
        super().OnUse(target)

    def SetDuration(self, duration: int):
        self.duration = duration
        return self

itemsList = [
    # === BASIC WEAPONS ===
    Weapon().SetName("Rusty Sword").SetRarity(95).SetUseCost(2).SetDamage(15),
    Weapon().SetName("Wooden Club").SetRarity(92).SetUseCost(2).SetDamage(12),
    Weapon().SetName("Iron Dagger").SetRarity(80).SetUseCost(1).SetDamage(8),
    Weapon().SetName("Steel Sword").SetRarity(75).SetUseCost(2).SetDamage(22),
    
    # === INTERMEDIATE WEAPONS ===
    Weapon().SetName("Adventurer's Sword").SetRarity(60).SetUseCost(2).SetDamage(28),
    Weapon().SetName("Iron Longsword").SetRarity(55).SetUseCost(2).SetDamage(25),
    Weapon().SetName("Mace").SetRarity(50).SetUseCost(3).SetDamage(42),
    Weapon().SetName("Battle Axe").SetRarity(45).SetUseCost(3).SetDamage(48),
    Weapon().SetName("Dagger").SetRarity(65).SetUseCost(1).SetDamage(9),
    
    # === SPECIAL EFFECT WEAPONS ===
    LifestealWeapon().SetName("Vampire Dagger").SetRarity(20).SetUseCost(1).SetDamage(12),
    Weapon().SetName("Poison Dagger").SetRarity(35).SetUseCost(1).SetDamage(10).SetEffectToApply(StatusEffect.PoisonEffect),
    Weapon().SetName("Venom Fang").SetRarity(18).SetUseCost(1).SetDamage(14).SetEffectToApply(StatusEffect.PoisonEffect),
    Weapon().SetName("Infected Blade").SetRarity(25).SetUseCost(2).SetDamage(18).SetEffectToApply(StatusEffect.BleedEffect),
    RapidfireWeapon().SetName("Shank").SetRarity(48).SetUseCost(1).SetDamage(3).SetAttackCount(4).SetEffectToApply(StatusEffect.BleedEffect),
    
    # === RAPIDFIRE WEAPONS ===
    RapidfireWeapon().SetName("Throwing Knives").SetRarity(40).SetUseCost(1).SetDamage(4).SetAttackCount(3),
    RapidfireWeapon().SetName("Twin Hatchets").SetRarity(22).SetUseCost(2).SetDamage(16).SetAttackCount(2),
    RapidfireWeapon().SetName("Hunter's Bow").SetRarity(28).SetUseCost(2).SetDamage(20).SetAttackCount(2),
    RapidfireWeapon().SetName("Bladed Whip").SetRarity(15).SetUseCost(2).SetDamage(12).SetAttackCount(3),
    
    # === LIFESTEAL WEAPONS ===
    LifestealWeapon().SetName("Crimson Fang").SetRarity(8).SetUseCost(1).SetDamage(18),
    LifestealWeapon().SetName("Bloodletter").SetRarity(12).SetUseCost(2).SetDamage(26),
    LifestealWeapon().SetName("Ghoul's Cleaver").SetRarity(5).SetUseCost(3).SetDamage(35),
    
    # === LEGENDARY & RARE WEAPONS ===
    Weapon().SetName("Excalibur").SetRarity(1).SetUseCost(2).SetDamage(65),
    Weapon().SetName("Warhammer").SetRarity(6).SetUseCost(4).SetDamage(62),
    Weapon().SetName("Dragon Slayer").SetRarity(2).SetUseCost(3).SetDamage(58),
    Weapon().SetName("Cursed Blade").SetRarity(4).SetUseCost(2).SetDamage(55).SetEffectToApply(StatusEffect.BleedEffect),
    
    # === ELEMENTAL WEAPONS ===
    ElementalWeapon().SetName("Flame Sword").SetRarity(14).SetUseCost(2).SetDamage(30).SetElement("fire"),
    ElementalWeapon().SetName("Frost Lance").SetRarity(11).SetUseCost(2).SetDamage(28).SetElement("ice"),
    ElementalWeapon().SetName("Lightning Axe").SetRarity(9).SetUseCost(3).SetDamage(40).SetElement("lightning"),
    ElementalWeapon().SetName("Nature's Bow").SetRarity(13).SetUseCost(2).SetDamage(22).SetElement("nature"),
    
    # === SNIPER WEAPONS ===
    SniperWeapon().SetName("Precision Rifle").SetRarity(16).SetUseCost(2).SetDamage(44),
    SniperWeapon().SetName("Sharpshooter's Gun").SetRarity(10).SetUseCost(2).SetDamage(52),
    SniperWeapon().SetName("Sniper Bow").SetRarity(7).SetUseCost(2).SetDamage(48).SetCritDamageMultiplier(3.0),
    
    # === DEFENSIVE WEAPONS ===
    DefensiveWeapon().SetName("Shield Sword").SetRarity(20).SetUseCost(2).SetDamage(20).SetDamageReduction(15),
    DefensiveWeapon().SetName("Defender's Mace").SetRarity(18).SetUseCost(3).SetDamage(38).SetDamageReduction(20).SetBlockChance(0.2),
    DefensiveWeapon().SetName("Sentinel's Blade").SetRarity(12).SetUseCost(2).SetDamage(24).SetDamageReduction(25).SetBlockChance(0.15),

    # === BASIC POTIONS ===
    HealthPotion().SetName("Lesser Health Potion").SetRarity(85).SetUseCost(1).SetUses(3).SetHealing(15),
    HealthPotion().SetName("Health Potion").SetRarity(70).SetUseCost(1).SetUses(2).SetHealing(30),
    HealthPotion().SetName("Greater Health Potion").SetRarity(40).SetUseCost(1).SetUses(1).SetHealing(50),
    HealthPotion().SetName("Superior Health Potion").SetRarity(22).SetUseCost(1).SetUses(1).SetHealing(75),
    HealthPotion().SetName("Legendary Health Potion").SetRarity(5).SetUseCost(1).SetUses(1).SetHealing(120),
    
    # === ENERGY POTIONS ===
    EnergyPotion().SetName("Energy Potion").SetRarity(50).SetUseCost(1).SetUses(2).SetEnergy(2),
    EnergyPotion().SetName("Greater Energy Potion").SetRarity(28).SetUseCost(1).SetUses(1).SetEnergy(5),
    EnergyPotion().SetName("Superior Energy Potion").SetRarity(12).SetUseCost(1).SetUses(1).SetEnergy(8),
    
    # === REGENERATION POTIONS ===
    RegenerationPotion().SetName("Regeneration Potion").SetRarity(65).SetUseCost(1).SetUses(1).SetDuration(5),
    RegenerationExtendPotion().SetName("Extended Regeneration").SetRarity(35).SetUseCost(1).SetUses(1).SetDuration(8),
    RegenerationExtendPotion().SetName("Superior Regeneration").SetRarity(18).SetUseCost(1).SetUses(1).SetDuration(10),
    
    # === UTILITY POTIONS ===
    HolyPotion().SetName("Holy Potion").SetRarity(32).SetUseCost(1).SetUses(1),
    HolyPotion().SetName("Divine Protection").SetRarity(16).SetUseCost(1).SetUses(1),
    Antidote().SetName("Antidote").SetRarity(45).SetUseCost(1).SetUses(2),
    Antidote().SetName("Superior Antidote").SetRarity(25).SetUseCost(1).SetUses(1),
    SmokeBomb().SetName("Smoke Bomb").SetRarity(28).SetUseCost(1).SetUses(1),
    SmokeBomb().SetName("Smoke Pellet").SetRarity(38).SetUseCost(1).SetUses(2),
    
    # === OFFENSIVE POTIONS ===
    PoisonApplyPotion().SetName("Poison Vial").SetRarity(35).SetUseCost(1).SetUses(2).SetPotency(2),
    PoisonApplyPotion().SetName("Toxic Serum").SetRarity(18).SetUseCost(1).SetUses(1).SetPotency(4),
    BleedApplyPotion().SetName("Bloodletting Vial").SetRarity(30).SetUseCost(1).SetUses(2).SetSeverity(2),
    BleedApplyPotion().SetName("Hemorrhage Potion").SetRarity(14).SetUseCost(1).SetUses(1).SetSeverity(5),
    
    # === DEBUFF POTIONS ===
    SlowingPotion().SetName("Slowing Potion").SetRarity(40).SetUseCost(1).SetUses(2).SetDuration(3),
    SlowingPotion().SetName("Paralysis Potion").SetRarity(20).SetUseCost(1).SetUses(1).SetDuration(5),

    # === BASIC ITEMS ===
    Item().SetName("Cloth Fragment").SetRarity(96),
    Item().SetName("Wooden Log").SetRarity(94),
    Item().SetName("Gravel Piece").SetRarity(97),
    Item().SetName("Rusty Metal").SetRarity(88),
    Item().SetName("Tattered Banner").SetRarity(85),
    
    # === COMMON CRAFTING MATERIALS ===
    Item().SetName("Iron Chunk").SetRarity(75),
    Item().SetName("Fur Pelt").SetRarity(70),
    Item().SetName("Wooden Plank").SetRarity(68),
    Item().SetName("Plant Fiber").SetRarity(72),
    Item().SetName("Bone Fragment").SetRarity(65),
    
    # === UNCOMMON MATERIALS ===
    Item().SetName("Silver Nugget").SetRarity(45),
    Item().SetName("Copper Ingot").SetRarity(50),
    Item().SetName("Crystal Shard").SetRarity(38),
    Item().SetName("Leather Strip").SetRarity(48),
    Item().SetName("Enchanted Dust").SetRarity(32),
    
    # === RARE MATERIALS ===
    Item().SetName("Gold Ore").SetRarity(18),
    Item().SetName("Ancient Scroll").SetRarity(22),
    Item().SetName("Mithril Fragment").SetRarity(12),
    Item().SetName("Phoenix Feather").SetRarity(8),
    Item().SetName("Moonstone").SetRarity(15),
    
    # === VALUABLE TREASURES ===
    Item().SetName("Silverware").SetRarity(50),
    Item().SetName("Golden Chalice").SetRarity(6),
    Item().SetName("Random Jewel").SetRarity(25),
    Item().SetName("Ancient Coin").SetRarity(14),
    Item().SetName("Rare Gemstone").SetRarity(4),
    Item().SetName("Obsidian Shard").SetRarity(20),
    Item().SetName("Diamond").SetRarity(2),
    Item().SetName("Crown of Kings").SetRarity(1),
]
