from enum import Enum

class EnemyTag(str, Enum):
    UNDEAD = 'Undead',
    CANT_BE_UNDEAD = 'Cant_Be_Undead',
    IMMUNE_TO_DAMAGE = 'Immune_To_Damage',
    BOSS = 'Boss',
    INFECTIOUS = "Infectious"