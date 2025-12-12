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
        self.stacks -= 1
        pass

    def AddStack(self, count: int):
        self.stacks += count

    def CanBeApplied(self) -> bool:
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
        self.attachedEntity.Damage(AttInfo(self.stacks, None, True))

        if (gc.playerCharacter.HasRelic(Relics.WyrmSpineCharm) and self.attachedEntity != gc.playerCharacter):
            self.attachedEntity.Damage(AttInfo(self.stacks, None, True))

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
        from Entity import Player
        from Relics import RendingClaw
        damage = random.randrange(1, 5)
        rendingRelicCount = gc.playerCharacter.GetRelicCount(RendingClaw)
        if type(self.attachedEntity) is not Player and rendingRelicCount > 0:
            damage += RendingClaw.EXTRA_BLEEDING_DAMAGE * rendingRelicCount
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
    
class InfectionEffect(AEffect):
    positive: bool = False
    HEALING_REDUCTION: float = 0.80
    ROT_CHANCE_PER_TICK: float = 0.15

    def OnEffectTick(self):
        import random
        if random.random() < InfectionEffect.ROT_CHANCE_PER_TICK:
            Apply(self.attachedEntity, RotEffect, 1)
            print(f"{self.attachedEntity.name} has contracted rot from the infection!")
        return super().OnEffectTick()

    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} is infected!")
        self.attachedEntity.healingMultiplier -= InfectionEffect.HEALING_REDUCTION
        return super().OnEffectApply()
    
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
    SHIELD_PER_STACK: int = 8
    positive: bool = True

    def OnEffectApply(self):
        added = FortitudeEffect.SHIELD_PER_STACK * self.stacks
        self.attachedEntity.shield += added
        # store how much we added so we can remove exactly
        self._added_shield = added
        print(f"{self.attachedEntity.name} gains a protective fortitude ({added} shield)!")
        return super().OnEffectApply()

    def OnEffectRemove(self):
        try:
            self.attachedEntity.shield -= self._added_shield

            if self.attachedEntity.shield < 0:
                self.attachedEntity.shield = 0
        except Exception:
            pass
        return super().OnEffectRemove()

    def GetName(self):
        return f"{Fore.CYAN}{Style.BRIGHT}Fortitude{Style.NORMAL}{Fore.RESET}"