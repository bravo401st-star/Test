from enum import Enum

class EnemyTag(str, Enum):
    UNDEAD = 'Undead',
    CANT_BE_UNDEAD = 'Cant_Be_Undead'