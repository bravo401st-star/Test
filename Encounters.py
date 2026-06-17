from abc import ABC, abstractmethod
import random

class ABaseEncounter(ABC):
    name: str = "Unnamed Encounter"
    description: str = ""
    encounterChance: int = 1
    canEscape: bool = True

    @abstractmethod
    def Trigger(self):
        pass

    def OnEncounterWin(self):
        import GameCore as gc
        gc.GenerateReward()

    def __str__(self):
        return f"{self.name}: {self.description}"
    
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

class CultistRitual(ABaseEncounter):
    name = "Cultist Ritual"
    description = "A group of cultists are performing a dark ritual. They attack you to stop you from interfering!"
    encounterChance = 1
    canEscape = False

    def Trigger(self):
        import GameCore as gc
        import Enemies

        print(self.description)
        level = max(1, gc.playerCharacter.level.level + random.randrange(-1, 3))
        for enemyName in ["Cultist", "Cultist", "Cultist", "Cultist", "Cultist", "Eldtritch Entity"]:
            enemy = Enemies.CreateEnemyByName(enemyName, level)
            gc.SpawnEnemy(enemy)
        gc.OnCombatStart()

__encounter_database__: list[ABaseEncounter] = [
    GoblinAmbush(),
    BanditRaid(),
    HauntedGraveyard(),
    WanderingMercenary(),
]

__boss_encounter_database__: list[ABaseEncounter] = [
    CultistRitual(),
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
