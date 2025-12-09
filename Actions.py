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
        self.repeatAmount: int | range = 1

    def SetName(self, name: str):
        self.actionName = name
        return self
    
    def SetRepeat(self, times: int | range):
        if type(times) is range and times.start == 0:
            times = range(1, times.stop, times.step)
            
        self.repeatAmount = times
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
        from AttackInfo import AttInfo
        import StatusEffect
        gc.playerCharacter.Damage(AttInfo(self.CalculateDamage(), self.parentEntity))

        for effect in self.effectsOnHit:
            StatusEffect.Apply(gc.playerCharacter, effect)

        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {round(self.CalculateDamage() * (1 - gc.playerCharacter.GetDamageResist()))} damage!" # I am well aware this has issues
    
    def SetEffectsOnHit(self, *effects):
        for effect in effects:
            self.effectsOnHit.append(effect)
        return self
    
    def CalculateDamage(self):
        return round((self.damage + self.parentEntity.additionalRawDamage) * self.parentEntity.outgoingDamageMultiplier)
    
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
            ally.additionalRawDamage += self.amount
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
    
class RemovePlayerBuffsAndAttackAction(AttackAction):
    def PerformAction(self):
        for eff in gc.playerCharacter.effects:
            if eff.positive:
                gc.playerCharacter.RemoveEffect(eff)
                print(f"{self.parentEntity.name} removes your {eff.GetName()} buff!")
        return super().PerformAction()
    
class ApplyEffectToSelfAction(AAction):
    def __init__(self, effect: type, stacks: int):
        super().__init__()
        self.effect = effect
        self.stacks = stacks

    def PerformAction(self):
        import StatusEffect
        StatusEffect.Apply(self.parentEntity, self.effect, self.stacks)
        return super().PerformAction()
    
class EmberlingGrow(AAction):
    def PerformAction(self):
        from Entity import EmberlingEnemy
        if type(self.parentEntity) is not EmberlingEnemy:
            return super().PerformAction()
        
        self.parentEntity.size += 1
        print(f"The {self.parentEntity.name} grows brighter!")

        return super().PerformAction()
    
class EmberlingDetonate(AAction):
    def PerformAction(self):
        from Entity import EmberlingEnemy
        if type(self.parentEntity) is not EmberlingEnemy:
            return super().PerformAction()
        
        self.parentEntity.Detonate()

        return super().PerformAction()
    
    def GetShortDesc(self):
        from Entity import EmberlingEnemy
        if type(self.parentEntity) is not EmberlingEnemy:
            return super().PerformAction()
        
        return super().GetShortDesc() + f" for {round(self.parentEntity.GetDetonateDamage() * (1 - gc.playerCharacter.GetDamageResist()))} damage!" # I am well aware this has issues
    
class ApplyEffectToPlayerAction(AAction):
    def __init__(self, effect: type, stacks: int = 1):
        super().__init__()
        self.effect = effect
        self.stacks = stacks

    def PerformAction(self):
        import StatusEffect
        StatusEffect.Apply(gc.playerCharacter, self.effect, self.stacks)
        print(f"{self.parentEntity.name} applies {self.effect.__name__} to the player!")
        return super().PerformAction()
    
class SorrowFeedAction(AAction):
    def __init__(self, damagePerDebuff: int = 1):
        super().__init__()
        self.damagePerDebuff = damagePerDebuff

    def PerformAction(self):
        debuffCount = 0
        for effect in gc.playerCharacter.effects:
            if not effect.positive:
                debuffCount += effect.stacks
        
        damageIncrease = debuffCount * self.damagePerDebuff
        self.parentEntity.additionalRawDamage += damageIncrease
        
        if damageIncrease > 0:
            print(f"{self.parentEntity.name} feeds on the player's suffering, gaining {damageIncrease} additional damage!")
        else:
            print(f"{self.parentEntity.name} finds no sorrow to feed upon...")
        
        return super().PerformAction()
    
class StealAndAttackAction(AttackAction):
    def __init__(self, damage, stealGoldRange: range):
        super().__init__(damage)
        self.stealGoldRange = stealGoldRange

    def PerformAction(self):
        from colorama import Fore, Style
        goldTaken = gc.playerCharacter.TakeGold(random.randrange(self.stealGoldRange.start, self.stealGoldRange.stop))

        if goldTaken > 0:
            print(f"{self.parentEntity.name} stole {Fore.YELLOW}{Style.BRIGHT}{goldTaken}{Style.RESET_ALL} gold!")
        else:
            print(f"[#{gc.GetIndexOfEnemy(self.parentEntity)}][LVL {self.parentEntity.level}] {self.parentEntity.name}: Huh? We got a broke bloke!")

        if hasattr(self.parentEntity, "gold"):
            goldTaken += int(getattr(self.parentEntity, "gold"))
        setattr(self.parentEntity, "gold", goldTaken)

        return super().PerformAction()
    
class EscapeAction(AAction):
    def __init__(self, escapeTaunt: str):
        self.escapeTaunt: str = escapeTaunt
        super().__init__()

    def PerformAction(self):
        from colorama import Fore, Style
        if len(self.escapeTaunt) > 0:
            print(f"[#{gc.GetIndexOfEnemy(self.parentEntity)}][LVL {self.parentEntity.level}] {self.parentEntity.name}: Ha ha! Sucker!")
        gc.RemoveEnemyFromScene(self.parentEntity)
        print(f"{Fore.RED}{Style.BRIGHT}{self.parentEntity.name}{Style.NORMAL} escaped!{Style.RESET_ALL}")
        return super().PerformAction()
    

#############################################################################
# Action set class
class ActionSet():
    def __init__(self):
        self.actions: list[AAction] = []
        self.actionIndex = 0
        self.currentActionPerformedCount = 0
        self.toRepeat: int = 1

    def Setup(self, entity):
        for act in self.actions:
            act.parentEntity = entity
        self.SetCurrentAction(self.actionIndex)

    def GetNextAction(self, index: int | None = None) -> AAction | None:
        if len(self.actions) <= 0:
            return None
        if type(index) is not int:
            index = self.actionIndex
        return self.actions[index]
    
    def SetCurrentAction(self, index: int):
        self.actionIndex = index
        self.currentActionPerformedCount = 0

        # Figure out how many times to repeat this action
        repeatRange: int | range = self.actions[self.actionIndex].repeatAmount
        self.toRepeat = repeatRange if (type(repeatRange) is int) else (random.randrange(repeatRange.start, repeatRange.stop, repeatRange.step)) # type: ignore
        pass
        
    def PerformNextAction(self):
        nextAction = self.GetNextAction()
        if nextAction is None:
            return
        
        nextAction.PerformAction()
        self.currentActionPerformedCount += 1

        # guard clause to repeat current action if we need to
        if (self.toRepeat > self.currentActionPerformedCount):
            return

        # Cycle to find next availible action to take
        index = self.actionIndex
        while True:
            limit = 100
            index += 1
            if (index >= len(self.actions)):
                index = 0

            nextAction = self.GetNextAction(index)
            if nextAction is None:
                break

            # Guard clauses my beloved
            if (limit <= 0 or len(self.actions) == 1):
                break
            if (random.random() <= nextAction.chance and nextAction.CanDoAction()):
                break
            limit -= 1
        self.SetCurrentAction(index)

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
