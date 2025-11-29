from abc import ABC, abstractmethod
import GameCore as gc
import random
import Entity

# Action Types
class AAction(ABC):
    def __init__(self):
        self.actionName = "Unnamed Action"
        self.actionShortDesc = "Peforming action..."
        self.chance = 1.0
        self.parentEntity: Entity.BasicEnemy = Entity.BasicEnemy()

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
    def PerformAction(self):
        pass

class AttackAction(AAction):
    def __init__(self, damage: int):
        self.damage = damage
        self.effectsOnHit: list[type] = []
        super().__init__()

    def PerformAction(self):
        import StatusEffect
        gc.playerCharacter.Damage(self.damage + self.parentEntity.additionalRawDamage)

        for effect in self.effectsOnHit:
            StatusEffect.Apply(gc.playerCharacter, effect)

        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.damage + self.parentEntity.additionalRawDamage} damage!"
    
    def SetEffectsOnHit(self, *effects):
        for effect in effects:
            self.effectsOnHit.append(effect)
        return self
    
class HealAction(AAction):
    def __init__(self, healing: int):
        self.healing = healing
        super().__init__()

    def PerformAction(self):
        self.parentEntity.Heal(self.healing)
        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.healing} HP!"
    
class HealRandomUndeadAction(AAction):
    def __init__(self, healing: int):
        super().__init__()
        self.healing = healing

    def CanDoAction(self):
        return gc.GetRandomEnemyByTag("Undead") != None
    
    def GetRandomUndead(self):
        return gc.GetRandomEnemyByTag("Undead")

    def PerformAction(self):
        undeadToHeal = self.GetRandomUndead()
        if (undeadToHeal == None):
            return super().PerformAction()
        print(f"{self.parentEntity.name} healed an undead!")
        undeadToHeal.Heal(self.healing)
        return super().PerformAction()
    
class TauntAction(AAction):
    def __init__(self, tauntText: str):
        super().__init__()
        self.tauntText = tauntText

    def PerformAction(self):
        print(f"[#{gc.GetIndexOfEnemy(self.parentEntity)}][LVL {self.parentEntity.level}] {self.parentEntity.name}: {self.tauntText}")
        return super().PerformAction()
    
class BuffAlliesAction(AAction):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount

    def PerformAction(self):
        allies = gc.GetAllEnemiesOfType(type(self.parentEntity))

        if allies is None:
            return super().PerformAction()

        for ally in allies:
            ally.additionalDamage += self.amount
            print(f"{ally.name} feels a stronger bond with their allies!")

        return super().PerformAction()
    
class NothingAction(AAction):
    def __init__(self):
        super().__init__()

    def PerformAction(self):
        return super().PerformAction()
    
class TransformAction(AAction):
    def __init__(self, toIndex: int):
        super().__init__()
        self.toIndex = toIndex

    def PerformAction(self):
        import Enemies
        enemyToCreate = Enemies.CreateEnemyByIndex(self.toIndex)
        if enemyToCreate is None:
            return super().PerformAction()
        print(f"{self.parentEntity.name} has transformed into {enemyToCreate.name}")
        gc.SpawnEnemy(enemyToCreate, True)
        gc.RemoveEnemyFromScene(self.parentEntity)
        return super().PerformAction()
    
    def GetShortDesc(self):
        import Enemies
        enemy = Enemies.GetByIndex(self.toIndex)
        if enemy is not None:
            return super().GetShortDesc() + enemy.name
        return super().GetShortDesc()
    
    
#############################################################################
# Action set class
class ActionSet():
    def __init__(self):
        self.actions: list[AAction] = []
        self.actionIndex = 0

    def Setup(self, entity):
        for act in self.actions:
            act.parentEntity = entity

    def GetNextAction(self) -> AAction | None:
        if len(self.actions) <= 0:
            return None
        return self.actions[self.actionIndex]
        
    def PerformNextAction(self):
        nextAction = self.GetNextAction()
        if nextAction is None:
            return
        
        nextAction.PerformAction()

        while True:
            limit = 100
            self.actionIndex += 1
            if (self.actionIndex >= len(self.actions)):
                self.actionIndex = 0

            nextAction = self.GetNextAction()
            if nextAction is None:
                break

            # Guard clauses my beloved
            if (limit <= 0 or len(self.actions) == 1):
                break
            if (random.random() <= nextAction.chance and nextAction.CanDoAction()):
                break
            limit -= 1

    def AppendAction(self, action: AAction):
        if issubclass(type(action), AAction) != True:
            raise TypeError(f"Type {type(action)} is not an Action!")
        
        self.actions.append(action)

    def GetActionByName(self, name: str) -> AAction | None:
        for action in self.actions:
            if action.actionName == name:
                return action
        return None
    
    def GetActionByType(self, actionType: type) -> AAction | None:
        for action in self.actions:
            if type(action) == actionType:
                return action
        return None
