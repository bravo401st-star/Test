from __future__ import annotations
from abc import ABC, abstractmethod
from colorama import Fore, Style
from Entity import AEntity, Player
from AttackInfo import AttInfo

# Abstract effect class, derive effects from this
class AEffect(ABC):
    positive: bool = False
    def __init__(self, entity, stacks: int = 1):
        self.attachedEntity: AEntity = entity
        self.stacks: int = stacks
    
    # To be run when the effect is applied
    def OnEffectApply(self):
        pass

    # To be run when the effect is removed
    def OnEffectRemove(self):
        pass

    # To be run at the start of each turn
    def OnEffectTick(self):
        self.RemoveStack()

    def AddStack(self, count: int = 1):
        self.stacks += count

    def RemoveStack(self, count: int = 1):
        self.stacks -= count

    def CanBeApplied(self) -> bool:
        import SkillSystem
        if not self.positive and isinstance(self.attachedEntity, Player):
            if self.attachedEntity._ironWillReady and SkillSystem.GetSkillNodeRank("sknd_ironwill") > 0:
                self.attachedEntity._ironWillReady = False
                print(f"Your iron will shrugged off {self.stacks} {self.GetName()}!")
                return False
        return True

    @abstractmethod
    def GetName(self) -> str:
        return "Unnamed Effect"

# Static function for applying an effect to an entity
def Apply(entity, effectType: type, stacks: int = 1) -> bool:
    # validate type is an effect
    if not issubclass(effectType, AEffect):
        return False
    
    # initalize the effect and apply
    effect: AEffect = effectType(entity, stacks)
    if not effect.CanBeApplied():
        return False
    
    if not effect.positive and entity.HasEffect(BlessedEffect):
        print(f"A blessing has blocked a negative effect on {entity.name}!")
        return False
    
    entity.OnEffectApply(effect)
    return True

def GetRandomEffect(negative: bool = True, positive: bool = True) -> type:
    import random
    import Relics
    effectsList: list[type] = []
    for effect in AEffect.__subclasses__():
        if effect.positive and not positive:
            continue
        if not effect.positive and not negative:
            continue
        effectsList.append(effect)
    
    rand = random.randint(0, len(effectsList) - 1)
    return effectsList[rand]

###############################################################################
# Effect definitions

class PoisonEffect(AEffect):
    def OnEffectTick(self):
        import GameCore as gc
        import Relics
        damage = self.stacks

        wyrmSpineCharmCount = gc.playerCharacter.GetRelicCount(Relics.WyrmSpineCharm)
        if (wyrmSpineCharmCount > 0 and self.attachedEntity != gc.playerCharacter):
            damage += Relics.WyrmSpineCharm.EXTRA_POISON_DAMAGE * wyrmSpineCharmCount
            for _ in range(wyrmSpineCharmCount * Relics.WyrmSpineCharm.EXTRA_TICKS):
                self.attachedEntity.Damage(AttInfo(damage, None, True))

        self.attachedEntity.Damage(AttInfo(damage, None, True))

        return super().OnEffectTick()
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} has been poisoned!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.GREEN}{Style.BRIGHT}Poison{Style.NORMAL}{Fore.RESET}"
    
    def AddStack(self, count):
        print(f"{self.attachedEntity.name} poison increases!")
        return super().AddStack(count)
    
class BleedEffect(AEffect):
    def OnEffectTick(self):
        import random
        import GameCore as gc
        import SkillSystem
        from Entity import Player
        from Relics import RendingClaw
        damage = random.randrange(1, 5)

        if not isinstance(self.attachedEntity, Player):
            rendingRelicCount = gc.playerCharacter.GetRelicCount(RendingClaw)
            if rendingRelicCount > 0:
                damage += RendingClaw.EXTRA_BLEEDING_DAMAGE * rendingRelicCount

            crimsonDrainRank = SkillSystem.GetSkillNodeRank("sknd_crimsondrain")
            if crimsonDrainRank > 0:
                gc.playerCharacter.Heal(SkillSystem.VAMPIRIC_CRIMSON_DRAIN_HEAL * crimsonDrainRank)

        self.attachedEntity.Damage(AttInfo(damage, None, True))
        return super().OnEffectTick()
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} is bleeding!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.RED}{Style.BRIGHT}Bleeding{Style.NORMAL}{Fore.RESET}"
    
    def AddStack(self, count):
        print(f"{self.attachedEntity.name} bleed increases!")
        return super().AddStack(count)

class BoggedEffect(AEffect):
    def OnEffectTick(self):
        if type(self.attachedEntity is Player):
            self.attachedEntity.stamina -= 1 # type: ignore
        return super().OnEffectTick()
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} feels slowed...")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.LIGHTCYAN_EX}Bogged{Style.NORMAL}{Fore.RESET}"
    
    def CanBeApplied(self):
        from Entity import Player
        return type(self.attachedEntity) is Player
    
    def AddStack(self, count):
        print(f"{self.attachedEntity.name} feels even slower.")
        return super().AddStack(count)
    
class BlessedEffect(AEffect):
    positive: bool = True

    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} has been blessed!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.YELLOW}{Style.BRIGHT}Blessed{Style.NORMAL}{Fore.RESET}"
    
class OnFireEffect(AEffect):
    CHANCE_TO_SPREAD: float = 0.7
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} erupts into flame!")
        return super().OnEffectApply()
    
    def AddStack(self, count = 1):
        print(f"The flames grow on {self.attachedEntity.name}")
        return super().AddStack(count)
    
    def OnEffectTick(self):
        import random
        import GameCore as gc
        import SkillSystem
        from ElementTags import ElementTag
        # chance to spread to random enemy
        controlledBurnRank = SkillSystem.GetSkillNodeRank("sknd_controlledburn")
        if random.random() <= (OnFireEffect.CHANCE_TO_SPREAD + (controlledBurnRank * SkillSystem.PYRO_ACCELERANT_DAMAGE_BONUS)) and len(gc.enemiesInScene) > 0:
            entity: AEntity = random.choice(gc.enemiesInScene)
            print(f"The flames spread to {entity.name}")
            Apply(entity, OnFireEffect, 1)
        damage = random.randrange(3, 16)
        accelerantRank = SkillSystem.GetSkillNodeRank("sknd_accelerant")
        if accelerantRank > 0:
            damage *= int(1 + SkillSystem.PYRO_ACCELERANT_DAMAGE_BONUS * accelerantRank)
        self.attachedEntity.Damage(AttInfo(damage, None, True).AddElements(ElementTag.FIRE))
        everlastingEmbersRank = SkillSystem.GetSkillNodeRank("sknd_everlastingembers")
        if everlastingEmbersRank > 0:
            return

        return super().OnEffectTick()
    
    def GetName(self):
        return f"{Fore.RED}{Style.BRIGHT}On Fire{Style.NORMAL}{Fore.RESET}"
    
class RegenerationEffect(AEffect):
    positive: bool = True

    def OnEffectTick(self):
        self.attachedEntity.Heal(self.stacks)
        return super().OnEffectTick()
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} feels healed!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.GREEN}{Style.BRIGHT}Regeneration{Style.NORMAL}{Fore.RESET}"
    
class PhaseShifted(AEffect):
    EVASION_OFFSET: float = 0.50
    positive: bool = True

    def OnEffectApply(self):
        self.attachedEntity.evasion += PhaseShifted.EVASION_OFFSET
        print(f"{self.attachedEntity.name} shifts from reality!")
        return super().OnEffectApply()
    
    def OnEffectRemove(self):
        self.attachedEntity.evasion -= PhaseShifted.EVASION_OFFSET
        print(f"{self.attachedEntity.name} shifts back to reality!")
        return super().OnEffectRemove()
    
    def GetName(self):
        return f"{Fore.MAGENTA}{Style.BRIGHT}Phase Shifted{Style.NORMAL}{Fore.RESET}"
    
class ThornedEffect(AEffect):
    positive: bool = True

    def OnEffectApply(self):
        self.attachedEntity.thorns += self.stacks
        self._added_thorns = self.stacks
        print(f"{self.attachedEntity.name} feels thorny!")
        return super().OnEffectApply()
    
    def OnEffectTick(self):
        self.attachedEntity.thorns -= 1
        self._added_thorns -= 1
        return super().OnEffectTick()
    
    def OnEffectRemove(self):
        self.attachedEntity.thorns -= self._added_thorns
        return super().OnEffectRemove()
    
    def AddStack(self, count):
        self.attachedEntity.thorns += count
        self._added_thorns += count
        print(f"{self.attachedEntity.name} feels even more thorny!")
        return super().AddStack(count)
    
    def GetName(self):
        return f"{Fore.GREEN}{Style.BRIGHT}Thorned{Style.NORMAL}{Fore.RESET}"
    
class Resistance(AEffect):
    DAMAGE_MULT: float = 0.50
    positive: bool = True

    def OnEffectApply(self):
        self.attachedEntity.damageResistance += Resistance.DAMAGE_MULT
        print(f"{self.attachedEntity.name} feels protected!")
        return super().OnEffectApply()
    
    def OnEffectRemove(self):
        self.attachedEntity.damageResistance -= Resistance.DAMAGE_MULT
        return super().OnEffectRemove()
    
    def GetName(self):
        return f"{Fore.WHITE}{Style.BRIGHT}Resistance{Style.NORMAL}{Fore.RESET}"
    
class CursedEffect(AEffect):
    positive: bool = False
    HEALING_REDUCTION: float = 1.0

    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} has been cursed!")
        self.attachedEntity.healingMultiplier -= self.HEALING_REDUCTION
        return super().OnEffectApply()

    def OnEffectRemove(self):
        self.attachedEntity.healingMultiplier += self.HEALING_REDUCTION
        return super().OnEffectRemove()

    def GetName(self):
        return f"{Fore.MAGENTA}{Style.DIM}Cursed{Style.NORMAL}{Fore.RESET}"
    
class MadnessEffect(AEffect):
    positive: bool = False

    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} has gone mad!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.MAGENTA}{Style.BRIGHT}Madness{Style.NORMAL}{Fore.RESET}"
    
class InfectionEffect(AEffect):
    positive: bool = False
    HEALING_REDUCTION: float = 0.80
    ROT_CHANCE_PER_TICK: float = 0.15

    def OnEffectTick(self):
        import random
        import SkillSystem
        chance = InfectionEffect.ROT_CHANCE_PER_TICK
        isPlayer: bool = isinstance(self.attachedEntity, Player)

        if not isPlayer:
            acceleratedDecayRank = SkillSystem.GetSkillNodeRank("sknd_accelerateddecay")
            if acceleratedDecayRank > 0:
                chance += SkillSystem.CARRION_ACCELERATED_DECAY_ROT_CHANCE_BONUS * acceleratedDecayRank

        if random.random() < InfectionEffect.ROT_CHANCE_PER_TICK:
            Apply(self.attachedEntity, RotEffect, self.stacks)
            print(f"{self.attachedEntity.name} has contracted rot from the infection!")
            if not isinstance(self.attachedEntity, Player):
                putridConversionRank = SkillSystem.GetSkillNodeRank("sknd_putridconversion")
                if putridConversionRank > 0:
                    self.attachedEntity.Damage(AttInfo(SkillSystem.CARRION_PUTRID_CONVERSION_DAMAGE_BONUS * putridConversionRank, None, True))

        if not isPlayer and SkillSystem.GetSkillNodeRank("sknd_endlessdecay") > 0:
            return

        return super().OnEffectTick()

    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} is infected!")
        self.attachedEntity.healingMultiplier -= InfectionEffect.HEALING_REDUCTION
        return super().OnEffectApply()
    
    def AddStack(self, count: int):
        print(f"{self.attachedEntity.name}'s infection spreads!")
        return super().AddStack(count)
    
    def OnEffectRemove(self):
        self.attachedEntity.healingMultiplier += InfectionEffect.HEALING_REDUCTION
        return super().OnEffectRemove()
    
    def GetName(self):
        return f"{Fore.GREEN}{Style.DIM}Infection{Style.NORMAL}{Fore.RESET}"
    
class RotEffect(AEffect):
    DAMAGE_PER_TICK: int = 3
    MAX_HEALTH_LOSS_PER_TICK: int = 1
    positive: bool = False

    def __init__(self, entity, stacks: int = 1):
        super().__init__(entity, stacks)
        self._max_health_reduced: int = 0

    def OnEffectTick(self):
        self.attachedEntity.Damage(AttInfo(RotEffect.DAMAGE_PER_TICK, None, True))
        if self.attachedEntity.maxHealth > RotEffect.MAX_HEALTH_LOSS_PER_TICK:
            self.attachedEntity.SetMaxHealth(self.attachedEntity.maxHealth - RotEffect.MAX_HEALTH_LOSS_PER_TICK)
            self._max_health_reduced += RotEffect.MAX_HEALTH_LOSS_PER_TICK
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} is rotting!")
        return super().OnEffectApply()
    
    def OnEffectRemove(self):
        # restore lost max health
        self.attachedEntity.SetMaxHealth(self.attachedEntity.maxHealth + self._max_health_reduced)
        return super().OnEffectRemove()
    
    def AddStack(self, count):
        print(f"{self.attachedEntity.name}'s rot spreads further!")
        return super().AddStack(count)
    
    def GetName(self):
        return f"{Fore.YELLOW}{Style.DIM}Rotting{Style.NORMAL}{Fore.RESET}"
    
class Vulnerablity(AEffect):
    DAMAGE_MULT: float = 0.50
    positive: bool = False

    def OnEffectApply(self):
        self.attachedEntity.damageResistance -= Vulnerablity.DAMAGE_MULT
        print(f"{self.attachedEntity.name} feels vulnerable!")
        return super().OnEffectApply()
    
    def OnEffectRemove(self):
        self.attachedEntity.damageResistance += Vulnerablity.DAMAGE_MULT
        return super().OnEffectRemove()
    
    def GetName(self):
        return f"{Fore.WHITE}{Style.DIM}Vulnerablity{Style.NORMAL}{Fore.RESET}"
    
class Weakness(AEffect):
    DAMAGE_MULT: float = 0.50
    positive: bool = False

    def OnEffectApply(self):
        self.attachedEntity.outgoingDamageMultiplier -= Weakness.DAMAGE_MULT
        print(f"{self.attachedEntity.name} feels weakened!")
        return super().OnEffectApply()
    
    def OnEffectRemove(self):
        self.attachedEntity.outgoingDamageMultiplier += Weakness.DAMAGE_MULT
        return super().OnEffectRemove()
    
    def GetName(self):
        return f"{Fore.YELLOW}{Style.DIM}Weakness{Style.NORMAL}{Fore.RESET}"

class BerserkEffect(AEffect):
    positive: bool = True
    DAMAGE_MULT: float = 0.50
    WEAKNESS_STACKS_ON_EXPIRE: int = 2

    def OnEffectApply(self):
        self.attachedEntity.outgoingDamageMultiplier += BerserkEffect.DAMAGE_MULT
        print(f"{self.attachedEntity.name} becomes enraged, dealing more damage!")
        return super().OnEffectApply()

    def OnEffectRemove(self):
        self.attachedEntity.outgoingDamageMultiplier -= BerserkEffect.DAMAGE_MULT
        print(f"{self.attachedEntity.name} calms down and feels weaker...")
        # apply weakness after berserk ends
        Apply(self.attachedEntity, Weakness, BerserkEffect.WEAKNESS_STACKS_ON_EXPIRE)
        return super().OnEffectRemove()

    def GetName(self):
        return f"{Fore.RED}{Style.BRIGHT}Berserk{Style.NORMAL}{Fore.RESET}"

class LifestealEffect(AEffect):
    positive: bool = True

    def OnEffectApply(self):
        amount = 0.5
        self.attachedEntity.lifesteal += amount
        print(f"{self.attachedEntity.name} feels vampiric power flowing through them!")
        return super().OnEffectApply()

    def OnEffectRemove(self):
        amount = 0.5
        self.attachedEntity.lifesteal -= amount
        return super().OnEffectRemove()

    def GetName(self):
        return f"{Fore.MAGENTA}{Style.BRIGHT}Lifesteal{Style.NORMAL}{Fore.RESET}"

class FortitudeEffect(AEffect):
    SHIELD_PER_STACK = 4
    positive: bool = True

    def OnEffectApply(self):
        self.attachedEntity.AddShield(FortitudeEffect.SHIELD_PER_STACK * self.stacks)
        print(f"{self.attachedEntity.name} gains a protective fortitude!")
        return super().OnEffectApply()
    
    def AddStack(self, count: int):
        self.attachedEntity.AddShield(FortitudeEffect.SHIELD_PER_STACK * count)
        print(f"{self.attachedEntity.name} gains more fortitude!")
        return super().AddStack(count)

    def GetName(self):
        return f"{Fore.CYAN}{Style.BRIGHT}Fortitude{Style.NORMAL}{Fore.RESET}"