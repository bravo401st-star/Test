from __future__ import annotations
from abc import ABC, abstractmethod

class ARelic(ABC):
    def __init__(self):
        self.name = "Unnamed Relic"
        self.description = "No description"
    
    def SetName(self, name: str):
        self.name = name
        return self
    
    def SetDescription(self, description: str):
        self.description = description
        return self
    
    def OnAcquire(self):
        pass

    def OnLose(self):
        pass
    
class FortunesEmblem(ARelic):
    LOOT_MULT = 0.4
    def __init__(self):
        super().__init__()
        self.name = "Fortune's Emblem"
        self.description = f"+{int(FortunesEmblem.LOOT_MULT * 100)}% increased loot drop rate. Item drops are rolled twice, highest rarity taken."

    def OnAcquire(self):
        import GameCore as gc
        gc.additionalLootChance += FortunesEmblem.LOOT_MULT

class GildedCompass(ARelic):
    SHOP_DISCOUNT = 0.2
    GOLD_MULT = 0.5
    def __init__(self):
        super().__init__()
        self.name = "Gilded Compass"
        self.description = f"+{int(GildedCompass.GOLD_MULT * 100)}% gold gained. Shops offer {int(GildedCompass.SHOP_DISCOUNT * 100)}% discount and an additional item."

    def OnAcquire(self):
        import GameCore as gc
        gc.goldMultiplier += GildedCompass.GOLD_MULT

class OraclesWhisper(ARelic):
    CRIT_CHANCE = 0.15
    def __init__(self):
        super().__init__()
        self.name = "Oracle's Whisper"
        self.description = f"+{int(OraclesWhisper.CRIT_CHANCE * 100)}% crit chance. First hit in every combat is guaranteed to crit."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += OraclesWhisper.CRIT_CHANCE

class StonehoofTotem(ARelic):
    DAMAGE_RESIST = 0.30
    DAMAGE_MULT_WHEN_NOT_ATTACK = 0.50
    def __init__(self):
        super().__init__()
        self.name = "Stonehoof Totem"
        self.description = f"+{int(StonehoofTotem.DAMAGE_RESIST * 100)}% less damage from all sources. Not attacking for a turn grants +{int(StonehoofTotem.DAMAGE_MULT_WHEN_NOT_ATTACK * 100)}% damage on the next one."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageResistance += StonehoofTotem.DAMAGE_RESIST

class PhoenixFeather(ARelic):
    REVIVE_HEALTH_PERCENT = 0.30
    def __init__(self):
        super().__init__()
        self.name = "Phoenix Feather"
        self.description = f"Upon death, revive with {int(PhoenixFeather.REVIVE_HEALTH_PERCENT * 100)}% health once."

class PhantomSigil(ARelic):
    ADDITIONAL_EVASION = 0.20
    DAMAGE_REFLECT: int = 15
    def __init__(self):
        super().__init__()
        self.name = "Phantom Sigil"
        self.description = f"+{int(PhantomSigil.ADDITIONAL_EVASION * 100)}% evasion chance. After dodging, instantly deal {PhantomSigil.DAMAGE_REFLECT} damage back." # TODO: implement damage retaliation on dodge

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.evasion += PhantomSigil.ADDITIONAL_EVASION

class CelestialOrb(ARelic):
    HEALING_MULT = 0.25
    HEAL_START_COMBAT_PERCENT = 0.10
    def __init__(self):
        super().__init__()
        self.name = "Celestial Orb"
        self.description = f"All healing effects are {int(CelestialOrb.HEALING_MULT * 100)}% stronger. At the start of combat, heal {int(CelestialOrb.HEAL_START_COMBAT_PERCENT * 100)}% max health."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.healingMultiplier += CelestialOrb.HEALING_MULT

class WyrmSpineCharm(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Wyrm Spine Charm"
        self.description = f"Your poison ticks an extra time every turn."

class EternalFlask(ARelic):
    EXTRA_USES: int = 1
    def __init__(self):
        super().__init__()
        self.name = "Eternal Flask"
        self.description = f"All potions gain +{EternalFlask.EXTRA_USES} extra use."

    def OnAcquire(self):
        import GameCore as gc
        import ItemSystem

        for item in ItemSystem.itemsList:
            if issubclass(type(item), ItemSystem.Potion):
                item.useCount += EternalFlask.EXTRA_USES
        
        for item in gc.playerCharacter.items:
            if issubclass(type(item), ItemSystem.Potion):
                item.useCount += EternalFlask.EXTRA_USES

class BloodOathPendant(ARelic):
    DAMAGE_MULT = 0.25
    HEALTH_LOST_PER_TURN = 10
    def __init__(self):
        super().__init__()
        self.name = "Blood Oath Pendant"
        self.description = f"+{int(BloodOathPendant.DAMAGE_MULT * 100)}% damage. -{BloodOathPendant.HEALTH_LOST_PER_TURN} HP at the start of every turn."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.outgoingDamageMultiplier += BloodOathPendant.DAMAGE_MULT

class ShadowboundMark(ARelic):
    EXTRA_EVASION = 0.35
    HEALING_REDUCTION_PERCENT = 0.50
    def __init__(self):
        super().__init__()
        self.name = "Shadowbound Mark"
        self.description = f"+{int(ShadowboundMark.EXTRA_EVASION * 100)}% evasion. Healing received is reduced by {int(ShadowboundMark.HEALING_REDUCTION_PERCENT * 100)}%."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.evasion += ShadowboundMark.EXTRA_EVASION
        gc.playerCharacter.healingMultiplier -= ShadowboundMark.HEALING_REDUCTION_PERCENT

class GlassforgeCrown(ARelic):
    EXTRA_CRIT_CHANCE = 0.40
    DAMAGE_RESISTANCE_REDUCTION = 0.20
    def __init__(self):
        super().__init__()
        self.name = "Glassforge Crown"
        self.description = f"+{int(GlassforgeCrown.EXTRA_CRIT_CHANCE * 100)}% crit chance. -{int(GlassforgeCrown.DAMAGE_RESISTANCE_REDUCTION * 100)}% more damage from all sources."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += GlassforgeCrown.EXTRA_CRIT_CHANCE
        gc.playerCharacter.damageResistance -= GlassforgeCrown.DAMAGE_RESISTANCE_REDUCTION

class TimewornHourglass(ARelic):
    SHIELD_AMOUNT = 15
    def __init__(self):
        super().__init__()
        self.name = "Timeworn Hourglass"
        self.description = f"At the start of combat, gain a shield that absorbs {TimewornHourglass.SHIELD_AMOUNT} damage."

class MindshackleTalisman(ARelic):
    SKIP_TURN_CHANCE = 0.20
    def __init__(self):
        super().__init__()
        self.name = "Mindshackle Talisman"
        self.description = f"Enemies have a {int(MindshackleTalisman.SKIP_TURN_CHANCE * 100)}% chance to skip their turn."

class KnowledgeScroll(ARelic):
    EXTRA_EXPERIENCE_PERCENT = 0.20
    def __init__(self):
        super().__init__()
        self.name = "Knowledge Scroll"
        self.description = f"+{int(KnowledgeScroll.EXTRA_EXPERIENCE_PERCENT * 100)}% experience gained from combat."

    def OnAcquire(self):
        import GameCore as gc
        gc.experienceMultiplier += KnowledgeScroll.EXTRA_EXPERIENCE_PERCENT

class CursedLocket(ARelic):
    EXPERIENCE_REDUCTION_PERCENT = 0.15
    EXTRA_GOLD_PERCENT = 0.15
    def __init__(self):
        super().__init__()
        self.name = "Cursed Locket"
        self.description = f"-{int(CursedLocket.EXPERIENCE_REDUCTION_PERCENT * 100)}% experience gained from combat. +{int(CursedLocket.EXTRA_GOLD_PERCENT * 100)}% gold gained from combat."

    def OnAcquire(self):
        import GameCore as gc
        gc.experienceMultiplier -= CursedLocket.EXPERIENCE_REDUCTION_PERCENT
        gc.goldMultiplier += CursedLocket.EXTRA_GOLD_PERCENT

class XenolithFragment(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Xenolith Fragment"
        self.description = f"At the start of combat, gain a random buff effect."

class SoulbinderCharm(ARelic):
    RELIC_DROP_CHANCE = 0.02
    def __init__(self):
        super().__init__()
        self.name = "Soulbinder Charm"
        self.description = f"Defeated enemies have a {int(SoulbinderCharm.RELIC_DROP_CHANCE * 100)}% chance to drop a random relic."

class Dreamcatcher(ARelic):
    EXTRA_STAMINA = 2
    def __init__(self):
        super().__init__()
        self.name = "Dreamcatcher"
        self.description = f"At the start of combat, gain +{Dreamcatcher.EXTRA_STAMINA} stamina for the first turn."

class SoulvesselJar(ARelic):
    killsToFill = 20
    def __init__(self):
        super().__init__()
        self.name = "Soulvessel Jar"
        self.description = f"+1 max energy every {SoulvesselJar.killsToFill} enemies defeated."
soulvesselJarKillsNeeded = SoulvesselJar.killsToFill

class GiantsRib(ARelic):
    EXTRA_DAMAGE_RESIST_PERCENT = 0.10
    EXTRA_MAX_HP: int = 60
    def __init__(self):
        super().__init__()
        self.name = "Giant's Rib"
        self.description = f"+{int(GiantsRib.EXTRA_DAMAGE_RESIST_PERCENT * 100)}% less damage from all sources. +{GiantsRib.EXTRA_MAX_HP} Max Health."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageResistance += GiantsRib.EXTRA_DAMAGE_RESIST_PERCENT
        gc.playerCharacter.maxHealth += GiantsRib.EXTRA_MAX_HP
        gc.playerCharacter.health += GiantsRib.EXTRA_MAX_HP

class FangoftheRaven(ARelic):
    EXTRA_CRIT_CHANCE_PERCENT = 0.20
    BLEED_AMOUNT: int = 8
    def __init__(self):
        self.name = "Fang of the Raven"
        self.description = f"+{int(FangoftheRaven.EXTRA_CRIT_CHANCE_PERCENT * 100)}% crit chance. On a crit, apply {FangoftheRaven.BLEED_AMOUNT} bleed."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += FangoftheRaven.EXTRA_CRIT_CHANCE_PERCENT

class RendingClaw(ARelic):
    EXTRA_BLEEDING_DAMAGE = 5
    BLEED_CHANCE = 0.5
    def __init__(self):
        self.name = "Rending Claw"
        self.description = f"+{int(RendingClaw.BLEED_CHANCE * 100)}% chance to apply bleed. +{RendingClaw.EXTRA_BLEEDING_DAMAGE} bleed damage."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.applyBleedChance += RendingClaw.BLEED_CHANCE

class ThornbackTortoiseShell(ARelic):
    ADDITIONAL_THORNS = 0.15
    def __init__(self):
        self.name = "Thornback Tortoise Shell"
        self.description = f"+{int(ThornbackTortoiseShell.ADDITIONAL_THORNS * 100)}% damage reflection."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageReflect += ThornbackTortoiseShell.ADDITIONAL_THORNS

class WardensBulwark(ARelic):
    DAMAGE_THRESHOLD = 15
    GRANTED_DEFENSE = 10
    def __init__(self):
        super().__init__()
        self.name = "Warden's Bulwark"
        self.description = f"Taking more than {WardensBulwark.DAMAGE_THRESHOLD} damage in a single hit grants +{WardensBulwark.GRANTED_DEFENSE} Defense next turn."
wardensBulwarkStoreDefense = 0

class BloodOiledChain(ARelic):
    BONUS_DAMAGE = 1
    def __init__(self):
        super().__init__()
        self.name = "Blood-Oiled Chain"
        self.description = f"Each time you attack, gain +{BloodOiledChain.BONUS_DAMAGE} Damage permanently for the encounter."
bloodOiledChainBonusDamagePerAttack = 0
        
class SmolderingCore(ARelic):
    START_BATTLE_FIRE_DAMAGE_TO_ALL = 5
    SPREADING_FIRE_DAMAGE_ON_KILL = 10
    def __init__(self):
        super().__init__()
        self.name = "Smoldering Core"
        self.description = f"At the start of each battle, deal {SmolderingCore.START_BATTLE_FIRE_DAMAGE_TO_ALL} fire damage to all enemies. Killing an enemy deals {SmolderingCore.SPREADING_FIRE_DAMAGE_ON_KILL} fire damage to all remaining ones."

def TriggerSmolderingCore(damage: int):
    from AttackInfo import AttInfo
    import GameCore as gc
    from ElementTags import ElementTag
    from colorama import Fore, Style
    print(f"{Fore.CYAN}Your {Style.BRIGHT}Smoldering Core{Style.NORMAL} glows bright and ignites all enemies for {damage} damage!{Style.RESET_ALL}")
    for enemy in gc.enemiesInScene:
        enemy.Damage(AttInfo(damage).AddElements(ElementTag.FIRE))

class VerdantCrest(ARelic):
    HEALTH_REGEN_PER_TURN = 5
    FIRE_WEAKNESS_PERCENT = 0.10
    def __init__(self):
        super().__init__()
        self.name = "Verdant Crest"
        self.description = f"Regenerate {VerdantCrest.HEALTH_REGEN_PER_TURN} health at the start of each turn. Weak to fire (you take +{int(VerdantCrest.FIRE_WEAKNESS_PERCENT * 100)}% fire damage)."

class LunarShard(ARelic):
    ADDITIONAL_CRIT_DAMAGE = 0.25
    def __init__(self):
        super().__init__()
        self.name = "Lunar Shard"
        self.description = f"Critical hits deal +{int(LunarShard.ADDITIONAL_CRIT_DAMAGE * 100)}% damage."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.criticalHitMultiplier += LunarShard.ADDITIONAL_CRIT_DAMAGE

class ThunderousHeart(ARelic):
    CHANCE_TO_STUN = 0.05
    def __init__(self):
        super().__init__()
        self.name = "Thunderous Heart"
        self.description = f"Your attacks have a {int(ThunderousHeart.CHANCE_TO_STUN * 100)}% chance to stun the enemy for one turn."

class GlitteringAmulet(ARelic):
    CHANCE_TO_APPLY_DEBUFF = 0.10
    def __init__(self):
        super().__init__()
        self.name = "Glittering Amulet"
        self.description = f"Your attacks have a {int(GlitteringAmulet.CHANCE_TO_APPLY_DEBUFF * 100)}% chance to apply a random debuff to the enemy."

class GolemCore(ARelic):
    TURN_THRESHOLD = 3
    DAMAGE_MULT = 0.20
    def __init__(self):
        super().__init__()
        self.name = "Golem Core"
        self.description = f"Every {GolemCore.TURN_THRESHOLD} turns, gain +{int(GolemCore.DAMAGE_MULT * 100)}% damage on that turn."

class PhylacteryShard(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Phylactery Shard"
        self.description = f"At the start of combat, automatically cleanse a debuff."

class GravedustLedger(ARelic):
    BONUS_ATTACKS_PER_KILL: int = 1
    def __init__(self):
        super().__init__()
        self.name = "Gravedust Ledger"
        self.description = f"Each time you kill an enemy, gain +{GravedustLedger.BONUS_ATTACKS_PER_KILL} temporary attack for that combat."

class HeartofZurhatch(ARelic):
    HEALTH_THRESHOLD = 0.40
    ADDITIONAL_DAMAGE = 0.30
    def __init__(self):
        super().__init__()
        self.name = "Heart of Zurhatch"
        self.description = f"When below {int(HeartofZurhatch.HEALTH_THRESHOLD * 100)}% HP, damage increased by +{int(HeartofZurhatch.ADDITIONAL_DAMAGE * 100)}%."

class ContagionVial(ARelic):
    BLEED_AMOUNT: int = 8
    _RELEVANT_EFFECTS: list[type] | None = None
    _description_cached: str | None = None
    
    def __init__(self):
        self.name = "Contagion Vial"

    @property
    def description(self) -> str:
        from colorama import Fore
        if ContagionVial._description_cached is None:
            ContagionVial._description_cached = f"When an enemy dies while afflicted with {self.GetListOfRelevantEffects()}, spread it to another enemy."
        return ContagionVial._description_cached
    
    @description.setter
    def description(self, value: str) -> None:
        ContagionVial._description_cached = value

    @classmethod
    def GetRelevantEffects(cls) -> list[type]:
        if cls._RELEVANT_EFFECTS is None:
            import sys
            # Use already-loaded StatusEffect if available, avoid circular import
            if 'StatusEffect' in sys.modules:
                StatusEffect = sys.modules['StatusEffect']
                cls._RELEVANT_EFFECTS = [StatusEffect.BleedEffect, StatusEffect.PoisonEffect, StatusEffect.RotEffect, StatusEffect.InfectionEffect]
            else:
                # Fallback: return empty list if StatusEffect hasn't loaded yet
                cls._RELEVANT_EFFECTS = []
        return cls._RELEVANT_EFFECTS

    def GetListOfRelevantEffects(self) -> str:
        string = str()
        effects = ContagionVial.GetRelevantEffects()
        for i, effect in enumerate(effects):
            tempEffect = effect(None)
            string += tempEffect.GetName() + ("/" if i != len(effects) - 1 else "")

        return string
    
class VenomousKeystone(ARelic):
    EXTRA_POISON: int = 1
    POISONED_ATTACK_DAMAGE: int = 4
    def __init__(self):
        super().__init__()
        self.name = "Venomous Keystone"
        self.description = f"When applying poison, apply +{VenomousKeystone.EXTRA_POISON} extra. When poisoned enemies attack you, they take {VenomousKeystone.POISONED_ATTACK_DAMAGE} damage."

class ParasiticSporeheart(ARelic):
    HEAL_ON_POISON: int = 3
    HEALING_REDUCTION_PERCENT: float = 0.30
    def __init__(self):
        super().__init__()
        self.name = "Parasitic Sporeheart"
        self.description = f"When applying Poison, also heal +{ParasiticSporeheart.HEAL_ON_POISON} HP. -{int(ParasiticSporeheart.HEALING_REDUCTION_PERCENT * 100)}% Healing received."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.healingMultiplier -= ParasiticSporeheart.HEALING_REDUCTION_PERCENT

class ExecutionersMark(ARelic):
    HP_THRESHOLD = 0.20
    ADDITIONAL_DAMAGE = 0.40
    def __init__(self):
        super().__init__()
        self.name = "Executioner's Mark"
        self.description = f"Enemies below {int(ExecutionersMark.HP_THRESHOLD * 100)}% HP take {int(ExecutionersMark.ADDITIONAL_DAMAGE * 100)}% more damage from you."

class ClockworkBloodgear(ARelic):
    HIT_THRESHOLD = 3
    DAMAGE_THRESHOLD = 7
    HIT_BONUS = 2.0
    DAMAGE_RECIEVED_BONUS = 2.0
    def __init__(self):
        super().__init__()
        self.name = "Clockwork Bloodgear"
        self.description = f"Every {ClockworkBloodgear.GetNumText(ClockworkBloodgear.HIT_THRESHOLD)} hit you deal is doubled. Every {ClockworkBloodgear.GetNumText(ClockworkBloodgear.DAMAGE_THRESHOLD)} hit against you is doubled."

    @classmethod
    def GetNumText(cls, num: int) -> str:
        if num == 1:
            return "1st"
        elif num == 2:
            return "2nd"
        elif num == 3:
            return "3rd"
        else:
            return f"{num}th"
        
class CarrioncoreGland(ARelic):
    DAMAGE_ADDITION = 0.35
    MAX_HEALTH_GAIN: int = 1

    def __init__(self):
        super().__init__()
        self.name = "Carrioncore Gland"
        self.description = f"+{int(CarrioncoreGland.DAMAGE_ADDITION * 100)}% damage against enemies afflicted with infection. Every time you kill an enemy, gain +{CarrioncoreGland.MAX_HEALTH_GAIN} max health."

class LarvalIdol(ARelic):
    MAX_ROT_STACKS = 3
    def __init__(self):
        super().__init__()
        self.name = "Larval Idol"
        self.description = f"You can never have more than {LarvalIdol.MAX_ROT_STACKS} Rot stacks. If you would gain more, they are reflected onto a random enemy instead."

"""
class KeystoneIdol(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Keystone Idol"
        self.description = f"Boss enemies drop an additional relic upon defeat."

"""

def GetRelicByName(name: str) -> ARelic | None:
    relicsList = GetRelicsList()
    for i, relic in enumerate(relicsList):
        if relic.name == name:
            return GetRelicByIndex(i)
    print("Unknown relic: \"" + name + "\"")
    return None

def GetRelicByIndex(index: int) -> ARelic | None:
    relicsList = GetRelicsList()
    if (index >= len(relicsList) or index < 0):
        return None
    return relicsList[index]

def GetRandomRelic() -> ARelic | None:
    import random
    relicsList = GetRelicsList()
    rand = random.randint(0, len(relicsList) - 1)
    return GetRelicByIndex(rand)

def GenerateRelics(cls) -> list[ARelic]:
    result = []
    for subclass in cls.__subclasses__():
        result.append(subclass())
        result.extend(GenerateRelics(subclass))
    return result

# Lazy-initialized relic list to avoid circular imports
_relicsList: list[ARelic] | None = None

def _InitRelicsList() -> None:
    global _relicsList
    if _relicsList is None:
        _relicsList = GenerateRelics(ARelic)

def GetRelicsList() -> list[ARelic]:
    """Get the initialized relic list, initializing if needed."""
    _InitRelicsList()
    return _relicsList or []

# For backward compatibility, provide 'relicsList' as a property-like accessor
def __getattr__(name):
    if name == "relicsList":
        return GetRelicsList()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
