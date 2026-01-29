import GameCore as gc
from abc import ABC
import StatusEffect
import Relics
from ElementTags import ElementTag
from Entity import AEntity

class AItem(ABC):
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
    
class JunkItem(AItem):
    tag = "JUNK"

class TreasureItem(AItem):
    tag = "USEFUL"

class ToolItem(AItem):
    tag = "TOOL"

class LevelableItem():
    def __init__(self):
        self.itemLevel = 1
        self.maxLevel = 10

    def Upgrade(self, amount: int = 1):
        self.itemLevel = min(self.itemLevel + amount, self.maxLevel)

    def CanUpgrade(self) -> bool:
        return self.itemLevel < self.maxLevel

    def SetMaxLevel(self, max: int):
        self.maxLevel = max
        return self
    
class UseableItem(AItem):
    def __init__(self):
        super().__init__()
        self._useCost = 1
        self.useCount = -1
        self.effectToApply: None | type = None
        self.effectStacks = 1

    def GetDesc(self):
        return super().GetDesc() + " - COST: " + str(self.useCost)

    def Use(self) -> bool:
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        if not self.CheckCanUse():
            return False
        
        self.ConsumeStamina()
        print(f"Using {self.name}")
        
        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()

        self.OnUse()
        return True

    def ConsumeStamina(self):
        gc.playerCharacter.stamina = max(gc.playerCharacter.stamina - self.useCost, 0)

    def CheckCanUse(self) -> bool:
        stamina = gc.playerCharacter.stamina
        if (stamina < self.useCost):
            print("Not enough stamina to use item! Need " + str(self.useCost) + " stamina, has " + str(stamina) + " stamina.")
            return False
        
        return True

    def OnUse(self):
        if (self.effectToApply != None):
            StatusEffect.Apply(gc.playerCharacter, self.effectToApply, self.effectStacks)
        pass

    def SetEffectToApply(self, effectType: type, stacks: int = 1):
        if not issubclass(effectType, StatusEffect.AEffect):
            return self
        
        self.effectToApply = effectType
        self.effectStacks = stacks
        return self

    def RemoveSelfFromInventory(self):
        if (self in gc.playerCharacter.items):
            gc.playerCharacter.items.remove(self)

    def SetUses(self, uses: int):
        self.useCount = uses
        return self
    
    def SetUseCost(self, cost: int):
        self._useCost = cost
        return self
    
    def get_useCost(self) -> int:
        return self._useCost
    
    useCost = property(get_useCost, SetUseCost)

class ShieldItem(UseableItem):
    tag = "SHIELD"
    def __init__(self):
        self.shieldAmount = 0
        super().__init__()

    def OnUse(self):
        from colorama import Fore, Style
        import random
        from AttackInfo import AttInfo
        shieldGain = self.CalculateShieldGain()
        gc.playerCharacter.AddShield(shieldGain)
        print(f"{Fore.MAGENTA}You brace your self using your {Style.BRIGHT}{self.name}{Style.NORMAL} gaining {Style.BRIGHT}{Fore.CYAN}{shieldGain}{Style.NORMAL}{Fore.MAGENTA} shield.{Fore.RESET}")
        if gc.playerCharacter.HasRelic(Relics.BulwarkGuidebook):
            random.choice(gc.enemiesInScene).Damage(AttInfo(shieldGain, gc.playerCharacter))
        return super().OnUse()
    
    def SetShield(self, amount: int):
        self.shieldAmount = amount
        return self
    
    def GetDesc(self):
        return super().GetDesc() + f" - SHIELD: {self.CalculateShieldGain()}"
    
    def CalculateShieldGain(self):
        bulwarkGuidebookBonus = self.shieldAmount * gc.playerCharacter.GetRelicCount(Relics.BulwarkGuidebook) * Relics.BulwarkGuidebook.SHIELD_ITEM_BONUS
        return self.shieldAmount + bulwarkGuidebookBonus


class TargetUseableItem(UseableItem):
    def Use(self, target: AEntity) -> bool:
        if (self.useCount == 0):
            self.RemoveSelfFromInventory()
            return False
        
        if not self.CheckCanUse():
            return False
        
        self.ConsumeStamina()
        print("Using " + self.name + " on " + target.name)
        
        if (self.useCount > 0):
            self.useCount -= 1
            if (self.useCount == 0):
                self.RemoveSelfFromInventory()

        self.OnUse(target)
        return True

    def OnUse(self, target: AEntity):
        if (self.effectToApply != None):
            import StatusEffect
            StatusEffect.Apply(target, self.effectToApply, self.effectStacks)
        pass

class Weapon(TargetUseableItem, LevelableItem):
    tag = "WEAPON"
    DAMAGE_MULT_PER_LEVEL = 0.12

    def __init__(self):
        super().__init__()
        LevelableItem.__init__(self)
        self.baseDamage = 1
        self.critChance = 0.0
        self.critDamageMult = 1.0
        self.elementType: ElementTag | None = None

    def GetDesc(self):
        from colorama import Fore, Style
        from RomanNumerals import IntToRoman
        elementText = f"[{Fore.RESET}{Style.NORMAL}{self.elementType.value}{self.elementType.name}{Fore.RESET}{Style.NORMAL}] " if self.elementType is not None else ""
        effectText = str()
        if self.effectToApply is not None:
            try:
                tempEffect = self.effectToApply(self, self.effectStacks)
                effectText = f" - Applies: {tempEffect.GetName()}"
            except Exception:
                effectText = f" - Applies: {self.effectToApply.__name__}"
        
        return f"[{Fore.YELLOW}{Style.BRIGHT}{IntToRoman(self.itemLevel)}{Style.NORMAL}{Fore.RESET}] {elementText}" + super().GetDesc() + f" - Damage: {self.GetDamage()}{effectText}"

    def OnUse(self, target: AEntity):
        from AttackInfo import AttInfo
        import random
        from colorama import Fore, Style
        import SkillSystem
        super().OnUse(target)

        # skills
        uncheckedViolenceRank = SkillSystem.GetSkillNodeRank("sknd_uncheckedviolence")
        if uncheckedViolenceRank > 0:
            gc.playerCharacter.Damage(AttInfo(3, None, True))

        seepingWoundRank = SkillSystem.GetSkillNodeRank("sknd_seepingwound")
        if seepingWoundRank > 0 and random.random() < SkillSystem.CARRION_SEEPING_WOUND_CHANCE * seepingWoundRank:
            StatusEffect.Apply(target, StatusEffect.InfectionEffect, 1)
        #

        totalCritChance = gc.playerCharacter.critialHitChance + self.critChance
        isCrit = random.random() < totalCritChance
        if gc.playerHasAttackedThisTurn == False and gc.playerCharacter.HasRelic(Relics.OraclesWhisper) and gc.isFirstTurn:
            isCrit = True
        gc.playerHasAttackedThisTurn = True
        attackInfo = AttInfo(self.GetDamage(), gc.playerCharacter)

        if self.elementType is not None:
            attackInfo.AddElements(self.elementType)

        if isCrit:
            print(Fore.RED + Style.BRIGHT + "Critical Hit!" + Style.RESET_ALL)
            attackInfo.damage = round(attackInfo.damage * (gc.playerCharacter.criticalHitMultiplier * self.critDamageMult))
            if (gc.playerCharacter.HasRelic(Relics.FangoftheRaven)):
                StatusEffect.Apply(target, StatusEffect.BleedEffect, Relics.FangoftheRaven.BLEED_AMOUNT)

            veinRendRank = SkillSystem.GetSkillNodeRank("sknd_veinrend")
            if veinRendRank > 0:
                StatusEffect.Apply(target, StatusEffect.BleedEffect, SkillSystem.VAMPIRIC_VEIN_REND_BLEED_STACKS * veinRendRank)
                for enemy in gc.enemiesInScene:
                    effect = enemy.GetEffect(StatusEffect.BleedEffect)
                    if effect is not None:
                        effect.OnEffectTick()
        
        if gc.playerCharacter.HasRelic(Relics.RendingClaw) and random.random() < gc.playerCharacter.applyBleedChance:
            StatusEffect.Apply(target, StatusEffect.BleedEffect, 1)

        if gc.playerCharacter.HasRelic(Relics.MalformedTenticle):
            random.choice(gc.enemiesInScene).Damage(AttInfo(5, None, True))

        self.DealDamage(attackInfo, target)
        bloodOiledChainCount = gc.playerCharacter.GetRelicCount(Relics.BloodOiledChain)
        if bloodOiledChainCount > 0:
            Relics.bloodOiledChainBonusDamagePerAttack += Relics.BloodOiledChain.BONUS_DAMAGE * bloodOiledChainCount

        if gc.playerCharacter.HasRelic(Relics.ThunderousHeart) and random.random() < Relics.ThunderousHeart.CHANCE_TO_STUN:
            target.ApplyStun(1)

        if gc.playerCharacter.HasRelic(Relics.GlitteringAmulet) and random.random() < Relics.GlitteringAmulet.CHANCE_TO_APPLY_DEBUFF:
            StatusEffect.Apply(target, StatusEffect.GetRandomEffect(negative=True, positive=False), 1)

    def DealDamage(self, attackInfo, target: AEntity) -> int:
        return target.Damage(attackInfo)
        
    def CheckCanUse(self) -> bool:
        return super().CheckCanUse() or gc.playerCharacter.bonusAttacks > 0
    
    def ConsumeStamina(self):
        if gc.playerCharacter.bonusAttacks > 0:
            gc.playerCharacter.bonusAttacks -= 1
            return
        super().ConsumeStamina()

    def SetDamage(self, damage: int):
        self.baseDamage = damage
        return self
    
    def GetDamage(self) -> int:
        damage = self.baseDamage + self.CalculateAdditionalLevelDamage()
        if (not gc.playerHasAttackedLastTurn) and gc.playerCharacter.HasRelic(Relics.StonehoofTotem):
            damage = round(damage * (1 + Relics.StonehoofTotem.DAMAGE_MULT_WHEN_NOT_ATTACK))
        damage = round(damage * gc.playerCharacter.outgoingDamageMultiplier)
        damage += gc.playerCharacter.additionalRawDamage
        return damage
    
    def CalculateAdditionalLevelDamage(self) -> int:
        return round(self.baseDamage * ((self.itemLevel - 1) * Weapon.DAMAGE_MULT_PER_LEVEL))
    
    def SetElement(self, elementType: ElementTag):
        self.elementType = elementType
        return self
    
    def get_useCost(self) -> int:
        import SkillSystem
        cost = super().get_useCost()
        uncheckedViolenceRank = SkillSystem.GetSkillNodeRank("sknd_uncheckedviolence")
        if uncheckedViolenceRank > 0:
            cost = max(1, cost - 1)

        return cost
    
    def set_useCost(self, cost: int) -> None:
        self._useCost = cost
    
    useCost = property(get_useCost, set_useCost)
    
class NoTargetWeapon(Weapon):
    def GetTarget(self) -> AEntity:
        import random
        return gc.enemiesInScene[random.randrange(0, len(gc.enemiesInScene))]
    
class SporecloudWeapon(UseableItem):
    def OnUse(self):
        from colorama import Fore, Style
        print(f"{Fore.GREEN}{Style.DIM}You spread poisonous spores throughout the area!{Style.RESET_ALL}")
        for enemy in gc.enemiesInScene:
            StatusEffect.Apply(enemy, StatusEffect.PoisonEffect, 8)
        return super().OnUse()
    
class LifestealWeapon(Weapon):
    def GetDesc(self):
        return super().GetDesc() + " - Heals for half damage dealt."

    def DealDamage(self, attackInfo, target: AEntity) -> int:
        result = super().DealDamage(attackInfo, target)
        gc.playerCharacter.Heal(result // 2)
        return result

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

class SniperWeapon(Weapon):
    """High damage weapon with lower attack cost but single target focus."""
    def __init__(self):
        super().__init__()
        self.critDamageMult = 2.5

    def GetDesc(self):
        return super().GetDesc() + " - High precision, increased crit damage."
    
    def OnUse(self, target):
        super().OnUse(target)

    def SetCritDamageMultiplier(self, mult: float):
        self.critDamageMult = mult
        return self
    
class BlightneedleWeapon(Weapon):
    SHIELD_ON_HIT = 2
    def GetDesc(self):
        return super().GetDesc() + f" - Gain {BlightneedleWeapon.SHIELD_ON_HIT} shield when attacking enemies inflicted with Rot."
    
    def OnUse(self, target):
        if target.HasEffect(StatusEffect.RotEffect):
            gc.playerCharacter.shield += BlightneedleWeapon.SHIELD_ON_HIT

        super().OnUse(target)

class RotfeederWeapon(Weapon):
    ROT_ON_HIT_STACKS = 1
    HEALTH_ON_HIT = 1
    def GetDesc(self):
        return super().GetDesc() + f" - Applies {RotfeederWeapon.ROT_ON_HIT_STACKS} stacks of Rot, and heals {RotfeederWeapon.HEALTH_ON_HIT} HP on hit when target is inflicted with rot."
    
    def OnUse(self, target):
        if target.HasEffect(StatusEffect.RotEffect):
            gc.playerCharacter.Heal(RotfeederWeapon.HEALTH_ON_HIT)
        StatusEffect.Apply(target, StatusEffect.RotEffect, RotfeederWeapon.ROT_ON_HIT_STACKS)
        super().OnUse(target)

class MaggotSalve(TargetUseableItem):
    PER_ROT_STACK = 3
    def GetDesc(self):
        return super().GetDesc() + f" - If you're under Rot, heal {MaggotSalve.PER_ROT_STACK} HP per Rot stack or into bleed on an enemy."
    
    def Use(self, target) -> bool:
        if (not target.HasEffect(StatusEffect.RotEffect)):
            print(f"{target.name} does not have any rot effect!")
            return False
        return super().Use(target)

    def OnUse(self, target):
        if target is gc.playerCharacter:
            target.Heal(target.GetEffectStacks(StatusEffect.RotEffect) * MaggotSalve.PER_ROT_STACK)
        else:
            StatusEffect.Apply(target, StatusEffect.BleedEffect, target.GetEffectStacks(StatusEffect.RotEffect))
        return super().OnUse(target)
    
class Potion(TargetUseableItem):
    tag = "POTION"

class HolyPotion(Potion):
    def GetDesc(self):
        return super().GetDesc() + f" - Removes negative status effects and protects from future effects for {self.effectStacks} turns."
    
    def OnUse(self, target):
        import StatusEffect
        StatusEffect.Apply(target, StatusEffect.BlessedEffect, self.effectStacks)
        target.ClearStatusEffects(True)
        super().OnUse(target)
        return True
    
    def SetDuration(self, stacks: int):
        self.effectStacks = stacks
        return self


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
            gc.RemoveEnemyFromScene(enemy)
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
    
class Bandage(Potion):
    def __init__(self):
        super().__init__()
        self.bleedCureAmount = 1

    def Use(self, target) -> bool:
        if (not target.HasEffect(StatusEffect.BleedEffect)):
            print(f"{target.name} does not have any bleed!")
            return False
        return super().Use(target)

    def OnUse(self, target):
        target.RemoveEffectStack(StatusEffect.BleedEffect, 3)
        return super().OnUse(target)
    
    def SetBleedCure(self, amount: int):
        self.bleedCureAmount = amount
        return self
    
    def GetDesc(self):
        return super().GetDesc() + f" - Removes {self.bleedCureAmount} bleed."

class EffectPotion(Potion):
    def __init__(self, effect_type: type | None = None, stacks: int = 1):
        super().__init__()
        # list of (effectType, stacks)
        self.effects: list[tuple[type, int]] = []
        if effect_type is not None:
            self.effects.append((effect_type, stacks))

    def SetEffect(self, effect_type: type, stacks: int = 1):
        self.effects = [(effect_type, stacks)]
        return self

    def AddEffect(self, effect_type: type, stacks: int = 1):
        self.effects.append((effect_type, stacks))
        return self

    def SetStacks(self, stacks: int):
        # overwrite stacks for the first effect if present
        if len(self.effects) > 0:
            eff, _ = self.effects[0]
            self.effects[0] = (eff, stacks)
        return self

    def GetDesc(self):
        if len(self.effects) == 0:
            return super().GetDesc()
        import StatusEffect
        effects = []
        for effectType, stacks in self.effects:
            try:
                tempEffect = effectType(self, stacks)
                effects.append(f"{tempEffect.stacks} {tempEffect.GetName()}")
            except Exception:
                effects.append(effectType.__name__)
        return super().GetDesc() + " - Applies: " + ", ".join(effects)

    def OnUse(self, target):
        import StatusEffect
        for eff, stacks in self.effects:
            StatusEffect.Apply(target, eff, stacks)
        super().OnUse(target)

itemsList = [
    # === BASIC WEAPONS ===
    Weapon().SetName("Rusty Sword").SetRarity(95).SetUseCost(2).SetDamage(15),
    Weapon().SetName("Wooden Club").SetRarity(92).SetUseCost(2).SetDamage(16),
    Weapon().SetName("Iron Dagger").SetRarity(80).SetUseCost(1).SetDamage(8),
    Weapon().SetName("Steel Sword").SetRarity(75).SetUseCost(2).SetDamage(22),
    Weapon().SetName("Torch").SetRarity(80).SetUseCost(1).SetDamage(5).SetElement(ElementTag.FIRE),
    
    # === INTERMEDIATE WEAPONS ===
    Weapon().SetName("Adventurer's Sword").SetRarity(60).SetUseCost(2).SetDamage(25),
    Weapon().SetName("Iron Longsword").SetRarity(55).SetUseCost(2).SetDamage(28),
    Weapon().SetName("Mace").SetRarity(50).SetUseCost(3).SetDamage(42),
    Weapon().SetName("Battle Axe").SetRarity(45).SetUseCost(3).SetDamage(48),
    Weapon().SetName("Dagger").SetRarity(65).SetUseCost(1).SetDamage(9),
    
    # === SPECIAL EFFECT WEAPONS ===
    LifestealWeapon().SetName("Vampire Dagger").SetRarity(20).SetUseCost(1).SetDamage(12),
    Weapon().SetName("Poison Dagger").SetRarity(35).SetUseCost(1).SetDamage(10).SetEffectToApply(StatusEffect.PoisonEffect),
    Weapon().SetName("Venom Fang").SetRarity(18).SetUseCost(1).SetDamage(14).SetEffectToApply(StatusEffect.PoisonEffect, 2),
    Weapon().SetName("Serrated Blade").SetRarity(25).SetUseCost(2).SetDamage(18).SetEffectToApply(StatusEffect.BleedEffect),
    RapidfireWeapon().SetName("Shank").SetRarity(48).SetUseCost(1).SetDamage(3).SetAttackCount(4).SetEffectToApply(StatusEffect.BleedEffect),
    
    # === RAPIDFIRE WEAPONS ===
    RapidfireWeapon().SetName("Throwing Knives").SetRarity(40).SetUseCost(1).SetDamage(4).SetAttackCount(3),
    RapidfireWeapon().SetName("Twin Hatchets").SetRarity(12).SetUseCost(2).SetDamage(16).SetAttackCount(2),
    RapidfireWeapon().SetName("Hunter's Bow").SetRarity(16).SetUseCost(2).SetDamage(12).SetAttackCount(2),
    RapidfireWeapon().SetName("Bladed Whip").SetRarity(10).SetUseCost(2).SetDamage(12).SetAttackCount(3),
    
    # === LIFESTEAL WEAPONS ===
    LifestealWeapon().SetName("Crimson Fang").SetRarity(8).SetUseCost(1).SetDamage(18),
    LifestealWeapon().SetName("Bloodletter").SetRarity(12).SetUseCost(2).SetDamage(26),
    LifestealWeapon().SetName("Ghoul's Cleaver").SetRarity(5).SetUseCost(3).SetDamage(35),

    # === ROT WEAPONS ===
    BlightneedleWeapon().SetName("Blightneedle Dagger").SetRarity(15).SetUseCost(1).SetDamage(15),
    RotfeederWeapon().SetName("Rotfeeder Blade").SetRarity(20).SetUseCost(2).SetDamage(22),
    MaggotSalve().SetName("Maggot Salve").SetRarity(30).SetUseCost(1).SetUses(2),
    
    # === LEGENDARY & RARE WEAPONS ===
    Weapon().SetName("Excalibur").SetRarity(1).SetUseCost(2).SetDamage(65),
    Weapon().SetName("Warhammer").SetRarity(6).SetUseCost(4).SetDamage(62),
    Weapon().SetName("Dragon Slayer").SetRarity(2).SetUseCost(3).SetDamage(58),
    Weapon().SetName("Cursed Blade").SetRarity(4).SetUseCost(2).SetDamage(55).SetEffectToApply(StatusEffect.BleedEffect, 5),
    
    # === ELEMENTAL WEAPONS ===
    Weapon().SetName("Flame Sword").SetRarity(14).SetUseCost(2).SetDamage(30).SetElement(ElementTag.FIRE),
    Weapon().SetName("Frost Lance").SetRarity(11).SetUseCost(2).SetDamage(28).SetElement(ElementTag.WATER),
    Weapon().SetName("Lightning Axe").SetRarity(9).SetUseCost(3).SetDamage(40).SetElement(ElementTag.LIGHTNING),
    
    # === SNIPER WEAPONS ===
    SniperWeapon().SetName("Sniper Bow").SetRarity(7).SetUseCost(2).SetDamage(48).SetCritDamageMultiplier(1.5),

    # === BASIC POTIONS ===
    HealthPotion().SetName("Lesser Health Potion").SetRarity(85).SetUseCost(1).SetUses(3).SetHealing(15),
    HealthPotion().SetName("Health Potion").SetRarity(70).SetUseCost(1).SetUses(2).SetHealing(30),
    HealthPotion().SetName("Greater Health Potion").SetRarity(40).SetUseCost(1).SetUses(1).SetHealing(50),
    HealthPotion().SetName("Superior Health Potion").SetRarity(22).SetUseCost(1).SetUses(1).SetHealing(75),
    HealthPotion().SetName("Legendary Health Potion").SetRarity(5).SetUseCost(1).SetUses(1).SetHealing(120),
    
    # === ENERGY POTIONS ===
    EnergyPotion().SetName("Energy Potion").SetRarity(50).SetUseCost(1).SetUses(2).SetEnergy(3),
    EnergyPotion().SetName("Greater Energy Potion").SetRarity(28).SetUseCost(1).SetUses(1).SetEnergy(5),
    EnergyPotion().SetName("Superior Energy Potion").SetRarity(12).SetUseCost(1).SetUses(1).SetEnergy(8),
    
    # === REGENERATION POTIONS ===
    RegenerationPotion().SetName("Regeneration Potion").SetRarity(65).SetUseCost(1).SetUses(1).SetDuration(5),
    RegenerationPotion().SetName("Extended Regeneration Potion").SetRarity(35).SetUseCost(1).SetUses(1).SetDuration(8),
    RegenerationPotion().SetName("Superior Regeneration Potion").SetRarity(18).SetUseCost(1).SetUses(1).SetDuration(10),
    
    # === UTILITY POTIONS ===
    HolyPotion().SetName("Holy Potion").SetRarity(32).SetUseCost(1).SetUses(1).SetDuration(5),
    HolyPotion().SetName("Divine Protection Potion").SetRarity(16).SetUseCost(1).SetUses(1).SetDuration(10),
    Antidote().SetName("Antidote").SetRarity(45).SetUseCost(1).SetUses(1),
    SmokeBomb().SetName("Smoke Bomb").SetRarity(28).SetUseCost(1).SetUses(1),
    SmokeBomb().SetName("Smoke Pellet").SetRarity(38).SetUseCost(1).SetUses(2),
    SporecloudWeapon().SetName("Spore Cloud Sack").SetRarity(45).SetUseCost(1).SetUses(2),
    Bandage().SetName("Bandage").SetRarity(84).SetUseCost(1).SetUses(2).SetBleedCure(3),
    Bandage().SetName("Tourniquet").SetRarity(72).SetUseCost(1).SetUses(2).SetBleedCure(50),
    
    # === OFFENSIVE POTIONS ===
    EffectPotion().SetName("Poison Vial").SetRarity(35).SetUseCost(1).SetUses(2).SetEffect(StatusEffect.PoisonEffect, 4),
    EffectPotion().SetName("Toxic Serum").SetRarity(18).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.PoisonEffect, 12),
    EffectPotion().SetName("Bloodletting Vial").SetRarity(30).SetUseCost(1).SetUses(2).SetEffect(StatusEffect.BleedEffect, 3),
    EffectPotion().SetName("Hemorrhage Potion").SetRarity(14).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.BleedEffect, 8),
    # === STATUS EFFECT POTIONS ===
    EffectPotion().SetName("Vulnerability Draught").SetRarity(30).SetUseCost(1).SetUses(2).SetEffect(StatusEffect.Vulnerablity, 3),
    EffectPotion().SetName("Weakening Potion").SetRarity(28).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.Weakness, 2),
    EffectPotion().SetName("Resistance Tonic").SetRarity(25).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.Resistance, 3),
    EffectPotion().SetName("Enfeebling Elixir").SetRarity(30).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.Weakness, 2).AddEffect(StatusEffect.Vulnerablity, 2),
    EffectPotion().SetName("Fortitude Tonic").SetRarity(26).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.FortitudeEffect, 2),
    EffectPotion().SetName("Berserker's Brew").SetRarity(14).SetUseCost(2).SetUses(1).SetEffect(StatusEffect.BerserkEffect, 3),
    EffectPotion().SetName("Vampiric Tonic").SetRarity(18).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.LifestealEffect, 6),
    EffectPotion().SetName("Thorny Brew").SetRarity(31).SetUseCost(1).SetUses(1).SetEffect(StatusEffect.ThornedEffect, 6),

    # === SHIELDING ITEMS ===
    ShieldItem().SetName("Training Wooden Shield").SetRarity(90).SetUseCost(1).SetShield(4),
    ShieldItem().SetName("Splintered Buckler").SetRarity(82).SetUseCost(1).SetShield(6),
    ShieldItem().SetName("Tattered Kite Shield").SetRarity(78).SetUseCost(2).SetShield(16),
    ShieldItem().SetName("Godkin Bulwark").SetRarity(3).SetUseCost(2).SetShield(40),

    # === SPECIAL SHIELDING ITEMS ===
    #ShieldItem().SetName("Smoke Bulwark").SetRarity(95).SetUseCost(2).SetShield(4),
    #ShieldItem().SetName("Venomglass Plate").SetRarity(95).SetUseCost(2).SetShield(4),
    #ShieldItem().SetName("Golem-Core Plating").SetRarity(95).SetUseCost(2).SetShield(4),
    #ShieldItem().SetName("Bloodforged Aegis").SetRarity(3).SetUseCost(2).SetShield(45),

    # === USEFUL ITEMS ===
    #TreasureItem().SetName("Relic Shard").SetRarity(5),
    #TreasureItem().SetName("Jade Key").SetRarity(10),
    TreasureItem().SetName("Rusted Cathedral Key").SetRarity(5),
    #TreasureItem().SetName("Explorer's Pass").SetRarity(15),
    #ToolItem().SetName("Shovel").SetRarity(40),
    ToolItem().SetName("Pickaxe").SetRarity(35),
    ToolItem().SetName("Lockpick Set").SetRarity(40),

    # === BASIC ITEMS ===
    JunkItem().SetName("Cloth Fragment").SetRarity(96),
    JunkItem().SetName("Wooden Log").SetRarity(94),
    JunkItem().SetName("Gravel Piece").SetRarity(97),
    JunkItem().SetName("Rusty Metal").SetRarity(88),
    JunkItem().SetName("Tattered Banner").SetRarity(85),
    
    # === COMMON CRAFTING MATERIALS ===
    JunkItem().SetName("Iron Chunk").SetRarity(75),
    JunkItem().SetName("Fur Pelt").SetRarity(70),
    JunkItem().SetName("Wooden Plank").SetRarity(68),
    JunkItem().SetName("Plant Fiber").SetRarity(72),
    JunkItem().SetName("Bone Fragment").SetRarity(65),
    
    # === UNCOMMON MATERIALS ===
    JunkItem().SetName("Silver Nugget").SetRarity(45),
    JunkItem().SetName("Copper Ingot").SetRarity(50),
    JunkItem().SetName("Crystal Shard").SetRarity(38),
    JunkItem().SetName("Leather Strip").SetRarity(48),
    JunkItem().SetName("Enchanted Dust").SetRarity(32),
    
    # === RARE MATERIALS ===
    JunkItem().SetName("Gold Ore").SetRarity(18),
    JunkItem().SetName("Ancient Scroll").SetRarity(22),
    JunkItem().SetName("Mithril Fragment").SetRarity(12),
    JunkItem().SetName("Phoenix Feather").SetRarity(8),
    JunkItem().SetName("Moonstone").SetRarity(15),
    
    # === VALUABLE TREASURES ===
    JunkItem().SetName("Silverware").SetRarity(50),
    JunkItem().SetName("Golden Chalice").SetRarity(6),
    JunkItem().SetName("Random Jewel").SetRarity(25),
    JunkItem().SetName("Ancient Coin").SetRarity(14),
    JunkItem().SetName("Rare Gemstone").SetRarity(4),
    JunkItem().SetName("Obsidian Shard").SetRarity(20),
    JunkItem().SetName("Diamond").SetRarity(2),
    JunkItem().SetName("Crown of Kings").SetRarity(1),
]

"""
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
"""