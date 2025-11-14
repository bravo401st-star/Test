import EnemyAttackPattern as AP

goblin_action_set = AP.ActionSet()
goblin_action_set.AppendAction(AP.AttackAction(10).SetName("Slash").SetShortDesc("Preparing to slash"))
goblin_action_set.AppendAction(AP.AttackAction(30).SetName("Stab").SetShortDesc("Preparing to stab"))
goblin_action_set.AppendAction(AP.HealAction(10).SetName("Heal").SetShortDesc("Healing self").SetChance(0.5))

goblin_necromancer_action_set = AP.ActionSet()
goblin_necromancer_action_set.AppendAction(AP.HealRandomUndeadAction("Undead Goblin").SetName("Heal Undead").SetShortDesc("Healing undead minion"))
goblin_necromancer_action_set.AppendAction(AP.AttackAction(5).SetName("Stab").SetShortDesc("Preparing to stab"))

granite_golem_action_set = AP.ActionSet()
granite_golem_action_set.AppendAction(AP.TauntAction("3...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.TauntAction("2...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.TauntAction("1...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.AttackAction(80).SetName("Smash").SetShortDesc("Preparing to SMASH"))
granite_golem_action_set.AppendAction(AP.TauntAction("HA HAH HA! PUNY HUMAN!").SetName("Taunt").SetShortDesc("Preparing to taunt yet again"))

