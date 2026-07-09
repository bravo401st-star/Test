from abc import ABC, abstractmethod
import GameCore as gc
import random
import Entity
from ElementTags import ElementTag
from EnemyTags import EnemyTag
from colorama import Fore, Style

# Action Types
class AAction(ABC):
    def __init__(self):
        self.actionName = "Unnamed Action"
        self.actionShortDesc = "Peforming action..."
        self.chance = 1.0
        self.parentEntity: Entity.BasicEnemy = Entity.BasicEnemy()
        self.repeatAmount: int | range = 1
        self.actionColor = Fore.RED
        self.forced = False

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
        if self.forced:
            return True
        if hasattr(self, 'condition') and self.condition is not None:
            return self.condition(self.parentEntity)
        return True
    
    def SetCondition(self, condition):
        self.condition = condition
        return self
    
    def SetColor(self, color):
        self.actionColor = color
        return self
    
    def OnActionSet(self):
        pass
    
    @abstractmethod
    def PerformAction(self):
        self.forced = False
        pass

class AttackAction(AAction):
    def __init__(self, damage: int, ignoreEvasion: bool = False, shieldPierce: float = 0):
        self.damage = damage
        self.effectsOnHit: list[type] = []
        self.element: ElementTag | None = None
        self.attackCount: int | range = 1
        self.attacksToPerform: int = 1
        self.ignoreEvasion = ignoreEvasion
        self.shieldPierce = shieldPierce
        super().__init__()

    def PerformAction(self):
        from AttackInfo import AttInfo
        import StatusEffect

        for _ in range(self.attacksToPerform):
            gc.playerCharacter.Damage(AttInfo(self.CalculateDamage(), self.parentEntity, self.ignoreEvasion, self.shieldPierce).AddElements(self.element))
            for effect in self.effectsOnHit:
                StatusEffect.Apply(gc.playerCharacter, effect)

        return super().PerformAction()
    
    def GetShortDesc(self):
        timesText = "!" if self.attacksToPerform <= 1 else f" {self.attacksToPerform} times!"
        return super().GetShortDesc() + f" for {round(self.CalculateDamage() * (1 - gc.playerCharacter.GetDamageResist()))} damage{timesText}" # I am well aware this has issues
    
    def SetEffectsOnHit(self, *effects):
        for effect in effects:
            self.effectsOnHit.append(effect)
        return self
    
    def SetElement(self, element: ElementTag):
        self.element = element
        return self
    
    def SetAttackCount(self, count: int | range):
        self.attackCount = count
        return self
    
    def OnActionSet(self):
        if type(self.attackCount) is range:
            self.attacksToPerform = random.randrange(self.attackCount.start, self.attackCount.stop)
        else:
            self.attacksToPerform = self.attackCount
        return super().OnActionSet()
    
    def CalculateDamage(self):
        return round((self.damage + self.parentEntity.additionalRawDamage) * self.parentEntity.outgoingDamageMultiplier)
    
class PaleWardenSpecialAttack(AttackAction):
    def CalculateDamage(self):
        return super().CalculateDamage() * self.parentEntity.deadSouls
    
class HealAction(AAction):
    def __init__(self, healing: int):
        super().__init__()
        self.healing = healing
        self.actionColor = Fore.YELLOW

    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        return self.parentEntity.health < self.parentEntity.maxHealth

    def PerformAction(self):
        self.parentEntity.Heal(self.healing)
        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.healing} HP!"
    
class SummonAction(AAction):
    def __init__(self, toSummon: int | str, amount: int = 1):
        super().__init__()
        self.toSummon = toSummon
        self.amount = amount

    def PerformAction(self):
        import Enemies
        for _ in range(self.amount):
            enemy_to_spawn = None
            if isinstance(self.toSummon, int):
                enemy_to_spawn = Enemies.CreateEnemyByIndex(self.toSummon, self.parentEntity.level)
            else:
                enemy_to_spawn = Enemies.CreateEnemyByName(self.toSummon, self.parentEntity.level)

            gc.SpawnEnemy(enemy_to_spawn, True)
        return super().PerformAction()
    
    def GetShortDesc(self):
        import EnemyList
        # If we were given an index, try to use the referenced name. If a string was provided, use it or look up the pool.
        name = str(self.toSummon)
        if isinstance(self.toSummon, int):
            try:
                name = EnemyList.__enemy_pool__[self.toSummon].name
            except Exception:
                name = str(self.toSummon)
        else:
            # try to find matching entry in enemy pool to get name
            for enemy in EnemyList.__enemy_pool__:
                if enemy.name == self.toSummon:
                    name = enemy.name
                    break

        return super().GetShortDesc() + f" {name}!"
    
class KindleAction(AAction):
    def PerformAction(self):
        self.parentEntity.Kindle()
        return super().PerformAction()
    
class ShieldRandomAlly(AAction):
    def __init__(self, shieldAmount: int, times: int):
        super().__init__()
        self.actionColor = Fore.YELLOW
        self.shieldAmount = shieldAmount
        self.timesToPerform = times

    def PerformAction(self):
        import copy
        li = copy.copy(gc.enemiesInScene)
        if self.parentEntity in li:
            li.remove(self.parentEntity)
        if len(li) <= 0:
            return super().PerformAction()
        for _ in range(self.timesToPerform):
            allyToShield = random.choice(li)
            allyToShield.AddShield(self.shieldAmount)
            print(f"{self.parentEntity.name} shielded {allyToShield.name} for {self.shieldAmount}!")
        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.shieldAmount}, {self.timesToPerform} times"
    
    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        return len(gc.enemiesInScene) > 1
    
class HealRandomUndeadAction(AAction):
    def __init__(self, healing: int):
        super().__init__()
        self.healing = healing
        self.actionColor = Fore.YELLOW

    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        return gc.GetRandomEnemyByTag(EnemyTag.UNDEAD) != None
    
    def GetRandomUndead(self):
        return gc.GetRandomEnemyByTag(EnemyTag.UNDEAD)

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
        self.actionColor = Fore.WHITE

    def PerformAction(self):
        print(f"[#{gc.GetIndexOfEnemy(self.parentEntity)}][LVL {self.parentEntity.level}] {self.parentEntity.name}: {self.tauntText}")
        return super().PerformAction()
    
class BloodDrainAction(AAction):
    DRAIN_PERCENT = 0.14
    MIN_DRAIN = 6

    def PerformAction(self):
        from AttackInfo import AttInfo
        drainAmount = max(self.MIN_DRAIN, int(gc.playerCharacter.health * self.DRAIN_PERCENT))
        # AttInfo with no attacker — we handle the heal manually so lifesteal doesn't double-dip
        actualDamage = gc.playerCharacter.Damage(AttInfo(drainAmount, None, False))
        if actualDamage > 0:
            self.parentEntity.Heal(actualDamage)
            print(f"{Fore.RED}The Vampire Spawn drains {actualDamage} HP directly from your veins!{Fore.RESET}")
        return super().PerformAction()

    def GetShortDesc(self):
        estimate = max(self.MIN_DRAIN, int(gc.playerCharacter.health * self.DRAIN_PERCENT))
        return f"Preparing to drain ~{estimate} HP from you"
    
class MimicSwallowAction(AAction):
    MAX_SWALLOWABLE_ITEMS = 3
    def __init__(self):
        import ItemSystem
        super().__init__()
        self.actionColor = Fore.RED
        self.itemTarget: ItemSystem.AItem | None = None

    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        flag = self.GetRandomItemFromPlayer() is not None
        if hasattr(self.parentEntity, "items"):
            if len(self.parentEntity.items) >= self.MAX_SWALLOWABLE_ITEMS:
                flag = False
        return flag

    def PerformAction(self):
        import GameCore as gc
        import ItemSystem
        import copy
        if self.itemTarget is None:
            return super().PerformAction()
        
        gc.playerCharacter.RemoveItem(self.itemTarget.name)
        print(f"{self.parentEntity.name} swallowed your {self.itemTarget.name}!")
        
        # add item to mimic's inventory
        if not hasattr(self.parentEntity, "items"):
            self.parentEntity.items = []
        self.parentEntity.items.append(copy.copy(self.itemTarget))
        self.itemTarget = None

        return super().PerformAction()
    
    def GetShortDesc(self):
        if self.itemTarget is not None:
            return super().GetShortDesc() + f" your {self.itemTarget.name}!"
        
        # Fallback
        return super().GetShortDesc() + " your item!"
    
    def OnActionSet(self):
        self.itemTarget = self.GetRandomItemFromPlayer()
        return super().OnActionSet()
    
    def GetRandomItemFromPlayer(self):
        import ItemSystem
        if len(gc.playerCharacter.items) <= 0:
            return None
        items = [item for item in gc.playerCharacter.items if not isinstance(item, ItemSystem.Weapon)]
        weapons = [item for item in gc.playerCharacter.items if isinstance(item, ItemSystem.Weapon)]

        if len(items) <= 0 and len(weapons) <= 1:
            return None
        
        if len(weapons) <= 1:
            return random.choice(items)
        
        return random.choice(items + weapons)
    
class MimicImitateAction(AttackAction):
    def __init__(self):
        super().__init__(0)
        self.actionColor = Fore.RED

    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        return hasattr(self.parentEntity, "lastPlayerAttack") and self.parentEntity.lastPlayerAttack > 0

    def CalculateDamage(self):
        from AttackInfo import AttInfo
        lastDmg = getattr(self.parentEntity, 'lastPlayerAttack', 8)
        self.damage = max(8, lastDmg)  # floor of 8 so it's never trivial
        return super().CalculateDamage()
    
    def GetShortDesc(self):
        return f"Imitating your last attack for {round(self.CalculateDamage() * (1 - gc.playerCharacter.GetDamageResist()))} damage!"
    
class MimicLureAction(AAction):
    def __init__(self):
        super().__init__()
        self.actionColor = Fore.YELLOW
        self.lureAmount = 0
    
    def PerformAction(self):
        self.lureAmount = random.randrange(15, 45)
        gc.playerCharacter.GiveGold(self.lureAmount)
        self.parentEntity.storedLureGold = (getattr(self.parentEntity, 'storedLureGold', 0) + self.lureAmount)
        print(f"{Fore.YELLOW}The Mimic spits out {self.lureAmount} gold! ...it glitters enticingly.{Fore.RESET}")
        return super().PerformAction()
    
class SacrificeAction(AAction):
    def __init__(self, healthSacrifice: int, allyName: str, damageBuff: float):
        super().__init__()
        self.healthSacrifice = healthSacrifice
        self.allyName = allyName
        self.actionColor = Fore.YELLOW

    def PerformAction(self):
        import AttackInfo
        # Implementation for sacrificing health to buff an ally
        print(f"{self.parentEntity.name} sacrifices {self.healthSacrifice} HP to empower {self.allyName}!")
        allies = gc.GetAllEnemiesOfName(self.allyName)
        if allies is None:
            return super().PerformAction()
            
        for ally in allies:
            if ally.name == self.allyName:
                ally.outgoingDamageMultiplier += self.damageBuff
                print(f"{ally.name} feels empowered by the sacrifice!")
                break
        self.parentEntity.Damage(AttackInfo.AttInfo(self.healthSacrifice, self.parentEntity, True, 1.0))
        return super().PerformAction()

class BuffAlliesAction(AAction):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount
        self.actionColor = Fore.YELLOW

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
        self.actionColor = Fore.WHITE

    def PerformAction(self):
        return super().PerformAction()
    
class TransformAction(AAction):
    def __init__(self, transformTo: int | str, count: int = 1):
        super().__init__()
        self.transformTo = transformTo
        self.count = count

    def PerformAction(self):
        import Enemies
        for _ in range(self.count):
            enemy_to_spawn = None
            if isinstance(self.transformTo, int):
                enemy_to_spawn = Enemies.CreateEnemyByIndex(self.transformTo, self.parentEntity.level)
            else:
                enemy_to_spawn = Enemies.CreateEnemyByName(self.transformTo, self.parentEntity.level)
            if enemy_to_spawn is None:
                return super().PerformAction()
            print(f"{self.parentEntity.name} has transformed into {enemy_to_spawn.name}")
            gc.SpawnEnemy(enemy_to_spawn, True)

        gc.RemoveEnemyFromScene(self.parentEntity)
        return super().PerformAction()
    
    def GetShortDesc(self):
        import Enemies
        enemy_to_spawn = None
        if isinstance(self.transformTo, int):
            enemy_to_spawn = Enemies.GetByIndex(self.transformTo)
        else:
            enemy_to_spawn = Enemies.GetByName(self.transformTo)
        if enemy_to_spawn is not None:
            return super().GetShortDesc() + enemy_to_spawn.name
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
        self.actionColor = Fore.YELLOW

    def PerformAction(self):
        import StatusEffect
        StatusEffect.Apply(self.parentEntity, self.effect, self.stacks)
        return super().PerformAction()
    
class EmberlingGrow(AAction):
    def __init__(self):
        super().__init__()
        self.actionColor = Fore.YELLOW

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
        print(f"{self.parentEntity.name} applies {self.effect(None).GetName()} to the player!")
        return super().PerformAction()
    
class DamageBasedOnThornsAction(AttackAction):
    def __init__(self, thornsDamageMultiplier: float):
        self.thornsDamageMultiplier = thornsDamageMultiplier
        super().__init__(0)
    
    def CalculateDamage(self):
        self.damage = int(self.parentEntity.thorns * self.thornsDamageMultiplier)
        return super().CalculateDamage()
    
class ProtectAction(AAction):
    def __init__(self, protectAmount: int):
        super().__init__()
        self.protectAmount = protectAmount
        self.actionColor = Fore.YELLOW

    def PerformAction(self):
        self.parentEntity.AddShield(self.protectAmount)
        print(f"{self.parentEntity.name} shields itself!")
        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.protectAmount}!"
    
class ShieldAndHealAction(AAction):
    def __init__(self, shieldAmount: int, healAmount: int):
        super().__init__()
        self.shieldAmount = shieldAmount
        self.healAmount = healAmount
        self.actionColor = Fore.YELLOW

    def PerformAction(self):
        self.parentEntity.AddShield(self.shieldAmount)
        self.parentEntity.Heal(self.healAmount)
        print(f"{self.parentEntity.name} shields itself and heals!")
        return super().PerformAction()
    
    def GetShortDesc(self):
        return super().GetShortDesc() + f" for {self.shieldAmount} shield and {self.healAmount} HP!"
    
class TotallyHarmlessWiggleAction(AAction):
    HEALTH_INCREMENT = 20
    def __init__(self):
        super().__init__()
        self.actionColor = Fore.WHITE

    def PerformAction(self):
        self.parentEntity.SetMaxHealth(self.parentEntity.maxHealth + TotallyHarmlessWiggleAction.HEALTH_INCREMENT)
        self.parentEntity.health += TotallyHarmlessWiggleAction.HEALTH_INCREMENT
        print(f"{self.parentEntity.name} wiggles harmlessly...")
        return super().PerformAction()
    
class HemorrhageFeastAction(AAction):
    BLEED_THRESHOLD = 4       # Minimum stacks to trigger
    DAMAGE_PER_STACK = 5      # Damage per Bleed stack consumed
    STACKS_CONSUMED = 3       # How many Bleed stacks it eats
    HEAL_FLAT = 18

    def CanDoAction(self):
        if not super().CanDoAction():
            return False
        import StatusEffect
        bleed = gc.playerCharacter.GetEffect(StatusEffect.BleedEffect)
        return bleed is not None and bleed.stacks >= self.BLEED_THRESHOLD

    def PerformAction(self):
        import StatusEffect
        from AttackInfo import AttInfo
        bleed = gc.playerCharacter.GetEffect(StatusEffect.BleedEffect)
        damage = self.DAMAGE_PER_STACK * bleed.stacks
        gc.playerCharacter.Damage(AttInfo(damage, None, True))  # ignores evasion - it's feeding on existing wounds
        bleed.RemoveStack(self.STACKS_CONSUMED)
        self.parentEntity.Heal(self.HEAL_FLAT)
        print(f"{Fore.RED}{Style.BRIGHT}The Vampire feasts on your hemorrhaging wounds!{Style.RESET_ALL}")
        return super().PerformAction()

    def GetShortDesc(self):
        import StatusEffect
        bleed = gc.playerCharacter.GetEffect(StatusEffect.BleedEffect)
        if bleed is None or bleed.stacks < self.BLEED_THRESHOLD:
            return "Watching your wounds... (needs 4+ Bleed)"
        return f"Preparing to feast on your {bleed.stacks} Bleed stacks ({bleed.stacks * self.DAMAGE_PER_STACK} damage)!"
    
class SorrowFeedAction(AAction):
    def __init__(self, damagePerDebuff: int = 1):
        super().__init__()
        self.damagePerDebuff = damagePerDebuff
        self.actionColor = Fore.YELLOW

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
        super().__init__()
        self.escapeTaunt: str = escapeTaunt
        self.actionColor = Fore.YELLOW

    def PerformAction(self):
        from colorama import Fore, Style
        if len(self.escapeTaunt) > 0:
            print(f"[#{gc.GetIndexOfEnemy(self.parentEntity)}][LVL {self.parentEntity.level}] {self.parentEntity.name}: Ha ha! Sucker!")
        gc.RemoveEnemyFromScene(self.parentEntity)
        print(f"{Fore.RED}{Style.BRIGHT}{self.parentEntity.name}{Style.NORMAL} escaped!{Style.RESET_ALL}")
        return super().PerformAction()
    
class VirulentBloomAction(AAction):
    def __init__(self):
        super().__init__()

    def PerformAction(self):
        import StatusEffect
        StatusEffect.Apply(gc.playerCharacter, StatusEffect.InfectionEffect, self.parentEntity.GetSporeCount() * self.parentEntity.BLOOM_STACKS)
        return super().PerformAction()
    
    def GetShortDesc(self):
        return f"Blooming {self.parentEntity.GetSporeCount()} spores to apply {self.parentEntity.GetSporeCount() * self.parentEntity.BLOOM_STACKS} infection"
    
class ConsumeSporeAction(AAction):
    def __init__(self):
        super().__init__()

    def PerformAction(self):
        if self.parentEntity.GetSporeCount() < self.parentEntity.SPORE_TARGET_AMOUNT:
            self.parentEntity.Heal(25)
        return super().PerformAction()
    
class PlagueHeartReformAction(SummonAction):
    def PerformAction(self):
        self.parentEntity.reformed = True
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
        self.SetCurrentActionIndex(self.actionIndex)
        self.ValidateCurrentAction()

    def ForceAction(self, actionToForce: int | str):
        if isinstance(actionToForce, int):
            self.SetCurrentActionIndex(actionToForce)
            self.GetAction().forced = True
        else:
            for i, action in enumerate(self.actions):
                if action.actionName == actionToForce:
                    self.SetCurrentActionIndex(i)
                    self.GetAction().forced = True
                    break

    def ValidateCurrentAction(self, checkChance: bool = True):
        if self.GetAction().forced:
            return
        if not self.GetAction().CanDoAction() or (checkChance and not random.random() <= self.GetAction().chance):
            self.SetCurrentActionIndex(self.CycleNextAction())

    def GetAction(self, index: int | None = None) -> AAction | None:
        if len(self.actions) <= 0:
            return None
        if type(index) is not int:
            index = self.actionIndex
        return self.actions[index]
    
    def SetCurrentActionIndex(self, index: int):
        self.actionIndex = index
        self.currentActionPerformedCount = 0
        self.actions[self.actionIndex].OnActionSet()

        # Figure out how many times to repeat this action
        repeatRange: int | range = self.actions[self.actionIndex].repeatAmount
        self.toRepeat = repeatRange if (type(repeatRange) is int) else (random.randrange(repeatRange.start, repeatRange.stop, repeatRange.step)) # type: ignore
        pass
        
    def PerformNextAction(self):
        nextAction = self.GetAction()
        if nextAction is None:
            return
        
        nextAction.PerformAction()
        self.currentActionPerformedCount += 1

        # guard clause to repeat current action if we need to
        if (self.toRepeat > self.currentActionPerformedCount):
            return

        self.SetCurrentActionIndex(self.CycleNextAction())

    def AppendAction(self, action: AAction):
        if issubclass(type(action), AAction) != True:
            raise TypeError(f"Type {type(action)} is not an Action!")
        
        self.actions.append(action)

    def CycleNextAction(self):
        # Cycle to find next availible action to take
        index = self.actionIndex
        while True:
            limit = 100
            index += 1
            if (index >= len(self.actions)):
                index = 0

            nextAction = self.GetAction(index)
            if nextAction is None:
                break

            # Guard clauses my beloved
            if (limit <= 0 or len(self.actions) == 1):
                break
            if (random.random() <= nextAction.chance and nextAction.CanDoAction()):
                break
            limit -= 1
        return index

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
