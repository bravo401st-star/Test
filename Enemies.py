import Entity
import copy
import random
import EnemyList

def CreateRandomEnemy(threatScale = 1, level: int = 1):
    randomEnemyRef = EnemyList.__enemy_pool__[random.randrange(0, len(EnemyList.__enemy_pool__))]
    return CreateEnemyByReference(randomEnemyRef, level)

def CreateEnemyByReference(enemyRef: Entity.BasicEnemy, level: int = 1):
    if (enemyRef == None):
        return None
    return copy.deepcopy(enemyRef).SetLevel(level)

def CreateEnemyByIndex(index: int, level: int = 1):
    if index >= len(EnemyList.__enemy_pool__):
        return None
    return CreateEnemyByReference(EnemyList.__enemy_pool__[index], level)

def CreateEnemyByName(name: str, level: int = 1):
    entityRef = None
    for enemy in EnemyList.__enemy_pool__:
        if (enemy.name == name):
            entityRef = enemy
            break

    if (entityRef == None):
        return None

    return CreateEnemyByReference(entityRef, level)