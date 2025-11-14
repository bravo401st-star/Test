import Entity
import ActionSets

__enemy_pool__ = [
    Entity.BasicEnemy().SetName("Goblin").SetMaxHealth(50).SetHealth(50).SetDropExp(range(1, 3)).AttachActionSet(ActionSets.goblin_action_set),
    Entity.NecromancerEnemy().SetName("Goblin Necromancer").SetMaxHealth(35).SetHealth(35).SetDropExp(range(2, 4)).AttachActionSet(ActionSets.goblin_necromancer_action_set),
    Entity.BasicEnemy().SetName("Granite Golem").SetMaxHealth(120).SetHealth(120).SetDropExp(range(5, 15)).AttachActionSet(ActionSets.granite_golem_action_set)
]
