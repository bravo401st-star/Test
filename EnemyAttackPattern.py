from abc import ABC, abstractmethod
import GameCore as gc
import random

# Action Types
class AAction(ABC):
    def __init__(self):
        self.actionName = "Unnamed Action"
        self.actionShortDesc = "Peforming action..."
        self.chance = 1.0
        pass

    def SetName(self, name: str):
        self.actionName = name
        return self
    
    def SetShortDesc(self, shortDesc: str):
        self.actionShortDesc = shortDesc
        return self
    
    def GetShortDesc(self):
        return self.actionShortDesc
    
    def SetChance(self, chance: float):
        self.chance = chance
        return self
    
    @abstractmethod
    def PerformAction(self, parent):
        pass

class AttackAction(AAction):
    def __init__(self, damage: int):
        self.damage = damage
        super().__init__()

    def PerformAction(self, parent):
        gc.playerCharacter.Damage(self.damage)
        return super().PerformAction(parent)
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.damage} damage!"
    
class HealAction(AAction):
    def __init__(self, healing: int):
        self.healing = healing
        super().__init__()

    def PerformAction(self, parent):
        parent.Heal(self.healing)
        return super().PerformAction(parent)
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.healing} HP!"
    
    
#############################################################################
# Action set class
class ActionSet():
    def __init__(self):
        self.actions = []
        self.actionIndex = 0

    def GetNextAction(self):
        return self.actions[self.actionIndex]
        
    def PerformNextAction(self, parent):
        if len(self.actions) <= 0:
            return
        
        self.GetNextAction().PerformAction(parent)

        while True:
            limit = 100
            self.actionIndex += 1
            if (self.actionIndex >= len(self.actions)):
                self.actionIndex = 0

            if (limit <= 0 or len(self.actions) == 1):
                break
            if (random.random() <= self.GetNextAction().chance):
                break
            limit -= 1

    def AppendAction(self, action: AAction):
        if issubclass(type(action), AAction) != True:
            raise TypeError(f"Type {type(action)} is not an Action!")
        
        self.actions.append(action)
