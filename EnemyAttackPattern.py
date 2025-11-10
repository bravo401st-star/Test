from abc import ABC, abstractmethod
import Entity
import GameCore as gc

# Action Types
class AAction(ABC):
    def __init__(self, entity: Entity.Entity):
        self.actionName = "Unnamed Action"
        self.actionShortDesc = "Peforming action..."
        self.parentEntity = entity
        pass

    def SetName(self, name: str):
        self.actionName = name
        return self
    
    def SetShortDesc(self, shortDesc: str):
        self.actionShortDesc = shortDesc
        return self

    @abstractmethod
    def PerformAction(self):
        pass

class AttackAction(AAction):
    def __init__(self, entity: Entity.Entity, damage: int):
        self.damage = damage
        super().__init__(entity)

    def PerformAction(self):
        gc.playerCharacter.Damage(self.damage)
        return super().PerformAction()
    
    
#############################################################################
# Action set class
class ActionSet():
    def __init__(self):
        self.actions = []
        self.actionIndex = 0
        
    def PerfermNextAction(self):
        self.actionIndex += 1
        if (self.actionIndex >= len(self.actions)):
            self.actionIndex = 0

    def AppendAction(self, action: AAction):
        if issubclass(type(action), AAction) != True:
            raise TypeError(f"Type {type(action)} is not an Action!")
        
        self.actions.append(action)
