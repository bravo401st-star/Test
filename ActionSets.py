import Actions as AP
import StatusEffect
from colorama import Fore
from ElementTags import ElementTag

goblin_action_set = AP.ActionSet()
goblin_action_set.AppendAction(AP.AttackAction(10).SetName("Slash").SetShortDesc("Preparing to slash"))
goblin_action_set.AppendAction(AP.AttackAction(8).SetName("Stab").SetShortDesc("Preparing to stab").SetAttackCount(2))
goblin_action_set.AppendAction(AP.HealAction(10).SetName("Heal").SetShortDesc("Healing self").SetChance(0.5))

goblin_necromancer_action_set = AP.ActionSet()
goblin_necromancer_action_set.AppendAction(AP.HealRandomUndeadAction(50).SetName("Heal Undead").SetShortDesc("Healing undead minion"))
goblin_necromancer_action_set.AppendAction(AP.AttackAction(5).SetName("Stab").SetShortDesc("Preparing to stab"))

granite_golem_action_set = AP.ActionSet()
granite_golem_action_set.AppendAction(AP.TauntAction("3...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.TauntAction("2...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.TauntAction("1...").SetName("Taunt").SetShortDesc("Preparing to taunt"))
granite_golem_action_set.AppendAction(AP.AttackAction(80).SetName("Smash").SetShortDesc("Preparing to SMASH"))
granite_golem_action_set.AppendAction(AP.TauntAction("HA HAH HA! PUNY HUMAN!").SetName("Taunt").SetShortDesc("Preparing to taunt yet again"))

dire_wolf_action_set = AP.ActionSet()
dire_wolf_action_set.AppendAction(AP.AttackAction(15).SetName("Bite").SetShortDesc("Preparing to bite"))
dire_wolf_action_set.AppendAction(AP.AttackAction(20).SetName("Chomp").SetShortDesc("Preparing to chomp").SetChance(0.2))
dire_wolf_action_set.AppendAction(AP.BuffAlliesAction(5).SetName("Howl").SetShortDesc("Preparing to howl").SetChance(0.75))

troll_brute_action_set = AP.ActionSet()
troll_brute_action_set.AppendAction(AP.AttackAction(25).SetName("Punch").SetShortDesc("Preparing to punch"))
troll_brute_action_set.AppendAction(AP.AttackAction(10).SetName("Slap").SetShortDesc("Preparing to slap").SetChance(0.5))
troll_brute_action_set.AppendAction(AP.NothingAction().SetName("Clumsy").SetShortDesc("Clumsily falling over themselves").SetChance(0.7))

cave_bat_action_set = AP.ActionSet()
cave_bat_action_set.AppendAction(AP.AttackAction(5).SetName("Bite").SetShortDesc("Preparing to bite").SetChance(0.5).SetEffectsOnHit(StatusEffect.BleedEffect, StatusEffect.BleedEffect))
cave_bat_action_set.AppendAction(AP.AttackAction(2).SetName("Nibble").SetShortDesc("Preparing to nibble"))
cave_bat_action_set.AppendAction(AP.AttackAction(5).SetName("Bite").SetShortDesc("Preparing to bite").SetChance(0.5).SetEffectsOnHit(StatusEffect.BleedEffect, StatusEffect.BleedEffect))

bog_skeleton_action_set = AP.ActionSet()
bog_skeleton_action_set.AppendAction(AP.AttackAction(15).SetName("Slash").SetShortDesc("Preparing to slash").SetEffectsOnHit(StatusEffect.BoggedEffect, StatusEffect.BoggedEffect))

boggy_pile_action_set = AP.ActionSet()
boggy_pile_action_set.AppendAction(AP.NothingAction().SetName("Shaking").SetShortDesc("Suspicous shaking...").SetRepeat(range(3)).SetColor(Fore.WHITE))
boggy_pile_action_set.AppendAction(AP.TransformAction(6).SetName("Transform").SetShortDesc("Transforming into "))

wraith_action_set = AP.ActionSet()
wraith_action_set.AppendAction(AP.ApplyEffectToSelfAction(StatusEffect.PhaseShifted, 1).SetName("Phasing").SetShortDesc("Phase Shifting"))
wraith_action_set.AppendAction(AP.RemovePlayerBuffsAndAttackAction(8).SetName("Mirror Shatter").SetShortDesc("Shattering your illusion and hitting"))

emberling_action_set = AP.ActionSet()
emberling_action_set.AppendAction(AP.EmberlingGrow().SetName("Grow").SetShortDesc("Preparing to grow...").SetRepeat(range(4)))
emberling_action_set.AppendAction(AP.EmberlingDetonate().SetName("Detonate").SetShortDesc("Preparing to detonate"))

mossbound_action_set = AP.ActionSet()
mossbound_action_set.AppendAction(AP.AttackAction(25).SetName("Heavy Slam").SetShortDesc("Preparing to slam"))
mossbound_action_set.AppendAction(AP.ApplyEffectToSelfAction(StatusEffect.Resistance, 3).SetName("Sporeshield").SetShortDesc("Preparing to release spores").SetChance(0.5))

crystal_husk_action_set = AP.ActionSet()
crystal_husk_action_set.AppendAction(AP.AttackAction(8).SetName("Jab").SetShortDesc("Preparing to jab"))
crystal_husk_action_set.AppendAction(AP.ApplyEffectToPlayerAction(StatusEffect.Vulnerablity, 3).SetName("Resonance").SetShortDesc("Preparing to resonate"))

crystal_shard_action_set = AP.ActionSet()
crystal_shard_action_set.AppendAction(AP.AttackAction(15).SetName("Jab").SetShortDesc("Preparing to jab"))

mourning_shade_action_set = AP.ActionSet()
mourning_shade_action_set.AppendAction(AP.ApplyEffectToPlayerAction(StatusEffect.Weakness, 3).SetName("Weep").SetShortDesc("Preparing to weep").SetRepeat(range(3)))
mourning_shade_action_set.AppendAction(AP.SorrowFeedAction().SetName("Sorrow Feed").SetShortDesc("Preparing to feed off your sorrow..."))
mourning_shade_action_set.AppendAction(AP.AttackAction(3).SetName("Screech").SetShortDesc("Preparing to screech").SetAttackCount(3))

bandit_action_set = AP.ActionSet()
bandit_action_set.AppendAction(AP.StealAndAttackAction(12, range(5,20)).SetName("Mug").SetShortDesc("Preparing to mug and stab"))
bandit_action_set.AppendAction(AP.TauntAction("Heh heh easy money boys!").SetName("Taunt").SetShortDesc("Preparing to taunt").SetChance(0.1))
bandit_action_set.AppendAction(AP.EscapeAction("Ha ha! Sucker!").SetName("Escape").SetShortDesc("Preparing to escape...").SetChance(0.2))

thornback_action_set = AP.ActionSet()
thornback_action_set.AppendAction(AP.ApplyEffectToSelfAction(StatusEffect.ThornedEffect, 10).SetName("Shellcurl").SetShortDesc("Preparing to curl up in shell").SetRepeat(range(4)))
thornback_action_set.AppendAction(AP.NothingAction().SetName("Nothing").SetShortDesc("Moving very slowly...").SetRepeat(range(2)))
thornback_action_set.AppendAction(AP.DamageBasedOnThornsAction(2).SetName("Spineburst").SetShortDesc("Preparing to burst spines"))
thornback_action_set.AppendAction(AP.ProtectAction(15).SetName("Shield").SetShortDesc("Preparing to shield").SetRepeat(range(2)))

carrion_maggot_action_set = AP.ActionSet()
carrion_maggot_action_set.AppendAction(AP.TotallyHarmlessWiggleAction().SetName("Wiggle").SetShortDesc("Wiggling, seems harmless...").SetColor(Fore.WHITE).SetRepeat(range(5, 7)))
carrion_maggot_action_set.AppendAction(AP.TransformAction(16).SetName("Transform").SetShortDesc("Transforming into "))

carrion_horror_action_set = AP.ActionSet()
carrion_horror_action_set.AppendAction(AP.AttackAction(30).SetName("Devour").SetShortDesc("Preparing to devour").SetAttackCount(3).SetEffectsOnHit(StatusEffect.InfectionEffect, StatusEffect.PoisonEffect))
carrion_horror_action_set.AppendAction(AP.AttackAction(2).SetName("RendingFlurry").SetShortDesc("Preparing to rend").SetAttackCount(15).SetEffectsOnHit(StatusEffect.InfectionEffect).SetRepeat(range(3)))
carrion_horror_action_set.AppendAction(AP.SummonAction(15, 3).SetName("Spawn").SetShortDesc("Preparing to spawn").SetChance(0.5))
carrion_horror_action_set.AppendAction(AP.ShieldAndHealAction(100, 25).SetName("Bury").SetShortDesc("Preparing to bury itself").SetChance(0.5))

ironclad_action_set = AP.ActionSet()
ironclad_action_set.AppendAction(AP.ShieldRandomAlly(20, 3).SetName("Protect").SetShortDesc("Shielding a random ally").SetRepeat(3))
ironclad_action_set.AppendAction(AP.AttackAction(16).SetName("Slice").SetShortDesc("Preparing to slice").SetChance(0.5))

magma_beast_action_set = AP.ActionSet()
magma_beast_action_set.AppendAction(AP.AttackAction(10).SetName("Burn").SetShortDesc("Preparing to burn you").SetAttackCount(2).SetElement(ElementTag.FIRE))