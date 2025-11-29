from abc import ABC, abstractmethod
from colorama import Fore, Style

# Abstract effect class, derive effects from this
class AEffect(ABC):
    positive: bool = False
    def __init__(self, entity, stacks: int = 1):
        self.attachedEntity = entity
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
        self.attachedEntity.Damage(self.stacks)

        if (gc.playerCharacter.HasRelic(Relics.WyrmSpineCharm) and self.attachedEntity != gc.playerCharacter):
            self.attachedEntity.Damage(self.stacks)

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
        self.attachedEntity.Damage(random.randrange(1, 5))
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
        self.attachedEntity.stamina -= 1
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