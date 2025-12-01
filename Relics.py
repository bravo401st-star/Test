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
    def __init__(self):
        super().__init__()
        self.name = "Fortune's Emblem"
        self.description = f"+40% increased loot drop rate. Item drops are rolled twice, highest rarity taken."

    def OnAcquire(self):
        import GameCore as gc
        gc.additionalLootChance += 0.4

class GildedCompass(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Gilded Compass"
        self.description = f"+50% gold gained. Shops offer 20% discount and an additional item."

    def OnAcquire(self):
        import GameCore as gc
        gc.goldMultiplier += 0.5

class OraclesWhisper(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Oracle's Whisper"
        self.description = f"+15% crit chance. First hit in every combat is guaranteed to crit."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += 0.15

class StonehoofTotem(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Stonehoof Totem"
        self.description = f"+30% less damage from all sources. Not attacking for a turn grants +50% damage on the next one."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageResistance += 0.30

class PhoenixFeather(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Phoenix Feather"
        self.description = f"Upon death, revive with 30% health once."

class PhantomSigil(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Phantom Sigil"
        self.description = f"+20% evasion chance. After dodging, instantly deal 15 damage back." # TODO: implement damage retaliation on dodge

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.evasion += 0.20

class CelestialOrb(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Celestial Orb"
        self.description = f"All healing effects are 25% stronger. At the start of combat, heal 10% max health."

class WyrmSpineCharm(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Wyrm Spine Charm"
        self.description = f"Your poison ticks an extra time every turn."

class EternalFlask(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Eternal Flask"
        self.description = f"All potions gain +1 extra use."

    def OnAcquire(self):
        import GameCore as gc
        import ItemSystem

        for item in ItemSystem.itemsList:
            if issubclass(type(item), ItemSystem.Potion):
                item.useCount += 1
        
        for item in gc.playerCharacter.items:
            if issubclass(type(item), ItemSystem.Potion):
                item.useCount += 1

class BloodOathPendant(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Blood Oath Pendant"
        self.description = f"+25% damage. -10 HP at the start of every turn."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageMultiplier += 0.25

class ShadowboundMark(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Shadowbound Mark"
        self.description = f"+35% evasion. Healing received is reduced by 50%."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.evasion += 0.35

class GlassforgeCrown(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Glassforge Crown"
        self.description = f"+40% crit chance. -20% more damage from all sources."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += 0.40
        gc.playerCharacter.damageResistance -= 0.20

class TimewornHourglass(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Timeworn Hourglass"
        self.description = f"At the start of combat, gain a shield that absorbs 15 damage."

class MindshackleTalisman(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Mindshackle Talisman"
        self.description = f"Enemies have a 20% chance to skip their turn."

class KnowledgeScroll(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Knowledge Scroll"
        self.description = f"+20% experience gained from combat."

    def OnAcquire(self):
        import GameCore as gc
        gc.experienceMultiplier += 0.20

class CursedLocket(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Cursed Locket"
        self.description = f"-15% experience gained from combat. +10% gold gained from combat."

    def OnAcquire(self):
        import GameCore as gc
        gc.experienceMultiplier -= 0.15
        gc.goldMultiplier += 0.10

class XenolithFragment(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Xenolith Fragment"
        self.description = f"At the start of combat, gain a random buff effect."

class SoulbinderCharm(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Soulbinder Charm"
        self.description = f"Defeated enemies have a 2% chance to drop a random relic."

class Dreamcatcher(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Dreamcatcher"
        self.description = f"At the start of combat, gain +2 stamina for the first turn."

class SoulvesselJar(ARelic):
    killsToFill = 20
    def __init__(self):
        super().__init__()
        self.name = "Soulvessel Jar"
        self.description = f"+1 max energy every {SoulvesselJar.killsToFill} enemies defeated."
soulvesselJarKillsNeeded = SoulvesselJar.killsToFill

class GiantsRib(ARelic):
    def __init__(self):
        super().__init__()
        self.name = "Giant's Rib"
        self.description = f"+10% less damage from all sources. +60 Max Health."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.damageResistance += 0.10
        gc.playerCharacter.maxHealth += 60
        gc.playerCharacter.health += 60

class FangoftheRaven(ARelic):
    def __init__(self):
        self.name = "Fang of the Raven"
        self.description = f"+20% crit chance. On a crit, apply 8 Bleed."

    def OnAcquire(self):
        import GameCore as gc
        gc.playerCharacter.critialHitChance += 0.20

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
