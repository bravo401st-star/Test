import Entity
import ActionSets
from EnemyTags import ElementTag

__enemy_pool__ = [
    Entity.BasicEnemy().SetName("Goblin").SetMaxHealth(45, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.goblin_action_set),
    Entity.NecromancerEnemy().SetName("Goblin Necromancer").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(2, 4)).AttachActionSet(ActionSets.goblin_necromancer_action_set),
    Entity.BasicEnemy().SetName("Granite Golem").SetMaxHealth(105, setHealthToo=True).SetDropExp(range(5, 15)).AttachActionSet(ActionSets.granite_golem_action_set),
    Entity.BasicEnemy().SetName("Dire Wolf").SetMaxHealth(40, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.dire_wolf_action_set),
    Entity.TrollEnemy().SetName("Troll Brute").SetMaxHealth(75, setHealthToo=True).SetDropExp(range(1, 9)).AttachActionSet(ActionSets.troll_brute_action_set),
    Entity.BasicEnemy().SetName("Cave Bat").SetMaxHealth(10, setHealthToo=True).SetDropExp(range(1, 2)).AttachActionSet(ActionSets.cave_bat_action_set),
    Entity.TransformOnDeathEnemy(7, "collapsed into a strange pile!").SetName("Bog Skeleton").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(1, 3)).SetTags(ElementTag.UNDEAD).AttachActionSet(ActionSets.bog_skeleton_action_set),
    Entity.BasicEnemy().SetName("Boggy Bone Pile").SetMaxHealth(5, setHealthToo=True).SetDropExp(0).SetTags(ElementTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.boggy_pile_action_set).DisableSpawnPool()
]

__naturally_spawning_pool___ = []
