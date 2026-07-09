import copy
from math import floor
import EventSystem
import ItemSystem
from abc import ABC
import GameCore as gc
import LevelHandler
import random
from colorama import Fore, Back, Style
import Actions
from EnemyTags import EnemyTag
import Relics
from AttackInfo import AttInfo
import StatusEffect

class AEntity(ABC):
    def __init__(self):
        from StatusEffect import AEffect
        self.health = 100
        self.name = "Unnamed Entity"
        self.level = 1
        self.maxHealth = self.health
        self._additionalRawDamage = 0
        self._outgoingDamageMultiplier = 1.0
        self.effects: list[AEffect] = []
        self._evasion = 0.0
        self._damageResistance = 0.0
        self.shield = 0
        self.lifesteal = 0.0
        self.damageReflect = 0.0
        self.stunCount = 0
        self._healingMultiplier = 1.0
        self.thorns: int = 0
        self.tempHealth = 0
        self.maxTempHealth = 0
        self.shieldStartOfTurnMult: float = 0.0
        self.turnsAlive = 0

    def OnSpawn(self):
        pass

    def GetHealthPercent(self) -> float:
        return self.health / self.maxHealth

    def ApplyStun(self, count: int):
        self.stunCount += count
        print(f"{Fore.YELLOW}{Style.DIM}{self.name} is stunned for {self.stunCount} turn{'s' if self.stunCount > 1 else ''}!{Style.RESET_ALL}")

    def OnEffectApply(self, effect):
        for eff in self.effects:
            if type(eff) is type(effect):
                # effect already exists on entity
                eff.AddStack(effect.stacks)
                return
            
        # apply a NEW effect
        effect.OnEffectApply()    
        self.effects.append(effect)
        pass

    def AddShield(self, amount: int):
        self.SetShield(self.shield + amount)

    def SetShield(self, amount: int):
        self.shield = amount

    def GetAdditionalDesc(self) -> str:
        string = str()
        if hasattr(self, "gold"):
            string = f" [GOLD: {Fore.YELLOW}{Style.BRIGHT}{int(getattr(self, 'gold'))}{Style.RESET_ALL}]"

        return string
    
    def set_additionalRawDamage(self, value: int):
        self._additionalRawDamage = value

    def get_additionalRawDamage(self) -> int:
        return self._additionalRawDamage

    def GetDamageResist(self) -> float:
        return min(0.8, self.damageResistance)
    
    def GetBonusHealthText(self) -> str:
        text = str()
        if self.shield > 0:
            text += f" ({Style.BRIGHT}{Fore.CYAN}{self.shield}{Style.RESET_ALL})"

        if self.tempHealth > 0:
            text += f" ({Style.DIM}{Fore.YELLOW}{self.tempHealth}{Style.RESET_ALL})"
        return text

    def DoTurn(self):
        import StatusEffect
        self.turnsAlive += 1
        effectsToRemove = []
        for effect in self.effects:
            effect.OnEffectTick()
            if effect.stacks <= 0:
                effectsToRemove.append(effect)

        for effect in effectsToRemove:
            self.RemoveEffect(effect)
        pass

    def HandleNewTurn(self):
        import StatusEffect, SkillSystem
        if not self.HasEffect(StatusEffect.FortitudeEffect):
            self.SetShield(round(self.shield * self.shieldStartOfTurnMult))

    def RemoveEffect(self, effect):
        self.effects.remove(effect)
        effect.OnEffectRemove()

    def RemoveEffectStack(self, effectType: type, amount: int = 1):
        try:
            effect = self.GetEffect(effectType)
            if effect is None:
                return
            effect.RemoveStack(amount)
        except:
            pass

    def ClearStatusEffects(self, ignorePositive = False):
        for effect in reversed(self.effects):
            if ignorePositive and effect.positive:
                continue
            self.RemoveEffect(effect)

    def HasEffect(self, effectType: type) -> bool:
        return self.GetEffect(effectType) is not None
    
    def GetEffectAmount(self, effectType: type) -> int:
        effect = self.GetEffect(effectType)
        return -1 if effect is None else effect.stacks
    
    def Cleanup(self):
        pass

    def SetName(self, name: str):
        self.name = name
        return self
    
    def SetLevel(self, level: int):
        self.level = level
        return self
    
    def IncreaseMaxHealth(self, amount: int):
        self.maxHealth += amount
        self.health += amount
    
    def SetMaxHealth(self, max: int, setHealthToo: bool = False):
        self.maxHealth = max
        if setHealthToo:
            self.SetHealth(max)
        self.health = min(self.health, self.maxHealth)
        return self
    
    def SetHealth(self, hp: int):
        self.health = hp
        return self
    
    def Kill(self):
        global e_EntityDeath
        e_EntityDeath.Trigger(self)

    def OnEvade(self, attackInfo: AttInfo):
        print(f"{self.name} evaded the attack!")

    def Damage(self, attackInfo: AttInfo) -> int:
        from ElementTags import ElementTag
        from StatusEffect import OnFireEffect, PoisonEffect, Apply
        import SkillSystem as sk
        if self.health <= 0 or attackInfo.damage == 0:
            return 0
        if not attackInfo.ignoresEvasion and self.CheckEvasion():
            self.OnEvade(attackInfo)
            return 0
        
        # Apply damage resistance
        attackInfo.damage -= int(attackInfo.damage * self.GetDamageResist())
        initalAttackDamageBeforeBlocked = attackInfo.damage
        
        # Deduct from shield first
        if self.shield > 0 and attackInfo.damage > 0:
            shieldDamage = abs(int(attackInfo.damage * (1.0 - attackInfo.shieldPierce)))
            blocked = 0
            if shieldDamage <= self.shield:
                self.AddShield(-shieldDamage)
                blocked = shieldDamage
                attackInfo.damage -= shieldDamage
            else:
                attackInfo.damage -= self.shield
                blocked = self.shield
                self.SetShield(0)

            print(f"{self.name} blocked {Fore.CYAN}{blocked}{Fore.RESET} damage!")

        # Then from temp health
        if self.tempHealth > 0:
            absorbed = 0
            if attackInfo.damage <= self.tempHealth:
                self.tempHealth -= attackInfo.damage
                absorbed = attackInfo.damage
                attackInfo.damage = 0
            else:
                attackInfo.damage -= self.tempHealth
                absorbed = self.tempHealth
                self.tempHealth = 0
            
            print(f"{self.name} absorbed {Fore.YELLOW}{absorbed}{Fore.RESET} damage!")
        
        if attackInfo.damage > 0:
            if attackInfo.damage >= 30:
                style = f"{Fore.RED}{Style.BRIGHT}"
            elif attackInfo.damage >= 15:
                style = f"{Fore.RED}{Style.NORMAL}"
            else:
                style = f"{Fore.RED}{Style.DIM}"
            print(f"{style}{self.name} took {attackInfo.damage} damage!{Style.RESET_ALL}")
            if attackInfo.HasElement(ElementTag.FIRE) and random.random() <= 0.5:
                Apply(self, OnFireEffect, 1)

        # Finally to health
        self.health -= attackInfo.damage
        
        # Handle attacker effects (lifesteal, reflect, thorns)
        attacker = attackInfo.attacker
        if attacker is not None:
            if attacker.lifesteal > 0:
                heal_amount = round(attackInfo.damage * attacker.lifesteal)
                if heal_amount > 0:
                    attacker.Heal(heal_amount)
            
            if self.damageReflect > 0:
                reflected = round(initalAttackDamageBeforeBlocked * self.damageReflect)
                attacker.Damage(AttInfo(reflected))
                print(f"{Fore.RED}{self.name} reflected {Style.BRIGHT}{reflected}{Style.NORMAL} damage back at {attacker.name}!{Fore.RESET}")
            
            if self.thorns > 0:
                attacker.Damage(AttInfo(self.thorns))

            if attacker is gc.playerCharacter:
                toxicCoatingRank = sk.GetSkillNodeRank("sknd_toxiccoating")
                if toxicCoatingRank > 0 and random.random() < sk.POISON_TOXIC_COATING_CHANCE * toxicCoatingRank:
                    Apply(self, PoisonEffect, sk.POISON_TOXIC_COATING_AMOUNT)
        
        if self.health <= 0:
            self.Kill()
        return attackInfo.damage

    def CheckEvasion(self) -> bool:
        if (self.evasion <= 0.0):
            return False
        roll = random.uniform(0.0, 1.0)
        if (roll < self.evasion):
            return True
        return False

    def Heal(self, amount: int):
        if amount == 0:
            return False
        
        amount = round(amount * self.healingMultiplier)
        
        self.health += amount
        if (self.health > self.maxHealth):
            diff = self.health - self.maxHealth
            self.tempHealth += diff
            self.tempHealth = min(self.maxTempHealth, self.tempHealth)
            self.health = self.maxHealth

        print(self.name + " healed for " + str(amount) + " health!")
        return True
    
    def GetEffectListText(self) -> str | None:
        if len(self.effects) <= 0:
            return None
        effectList = "["

        for effect in self.effects:
            effectList += f"{effect.GetName()} ({effect.stacks}), "

        return effectList[:-2] + "]"
    
    def GetRandomNegativeStatusEffect(self):
        from StatusEffect import AEffect
        negativeEffects: list[AEffect] = []
        for effect in self.effects:
            if not effect.positive:
                negativeEffects.append(effect)
        if len(negativeEffects) <= 0:
            return None
        return random.choice(negativeEffects)
    
    def GetEffect(self, effectType: type):
        for effect in self.effects:
            if type(effect) is effectType:
                return effect
        return None
    
    def GetEffectStacks(self, effectType: type) -> int:
        effect = self.GetEffect(effectType)
        if effect is None:
            return 0
        return effect.stacks
    
    def get_outgoingDamageMultiplier(self) -> float:
        return self._outgoingDamageMultiplier
    
    def set_outgoingDamageMultiplier(self, value: float):
        self._outgoingDamageMultiplier = value

    def get_healingMultiplier(self) -> float:
        return max(0, self._healingMultiplier)
    
    def set_healingMultiplier(self, value: float):
        self._healingMultiplier = value

    def get_damageResistance(self) -> float:
        return self._damageResistance
    
    def set_damageResistance(self, value: float):
        self._damageResistance = value

    def get_evasion(self) -> float:
        return min(0.75, self._evasion)
    
    def set_evasion(self, value: float):
        self._evasion = value
        
    # properties
    additionalRawDamage = property(get_additionalRawDamage, set_additionalRawDamage)
    outgoingDamageMultiplier = property(get_outgoingDamageMultiplier, set_outgoingDamageMultiplier)
    healingMultiplier = property(get_healingMultiplier, set_healingMultiplier)
    damageResistance = property(get_damageResistance, set_damageResistance)
    evasion = property(get_evasion, set_evasion)


e_EntityDeath = EventSystem.Event(AEntity)

class BasicEnemy(AEntity):
    def __init__(self):
        super().__init__()
        self.exp = range(1, 2)
        self.actionSet = None
        self.tags = []
        self.canSpawnInEncounters = True

    def OnSpawn(self):
        if self.actionSet is not None:
            self.actionSet.Setup(self)

        # scale health by level
        self.SetMaxHealth(round(self.maxHealth * (1 + 0.06 * (self.level - 1)) * float(gc.setDifficulty.value)), True)
        return super().OnSpawn()

    def SetDropExp(self, xp: range | int):
        self.exp = xp
        return self
    
    def DisableSpawnPool(self):
        self.canSpawnInEncounters = False
        return self
    
    def GetDangerRating(self) -> float:
        """Estimate how dangerous this enemy is for scaling and spawning."""
        score = float(self.maxHealth)
        score += float(self.shield) * 0.5
        score += float(self.tempHealth) * 0.4

        if self.actionSet is not None:
            for action in self.actionSet.actions:
                score += self._GetActionThreat(action)

        return max(0.0, score)

    def _GetAverageActionRepeats(self, repeatAmount: int | range) -> float:
        if isinstance(repeatAmount, range):
            if repeatAmount.step == 0:
                return 1.0
            last = repeatAmount.stop - repeatAmount.step
            return max(1.0, (repeatAmount.start + last) / 2)
        return float(repeatAmount)

    def _GetActionThreat(self, action) -> float:
        import Actions

        repeatCount = self._GetAverageActionRepeats(action.repeatAmount)
        chance = getattr(action, "chance", 1.0)

        if isinstance(action, Actions.EmberlingDetonate):
            return self.GetDetonateDamage() * repeatCount * chance
        if isinstance(action, Actions.DamageBasedOnThornsAction):
            damage = int(self.thorns * action.thornsDamageMultiplier)
            return damage * getattr(action, "attackCount", 1) * repeatCount * chance
        if isinstance(action, Actions.AttackAction):
            damage = getattr(action, "damage", 0)
            attackCount = getattr(action, "attackCount", 1)
            if isinstance(attackCount, range):
                attackCount = int((attackCount.start + attackCount.stop) / 2) if attackCount.stop != 0 else int(attackCount.start)
            return damage * attackCount * repeatCount * chance
        if isinstance(action, Actions.SummonAction):
            return 10.0 * getattr(action, "amount", 1) * repeatCount * chance
        if isinstance(action, Actions.ShieldAndHealAction):
            heal = getattr(action, "healAmount", 0)
            shield = getattr(action, "shieldAmount", 0)
            return (heal * 0.4 + shield * 0.3) * repeatCount * chance
        if isinstance(action, Actions.ProtectAction):
            return getattr(action, "protectAmount", 0) * 0.2 * repeatCount * chance
        if isinstance(action, Actions.HealAction):
            return getattr(action, "healing", 0) * 0.4 * repeatCount * chance
        if isinstance(action, Actions.HealRandomUndeadAction):
            return getattr(action, "healing", 0) * 0.5 * repeatCount * chance
        if isinstance(action, Actions.BuffAlliesAction):
            return getattr(action, "amount", 0) * 1.5 * repeatCount * chance
        if isinstance(action, Actions.ApplyEffectToPlayerAction):
            return getattr(action, "stacks", 0) * 4.0 * repeatCount * chance
        if isinstance(action, Actions.ApplyEffectToSelfAction):
            return getattr(action, "stacks", 0) * 1.0 * repeatCount * chance
        if isinstance(action, Actions.SorrowFeedAction):
            return getattr(action, "damagePerDebuff", 0) * 2.0 * repeatCount * chance
        if isinstance(action, Actions.StealAndAttackAction):
            damage = getattr(action, "damage", 0) * getattr(action, "attackCount", 1)
            return (damage + 5) * repeatCount * chance
        if isinstance(action, Actions.TotallyHarmlessWiggleAction):
            return 15.0 * repeatCount * chance
        if isinstance(action, Actions.TransformAction):
            return 12.0 * repeatCount * chance
        return 0.0

    def OnEffectApply(self, effect):
        import StatusEffect, SkillSystem
        if isinstance(effect, StatusEffect.PoisonEffect):
            venomousKeystoneCount = gc.playerCharacter.GetRelicCount(Relics.VenomousKeystone)
            if venomousKeystoneCount > 0:
                effect.AddStack(venomousKeystoneCount * Relics.VenomousKeystone.EXTRA_POISON)

            parasiticSporeheartCount = gc.playerCharacter.GetRelicCount(Relics.ParasiticSporeheart)
            if parasiticSporeheartCount > 0:
                gc.playerCharacter.Heal(parasiticSporeheartCount * Relics.ParasiticSporeheart.HEAL_ON_POISON)

        volatileReactionRank = SkillSystem.GetSkillNodeRank("sknd_volatilereactions")
        if not effect.positive and volatileReactionRank > 0:
            self.Damage(AttInfo(SkillSystem.ALCHEMY_VOLATILE_REACTIONS_DAMAGE * volatileReactionRank, None, True))

        return super().OnEffectApply(effect)
    
    def Kill(self):
        import Relics
        import Commands
        import StatusEffect
        import SkillSystem
        if self.exp == 0:
            return super().Kill()
        toDrop = self.level + random.randrange(self.exp.start, self.exp.stop) if type(self.exp) is range else self.exp
        gc.playerCharacter.level.GrantExperience(round(toDrop * gc.playerCharacter.experienceMultiplier))
        gc.playerCharacter.GiveGold(round(toDrop * gc.playerCharacter.goldMultiplier))

        soulbinderCharmCount = gc.playerCharacter.GetRelicCount(Relics.SoulbinderCharm)
        if soulbinderCharmCount > 0:
            Relics.SoulbinderCharm.Trigger()
            if (random.random() < Relics.SoulbinderCharm.RELIC_DROP_CHANCE * soulbinderCharmCount):
                gc.GiveRelicReward()

        noWitnessRank = SkillSystem.GetSkillNodeRank("sknd_nowitnesses")
        if noWitnessRank > 0:
            gc.playerCharacter._tempEvasionBonus += SkillSystem.SHADOW_NO_WITNESSES_EVASION_BONUS * noWitnessRank

        if gc.playerCharacter.HasRelic(Relics.SoulvesselJar):
            Relics.soulvesselJarKillsNeeded -= 1
            if Relics.soulvesselJarKillsNeeded <= 0:
                Relics.soulvesselJarKillsNeeded = 20
                print(f"{Fore.CYAN}Your {Style.BRIGHT}Soulvessel Jar{Style.RESET_ALL}{Fore.CYAN} has filled and grants you a their energy!{Style.RESET_ALL}")
                gc.playerCharacter.maxStamina += 1

        if hasattr(self, "gold"):
            gc.playerCharacter.GiveGold(int(getattr(self, "gold")))

        smolderingCoreCount = gc.playerCharacter.GetRelicCount(Relics.SmolderingCore)
        if smolderingCoreCount > 0:
            Relics.TriggerSmolderingCore(Relics.SmolderingCore.SPREADING_FIRE_DAMAGE_ON_KILL * smolderingCoreCount)

        graveDustLedgerCount = gc.playerCharacter.GetRelicCount(Relics.GravedustLedger)
        if graveDustLedgerCount > 0:
            gc.playerCharacter.bonusAttacks += Relics.GravedustLedger.BONUS_ATTACKS_PER_KILL * graveDustLedgerCount
            print(f"{Fore.CYAN}Your {Style.BRIGHT}Gravedust Ledger{Style.RESET_ALL}{Fore.CYAN} has granted you {Relics.GravedustLedger.BONUS_ATTACKS_PER_KILL * graveDustLedgerCount} bonus attack{'s' if Relics.GravedustLedger.BONUS_ATTACKS_PER_KILL * graveDustLedgerCount > 1 else ''}!{Style.RESET_ALL}")
        
        if gc.playerCharacter.HasRelic(Relics.ContagionVial):
            # check if enemy has any effects that can be spread
            for effect in self.effects:
                if type(effect) in Relics.ContagionVial.GetRelevantEffects():
                    enemyList = copy.copy(gc.enemiesInScene)
                    enemyList.remove(self)
                    if len(enemyList) == 0:
                        continue
                    unluckyEnemy = random.choice(enemyList)
                    StatusEffect.Apply(unluckyEnemy, type(effect), effect.stacks)
                    print(f"{Fore.GREEN}The {Style.BRIGHT}Contagion Vial{Style.NORMAL} has spread {effect.GetName()} to {unluckyEnemy.name}!{Style.RESET_ALL}")

        carrionCount = gc.playerCharacter.GetRelicCount(Relics.CarrioncoreGland)
        if carrionCount > 0:
            gc.playerCharacter.maxHealth += Relics.CarrioncoreGland.MAX_HEALTH_GAIN * carrionCount
            gc.playerCharacter.health += Relics.CarrioncoreGland.MAX_HEALTH_GAIN * carrionCount

        feastEternalRank = SkillSystem.GetSkillNodeRank("sknd_feasteternal")
        if feastEternalRank > 0 and self.HasEffect(StatusEffect.BleedEffect):
            gc.playerCharacter._tempDamageBonus += SkillSystem.VAMPIRIC_FEAST_ETERNAL_DAMAGE_BONUS * feastEternalRank
            gc.playerCharacter.Heal(SkillSystem.VAMPIRIC_FEAST_ETERNAL_HEAL * feastEternalRank)

        plagueDeathRank = SkillSystem.GetSkillNodeRank("sknd_plaguedeath")
        poisonAmount = self.GetEffectAmount(StatusEffect.PoisonEffect)
        if plagueDeathRank > 0 and poisonAmount > 0:
            otherEnemies = copy.copy(gc.enemiesInScene)
            otherEnemies.remove(self)
            if len(otherEnemies) > 0:
                for enemy in otherEnemies:
                    StatusEffect.Apply(enemy, StatusEffect.PoisonEffect, max(1, floor(poisonAmount / len(otherEnemies))))

        reagentHarvestRank = SkillSystem.GetSkillNodeRank("sknd_reagentharvest")
        if reagentHarvestRank > 0 and random.random() < SkillSystem.ALCHEMY_REAGENT_HARVEST_CHANCE * reagentHarvestRank:
            potionsInInventory = [item for item in gc.playerCharacter.items if isinstance(item, ItemSystem.Potion)]
            if len(potionsInInventory) > 0:
                potion = random.choice(potionsInInventory)
                potion.useCount += 1
                print(f"{Fore.CYAN}Your {Style.BRIGHT}{potion.name}{Style.NORMAL}{Fore.CYAN} has been replenished by {SkillSystem.ALCHEMY_REAGENT_HARVEST_USE_RESTORE}!{Style.RESET_ALL}")

        return super().Kill()
    
    def Damage(self, attackInfo: AttInfo) -> int:
        import SkillSystem

        if self.HasTag(EnemyTag.IMMUNE_TO_DAMAGE):
             return 0

        executionersMarkCount = gc.playerCharacter.GetRelicCount(Relics.ExecutionersMark)
        if executionersMarkCount > 0 and self.GetHealthPercent() <= Relics.ExecutionersMark.HP_THRESHOLD:
            attackInfo.damage = round(attackInfo.damage * (1 + Relics.ExecutionersMark.ADDITIONAL_DAMAGE * executionersMarkCount))

        if isinstance(attackInfo.attacker, Player):
            import StatusEffect
            if gc.playerCharacter.HasRelic(Relics.ClockworkBloodgear):
                if gc.currentAttacksCount % Relics.ClockworkBloodgear.HIT_THRESHOLD == 0:
                    attackInfo.damage = round(attackInfo.damage * Relics.ClockworkBloodgear.HIT_BONUS)
            gc.currentAttacksCount += 1

            carrionCount = gc.playerCharacter.GetRelicCount(Relics.CarrioncoreGland)
            if carrionCount > 0 and self.HasEffect(StatusEffect.InfectionEffect):
                attackInfo.damage = round(attackInfo.damage * (1 + Relics.CarrioncoreGland.DAMAGE_ADDITION * carrionCount))

            serratedBlowsRank = SkillSystem.GetSkillNodeRank("sknd_serratedblows")
            if serratedBlowsRank > 0 and random.random() < SkillSystem.VAMPIRIC_SERRATED_BLOWS_CHANCE * serratedBlowsRank:
                StatusEffect.Apply(self, StatusEffect.BleedEffect, 1)

            cripplingBlowsRank = SkillSystem.GetSkillNodeRank("sknd_cripplingblows")
            if cripplingBlowsRank > 0:
                StatusEffect.Apply(self, StatusEffect.Weakness, 1)

            taintedBladeRank = SkillSystem.GetSkillNodeRank("sknd_taintedblade")
            if taintedBladeRank > 0 and random.random() < SkillSystem.ALCHEMY_TAINTED_BLADE_CHANCE * taintedBladeRank:
                negativeEffects: list[tuple[type, int]] = []
                for item in gc.playerCharacter.items:
                    if not isinstance(item, ItemSystem.Potion):
                        continue

                    if getattr(item, "effectToApply", None) is not None:
                        effectType = item.effectToApply
                        if getattr(effectType, "positive", False) is False:
                            negativeEffects.append((effectType, item.effectStacks))

                    for effectType, stacks in getattr(item, "effects", []):
                        if getattr(effectType, "positive", False) is False:
                            negativeEffects.append((effectType, stacks))

                if len(negativeEffects) > 0:
                    effectType, stacks = random.choice(negativeEffects)
                    if StatusEffect.Apply(self, effectType, stacks):
                        try:
                            effectName = effectType(self, stacks).GetName()
                        except Exception:
                            effectName = effectType.__name__
                        print(f"{Fore.RED}Tainted Blade applies {effectName} to {self.name}!{Fore.RESET}")

        return super().Damage(attackInfo)
    
    def AttachActionSet(self, actionSet: Actions.ActionSet):
        self.actionSet = copy.deepcopy(actionSet)
        return self

    def DoTurn(self):
        super().DoTurn()
        if (self.health <= 0):
            return
        if gc.playerCharacter.HasRelic(Relics.MindshackleTalisman):
            if random.randrange(0, 100) < int(Relics.MindshackleTalisman.SKIP_TURN_CHANCE * 100):
                print(f"{Fore.MAGENTA}The {Style.BRIGHT}{self.name}{Style.NORMAL}{Fore.MAGENTA} is unable to act this turn!{Style.RESET_ALL}")
                return
        if self.stunCount > 0:
            self.stunCount -= 1
            print(f"{Fore.MAGENTA}The {Style.BRIGHT}{self.name}{Style.NORMAL}{Fore.MAGENTA} is stunned and cannot act this turn!{Style.RESET_ALL}")
            return
        if self.actionSet != None:
            self.actionSet.PerformNextAction()

    def HandleNewTurn(self):
        import SkillSystem, StatusEffect
        if self.GetEffectAmount(StatusEffect.PoisonEffect) >= SkillSystem.POISON_NEUROTOXINS_THRESHOLD:
            neurotoxinsRank = SkillSystem.GetSkillNodeRank("sknd_neurotoxins")
            if neurotoxinsRank > 0 and random.random() < SkillSystem.POISON_NEUROTOXINS_STUN_CHANCE * neurotoxinsRank:
                self.ApplyStun(1)
        return super().HandleNewTurn()

    def SetTags(self, *tags: str):
        self.tags = list(tags)
        return self

    def AddTags(self, *tags: str):
        for tag in tags:
            if self.HasTag(tag):
                continue
            self.tags.append(tag)
        return self
    
    def RemoveTag(self, tag: str):
        if tag in self.tags:
            self.tags.remove(tag)
    
    def HasTag(self, *tags: str):
        for tagInList in tags:
            for t in self.tags:
                if t == tagInList:
                    return True
        return False
    
    def get_outgoingDamageMultiplier(self) -> float:
        import SkillSystem
        import StatusEffect
        multiplier = super().get_outgoingDamageMultiplier()
        heatExhaustionRank = SkillSystem.GetSkillNodeRank("sknd_heatexhaustion")
        if heatExhaustionRank > 0 and self.HasEffect(StatusEffect.OnFireEffect):
            multiplier *= 1 - (SkillSystem.PYRO_HEAT_EXHAUSTION_DAMAGE_REDUCTION * heatExhaustionRank)
        return multiplier
    
    outgoingDamageMultiplier = property(get_outgoingDamageMultiplier, AEntity.set_outgoingDamageMultiplier)
    
class NecromancerEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()
    
    def TryToRaiseDead(self, entity: BasicEnemy):
        import Enemies
        if (entity is self):
            return
        if (not issubclass(type(entity), BasicEnemy)):
            return
        if (entity.HasTag(EnemyTag.UNDEAD, EnemyTag.CANT_BE_UNDEAD)):
            return
        undead = Enemies.CreateEnemyByName(entity.name)
        if (undead == None):
            return
        undead.SetName(f"Undead {undead.name}")
        undead.SetMaxHealth(int(undead.maxHealth / 2))
        undead.SetHealth(undead.maxHealth)
        undead.AddTags(EnemyTag.UNDEAD)

        print(f"{self.name} is raising an {undead.name}!!")
        gc.SpawnEnemy(undead)

class TrollEnemy(BasicEnemy):
    HEAL_PER_TURN = 5
    def __init__(self):
        super().__init__()

    def DoTurn(self):
        self.Heal(self.HEAL_PER_TURN)
        print(f"The {self.name}'s wounds heal rapidly!")
        return super().DoTurn()
    
class EldtritchEntityEnemy(BasicEnemy):
    def OnSpawn(self):
        self.UpdateImmunity()
        return super().OnSpawn()

    def UpdateImmunity(self):
         cultists = gc.GetAllEnemiesOfName("Cultist")
         if len(cultists) > 0:
             self.AddTags(EnemyTag.IMMUNE_TO_DAMAGE)
         else:
             self.RemoveTag(EnemyTag.IMMUNE_TO_DAMAGE)

    def Damage(self, attackInfo):
        self.UpdateImmunity()
        if self.HasTag(EnemyTag.IMMUNE_TO_DAMAGE):
            print(f"{Fore.RED}{Style.BRIGHT}{self.name}{Style.NORMAL} is protected by the nearby cultists and takes no damage!{Style.RESET_ALL}")

        return super().Damage(attackInfo)
    
class PaleWardenEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()
        self.deadSouls = 0
        self.phaseTwo = False
        self.damageResistance += 0.2

    def GetBoundSoulCount(self):
        self.boundSouls = len(gc.GetAllEnemiesOfName("Bound Soul"))
        return self.boundSouls
    
    def HandleNewTurn(self):
        if self.health < self.maxHealth:
            totalHeal = 0
            for enemy in gc.enemiesInScene:
                if enemy.name == "Bound Soul":
                    totalHeal += enemy.Damage(AttInfo(5, self, True, 1))

            if totalHeal > 0:
                print(f"{Fore.YELLOW}Pale warden drains their bound souls for health...{Fore.RESET}")
                self.Heal(totalHeal)

        return super().HandleNewTurn()
    
    def Damage(self, attackInfo):
        damage = super().Damage(attackInfo)
        if not self.phaseTwo and damage != 0 and self.health <= self.maxHealth // 2:
            print(f"{Fore.GREEN}{Style.BRIGHT}The Wardens grip on their souls weaken! Killing souls now hurts the warden!")
            self.phaseTwo = True
        return damage
    
    def Heal(self, amount):
        healed = super().Heal(amount)
        if self.phaseTwo and healed and self.health > self.maxHealth // 2:
            print(f"{Fore.GREEN}{Style.BRIGHT}The Wardens grip on their souls weaken! Killing souls now hurts the warden!")
            self.phaseTwo = False
        return healed
    
    def HandleBoundSoulKilled(self):
        self.deadSouls += 1
        if self.phaseTwo:
            print(f"{Fore.GREEN}The released soul turns on it's weakened captor!")
            self.Damage(AttInfo(25, self, True, 1))
        else:
            print(f"{Fore.RED}The released soul returns to it's captor and heals them!")
            self.Heal(20)
    
class BoundSoulEnemy(BasicEnemy):
    def Kill(self):
        wardens = gc.GetAllEnemiesOfName("Pale Warden")
        for warden in wardens:
            warden.HandleBoundSoulKilled()
        return super().Kill()

class WraithEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()
        self.damageReflect = 0.5
    
class TransformOnDeathEnemy(BasicEnemy):
    def __init__(self, transformIndex: int, flavorText: str = "", amountToSpawn: int | range = 1):
        super().__init__()
        self.transformToIndex: int = transformIndex
        self.flavorText: str = flavorText
        self.amountToSpawn: int = amountToSpawn if type(amountToSpawn) is int else random.randrange(amountToSpawn.start, amountToSpawn.stop, amountToSpawn.step) # type: ignore

    def Kill(self):
        import Enemies
        if (self.flavorText != ""):
            print(f"{self.name} {self.flavorText}")

        for i in range(self.amountToSpawn):
            gc.SpawnEnemy(Enemies.CreateEnemyByIndex(self.transformToIndex, self.level), True)
        return super().Kill()
    
class EmberlingEnemy(BasicEnemy):
    EMBERLING_DAMAGE_MULT: float = 3
    def __init__(self):
        super().__init__()
        self.size = 1

    def Detonate(self):
        from ElementTags import ElementTag
        print(f"Emberling detonates itself!")
        gc.playerCharacter.Damage(AttInfo(self.GetDetonateDamage(), self).AddElements(ElementTag.FIRE))
        self.size = int(self.size * 0.5)

    def GetDetonateDamage(self) -> int:
        return round(self.size * EmberlingEnemy.EMBERLING_DAMAGE_MULT)

    def Kill(self):
        self.Detonate()
        return super().Kill()

    def GetAdditionalDesc(self) -> str:
        return super().GetAdditionalDesc() + f" [SIZE: {Fore.RED}{self.size}{Fore.RESET}]"
    
class MossboundGuardianEnemy(BasicEnemy):
    REGROW_AMOUNT = 10
    GROWTH_PREVENTION_TURNS = 3
    def __init__(self):
        self.growthCooldown = 0
        super().__init__()

    def DoTurn(self):
        super().DoTurn()
        if (self.growthCooldown > 0):
            self.growthCooldown -= 1
            if self.growthCooldown <= 0:
                print(f"The {self.name}'s moss starts to grow once more!")
            return
        self.tempHealth += MossboundGuardianEnemy.REGROW_AMOUNT
        print(f"{Fore.GREEN}The moss rapidly grows on the {self.name}.{Fore.RESET} (If only you could stop its growth...)")

    def Damage(self, attackInfo: AttInfo) -> int:
        from ElementTags import ElementTag
        if attackInfo.HasElement(ElementTag.FIRE):
            print(f"{Fore.RED}Fire burns the {Style.BRIGHT}{self.name}{Style.NORMAL} and prevents it's growth!{Style.RESET_ALL}")
            self.growthCooldown = MossboundGuardianEnemy.GROWTH_PREVENTION_TURNS
        return super().Damage(attackInfo)
    
class CarrionHorrorEnemy(BasicEnemy):
    def Kill(self):
        import Relics
        if not gc.playerCharacter.HasRelic(Relics.CarrioncoreGland):
            gc.GiveRelicReward(Relics.CarrioncoreGland())
        else:
            gc.GiveRelicReward()
        return super().Kill()

class IroncladEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()
        self.shieldStartOfTurnMult = 1.0

    def OnSpawn(self):
        self.SetShield(50)
        self.actionSet.actions[0].PerformAction()
        return super().OnSpawn()

    def Damage(self, attackInfo):
        from ElementTags import ElementTag
        if attackInfo.HasElement(ElementTag.LIGHTNING):
            print(f"{Fore.YELLOW}Lightning shocks the metalic armor around the {Style.BRIGHT}{self.name}{Style.NORMAL} stunning them!{Fore.RESET}")
            self.ApplyStun(1)
        return super().Damage(attackInfo)
    
class MagmaBeastEnemy(BasicEnemy):
    WATER_ELEMENT_WEAKNESS_DAMAGE_MULT = 1.5
    def Damage(self, attackInfo):
        from ElementTags import ElementTag
        if attackInfo.HasElement(ElementTag.WATER):
            print(f"{Fore.BLUE}Water{Fore.RESET} cools down the beast damaging it even more!")
            attackInfo.damage = round(attackInfo.damage * MagmaBeastEnemy.WATER_ELEMENT_WEAKNESS_DAMAGE_MULT)
        return super().Damage(attackInfo)
    
class VampireSpawnEnemy(BasicEnemy):
    BLOOD_THRESHOLD = 45      # HP healed before feeding
    POST_FEED_DAMAGE_MULT = 0.35
    POST_FEED_LIFESTEAL = 0.20

    def __init__(self):
        super().__init__()
        self.lifesteal = 0.25   # starts with meaningful lifesteal
        self.bloodConsumed = 0
        self.hasFed = False

    def Heal(self, amount: int):
        result = super().Heal(amount)
        if result and not self.hasFed:
            self.bloodConsumed += round(amount * self.healingMultiplier)
            if self.bloodConsumed >= self.BLOOD_THRESHOLD:
                self.Feed()
        return result

    def Feed(self):
        import Actions as AP
        self.hasFed = True
        self.outgoingDamageMultiplier += self.POST_FEED_DAMAGE_MULT
        self.lifesteal += self.POST_FEED_LIFESTEAL
        self.SetMaxHealth(round(self.maxHealth * 1.5), True)

        # Add the lunge to the action set
        lugeAction = AP.AttackAction(30).SetName("Predatory Lunge") \
            .SetShortDesc("Rushing with supernatural speed") \
            .SetAttackCount(2).SetChance(0.50) \
            .SetEffectsOnHit(StatusEffect.BleedEffect, StatusEffect.BleedEffect, StatusEffect.BleedEffect)
        self.actionSet.AppendAction(lugeAction)
        self.actionSet.Setup(self)

        print(f"{Fore.RED}{Style.BRIGHT}The Vampire Spawn has fed. Its wounds close and its eyes burn crimson.{Style.RESET_ALL}")
        print(f"It looks stronger than before...")

    def DoTurn(self):
        import StatusEffect
        # Passive: drain HP from the player's active Bleed each turn
        playerBleed = gc.playerCharacter.GetEffect(StatusEffect.BleedEffect)
        if playerBleed is not None and playerBleed.stacks > 0:
            passiveHeal = playerBleed.stacks * 2
            self.Heal(passiveHeal)
            print(f"{Fore.RED}The Vampire feeds on your wounds! ({Style.BRIGHT}+{passiveHeal}{Style.NORMAL} HP){Fore.RESET}")
        return super().DoTurn()

    def GetAdditionalDesc(self) -> str:
        fed = f" {Fore.RED}{Style.BRIGHT}[FED]{Style.RESET_ALL}" if self.hasFed else ""
        blood = f" [{Fore.RED}Blood: {self.bloodConsumed}/{self.BLOOD_THRESHOLD}{Fore.RESET}]" if not self.hasFed else ""
        return super().GetAdditionalDesc() + fed + blood
    
class MimicEnemy(BasicEnemy):
    def __init__(self):
        super().__init__()
        self.items = []
        self.lastPlayerAttack = 0
        self.storedLureGold = 0

    def DoTurn(self):
        if hasattr(self, 'storedLureGold') and self.storedLureGold > 0:
            taken = gc.playerCharacter.TakeGold(self.storedLureGold)
            print(f"{Fore.RED}The Mimic reclaims its fake gold! {taken} gold vanishes from your pouch!{Fore.RESET}")
            self.storedLureGold = 0
        return super().DoTurn()

    def Damage(self, attackInfo: AttInfo) -> int:
        if attackInfo.attacker is gc.playerCharacter:
            self.lastPlayerAttack = attackInfo.damage
        return super().Damage(attackInfo)

    def Kill(self):
        if len(self.items) > 0:
            for item in self.items:
                gc.playerCharacter.GiveItem(item)
        return super().Kill()
    
    def GetAdditionalDesc(self) -> str:
        stored_text = ""
        if len(self.items) > 0:
            stored_text = ", ".join(item.name for item in self.items)
        else:
            return super().GetAdditionalDesc()
        return super().GetAdditionalDesc() + f" Stored Items: {Fore.LIGHTYELLOW_EX}{stored_text}{Fore.RESET}"
    
class GiantSpiderEnemy(BasicEnemy):
    def get_outgoingDamageMultiplier(self) -> float:
        import StatusEffect
        multiplier = super().get_outgoingDamageMultiplier()
        if gc.playerCharacter.HasEffect(StatusEffect.WebbedEffect):
            multiplier *= 1.6
        return multiplier
    outgoingDamageMultiplier = property(get_outgoingDamageMultiplier, AEntity.set_outgoingDamageMultiplier)

class SlimeEnemy(BasicEnemy):
    def __init__(self, splitName: str):
        super().__init__()
        self.splitName = splitName
        self.splitting = False

    def Damage(self, attackInfo: AttInfo) -> int:
        import Actions as AP
        damageTaken = super().Damage(attackInfo)
        if not self.splitting and self.health <= self.maxHealth // 2:
            splitAction = AP.TransformAction(self.splitName, 2).SetName("Split") \
                .SetShortDesc("Splitting into ")
            self.actionSet = Actions.ActionSet()
            self.actionSet.AppendAction(splitAction)
            self.actionSet.Setup(self)
            self.splitting = True

        return damageTaken
    
class HollowedProphetEnemy(BasicEnemy):
    HIT_THRESHOLD = 3
    def __init__(self):
        super().__init__()
        self.hitsThisTurn = 0

    def Damage(self, attackInfo):
        damage = super().Damage(attackInfo)
        if attackInfo.attacker is gc.playerCharacter:
            self.hitsThisTurn += 1
        return damage
    
    def DoTurn(self):
        if self.hitsThisTurn >= self.HIT_THRESHOLD:
            gc.playerCharacter.Damage(AttInfo(self.hitsThisTurn * 8, self))
            print(f"Holy karmic justice has caused you to take {Fore.RED}{self.hitsThisTurn * 8}{Fore.RESET} damage for hitting {Style.BRIGHT}{self.name}{Style.NORMAL} {self.hitsThisTurn} times!")
        self.hitsThisTurn = 0
        return super().DoTurn()
    
    def GetAdditionalDesc(self):
        return super().GetAdditionalDesc() + f" [{Fore.RED}{self.hitsThisTurn}/{self.HIT_THRESHOLD} HITS{Fore.RESET}]"

class EffectOnDeathEnemy(BasicEnemy):
    def __init__(self, effectToApply: type | None, amount = 1):
        super().__init__()
        self.effectToApply: type | None = None
        self.amount = amount

    def Kill(self):
        if self.effectToApply is not None:
            StatusEffect.Apply(gc.playerCharacter, self.effectToApply, self.amount)
        return super().Kill()
    
class ShadowAssassinEnemy(BasicEnemy):
    # starts off really strong then weakens at specified turn
    WEAKEN_TURN = 3
    STRONG_MULT = 1.9
    WEAK_MULT = 0.5
    def get_outgoingDamageMultiplier(self) -> float:
        multiplier = super().get_outgoingDamageMultiplier()
        if self.turnsAlive < self.WEAKEN_TURN:
            multiplier *= self.STRONG_MULT
        else:
            multiplier *= self.WEAK_MULT
        return multiplier
    outgoingDamageMultiplier = property(get_outgoingDamageMultiplier, AEntity.set_outgoingDamageMultiplier)

class PlagueHeartEnemy(BasicEnemy):
    SPORE_TARGET_AMOUNT = 3
    BLOOM_STACKS = 2
    SHIELD_PER_INFECTION = 2
    SURGE_THRESHOLD = 8

    def __init__(self):
        super().__init__()
        self.reformed = False
        self.damageResistance += 0.1

    def DoTurn(self):
        infectionStacks = self.GetEffectAmount(StatusEffect.InfectionEffect)
        if infectionStacks > 0:
            self.AddShield(infectionStacks * self.SHIELD_PER_INFECTION)

        value = super().DoTurn()
        if self.turnsAlive % 3 == 0 and self.GetSporeCount() > 0:
            self.actionSet.ForceAction("Virulent Bloom")
        return value
    
    def GetSporeCount(self):
        return len(gc.GetAllEnemiesOfName("Plague Spore"))
    
    def IsPlayerSufficientlyInfected(self):
        return gc.playerCharacter.GetEffectAmount(StatusEffect.InfectionEffect) >= self.SURGE_THRESHOLD
    pass

class PlagueSporeEnemy(BasicEnemy):
    def Kill(self):
        print(f"{Fore.RED}The {self.name} bursts and spreads its infection{Fore.RESET}")
        gc.playerCharacter.Damage(AttInfo(15, self))
        for heart in gc.GetAllEnemiesOfType(PlagueHeartEnemy):
            StatusEffect.Apply(heart, StatusEffect.InfectionEffect, 4)
        return super().Kill()
    pass

class AshenRevenantEnemy(BasicEnemy):
    WISP_TARGET_COUNT = 2
    FURY_DAMAGE_THRESHOLD = 15
    FURY_IGNITE_AMOUNT = 5
    def __init__(self):
        super().__init__()
        self.damageResistance += 0.15
        self.fury: int = 0
        self.emberForm = False

    def Damage(self, attackInfo):
        damage = super().Damage(attackInfo)
        if damage >= self.FURY_DAMAGE_THRESHOLD:
            self.AddFury(int(damage / self.FURY_DAMAGE_THRESHOLD))
        if self.health <= self.maxHealth * 0.4 and not self.emberForm:
            self.emberForm = True
            print(f"{Fore.RED}{Style.BRIGHT}The injured {self.name} enters it\'s final form!{Style.RESET_ALL}")

    def AddFury(self, amount: int):
        print(f"{Fore.RED}Fury builds within the {Style.BRIGHT}{self.name}{Style.NORMAL}. The {Style.BRIGHT}{self.name}{Style.NORMAL} gains {Style.BRIGHT}{amount} fury{Style.NORMAL}{Style.RESET_ALL}")
        self.fury += amount
        if self.fury >= self.GetFuryIgniteThreshold():
            print(f"{Fore.RED}The {self.name}'s fury builds to a boiling point. {self.name} ignites it's embers!{Fore.RESET}")
            gc.playerCharacter.Damage(AttInfo(30 + self.fury * 12, self) if not self.emberForm else AttInfo(40 + self.fury * 15, self))
            self.fury = 0

    def GetFuryIgniteThreshold(self) -> int:
        threshold = self.FURY_IGNITE_AMOUNT
        if self.emberForm:
            threshold -= 1
        return threshold

    def GetTotalWisps(self):
        return len(gc.GetAllEnemiesOfName("Cinder Wisp"))
    
    def GetAdditionalDesc(self):
        return super().GetAdditionalDesc() + f" [{Fore.RED}FURY: {self.fury}/{self.GetFuryIgniteThreshold()}{Fore.RESET}]{"" if not self.emberForm else f" [{Fore.RED}EMBER FORM{Fore.RESET}]"}"

class CinderWispEnemy(BasicEnemy):
    def Kindle(self):
        for revenant in gc.GetAllEnemiesOfType(AshenRevenantEnemy):
            revenant.AddFury(1)

class Player(AEntity):
    def __init__(self):
        super().__init__()
        self.items = []
        self.maxStamina = 5
        self.stamina = self.maxStamina
        self.level = LevelHandler.LevelHandler()
        self.gold = 0
        self.relics: list[Relics.ARelic] = []
        self.critialHitChance: float = 0.05 # 5% base crit chance
        self.criticalHitMultiplier: float = 2.0
        self.applyBleedChance: float = 0.0
        self.bonusAttacks: int = 0
        self.goldMultiplier = 1.0
        self.lootDropChance = 1.0
        self.experienceMultiplier = 1.0
        self._tempDamageBonus = 0.0
        self._tempDamageResistanceBonus = 0.0
        self._tempEvasionBonus = 0.0
        self._nextTurnDamageBonusStored = 0.0
        self.shieldMultiplier = 1.0
        self.turnsSinceLastEvasion: int = 0
        self.successfulEvasionsThisCombat = 0

        # Skill triggers
        self._ironWillReady: bool = True
        self._unbreakableReady: bool = True

    def GiveRelic(self, relic: Relics.ARelic | None):
        if relic is None:
            return

        self.relics.append(relic)
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + relic.name + Style.RESET_ALL + " acquired by " + self.name + Style.RESET_ALL)
        relic.OnAcquire()

    def AddShield(self, amount: int):
        super().AddShield(round(amount * self.shieldMultiplier))

    def RemoveRelic(self, relicType: type):
        for relic in self.relics:
            if type(relic) is relicType:
                self.relics.remove(relic)
                print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + relic.name + Style.RESET_ALL + " removed from " + self.name + Style.RESET_ALL)
                return

    def GiveItem(self, item):
        if item is None:
            return

        self.items.append(copy.copy(item))
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + item.name + Style.RESET_ALL + " given to " + self.name + Style.RESET_ALL)

    def HasRelic(self, relicType: type) -> bool:
        for relic in self.relics:
            if type(relic) is relicType:
                return True
        return False
    
    def HasItem(self, itemName: str) -> bool:
        for item in self.items:
            if item.name == itemName:
                return True
        return False
    
    def GetAllItemsOfType(self, itemType: type) -> list:
        matching = []
        for item in self.items:
            if isinstance(item, itemType):
                matching.append(item)

        return matching
    
    def GetRandomItemOfType(self, itemType: type):
        # get all items that match that type
        matching = self.GetAllItemsOfType(itemType)

        if len(matching) <= 0:
            return None

        return random.choice(matching)
    
    def GetItemCount(self, itemName: str) -> int:
        count = 0
        for item in self.items:
            if item.name == itemName:
                count += 1
        
        return count
    
    def RemoveItem(self, itemName: str) -> bool:
        for i, item in enumerate(self.items):
            if item.name == itemName:
                self.items.pop(i)
                return True
        return False
    
    def GetRelicCount(self, relicType: type) -> int:
        count = 0
        for relic in self.relics:
            if type(relic) is relicType:
                count += 1
        return count

    def Damage(self, attackInfo: AttInfo) -> int:
        from ElementTags import ElementTag
        import StatusEffect
        import SkillSystem
        if (gc.godmode):
            print(f"Godly power has blocked {attackInfo.damage} damage.")
            return 0
        
        thermalShieldingRank = SkillSystem.GetSkillNodeRank("sknd_thermalshielding")
        if thermalShieldingRank > 0 and attackInfo.HasElement(ElementTag.FIRE):
            reduction = SkillSystem.PYRO_THERMAL_SHIELDING_DEFENSE_BONUS * thermalShieldingRank
            print(f"{Fore.YELLOW}Your Thermal Shielding skill reduces the fire damage by {round(reduction * 100)}%!{Fore.RESET}")
            attackInfo.damage = round(attackInfo.damage * (1 - reduction))
        
        verdantCrestCount = self.GetRelicCount(Relics.VerdantCrest)
        if verdantCrestCount > 0 and attackInfo.HasElement(ElementTag.FIRE):
            attackInfo.damage += round(attackInfo.damage * (Relics.VerdantCrest.FIRE_WEAKNESS_PERCENT * verdantCrestCount))

        if gc.playerCharacter.HasRelic(Relics.ClockworkBloodgear):
            if gc.currentHitsRecievedCount % Relics.ClockworkBloodgear.DAMAGE_THRESHOLD == 0:
                attackInfo.damage = round(attackInfo.damage * Relics.ClockworkBloodgear.DAMAGE_RECIEVED_BONUS)

        shockAbsorberCount = self.GetRelicCount(Relics.ShockAbsorber)
        if shockAbsorberCount > 0:
            attackInfo.damage = min(attackInfo.damage, Relics.ShockAbsorber.MAX_DAMAGE_RECIEVED)

        result = super().Damage(attackInfo)

        if shockAbsorberCount > 0:
            self.AddShield(Relics.ShockAbsorber.SHIELD_GAIN * shockAbsorberCount)

        if result != 0:
            wardensBulwarkCount = gc.playerCharacter.GetRelicCount(Relics.WardensBulwark)
            if wardensBulwarkCount > 0 and attackInfo.damage > Relics.WardensBulwark.DAMAGE_THRESHOLD:
                self.shield += Relics.WardensBulwark.GRANTED_DEFENSE * wardensBulwarkCount

            if isinstance(attackInfo.attacker, BasicEnemy):
                venomousKeystoneCount = self.GetRelicCount(Relics.VenomousKeystone)
                if attackInfo.attacker.HasEffect(StatusEffect.PoisonEffect) and venomousKeystoneCount > 0:
                    attackInfo.attacker.Damage(AttInfo(Relics.VenomousKeystone.POISONED_ATTACK_DAMAGE * venomousKeystoneCount))

                gc.currentHitsRecievedCount += 1
            
            painFueledPowerSkillRank = SkillSystem.GetSkillNodeRank("sknd_painfueledpower")
            if painFueledPowerSkillRank > 0:
                self._nextTurnDamageBonusStored += SkillSystem.BERSERKER_PAIN_FUELED_POWER_BONUS * painFueledPowerSkillRank

        return result
    
    def CheckEvasion(self) -> bool:
        import SkillSystem
        # force a fail to dodge if we have death or glory skill AND are within the health threshold
        if self.GetHealthPercent() <= SkillSystem.BERSERKER_DEATH_OR_GLORY_HP_THRESHOLD and SkillSystem.GetSkillNodeRank("sknd_deathorglory") > 0:
            return False
        ghostStepRank = SkillSystem.GetSkillNodeRank("sknd_ghoststep")
        if self.successfulEvasionsThisCombat == 0 and ghostStepRank > 0:
            return True
        
        return super().CheckEvasion()
    
    def GiveGold(self, amount: int):
        import SkillSystem
        self.gold += amount
        
        # skill check
        if SkillSystem.IsSkillNodeUnlocked("sknd_bloodforcoin"):
            healAmt = floor(amount / 5)
            if healAmt > 0:
                self.Heal(healAmt)

        print(f"{self.name} received {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}! Current gold: {Fore.YELLOW}{Style.BRIGHT}{self.gold}{Style.RESET_ALL}")

    def SpendGold(self, amount: int) -> bool:
        if (self.gold < amount):
            print(f"Not enough gold! Need {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}, has {Fore.YELLOW}{Style.BRIGHT}{self.gold} gold{Style.RESET_ALL}.")
            return False
        self.TakeGold(amount)
        print(f"{self.name} spent {Fore.YELLOW}{Style.BRIGHT}{amount} gold{Style.RESET_ALL}. Current gold: {Fore.YELLOW}{Style.BRIGHT}{self.gold}{Style.RESET_ALL}")
        return True
    
    def Kill(self):
        import SkillSystem
        if self._unbreakableReady and SkillSystem.GetSkillNodeRank("sknd_unbreakable") > 0:
            self.SetHealth(1)
            self._unbreakableReady = False
            print(f"{Fore.CYAN}Your unbreakable tenacity saved you from certain death!{Fore.RESET}")
            return
        if self.HasRelic(Relics.PhoenixFeather):
            print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}Phoenix Feather{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX} glows brightly, resurrecting {self.name}!{Style.RESET_ALL}")
            self.SetHealth(round(self.maxHealth * Relics.PhoenixFeather.REVIVE_HEALTH_PERCENT))
            self.RemoveRelic(Relics.PhoenixFeather)
            return
        return super().Kill()
    
    def OnEvade(self, attackInfo):
        import SkillSystem
        if self.HasRelic(Relics.PhantomSigil) and attackInfo.attacker is not None:
            attackInfo.attacker.Damage(AttInfo(Relics.PhantomSigil.DAMAGE_REFLECT))
        umbraVeilRank = SkillSystem.GetSkillNodeRank("sknd_umbralveil")
        if umbraVeilRank > 0:
            self._tempDamageResistanceBonus += umbraVeilRank * SkillSystem.SHADOW_UMBRAL_VEIL_DAMAGE_REDUCTION
        self.turnsSinceLastEvasion = 0
        self.successfulEvasionsThisCombat += 1
        return super().OnEvade(attackInfo)

    def GetGold(self) -> int:
        return self.gold
    
    def TakeGold(self, targetAmount) -> int:
        oldGold = self.gold
        self.gold = max(0, self.gold - targetAmount)
        return oldGold - self.gold
    
    def CanAfford(self, amount: int) -> bool:
        return self.gold >= amount
    
    def DoTurn(self):
        import SkillSystem
        import StatusEffect

        # if we have any next turn damage bonus apply that and reset the stored value
        self._tempDamageBonus += self._nextTurnDamageBonusStored
        self._nextTurnDamageBonusStored = 0

        bloodOathCount = self.GetRelicCount(Relics.BloodOathPendant)
        if bloodOathCount > 0:
            self.Damage(AttInfo(Relics.BloodOathPendant.HEALTH_LOST_PER_TURN * bloodOathCount))

        if self.HasRelic(Relics.VerdantCrest):
            heal_amount = Relics.VerdantCrest.HEALTH_REGEN_PER_TURN
            self.Heal(heal_amount)
            print(f"{Fore.GREEN}The Verdant Crest heals {self.name} for {heal_amount} HP!{Fore.RESET}")

        bloodFrenzyRank = SkillSystem.GetSkillNodeRank("sknd_bloodfrenzy")
        if bloodFrenzyRank > 0 and self.GetHealthPercent() <= SkillSystem.BERSERKER_BLOOD_FRENZY_HP_THRESHOLD:
            self.stamina += SkillSystem.BERSERKER_BLOOD_FRENZY_STAMINA_GAIN * bloodFrenzyRank

        infectiousPresenceRank = SkillSystem.GetSkillNodeRank("sknd_infectiouspresence")
        if infectiousPresenceRank > 0:
            for enemy in gc.enemiesInScene:
                if random.random() < SkillSystem.CARRION_INFECTIOUS_PRESENCE_CHANCE_TO_INFECT * infectiousPresenceRank:
                    StatusEffect.Apply(enemy, StatusEffect.InfectionEffect, 1)

        lastStandRank = SkillSystem.GetSkillNodeRank("sknd_laststand")
        if lastStandRank > 0 and self.GetHealthPercent() <= SkillSystem.BULWARK_LAST_STAND_HP_THRESHOLD:
            self.shield += SkillSystem.BULWARK_LAST_STAND_SHIELD_GAIN * lastStandRank

        return super().DoTurn()
    
    def OnEffectApply(self, effect):
        import StatusEffect
        super().OnEffectApply(effect)

        # check for LarvalIdol relic and spread extra rot to enemies
        if isinstance(effect, StatusEffect.RotEffect):
            rotEffect = self.GetEffect(StatusEffect.RotEffect)
            if rotEffect is not None and rotEffect.stacks > 3 and gc.playerCharacter.HasRelic(Relics.LarvalIdol):
                diff = rotEffect.stacks - 3
                rotEffect.stacks = 3
                print(f"{Fore.GREEN}The {Style.BRIGHT}Larval Idol{Style.NORMAL} spreads rot to an enemy!{Style.RESET_ALL}")
                StatusEffect.Apply(random.choice(gc.enemiesInScene), StatusEffect.RotEffect, diff)

    
    def get_additionalRawDamage(self) -> int:
        import SkillSystem
        additional = super().get_additionalRawDamage()

        hasBloodOiledChain = self.HasRelic(Relics.BloodOiledChain)
        if hasBloodOiledChain:
            additional += Relics.bloodOiledChainBonusDamagePerAttack

        slipAwayRank = SkillSystem.GetSkillNodeRank("sknd_slipaway")
        if slipAwayRank > 0 and self.turnsSinceLastEvasion == 1:
            additional += SkillSystem.SHADOW_SLIP_AWAY_DAMAGE_BONUS * slipAwayRank

        return additional
    
    def get_outgoingDamageMultiplier(self) -> float:
        import SkillSystem
        mult = super().get_outgoingDamageMultiplier()
        mult += self._tempDamageBonus

        golemCoreCount = self.GetRelicCount(Relics.GolemCore)
        if golemCoreCount > 0 and gc.currentTurn % Relics.GolemCore.TURN_THRESHOLD == 0:
            mult += Relics.GolemCore.DAMAGE_MULT * golemCoreCount

        if self.GetHealthPercent() < Relics.HeartofZurhatch.HEALTH_THRESHOLD:
            heartOfZurhatchCount = self.GetRelicCount(Relics.HeartofZurhatch)
            if heartOfZurhatchCount > 0:
                mult += Relics.HeartofZurhatch.ADDITIONAL_DAMAGE * heartOfZurhatchCount

        merchantPowerSkillRank = SkillSystem.GetSkillNodeRank("sknd_merchantpower")
        if merchantPowerSkillRank > 0:
            mult += (SkillSystem.GREED_MERCANTILE_POWER_DAMAGE_BONUS * floor(self.gold / SkillSystem.GREED_MERCANTILE_POWER_GOLD_THRESHOLD)) * merchantPowerSkillRank

        rageSparkSkillRank = SkillSystem.GetSkillNodeRank("sknd_ragespark")
        if rageSparkSkillRank > 0 and self.GetHealthPercent() <= SkillSystem.BERSERKER_RAGE_SPARK_HP_THRESHOLD:
            mult += SkillSystem.BERSERKER_RAGE_SPARK_DAMAGE_BONUS * rageSparkSkillRank

        if self.GetHealthPercent() <= SkillSystem.BERSERKER_DEATH_OR_GLORY_HP_THRESHOLD and SkillSystem.GetSkillNodeRank("sknd_deathorglory") > 0:
            mult += SkillSystem.BERSERKER_DEATH_OR_GLORY_DAMAGE_BONUS

        return mult
    
    def get_damageResistance(self):
        import SkillSystem
        resistance = super().get_damageResistance()
        resistance += self._tempDamageResistanceBonus
        return resistance
    
    def get_evasion(self):
        evade = super().get_evasion()
        evade += self._tempEvasionBonus
        return evade
    
    evasion = property(get_evasion, AEntity.set_evasion)
    damageResistance = property(get_damageResistance, AEntity.set_damageResistance)
    additionalRawDamage = property(get_additionalRawDamage, AEntity.set_additionalRawDamage)
    outgoingDamageMultiplier = property(get_outgoingDamageMultiplier, AEntity.set_outgoingDamageMultiplier)