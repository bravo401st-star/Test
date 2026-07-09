from abc import ABC, abstractmethod
from colorama import Fore
import random

class ABaseEncounter(ABC):
    name: str = "Unnamed Encounter"
    description: str = ""
    encounterChance: int = 1
    escapeAllowed: bool = True

    @abstractmethod
    def Trigger(self):
        pass

    def OnEncounterWin(self):
        import GameCore as gc
        gc.GenerateReward()

    def __str__(self):
        return f"{self.name}: {self.description}"
    
class ABossEncounter(ABaseEncounter):
    escapeAllowed: bool = False

    def Trigger(self):
        pass

    def OnEncounterWin(self):
        import GameCore as gc
        print(f"{self.name} has been defeated! You have proven your strength and courage.")
        gc.GenerateReward()
        gc.GiveRelicReward()
    
class FirstEncounter(ABaseEncounter):
    name = "First Encounter"
    description = "Your adventure begins as you step into the unknown. A goblin appears before you, ready to attack!"
    encounterChance = 100

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        enemy = Enemies.CreateEnemyByName("Goblin", 1)
        gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class MimicEncounter(ABaseEncounter):
    name = "Mimic Encounter"
    description = "As you approach, it suddenly transforms into a fearsome mimic!"
    encounterChance = 5

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 2))
        enemy = Enemies.CreateEnemyByName("Mimic", level)
        gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

    def OnEncounterWin(self):
        import GameCore as gc
        from GameEvent import TreasureEvent
        print(f"The {self.name} has been defeated! You open it's corpse and find a treasure inside.")
        TreasureEvent.GetReward()        
    
class RandomEncounter(ABaseEncounter):
    name = "Random Encounter"
    description = "You encounter a random group of enemies!"
    encounterChance = 10

    def Trigger(self):
        import GameCore as gc
        import Enemies
        from Entity import BasicEnemy

        print("You venture deeper into the wilderness...")
        for _ in range(0, random.randrange(1, 2 + gc.playerCharacter.level.level // 5)):
            level = max(1, gc.playerCharacter.level.level + random.randrange(-5, 3))
            enemy: BasicEnemy | None = Enemies.CreateRandomEnemy(1, level)
            if enemy is None:
                continue
            gc.SpawnEnemy(enemy)

        gc.OnCombatStart()

class GoblinAmbush(ABaseEncounter):
    name = "Goblin Ambush"
    description = "A group of goblins jump out from the bushes and attack you!"
    encounterChance = 5

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 2))
        for _ in range(random.randrange(3, 4)):
            enemy = Enemies.CreateEnemyByName("Goblin", level)
            gc.SpawnEnemy(enemy)
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Goblin Necromancer", level))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Goblin Warlord", level))
        gc.OnCombatStart()

class BanditRaid(ABaseEncounter):
    name = "Bandit Raid"
    description = "A band of desperate bandits rushes you, looking for your gold!"
    encounterChance = 4

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-2, 2))
        for enemyName in ["Bandit", "Bandit", "Bandit", "Bandit"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class HauntedGraveyard(ABaseEncounter):
    name = "Haunted Graveyard"
    description = "A chilling presence rises from the graveyard. Undead creatures approach!"
    encounterChance = 3

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Wraith", "Bog Skeleton", "Wraith", "Bog Skeleton"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class WanderingMercenary(ABaseEncounter):
    name = "Wandering Mercenary"
    description = "A lone mercenary offers a fight for the right price. He is not interested in mercy."
    encounterChance = 2

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(15, 20))
        enemy = Enemies.CreateEnemyByName("Goblin Warlord", level)
        gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class PackHunterAmbush(ABaseEncounter):
    name = "Pack Hunter Ambush"
    description = "A hungry pack of beasts surges from the underbrush, eager to tear you apart."
    encounterChance = 4

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-2, 2))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Dire Wolf", level))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Cave Bat", level))
        gc.OnCombatStart()

class NecromancersRite(ABaseEncounter):
    name = "Necromancer's Rite"
    description = "A necromancer raises the dead as a ritual of war."
    encounterChance = 3

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Goblin Necromancer", level))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Bog Skeleton", level))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Wraith", level))
        gc.OnCombatStart()

class CrystalWard(ABaseEncounter):
    name = "Crystal Ward"
    description = "A ring of crystal guardians rises around a shimmering core."
    encounterChance = 3

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 2))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Crystal Cluster", level))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Crystal Sentry", level))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Crystal Shard", level))
        gc.OnCombatStart()

class BanditExecutioners(ABaseEncounter):
    name = "Bandit Executioners"
    description = "A ruthless bandit crew has arranged a professional ambush."
    encounterChance = 4

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-2, 2))
        for _ in range(3):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Bandit", level))
        gc.SpawnEnemy(Enemies.CreateEnemyByName("Goblin Warlord", level))
        gc.OnCombatStart()

class PlagueMire(ABaseEncounter):
    name = "Plague Mire"
    description = "The marsh breathes with rot and contagion. Something sickly watches from the reeds."
    encounterChance = 3

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 2))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Plague Zombie", level))
        for _ in range(2):
            gc.SpawnEnemy(Enemies.CreateEnemyByName("Carrion Maggot", level))
        gc.OnCombatStart()

class CultistRitual(ABossEncounter):
    name = "Cultist Ritual"
    description = "A group of cultists are performing a dark ritual. They attack you to stop you from interfering!"
    encounterChance = 1

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Eldtritch Entity", "Cultist", "Cultist", "Cultist", "Cultist"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class ThePaleWarden(ABossEncounter):
    name = "The Pale Warden"
    description = "A very pale warden aproaches you. With spectral souls bound to his will, he exclaims that you'll be a fine addition to his collection."
    encounterChance = 1

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Pale Warden", "Bound Soul", "Bound Soul", "Bound Soul"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class PlagueHeart(ABossEncounter):
    name = "Plague Heart"
    description = f"A sickly heart pulses with malice. Multiple plague infested spores appear around you, this heart has {Fore.GREEN}ill{Fore.RESET} intentions..."
    encounterChance = 1

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Plague Heart", "Plague Spore", "Plague Spore", "Plague Spore"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

class AshenRevenant(ABossEncounter):
    name = "Ashen Revenant"
    description = f""
    encounterChance = 1

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Ashen Revenant", "Cinder Wisp", "Cinder Wisp"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

__encounter_database__: list[ABaseEncounter] = [
    GoblinAmbush(),
    BanditRaid(),
    WanderingMercenary(),
    PackHunterAmbush(),
    NecromancersRite(),
    CrystalWard(),
    BanditExecutioners(),
    PlagueMire(),
]

__boss_encounter_database__: list[ABaseEncounter] = [
    CultistRitual(),
    ThePaleWarden(),
    PlagueHeart(),
    AshenRevenant(),
]

def PopulateEncounterDatabase(cls) -> list[ABaseEncounter]:
    result = []
    for subclass in cls.__subclasses__():
        result.append(subclass())
        result.extend(PopulateEncounterDatabase(subclass))
    return result

__all_encounters_database__: list[ABaseEncounter] | None = None

def _InitEncountersList() -> None:
    global __all_encounters_database__
    if __all_encounters_database__ is None:
        __all_encounters_database__ = PopulateEncounterDatabase(ABaseEncounter)

def GetAllEncounters() -> list[ABaseEncounter]:
    """Get the initialized encounter list, initializing if needed."""
    _InitEncountersList()
    return __all_encounters_database__ or []


def GetRandomEncounter(encounterList: list[ABaseEncounter]) -> ABaseEncounter | None:
    if len(encounterList) == 0:
        return None

    total = sum(encounter.encounterChance for encounter in encounterList)
    if total <= 0:
        return None

    roll = random.randrange(0, total)
    current = 0
    for encounter in encounterList:
        current += encounter.encounterChance
        if roll < current:
            return encounter

    return encounterList[-1]

def GetRandomBossEncounter() -> ABaseEncounter | None:
    return GetRandomEncounter(__boss_encounter_database__)
