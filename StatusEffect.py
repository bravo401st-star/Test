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

    for eff in entity.effects:
        if type(eff) is effectType:
            # effect already exists on entity
            eff.AddStack(effect.stacks)
            return True
        
    entity.effects.append(effect)
    effect.OnEffectApply()
    return True

def GetRandomEffect(positive: bool = False) -> type:
    import random
    import Relics
    effectsList: list[type] = []
    for effect in AEffect.__subclasses__():
        if not effect.positive and positive:
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
        return f"{Fore.GREEN}{Style.BRIGHT}Poison{Style.RESET_ALL}"
    
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
        return f"{Fore.RED}{Style.BRIGHT}Bleeding{Style.RESET_ALL}"
    
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
        return f"{Fore.LIGHTCYAN_EX}Bogged{Style.RESET_ALL}"
    
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
        return f"{Fore.YELLOW}{Style.BRIGHT}Blessed{Style.RESET_ALL}"
    
class RegenerationEffect(AEffect):
    positive: bool = True

    def OnEffectTick(self):
        self.attachedEntity.Heal(self.stacks)
        return super().OnEffectTick()
    
    def OnEffectApply(self):
        print(f"{self.attachedEntity.name} feels healed!")
        return super().OnEffectApply()
    
    def GetName(self):
        return f"{Fore.GREEN}{Style.BRIGHT}Regeneration{Style.RESET_ALL}"
    
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
        return f"{Fore.MAGENTA}{Style.BRIGHT}Phase Shifted{Style.RESET_ALL}"
    
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
        return f"{Fore.WHITE}{Style.BRIGHT}Resistance{Style.RESET_ALL}"
    
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
        return f"{Fore.WHITE}{Style.DIM}Vulnerablity{Style.RESET_ALL}"
    
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
        return f"{Fore.YELLOW}{Style.DIM}Weakness{Style.RESET_ALL}"

class BerserkEffect(AEffect):
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
        return f"{Fore.RED}{Style.BRIGHT}Berserk{Style.RESET_ALL}"

class LifestealEffect(AEffect):
    positive: bool = True

    def OnEffectApply(self):
        amount = 0.5
        # use dynamic attribute to track lifesteal fraction
        if not hasattr(self.attachedEntity, 'lifesteal_fraction'):
            self.attachedEntity.lifesteal = 0.0
        self.attachedEntity.lifesteal += amount
        print(f"{self.attachedEntity.name} feels vampiric power flowing through them!")
        return super().OnEffectApply()

    def OnEffectRemove(self):
        amount = 0.5
        self.attachedEntity.lifesteal -= amount
        if self.attachedEntity.lifesteal <= 0:
            try:
                delattr(self.attachedEntity, 'lifesteal_fraction')
            except Exception:
                pass
        return super().OnEffectRemove()

    def GetName(self):
        return f"{Fore.MAGENTA}{Style.BRIGHT}Lifesteal{Style.RESET_ALL}"

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
        return f"{Fore.CYAN}{Style.BRIGHT}Fortitude{Style.RESET_ALL}"