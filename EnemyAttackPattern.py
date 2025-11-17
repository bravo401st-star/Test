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
    
    def CanDoAction(self) -> bool:
        return True
    
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
    
class HealRandomUndeadAction(AAction):
    def __init__(self, healing: int):
        super().__init__()
        self.healing = healing

    def CanDoAction(self):
        return gc.GetRandomEnemyByType("Undead") != None
    
    def GetRandomUndead(self):
        return gc.GetRandomEnemyByTag("Undead")

    def PerformAction(self, parent):
        undeadToHeal = self.GetRandomUndead()
        if (undeadToHeal == None):
            return super().PerformAction(parent)
        print(f"{parent.name} healed an undead!")
        undeadToHeal.Heal(self.healing)
        return super().PerformAction(parent)
    
class TauntAction(AAction):
    def __init__(self, tauntText: str):
        super().__init__()
        self.tauntText = tauntText

    def PerformAction(self, parent):
        print(f"[#{gc.GetIndexOfEnemy(parent)}][LVL {parent.level}] {parent.name}: {self.tauntText}")
        return super().PerformAction(parent)
    
    
#############################################################################
# Action set class
class ActionSet():
    def __init__(self):
        self.actions = []
        self.actionIndex = 0

    def GetNextAction(self) -> AAction:
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
            if (self.GetNextAction().CanDoAction()):
                break
            limit -= 1

    def AppendAction(self, action: AAction):
        if issubclass(type(action), AAction) != True:
            raise TypeError(f"Type {type(action)} is not an Action!")
        
        self.actions.append(action)

    def GetActionByName(self, name: str) -> AAction:
        for action in self.actions:
            if action.actionName == name:
                return action
        return None
    
    def GetActionByType(self, actionType: type) -> AAction:
        for action in self.actions:
            if type(action) == actionType:
                return action
        return None
