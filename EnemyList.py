import Entity
import ActionSets
from EnemyTags import EnemyTag

__enemy_pool__ = [
    Entity.BasicEnemy().SetName("Goblin").SetMaxHealth(45, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.goblin_action_set),
    Entity.NecromancerEnemy().SetName("Goblin Necromancer").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(2, 4)).AttachActionSet(ActionSets.goblin_necromancer_action_set),
    Entity.BasicEnemy().SetName("Granite Golem").SetMaxHealth(105, setHealthToo=True).SetDropExp(range(7, 10)).AttachActionSet(ActionSets.granite_golem_action_set),
    Entity.BasicEnemy().SetName("Dire Wolf").SetMaxHealth(40, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.dire_wolf_action_set),
    Entity.TrollEnemy().SetName("Troll Brute").SetMaxHealth(75, setHealthToo=True).SetDropExp(range(5, 9)).AttachActionSet(ActionSets.troll_brute_action_set),
    Entity.BasicEnemy().SetName("Cave Bat").SetMaxHealth(10, setHealthToo=True).SetDropExp(range(1, 2)).AttachActionSet(ActionSets.cave_bat_action_set),
    Entity.TransformOnDeathEnemy(7, "collapsed into a strange pile!").SetName("Bog Skeleton").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(1, 3)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.bog_skeleton_action_set),
    Entity.BasicEnemy().SetName("Boggy Bone Pile").SetMaxHealth(5, setHealthToo=True).SetDropExp(0).SetTags(EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.boggy_pile_action_set).DisableSpawnPool(),
    Entity.WraithEnemy().SetName("Wraith").SetMaxHealth(46, setHealthToo=True).SetDropExp(range(1,4)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.wraith_action_set),
    Entity.EmberlingEnemy().SetName("Emberling").SetMaxHealth(24, setHealthToo=True).SetDropExp(range(1,3)).AttachActionSet(ActionSets.emberling_action_set),
    Entity.MossboundGuardianEnemy().SetName("Mossbound Guardian").SetMaxHealth(60, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.mossbound_action_set),
    Entity.TransformOnDeathEnemy(12, "split into multiple shards!", range(2,4)).SetName("Crystal Cluster").SetMaxHealth(42, setHealthToo=True).SetDropExp(range(2,5)).AttachActionSet(ActionSets.crystal_husk_action_set),
    Entity.BasicEnemy().SetName("Crystal Shard").SetMaxHealth(8, setHealthToo=True).SetDropExp(range(1,3)).DisableSpawnPool().AttachActionSet(ActionSets.crystal_shard_action_set),
    Entity.BasicEnemy().SetName("Mourning Shade").SetMaxHealth(50, setHealthToo=True).SetDropExp(range(1,3)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.mourning_shade_action_set),
    Entity.BasicEnemy().SetName("Bandit").SetMaxHealth(35, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.bandit_action_set),
    Entity.BasicEnemy().SetName("Carrion Maggot").SetMaxHealth(20, setHealthToo=True).SetDropExp(range(1,3)).AttachActionSet(ActionSets.carrion_maggot_action_set),
    Entity.CarrionHorrorEnemy().SetName("Carrion Horror").SetMaxHealth(225, setHealthToo=True).SetDropExp(range(24,37)).AttachActionSet(ActionSets.carrion_horror_action_set).DisableSpawnPool(),
    Entity.BasicEnemy().SetName("Thornback Tortoise").SetMaxHealth(100, setHealthToo=True).SetDropExp(range(1,6)).AttachActionSet(ActionSets.thornback_action_set),
    #Entity.BasicEnemy().SetName("Hollowed Prophet").SetMaxHealth(35, setHealthToo=True).SetDropExp(range(2,4)),
    #Entity.BasicEnemy().SetName("Cultist"),
    Entity.IroncladEnemy().SetName("Ironclad Marshal").SetMaxHealth(65, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.ironclad_action_set),
    Entity.MagmaBeastEnemy().SetName("Magmatic Beast").SetMaxHealth(36, setHealthToo=True).SetDropExp(range(2,4)).AttachActionSet(ActionSets.magma_beast_action_set),
    #Entity.BasicEnemy().SetName("Slime"),
    #Entity.BasicEnemy().SetName("Mimic"),
    #Entity.BasicEnemy().SetName("Vampire Spawn"),
]

__naturally_spawning_pool___ = []
