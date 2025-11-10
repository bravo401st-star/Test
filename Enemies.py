import Entity
import copy
import random

__enemy_pool__ = [
    Entity.BasicEnemy().SetName("Goblin").SetMaxHealth(50).SetHealth(50).SetDropExp(range(1, 3))
]

def CreateRandomEnemy(threatScale = 1, level: int = 1):
    randomEnemyRef = __enemy_pool__[random.randrange(0, len(__enemy_pool__) - 1)]
    return CreateEnemyByReference(randomEnemyRef, level)

def CreateEnemyByReference(enemyRef: Entity.BasicEnemy, level: int = 1):
    if (enemyRef == None):
        return None
    return copy.deepcopy(enemyRef).SetLevel(level)

def CreateEnemyByIndex(index: int, level: int = 1):
    global __enemy_pool__
    if index >= len(__enemy_pool__):
        return None
    return CreateEnemyByReference(__enemy_pool__[index], level)

def CreateEnemyByName(name: str, level: int = 1):
    global __enemy_pool__
    entityRef = None
    for enemy in __enemy_pool__:
        if (enemy.name == name):
            entityRef = enemy
            break

    if (entityRef == None):
        return None

    return CreateEnemyByReference(entityRef, level)