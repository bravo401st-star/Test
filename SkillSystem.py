from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Callable
import ShopSystem

playerSkillPoints = 0

# ===== SKILL STAT CONSTANTS =====
# Poison Tree
POISON_TOXIC_COATING_CHANCE = 0.10
POISON_LINGERING_VENOM_BONUS_DURATION = 2
POISON_WEAKENING_TOXINS_DEBUFF = -0.15
POISON_COMPOUNDING_DOSE_DAMAGE_BONUS = 2
POISON_TERMINAL_EXPLOSION_DAMAGE = 15

# Greed Tree
GREED_COIN_SENSE_BONUS = 0.15
GREED_GILDED_HANDS_SELL_BONUS = 0.30
GREED_SCAVENGERS_EYE_DROP_CHANCE = 0.10
GREED_BLOOD_FOR_COIN_GOLD = 5
GREED_MERCANTILE_POWER_GOLD_THRESHOLD = 25
GREED_MERCANTILE_POWER_DAMAGE_BONUS = 0.04
GREED_KING_OF_SPOILS_DISCOUNT = 0.20

# Berserker Tree
BERSERKER_RAGE_SPARK_HP_THRESHOLD = 0.80
BERSERKER_RAGE_SPARK_DAMAGE_BONUS = 0.02
BERSERKER_BLOOD_FRENZY_HP_THRESHOLD = 0.60
BERSERKER_BLOOD_FRENZY_STAMINA_GAIN = 1
BERSERKER_RECKLESS_ASSAULT_DAMAGE_BONUS = 0.08
BERSERKER_RECKLESS_ASSAULT_DAMAGE_TAKEN = 0.12
BERSERKER_PAIN_FUELED_POWER_BONUS = 0.03
BERSERKER_DEATH_OR_GLORY_HP_THRESHOLD = 0.30
BERSERKER_DEATH_OR_GLORY_DAMAGE_BONUS = 0.50

# Carrion Tree
CARRION_SEEPING_WOUND_CHANCE = 0.05
CARRION_ACCELERATED_DECAY_ROT_CHANCE_BONUS = 0.30
CARRION_PUTRID_CONVERSION_DAMAGE_BONUS = 4
CARRION_PUTREFIED_RESILIENCE_SHIELD_PER_STACK = 1
CARRION_INFECTIOUS_PRESENCE_CHANCE_TO_INFECT = 0.08

# Vampiric Tree
VAMPIRIC_BLOOD_TASTE_HEAL_PERCENT = 0.02
VAMPIRIC_SERRATED_BLOWS_CHANCE = 0.08
VAMPIRIC_CRIMSON_DRAIN_HEAL = 3
VAMPIRIC_SANGUINE_OVERFLOW_TEMP_HP_CAP = 20
VAMPIRIC_VEIN_REND_BLEED_STACKS = 2
VAMPIRIC_FEAST_ETERNAL_HEAL = 5
VAMPIRIC_FEAST_ETERNAL_DAMAGE_BONUS = 0.10

# Bulwark Tree
BULWARK_BRACE_DEFENSE = 4
BULWARK_HARDENED_SKIN_DAMAGE_REDUCTION = 0.02
BULWARK_TOUGH_AS_NAILS_MAX_HP_BONUS = 10
BULWARK_LAST_STAND_HP_THRESHOLD = 0.40
BULWARK_LAST_STAND_SHIELD_GAIN = 10

# Tactician Tree
TACTICIAN_CALCULATED_PATIENCE_DAMAGE_BONUS = 0.10
TACTICIAN_OPENING_GAMBIT_DAMAGE_BONUS = 0.25
TACTICIAN_PRESS_ADVANTAGE_STAMINA_GAIN = 1

# Alchemy Tree
ALCHEMY_POTENT_BREWS_STRENGTH_BONUS = 0.25
ALCHEMY_LINGERING_EFFECTS_DURATION_BONUS = 1
ALCHEMY_VOLATILE_REACTIONS_DAMAGE = 5
ALCHEMY_EMERGENCY_CONCOCTION_HP_THRESHOLD = 0.30
ALCHEMY_MASTER_ALCHEMIST_EXTRA_USES = 1

# Shadow Tree
SHADOW_LIGHTFOOT_EVASION = 0.10
SHADOW_SLIP_AWAY_DAMAGE_BONUS = 5
SHADOW_CRIPPLING_BLOWS_WEAK_DEBUFF = -0.10
SHADOW_UMBRAL_VEIL_DAMAGE_REDUCTION = 0.50
SHADOW_NO_WITNESSES_EVASION_BONUS = 0.15

@dataclass
class SkillNode():
    name: str = "Unnamed Node"
    id: str = "node_01"
    description: str = ""
    rank: int = 0
    maxRank: int = 1
    unlockCallback: list[Callable] = field(default_factory=list)
    rankUpCallback: list[Callable] = field(default_factory=list)

    def CanRankUp(self) -> bool:
        return self.rank < self.maxRank
    
    def IsUnlocked(self) -> bool:
        return self.rank > 0
    
    def OnUnlock(self):
        for callback in self.unlockCallback:
            callback()

    def OnRankUp(self):
        if self.rank == 0:
            self.OnUnlock()
        self.rank += 1
        for callback in self.rankUpCallback:
            callback()
    pass

class SkillTree():
    def __init__(self, name: str, id: str) -> None:
        self.name: str = name
        self.id: str = id
        self.unlocked: bool = False
        self.complete: bool = False
        self.nodes: list[SkillNode] = []

    def AppendNode(self, node: SkillNode):
        self.nodes.append(node)
        return self
    
    def TryInvest(self) -> bool:
        global playerSkillPoints
        if not self.unlocked:
            return False
        if playerSkillPoints <= 0:
            return False
        if self.complete:
            return False
        if len(self.nodes) <= 0:
            return False
        
        # get first node that can be unlocked/ranked up
        for node in self.nodes:
            if node.CanRankUp():
                node.OnRankUp()
                playerSkillPoints -= 1
                return True
        
        return False
    
    pass


def ModifyPlayerStat(statName: str, amount: float | int) -> Callable:
    def callback():
        import GameCore as gc
        if hasattr(gc.playerCharacter, statName):
            current = getattr(gc.playerCharacter, statName)
            setattr(gc.playerCharacter, statName, current + amount)
        else:
            print("INVALID PLAYER STAT")
    return callback

def IncreaseMaxHealth(amount: int) -> Callable:
    def callback():
        import GameCore as gc
        gc.playerCharacter.IncreaseMaxHealth(amount)
    return callback

# TODO: VAMPIRIC, BULWARK, TACTICIAN, ALCHEMY, SHADOW, POISON
__skill_trees__: list[SkillTree] = [

    SkillTree("Greed", "sktr_greed")
        .AppendNode(SkillNode(name="Coin Sense", id="sknd_coinsense", description=f"Gain +{int(GREED_COIN_SENSE_BONUS * 100)}% gold", maxRank=3, rankUpCallback=[ModifyPlayerStat("goldMultiplier", GREED_COIN_SENSE_BONUS)]))
        .AppendNode(SkillNode(name="Gilded Hands", id="sknd_gildedhands", description=f"Items sell for +{int(GREED_GILDED_HANDS_SELL_BONUS * 100)}% more gold.", maxRank=2, rankUpCallback=[lambda: setattr(ShopSystem.Shop, "shopSellPrice", ShopSystem.Shop.shopSellPrice + GREED_GILDED_HANDS_SELL_BONUS)]))
        .AppendNode(SkillNode(name="Scavenger's Eye", id="sknd_scavengerseye", description=f"Enemies have a +{int(GREED_SCAVENGERS_EYE_DROP_CHANCE * 100)}% chance to drop an extra item.", maxRank=5, rankUpCallback=[ModifyPlayerStat("lootDropChance", GREED_SCAVENGERS_EYE_DROP_CHANCE)]))
        .AppendNode(SkillNode(name="Blood for Coin", id="sknd_bloodforcoin", description=f"Heal 1 HP for every {GREED_BLOOD_FOR_COIN_GOLD} gold gained.", maxRank=1))
        .AppendNode(SkillNode(name="Mercantile Power", id="sknd_merchantpower", description=f"For every {GREED_MERCANTILE_POWER_GOLD_THRESHOLD} gold held, gain +{int(GREED_MERCANTILE_POWER_DAMAGE_BONUS * 100)}% damage.", maxRank=1))
        .AppendNode(SkillNode(name="King of Spoils", id="sknd_kingofspoils", description=f"Shops offer 1 relic and {int(GREED_KING_OF_SPOILS_DISCOUNT * 100)}% discounts.", maxRank=1, rankUpCallback=[lambda: setattr(ShopSystem.Shop, "shopPrices", ShopSystem.Shop.shopPrices - GREED_KING_OF_SPOILS_DISCOUNT), lambda: setattr(ShopSystem.Shop, "shopRelicCount", ShopSystem.Shop.shopRelicCount + 1)])),

    SkillTree("Berserker", "sktr_berserker")
        .AppendNode(SkillNode(name="Rage Spark", id="sknd_ragespark", description=f"Below {int(BERSERKER_RAGE_SPARK_HP_THRESHOLD * 100)}% HP, deal +{int(BERSERKER_RAGE_SPARK_DAMAGE_BONUS * 100)}% damage.", maxRank=5))
        .AppendNode(SkillNode(name="Blood Frenzy", id="sknd_bloodfrenzy", description=f"Below {int(BERSERKER_BLOOD_FRENZY_HP_THRESHOLD * 100)}% HP, gain +{BERSERKER_BLOOD_FRENZY_STAMINA_GAIN} stamina per turn.", maxRank=1))
        .AppendNode(SkillNode(name="Reckless Assault", id="sknd_recklessassault", description=f"Deal +{int(BERSERKER_RECKLESS_ASSAULT_DAMAGE_BONUS * 100)}% damage but take +{int(BERSERKER_RECKLESS_ASSAULT_DAMAGE_TAKEN * 100)}% damage.", maxRank=3, rankUpCallback=[ModifyPlayerStat("outgoingDamageMultiplier", BERSERKER_RECKLESS_ASSAULT_DAMAGE_BONUS), ModifyPlayerStat("damageResistance", -BERSERKER_RECKLESS_ASSAULT_DAMAGE_TAKEN)]))
        .AppendNode(SkillNode(name="Pain Fueled Power", id="sknd_painfueledpower", description=f"Each time you take damage, gain +{int(BERSERKER_PAIN_FUELED_POWER_BONUS * 100)}% damage next turn.", maxRank=4))
        .AppendNode(SkillNode(name="Unchecked Violence", id="sknd_uncheckedviolence", description=f"Your attacks cost 1 less stamina (min 1 stamina), but you lose 3 HP per attack.", maxRank=1))
        .AppendNode(SkillNode(name="Death or Glory", id="sknd_deathorglory", description=f"Below {int(BERSERKER_DEATH_OR_GLORY_HP_THRESHOLD * 100)}% HP, deal +{int(BERSERKER_DEATH_OR_GLORY_DAMAGE_BONUS * 100)}% damage and cannot evade.", maxRank=1)),
    
    SkillTree("Carrion", "sktr_carrion")
        .AppendNode(SkillNode(name="Seeping Wound", id="sknd_seepingwound", description=f"Your attacks have a +{int(CARRION_SEEPING_WOUND_CHANCE * 100)}% chance to apply Infection.", maxRank=4, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Infectious Presence", id="sknd_infectiouspresence", description=f"Enemies in combat have a +{int(CARRION_INFECTIOUS_PRESENCE_CHANCE_TO_INFECT * 100)}% chance per turn to gain Infection.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Accelerated Decay", id="sknd_accelerateddecay", description=f"Infection has a {int(CARRION_ACCELERATED_DECAY_ROT_CHANCE_BONUS * 100)}% higher chance per turn to create rot.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Putrid Conversion", id="sknd_putridconversion", description=f"When Infection creates rot, deal +{CARRION_PUTRID_CONVERSION_DAMAGE_BONUS} bonus damage to that enemy.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Putrefied Resilience", id="sknd_putrefiedresilience", description=f"For every stack of rot on an enemy, gain +{CARRION_PUTREFIED_RESILIENCE_SHIELD_PER_STACK} shield at the end of your turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Endless Decay", id="sknd_endlessdecay", description="Infection on enemies never runs out.", maxRank=1, rankUpCallback=[])),

    SkillTree("Vampiric", "sktr_vampiric")
        .AppendNode(SkillNode(name="Blood Taste", id="sknd_bloodtaste", description=f"Dealing damage heals you for {int(VAMPIRIC_BLOOD_TASTE_HEAL_PERCENT * 100)}% of damage dealt.", maxRank=5, rankUpCallback=[ModifyPlayerStat("lifesteal", VAMPIRIC_BLOOD_TASTE_HEAL_PERCENT)]))
        .AppendNode(SkillNode(name="Serrated Blows", id="sknd_serratedblows", description=f"Your attacks have a +{int(VAMPIRIC_SERRATED_BLOWS_CHANCE * 100)}% chance to apply Bleed.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Crimson Drain", id="sknd_crimsondrain", description=f"You heal +{VAMPIRIC_CRIMSON_DRAIN_HEAL} HP whenever Bleed deals damage.", maxRank=2, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Vein Rend", id="sknd_veinrend", description=f"Critical hits apply +{VAMPIRIC_VEIN_REND_BLEED_STACKS} Bleed stack and trigger bleeds on ALL enemies", maxRank=4, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Sanguine Overflow", id="sknd_sanguineoverflow", description=f"Healing beyond Max HP becomes temporary HP (up to {VAMPIRIC_SANGUINE_OVERFLOW_TEMP_HP_CAP}).", maxRank=1, rankUpCallback=[ModifyPlayerStat("maxTempHealth", VAMPIRIC_SANGUINE_OVERFLOW_TEMP_HP_CAP)]))
        .AppendNode(SkillNode(name="Feast Eternal", id="sknd_feasteternal", description=f"Each enemy killed while Bleeding restores {VAMPIRIC_FEAST_ETERNAL_HEAL} HP and grants +{int(VAMPIRIC_FEAST_ETERNAL_DAMAGE_BONUS * 100)}% damage for that turn.", maxRank=1, rankUpCallback=[])),

    SkillTree("Bulwark", "sktr_bulwark")
        .AppendNode(SkillNode(name="Brace", id="sknd_brace", description=f"Gain +{BULWARK_BRACE_DEFENSE} shield at the start of combat.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Hardened Skin", id="sknd_hardenedSkin", description=f"Take {int(BULWARK_HARDENED_SKIN_DAMAGE_REDUCTION * 100)}% less damage from all sources.", maxRank=5, rankUpCallback=[ModifyPlayerStat("damageResistance", BULWARK_HARDENED_SKIN_DAMAGE_REDUCTION)]))
        .AppendNode(SkillNode(name="Tough as Nails", id="sknd_toughasnails", description=f"Increase your maximum health by {BULWARK_TOUGH_AS_NAILS_MAX_HP_BONUS}", maxRank=4, rankUpCallback=[IncreaseMaxHealth(BULWARK_TOUGH_AS_NAILS_MAX_HP_BONUS)]))
        .AppendNode(SkillNode(name="Last Stand", id="sknd_laststand", description=f"Below {int(BULWARK_LAST_STAND_HP_THRESHOLD * 100)}% HP, gain +{BULWARK_LAST_STAND_SHIELD_GAIN} shield per turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Iron Will", id="sknd_ironwill", description="The first debuff applied to you each combat is negated.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Unbreakable", id="sknd_unbreakable", description="Once per combat, damage that would kill you leaves you at 1 HP instead.", maxRank=1, rankUpCallback=[])),

    SkillTree("Tactician", "sktr_tactician")
        .AppendNode(SkillNode(name="Calculated Patience", id="sknd_calculatedpatience", description=f"If you do not attack this turn, gain +{int(TACTICIAN_CALCULATED_PATIENCE_DAMAGE_BONUS * 100)}% damage on your next attack.", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Stored Momentum", id="sknd_storedmomentum", description=f"If you do not attack this turn, also gain +{TACTICIAN_PRESS_ADVANTAGE_STAMINA_GAIN} stamina next turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Opening Gambit", id="sknd_openinggambit", description=f"Your first attack each combat deals +{int(TACTICIAN_OPENING_GAMBIT_DAMAGE_BONUS * 100)}% damage.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Press the Advantage", id="sknd_presstheadvantage", description=f"After a crit or kill, gain +{TACTICIAN_PRESS_ADVANTAGE_STAMINA_GAIN} stamina next turn.", maxRank=1, rankUpCallback=[]))
        #.AppendNode(SkillNode(name="Enemy Exploitation", id="sknd_tacticalreset", description="If an enemy misses, delays, or skips, your next attack deals +30% damage.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Perfect Control", id="sknd_perfectcontrol", description="At the beginning of combat, take an extra turn.", maxRank=1, rankUpCallback=[])),

    SkillTree("Alchemy", "sktr_alchemy")
        .AppendNode(SkillNode(name="Quick Mix", id="sknd_quickmix", description="Using a potion costs no stamina.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Potent Brews", id="sknd_potentbrews", description=f"Health potions are +{int(ALCHEMY_POTENT_BREWS_STRENGTH_BONUS * 100)}% stronger.", maxRank=4, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Lingering Effects", id="sknd_lingeringeffects", description=f"Potion effects last +{ALCHEMY_LINGERING_EFFECTS_DURATION_BONUS} turn.", maxRank=5, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Volatile Reactions", id="sknd_volatilereactions", description=f"When you apply a debuff, deal +{ALCHEMY_VOLATILE_REACTIONS_DAMAGE} bonus damage.", maxRank=2, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Emergency Concoction", id="sknd_emergencyconcoction", description=f"Once per combat, auto-use a potion at {int(ALCHEMY_EMERGENCY_CONCOCTION_HP_THRESHOLD * 100)}% HP.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Master Alchemist", id="sknd_masteralchemist", description=f"Potions gain +{ALCHEMY_MASTER_ALCHEMIST_EXTRA_USES} extra use and cleanse 1 debuff.", maxRank=1, rankUpCallback=[])),

    SkillTree("Shadow", "sktr_shadow")
        .AppendNode(SkillNode(name="Lightfoot", id="sknd_lightfoot", description=f"Gain +{int(SHADOW_LIGHTFOOT_EVASION * 100)}% evasion.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Slip Away", id="sknd_slipaway", description=f"After dodging, gain +{SHADOW_SLIP_AWAY_DAMAGE_BONUS} damage next turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Crippling Blows", id="sknd_cripplingblows", description=f"Your attacks apply Weak ({int(SHADOW_CRIPPLING_BLOWS_WEAK_DEBUFF * 100)}% damage) for 1 turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Umbral Veil", id="sknd_umbralveil", description=f"After evading, gain {int(SHADOW_UMBRAL_VEIL_DAMAGE_REDUCTION * 100)}% damage reduction for 1 turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="No Witnesses", id="sknd_nowitnesses", description=f"Killing an enemy grants +{int(SHADOW_NO_WITNESSES_EVASION_BONUS * 100)}% evasion next turn.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Ghost Step", id="sknd_ghoststep", description="Once per combat, guarantee an evade and gain an extra action.", maxRank=1, rankUpCallback=[])),

    SkillTree("Poison", "sktr_poison")
        .AppendNode(SkillNode(name="Toxic Coating", id="sknd_toxiccoating", description=f"Your attacks have a +{int(POISON_TOXIC_COATING_CHANCE * 100)}% chance to apply Poison.", maxRank=5, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Lingering Venom", id="sknd_lingeringvenom", description=f"Poison lasts +{POISON_LINGERING_VENOM_BONUS_DURATION} turns.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Weakening Toxins", id="sknd_weakeningtoxins", description=f"Enemies suffering from Poison deal {int(POISON_WEAKENING_TOXINS_DEBUFF * 100)}% damage.", maxRank=4, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Compounding Dose", id="sknd_compoundingdose", description=f"Applying Poison to a poisoned enemy increases Poison damage by +{POISON_COMPOUNDING_DOSE_DAMAGE_BONUS}.", maxRank=1, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Venom Circulation", id="sknd_venomcirculation", description="When Poison deals damage, you gain +1 stamina (once per turn).", maxRank=3, rankUpCallback=[]))
        .AppendNode(SkillNode(name="Terminal Poison", id="sknd_terminalpoison", description=f"When Poison expires on an enemy, it explodes for {POISON_TERMINAL_EXPLOSION_DAMAGE} damage and applies 1 Poison to all other enemies.", maxRank=1, rankUpCallback=[])),

]

def GetSkillNodeRank(nodeID: str) -> int:
    """
    Gets the rank of a given nodeID\n
    (Node ids have a "sknd_NAME" format!)\n
    returns -1 if no node found!
    """
    node = GetSkillNode(nodeID)
    if node is not None:
        return node.rank
    return -1

def IsSkillNodeUnlocked(nodeID: str) -> bool:
    """
    Gets whether or not a skillnode has been unlocked\n
    (Node ids have a "sknd_NAME" format!)
    """
    node = GetSkillNode(nodeID)
    if node is not None:
        return node.IsUnlocked()
    return False

def GetSkillNode(nodeID: str) -> SkillNode | None:
    """
    Gets the node of a given nodeID!\n
    (Node ids have a "sknd_NAME" format!)\n
    returns None if no node found!
    """
    for tree in __skill_trees__:
        for node in tree.nodes:
            if node.id == nodeID:
                return node
    return None