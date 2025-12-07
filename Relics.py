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
        self.description = f"+{int(FangoftheRaven.EXTRA_CRIT_CHANCE_PERCENT * 100)}% crit chance. On a crit, apply {FangoftheRaven.BLEED_AMOUNT} Bleed."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += FangoftheRaven.EXTRA_CRIT_CHANCE_PERCENT

"""
class KeystoneIdol(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Keystone Idol"
        self.description = f"Boss enemies drop an additional relic upon defeat."

"""

def GetRelicByName(name: str) -> ARelic | None:
    for relic in relicsList:
        if relic.name == name:
            return relic
    print("Unknown relic: \"" + name + "\"")
    return None

def GetRelicByIndex(index: int) -> ARelic | None:
    if (index >= len(relicsList) or index < 0):
        return None
    return relicsList[index]

def GetRandomRelic() -> ARelic:
    import random
    rand = random.randint(0, len(relicsList) - 1)
    return relicsList[rand]

def GenerateRelics(cls) -> list[ARelic]:
    result = []
    for subclass in cls.__subclasses__():
        result.append(subclass())
        result.extend(GenerateRelics(subclass))
    return result

relicsList: list[ARelic] = GenerateRelics(ARelic)
