import EnemyAttackPattern as AP

goblin_action_set = AP.ActionSet()
goblin_action_set.AppendAction(AP.AttackAction(10).SetName("Slash").SetShortDesc("Preparing to slash"))
goblin_action_set.AppendAction(AP.AttackAction(30).SetName("Stab").SetShortDesc("Preparing to stab"))
goblin_action_set.AppendAction(AP.HealAction(10).SetName("Heal").SetShortDesc("Healing self").SetChance(0.5))