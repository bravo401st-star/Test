import Entity
import ActionSets
from EnemyTags import EnemyTag
import StatusEffect

__enemy_pool__ = [
    Entity.BasicEnemy().SetName("Goblin").SetMaxHealth(35, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.goblin_action_set),
    Entity.NecromancerEnemy().SetName("Goblin Necromancer").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(2, 4)).AttachActionSet(ActionSets.goblin_necromancer_action_set),
    Entity.BasicEnemy().SetName("Granite Golem").SetMaxHealth(105, setHealthToo=True).SetDropExp(range(7, 10)).AttachActionSet(ActionSets.granite_golem_action_set),
    Entity.BasicEnemy().SetName("Dire Wolf").SetMaxHealth(40, setHealthToo=True).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.dire_wolf_action_set),
    Entity.TrollEnemy().SetName("Troll Brute").SetMaxHealth(75, setHealthToo=True).SetDropExp(range(5, 9)).AttachActionSet(ActionSets.troll_brute_action_set),
    Entity.BasicEnemy().SetName("Cave Bat").SetMaxHealth(10, setHealthToo=True).SetDropExp(range(1, 2)).AttachActionSet(ActionSets.cave_bat_action_set),
    Entity.TransformOnDeathEnemy(7, "collapsed into a strange pile!").SetName("Bog Skeleton").SetMaxHealth(30, setHealthToo=True).SetDropExp(range(1, 3)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.bog_skeleton_action_set),
    Entity.BasicEnemy().SetName("Boggy Bone Pile").SetMaxHealth(5, setHealthToo=True).SetDropExp(0).SetTags(EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.boggy_pile_action_set).DisableSpawnPool(),
    Entity.WraithEnemy().SetName("Wraith").SetMaxHealth(46, setHealthToo=True).SetDropExp(range(2,6)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.wraith_action_set),
    Entity.EmberlingEnemy().SetName("Emberling").SetMaxHealth(24, setHealthToo=True).SetDropExp(range(1,3)).AttachActionSet(ActionSets.emberling_action_set),
    Entity.MossboundGuardianEnemy().SetName("Mossbound Guardian").SetMaxHealth(60, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.mossbound_action_set),
    Entity.TransformOnDeathEnemy(12, "split into multiple shards!", range(2,4)).SetName("Crystal Cluster").SetMaxHealth(42, setHealthToo=True).SetDropExp(range(2,5)).AttachActionSet(ActionSets.crystal_husk_action_set),
    Entity.BasicEnemy().SetName("Crystal Shard").SetMaxHealth(8, setHealthToo=True).SetDropExp(range(1,3)).DisableSpawnPool().AttachActionSet(ActionSets.crystal_shard_action_set),
    Entity.BasicEnemy().SetName("Mourning Shade").SetMaxHealth(50, setHealthToo=True).SetDropExp(range(1,3)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.mourning_shade_action_set),
    Entity.BasicEnemy().SetName("Bandit").SetMaxHealth(35, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.bandit_action_set),
    Entity.BasicEnemy().SetName("Carrion Maggot").SetMaxHealth(20, setHealthToo=True).SetDropExp(range(1,3)).AttachActionSet(ActionSets.carrion_maggot_action_set),
    Entity.CarrionHorrorEnemy().SetName("Carrion Horror").SetMaxHealth(225, setHealthToo=True).SetDropExp(range(24,37)).AttachActionSet(ActionSets.carrion_horror_action_set).DisableSpawnPool(),
    Entity.BasicEnemy().SetName("Thornback Tortoise").SetMaxHealth(100, setHealthToo=True).SetDropExp(range(1,6)).AttachActionSet(ActionSets.thornback_action_set),
    Entity.BasicEnemy().SetName("Goblin Warlord").SetMaxHealth(50, setHealthToo=True).SetDropExp(range(3,6)).AttachActionSet(ActionSets.goblin_warlord_action_set),
    Entity.HollowedProphetEnemy().SetName("Hollowed Prophet").SetMaxHealth(65, setHealthToo=True).SetDropExp(range(2,4)).AttachActionSet(ActionSets.hollowed_prophet_action_set),
    Entity.IroncladEnemy().SetName("Ironclad Marshal").SetMaxHealth(20, setHealthToo=True).SetDropExp(range(1,4)).AttachActionSet(ActionSets.ironclad_action_set),
    Entity.MagmaBeastEnemy().SetName("Magmatic Beast").SetMaxHealth(36, setHealthToo=True).SetDropExp(range(2,4)).AttachActionSet(ActionSets.magma_beast_action_set),
    Entity.SlimeEnemy(splitName="Small Slime").SetName("Slime").SetMaxHealth(60, setHealthToo=True).SetDropExp(range(3,5)).AttachActionSet(ActionSets.slime_action_set),
    Entity.SlimeEnemy(splitName="Mini Slime").SetName("Small Slime").SetMaxHealth(22, setHealthToo=True).SetDropExp(range(2,4)).AttachActionSet(ActionSets.small_slime_action_set).DisableSpawnPool(),
    Entity.BasicEnemy().SetName("Mini Slime").SetMaxHealth(8, setHealthToo=True).SetDropExp(range(1,2)).AttachActionSet(ActionSets.mini_slime_action_set).DisableSpawnPool(),
    Entity.MimicEnemy().SetName("Mimic").SetMaxHealth(100, setHealthToo=True).SetDropExp(range(7,13)).AttachActionSet(ActionSets.mimic_action_set).DisableSpawnPool(),
    Entity.VampireSpawnEnemy().SetName("Vampire Spawn").SetMaxHealth(85, setHealthToo=True).SetDropExp(range(5,9)).SetTags(EnemyTag.UNDEAD).AttachActionSet(ActionSets.vampire_spawn_action_set),
    Entity.GiantSpiderEnemy().SetName("Giant Spider").SetMaxHealth(72, setHealthToo=True).SetDropExp(range(4,7)).AttachActionSet(ActionSets.giant_spider_action_set),
    Entity.EffectOnDeathEnemy(StatusEffect.InfectionEffect, 1).SetName("Plague Rat").SetMaxHealth(15, setHealthToo=True).SetDropExp(range(1,2)).AttachActionSet(ActionSets.plague_rat_action_set),
    Entity.ShadowAssassinEnemy().SetName("Shadow Assassin").SetMaxHealth(28, setHealthToo=True).SetDropExp(range(3,5)).AttachActionSet(ActionSets.shadow_assassin_action_set),

    # Boss - Cultist Ritual
    Entity.EldtritchEntityEnemy().SetName("Eldtritch Entity").SetMaxHealth(195, setHealthToo=True).SetDropExp(range(25,35)).SetTags(EnemyTag.BOSS, EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.eldtritch_entity_action_set).DisableSpawnPool(),
    Entity.BasicEnemy().SetName("Cultist").SetMaxHealth(60, setHealthToo=True).SetDropExp(range(1,3)).AttachActionSet(ActionSets.cultist_action_set).DisableSpawnPool(),

    # Boss - The Pale Warden
    Entity.PaleWardenEnemy().SetName("Pale Warden").SetMaxHealth(190, setHealthToo=True).SetDropExp(range(25,35)).SetTags(EnemyTag.BOSS, EnemyTag.UNDEAD).AttachActionSet(ActionSets.pale_warden_action_set).DisableSpawnPool(),
    Entity.BoundSoulEnemy().SetName("Bound Soul").SetMaxHealth(25, setHealthToo=True).SetDropExp(0).SetTags(EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.bound_soul_action_set).DisableSpawnPool(),

    # Boss - Plague Heart
    Entity.PlagueHeartEnemy().SetName("Plague Heart").SetMaxHealth(175, setHealthToo=True).SetDropExp(range(25,35)).SetTags(EnemyTag.BOSS, EnemyTag.CANT_BE_UNDEAD, EnemyTag.INFECTIOUS).AttachActionSet(ActionSets.plague_heart_action_set).DisableSpawnPool(),
    Entity.PlagueSporeEnemy().SetName("Plague Spore").SetMaxHealth(35, setHealthToo=True).SetDropExp(0).SetTags(EnemyTag.CANT_BE_UNDEAD, EnemyTag.INFECTIOUS).AttachActionSet(ActionSets.plague_spore_action_set).DisableSpawnPool(),

    # Boss - Ashen Revenant
    Entity.AshenRevenantEnemy().SetName("Ashen Revenant").SetMaxHealth(200, setHealthToo=True).SetDropExp(range(25,35)).SetTags(EnemyTag.BOSS, EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.ashen_revenant_action_set).DisableSpawnPool(),
    Entity.CinderWispEnemy().SetName("Cinder Wisp").SetMaxHealth(40, setHealthToo=True).SetDropExp(0).SetTags(EnemyTag.CANT_BE_UNDEAD).AttachActionSet(ActionSets.cinder_wisp_action_set).DisableSpawnPool(),

]

__naturally_spawning_pool___ = []
