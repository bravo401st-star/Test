import Entity
import copy
import random
import EnemyList

def CreateRandomEnemy(threatScale = 1, level: int = 1) -> Entity.BasicEnemy | None:
    import GameCore as gc

    if len(EnemyList.__naturally_spawning_pool___) <= 0:
        for enemy in EnemyList.__enemy_pool__:
            if enemy.canSpawnInEncounters:
                EnemyList.__naturally_spawning_pool___.append(enemy)

    if len(EnemyList.__naturally_spawning_pool___) <= 0:
        return None

    progressFactor = 1.0
    killFactor = 1.0
    if hasattr(gc, "playerCharacter") and gc.playerCharacter is not None:
        progressFactor = 1.0 + max(0, gc.playerCharacter.level.level - 1) * 0.05
    if hasattr(gc, "killCount"):
        killFactor = 1.0 + max(0, gc.killCount) * 0.01

    effectiveThreat = max(0.1, threatScale * progressFactor * killFactor)
    candidates: list[tuple[Entity.BasicEnemy, float]] = []

    for enemyRef in EnemyList.__naturally_spawning_pool___:
        candidateLevel = max(1, level + random.randrange(-1, 2))
        candidate = CreateEnemyByReference(enemyRef, candidateLevel)
        if candidate is None:
            continue
        danger = EvaluateEnemyDanger(candidate)
        weight = max(0.01, danger * effectiveThreat)
        candidates.append((candidate, weight))

    totalWeight = sum(weight for _, weight in candidates)
    if totalWeight <= 0 or len(candidates) == 0:
        return CreateEnemyByReference(EnemyList.__naturally_spawning_pool___[random.randrange(0, len(EnemyList.__naturally_spawning_pool___))], level)

    roll = random.uniform(0, totalWeight)
    current = 0.0
    for candidate, weight in candidates:
        current += weight
        if roll <= current:
            return candidate
    return candidates[-1][0]

def CreateEnemyByReference(enemyRef: Entity.BasicEnemy, level: int = 1):
    if (enemyRef == None):
        return None
    return copy.deepcopy(enemyRef).SetLevel(level)

def EvaluateEnemyDanger(enemy: Entity.BasicEnemy | None) -> float:
    """Return an estimated danger score for an enemy for spawn scaling."""
    if enemy is None:
        return 0.0
    if hasattr(enemy, "GetDangerRating"):
        return enemy.GetDangerRating()
    return float(enemy.maxHealth)

def CreateEnemyByIndex(index: int, level: int = 1):
    if index >= len(EnemyList.__enemy_pool__):
        return None
    return CreateEnemyByReference(EnemyList.__enemy_pool__[index], level)

def GetByIndex(index: int) -> None | Entity.BasicEnemy:
    if index >= len(EnemyList.__enemy_pool__):
        return None
    return EnemyList.__enemy_pool__[index]

def GetByName(name: str) -> None | Entity.BasicEnemy:
    entityRef = None
    for enemy in EnemyList.__enemy_pool__:
        if (enemy.name == name):
            entityRef = enemy
            break
    return entityRef

def CreateEnemyByName(name: str, level: int = 1):
    entityRef = GetByName(name)

    if (entityRef == None):
        return None

    return CreateEnemyByReference(entityRef, level)