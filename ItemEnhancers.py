from ItemSystem import AItem, UseableItem, Weapon
from abc import ABC, abstractmethod
from ElementTags import ElementTag
import StatusEffect
    
class AEnhancement(ABC):
    @abstractmethod
    def ApplyEnhancement(self, weapon: Weapon):
        pass
    
    @abstractmethod
    def GetDescription(self) -> str:
        return "N/A"

class EnhancementItem(UseableItem):
    tag = "ENHANCEMENT"
    def __init__(self):
        super().__init__()
        self.enhancementType: AEnhancement | None = None
        self.chosenItem: AItem | None = None

    def CheckCanUse(self) -> bool:
        return super().CheckCanUse()

    def Use(self):
        import Commands
        import GameCore as gc
        from colorama import Fore, Style

        # Get the player to choose a weapon to enhance
        Commands.PrintOutInventory()
        choice = input(f"Choose weapon to enhance with {Fore.GREEN}{self.enhancementType.GetDescription()}{Style.RESET_ALL} (leave blank to cancel): ")
        if (not choice.isnumeric()):
            return False
        choice = int(choice) - 1
        if (choice < 0 or choice >= len(gc.playerCharacter.items)):
            return False
        if (self.enhancementType is not None and not issubclass(type(gc.playerCharacter.items[choice]), Weapon)):
            print("You can only enhance weapons!")
            return False
        self.chosenItem = gc.playerCharacter.items[choice]

        return super().Use()
    
    def OnUse(self):
        import GameCore as gc
        self.enhancementType.ApplyEnhancement(self.chosenItem)
        return super().OnUse()

    def SetEnhancementType(self, enhancementType: AEnhancement):
        self.enhancementType = enhancementType
        return self
    
    def GetDesc(self) -> str:
        if (self.enhancementType is not None):
            return super().GetDesc() + f" - Enhances a weapon with {self.enhancementType.GetDescription()}"
        return super().GetDesc()
    
class LevelEnhancement(AEnhancement):
    def __init__(self, levelIncrease: int):
        self.levelIncrease = levelIncrease

    def ApplyEnhancement(self, weapon: Weapon):
        weapon.Upgrade(self.levelIncrease)

    def GetDescription(self) -> str:
        return f"+{self.levelIncrease} Levels"
    
class ElementEnhancement(AEnhancement):
    def __init__(self, element: ElementTag):
        self.element = element

    def ApplyEnhancement(self, weapon: Weapon):
        weapon.SetElement(self.element)

    def GetDescription(self) -> str:
        return f"{self.element} Element"

class EffectEnhancement(AEnhancement):
    def __init__(self, effect: type, stacks: int = 1):
        self.effect = effect
        self.stacks = stacks

    def ApplyEnhancement(self, weapon: Weapon):
        weapon.SetEffectToApply(self.effect, self.stacks)

    def GetDescription(self) -> str:
        if self.effect is not None:
            try:
                tempEffect = self.effect(self, self.stacks)
                effectText = f"{tempEffect.GetName()}"
            except Exception:
                effectText = f"{self.effect.__name__}"
        return f"{self.stacks} {effectText}"