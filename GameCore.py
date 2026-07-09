import Encounters
import Items
import Entity
import Enemies
import random
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Back, Style

MAX_ENEMIES_IN_SCENE = 16
ENCOUNTERS_TO_NEXT_BOSS = 25

playerCharacter = Entity.Player().SetName("Player").SetMaxHealth(max=100, setHealthToo=True)
enemiesInScene: list[Entity.BasicEnemy] = []
gameRunning = True
showPlayerInfo = True
godmode = False
killCount = 0
playerHasAttackedThisTurn = False
playerHasAttackedLastTurn = False
isFirstTurn = True
currentTurn = 1
currentAttacksCount = 0
currentHitsRecievedCount = 0
currentEncounterReference: Encounters.ABaseEncounter | None = None
totalEncountersCompleted = 0
usedCheats: bool = False

# Game settings
class EDifficulty(str, Enum):
    EASY = 0.7,
    NORMAL = 1,
    HARD = 1.5,
    IMPOSSIBLE = 2,
    ACTUALLY_IMPOSSIBLE = 4

@dataclass
class GameSettings():
    difficulty: EDifficulty
    pass

setDifficulty = EDifficulty.NORMAL

def Init():
    global setDifficulty
    import Commands
    # Setup settings
    while True:
        Commands.c_clear()
        for index, diff in enumerate(EDifficulty.__members__.keys(), 1):
            print(f"{index}. {diff}")
        choice = input("Choose a difficulty: ")
        if not choice.isdigit():
            continue

        index = int(choice)
        members = list(EDifficulty)
        if index <= 0 or index > len(members):
            continue
        
        setDifficulty = members[index - 1]
        Commands.c_clear()
        print(f"Difficulty set to: {setDifficulty.name.title()}")
        break


    playerCharacter.name = input("Please state your name: ")
    if playerCharacter.name.strip() == "":
        playerCharacter.name = "Player"
    print("\nI see... your name is " + playerCharacter.name + "!"
           + "\n\nPlease take these items and begin your quest!!")
    playerCharacter.GiveItem(Items.GetItemByName("Rusty Sword"))
    playerCharacter.GiveItem(Items.GetItemByName("Training Wooden Shield"))
    playerCharacter.GiveItem(Items.GetItemByName("Lesser Health Potion"))

    playerCharacter.damageResistance -= ((float(setDifficulty.value) - 1) / 1) * 0.25

    StartEncounter(Encounters.FirstEncounter())

def SpawnEnemy(enemy: Entity.BasicEnemy | None, force: bool = False, cacheToScene: bool = True):
    global enemiesInScene
    global MAX_ENEMIES_IN_SCENE
    if enemy == None or (len(enemiesInScene) >= MAX_ENEMIES_IN_SCENE and not force):
        return
    if cacheToScene:
        enemiesInScene.append(enemy)
    enemy.OnSpawn()
    print(f"A [LVL {enemy.level}]" + Fore.RED + Style.BRIGHT + enemy.name + Style.RESET_ALL + " has appeared!")
    pass

def GetIndexOfEnemy(enemy: Entity.BasicEnemy) -> int:
    global enemiesInScene
    index = 1

    for en in enemiesInScene:
        index += 1
        if en is enemy:
            break

    return index

def GetEntityByIndex(index: int):
    global enemiesInScene

    if (index < 0 or index > len(enemiesInScene)):
        return None

    if (index == 0):
        return playerCharacter
    else:
        return enemiesInScene[index - 1]
    
def GetRandomEnemyByType(searchType: type) -> Entity.BasicEnemy | None:
    global enemiesInScene
    listOfType = []
    for enemy in enemiesInScene:
        if issubclass(type(enemy), searchType):
            listOfType.append(enemy)

    if (len(listOfType) <= 0):
        return None
    return listOfType[random.randrange(0, len(listOfType))]

def GetRandomEnemyByTag(searchTag: str) -> Entity.BasicEnemy | None:
    global enemiesInScene
    listOfTag = []
    for enemy in enemiesInScene:
        if issubclass(type(enemy), Entity.BasicEnemy) and enemy.HasTag(searchTag):
            listOfTag.append(enemy)

    if (len(listOfTag) <= 0):
        return None
    return listOfTag[random.randrange(0, len(listOfTag))]
    
def OnEntityDie(entity: Entity.AEntity | None):
    global gameRunning
    global killCount
    global playerCharacter
    global enemiesInScene
    if entity == None:
        return
    if type(entity) is Entity.Player:
        print("You died!")
        gameRunning = False
        return
    
    if issubclass(type(entity), Entity.BasicEnemy):
        print(entity.name + " has died!")
        RemoveEnemyFromScene(entity) # type: ignore
        killCount += 1

        for enemy in enemiesInScene:
            if issubclass(type(enemy), Entity.NecromancerEnemy):
                enemy.TryToRaiseDead(entity) # pyright: ignore[reportAttributeAccessIssue]
                break
            enemy.actionSet.ValidateCurrentAction(False)
    pass
Entity.e_EntityDeath.Subscribe(OnEntityDie)

def RemoveEnemyFromScene(enemy: Entity.BasicEnemy):
    global enemiesInScene
    if enemy in enemiesInScene:
            enemiesInScene.remove(enemy)
            enemy.Cleanup()
            return True
    return False

def GetCountOfEntityType(entityType: type) -> int:
    global enemiesInScene
    count = 0
    if not issubclass(entityType, Entity.AEntity):
        return count
    
    for entity in enemiesInScene:
        if issubclass(type(entity), entityType):
            count += 1

    return count

def GetAllEnemiesOfType(entityType: type) -> list[Entity.AEntity] | None:
    global enemiesInScene
    enemiesOfType = []
    if not issubclass(entityType, Entity.AEntity):
        return None
    
    for entity in enemiesInScene:
        if type(entity) is entityType:
            enemiesOfType.append(entity)

    return enemiesOfType

def GetAllEnemiesOfName(enemyName: str):
    global enemiesInScene
    enemiesOfName = []
    for enemy in enemiesInScene:
        if enemy.name.lower() == enemyName.lower():
            enemiesOfName.append(enemy)

    return enemiesOfName

def IsEncounterActive() -> bool:
    if (len(enemiesInScene) > 0):
        return True
    return False

def CheckHandleEncounterEnd(allowReward: bool = True):
    import Commands
    global currentEncounterReference
    global enemiesInScene
    global playerCharacter
    if IsEncounterActive():
        return True
    if allowReward:
        currentEncounterReference.OnEncounterWin()
        currentEncounterReference = None

    OnCombatEnd()

def OnCombatEnd():
    import Commands
    global totalEncountersCompleted
    global currentEncounterReference
    playerCharacter.tempHealth = 0
    totalEncountersCompleted += 1
    currentEncounterReference = None

    EndPlayerTurn()
    Commands.c_clear()
    ChooseNextEvent()
    SetupNextCombatEncounter()

def GenerateReward():
    import Relics
    import Commands
    from math import floor
    global playerCharacter

    itemsToGive = floor(playerCharacter.lootDropChance)
    percentLeft = playerCharacter.lootDropChance - itemsToGive

    if random.random() < percentLeft:
        itemsToGive += 1
    
    rolls = 2 if playerCharacter.HasRelic(Relics.FortunesEmblem) else 1
    for _ in range(0, itemsToGive):
        rewardItem = Items.GetRandomItem(True, rolls)
        if (Commands.PromptYesNoQuestion(f"You have defeated all enemies in the area! You find a {Style.BRIGHT}{Fore.MAGENTA}{rewardItem.name}{Style.RESET_ALL} as a reward. Do you want to keep it?", True)):
            playerCharacter.GiveItem(rewardItem)

    # give relic reward chance
    if playerCharacter.level.level >= 5 and random.randrange(0, 100) < 5:
        GiveRelicReward()

def GiveRelicReward(relic = None):
    import Relics, Commands
    if relic is None:
        relic = Relics.GetRandomRelic()
    if not issubclass(type(relic), Relics.ARelic) or relic is None:
        return
    if (Commands.PromptYesNoQuestion(f"As a reward for your victory, you find a {Style.BRIGHT}{Fore.CYAN}{relic.name}{Style.RESET_ALL}. Do you want to keep it?", True)):
        playerCharacter.GiveRelic(relic)

def ChooseNextEvent():
    import GameEvent as ge

    # Roll for a random event
    eventRoll = random.randrange(0, 100)
    if (eventRoll < 50):
        event = ge.GetRandomEvent()
        if (event != None):
            event.TriggerEvent()
    
def SetupNextCombatEncounter():
    global currentEncounterReference
    import Encounters as enc

    if currentEncounterReference is not None:
        return

    if totalEncountersCompleted > 0 and totalEncountersCompleted % ENCOUNTERS_TO_NEXT_BOSS == 0:
        print(f"{Fore.YELLOW}A powerful presence can be felt nearby...{Style.RESET_ALL}")
        StartEncounter(enc.GetRandomBossEncounter())
        return

    encounter: Encounters.ABaseEncounter | None = None
    # Roll for a staged encounter
    eventRoll = random.randrange(0, 100)
    if (eventRoll < 15 and totalEncountersCompleted >= 10): # roll a pre-defined encounter if the player has completed at least 10 encounters
        encounter = enc.GetRandomEncounter(enc.__encounter_database__)
    else:
        encounter = enc.RandomEncounter()

    if encounter is not None:
        StartEncounter(encounter)

def StartEncounter(encounter: Encounters.ABaseEncounter):
    global currentEncounterReference
    currentEncounterReference = encounter
    encounter.Trigger()

def OnCombatStart():
    import Relics
    import StatusEffect
    import SkillSystem
    from AttackInfo import AttInfo
    from ElementTags import ElementTag
    global isFirstTurn
    global playerCharacter
    global playerHasAttackedThisTurn
    global enemiesInScene
    global currentTurn

    isFirstTurn = True
    currentTurn = 0
    playerHasAttackedThisTurn = False
    Relics.bloodOiledChainBonusDamagePerAttack = 0
    playerCharacter.bonusAttacks = 0
    playerCharacter._ironWillReady = True
    playerCharacter._unbreakableReady = True
    playerCharacter.successfulEvasionsThisCombat = 0
    OnPlayerTurnStart()

    if playerCharacter.HasRelic(Relics.TimewornHourglass):
        playerCharacter.shield += Relics.TimewornHourglass.SHIELD_AMOUNT
        print(f"{Fore.CYAN}Your {Style.BRIGHT}Timeworn Hourglass{Style.NORMAL} grants you a shield that absorbs {Relics.TimewornHourglass.SHIELD_AMOUNT} damage!{Style.RESET_ALL}")

    if playerCharacter.HasRelic(Relics.XenolithFragment):
        buff = StatusEffect.GetRandomEffect(negative=False, positive=True)
        StatusEffect.Apply(playerCharacter, buff, random.randint(1, 5))

    if playerCharacter.HasRelic(Relics.Dreamcatcher):
        playerCharacter.stamina += 2
        print(f"{Fore.CYAN}Your {Style.BRIGHT}Dreamcatcher{Style.NORMAL} grants you +{Relics.Dreamcatcher.EXTRA_STAMINA} stamina for the first turn!{Style.RESET_ALL}")
    
    if playerCharacter.HasRelic(Relics.CelestialOrb):
        playerCharacter.Heal(round(playerCharacter.maxHealth * Relics.CelestialOrb.HEAL_START_COMBAT_PERCENT))

    smolderingCoreCount = playerCharacter.GetRelicCount(Relics.SmolderingCore)
    if smolderingCoreCount > 0:
        Relics.TriggerSmolderingCore(Relics.SmolderingCore.START_BATTLE_FIRE_DAMAGE_TO_ALL * smolderingCoreCount)

    if playerCharacter.HasRelic(Relics.PhylacteryShard):
        negativeEffect = playerCharacter.GetRandomNegativeStatusEffect()
        if negativeEffect is not None:
            playerCharacter.RemoveEffect(negativeEffect)
            print(f"{Fore.CYAN}Your {Style.BRIGHT}Phylactery Shard{Style.NORMAL} removes {negativeEffect.GetName()}{Fore.CYAN} from you!{Style.RESET_ALL}")

    braceSkillRank = SkillSystem.GetSkillNodeRank("sknd_brace")
    if braceSkillRank > 0:
        playerCharacter.shield += SkillSystem.BULWARK_BRACE_DEFENSE * braceSkillRank

    ghostStepRank = SkillSystem.GetSkillNodeRank("sknd_ghoststep")
    if ghostStepRank > 0:
        playerCharacter.bonusAttacks += 1


def EndPlayerTurn():
    import SkillSystem
    import StatusEffect
    global isFirstTurn

    isFirstTurn = False
    playerCharacter._tempDamageBonus = 0

    putrefiedResilienceRank = SkillSystem.GetSkillNodeRank("sknd_putrefiedresilience")
    if putrefiedResilienceRank > 0:
        for enemy in enemiesInScene:
            playerCharacter.shield += SkillSystem.CARRION_PUTREFIED_RESILIENCE_SHIELD_PER_STACK * putrefiedResilienceRank * enemy.GetEffectStacks(StatusEffect.RotEffect)

    if not IsEncounterActive():
        return
    ProcessEnemyTurn()
    if not IsEncounterActive():
        return
    OnPlayerTurnStart()
    pass

def OnPlayerTurnStart():
    from time import sleep
    import SkillSystem
    import StatusEffect
    import Commands
    import Relics
    global playerCharacter
    global playerHasAttackedThisTurn
    global playerHasAttackedLastTurn
    global currentTurn

    print(f"\n{Fore.GREEN}{'─' * 15} Your Turn {'─' * 15}{Style.RESET_ALL}")
    currentTurn += 1
    playerCharacter.turnsSinceLastEvasion += 1
    playerCharacter._tempDamageResistanceBonus = 0
    playerCharacter._tempEvasionBonus = 0
    playerCharacter.stamina = playerCharacter.maxStamina
    playerCharacter.DoTurn()
    playerHasAttackedLastTurn = playerHasAttackedThisTurn
    playerHasAttackedThisTurn = False

    apexVenomRank = SkillSystem.GetSkillNodeRank("sknd_apexvenom")
    if apexVenomRank > 0:
        for enemy in enemiesInScene:
            if enemy.HasEffect(StatusEffect.PoisonEffect):
                playerCharacter._tempDamageBonus += apexVenomRank * SkillSystem.POISON_APEXPOISON_DAMAGE_GAIN

    scorchingPresenceRank = SkillSystem.GetSkillNodeRank("sknd_scorchingpresence")
    if scorchingPresenceRank > 0:
        for enemy in enemiesInScene:
            StatusEffect.Apply(enemy, StatusEffect.OnFireEffect, scorchingPresenceRank * SkillSystem.PYRO_IGNITE_AMOUNT)

    if playerCharacter.stunCount > 0:
        playerCharacter.stunCount -= 1
        print(f"{Fore.MAGENTA}You are stunned and cannot act this turn!{Style.RESET_ALL}")
        sleep(2)
        EndPlayerTurn()
    playerCharacter.HandleNewTurn()
    
    thornBackRelicCount = playerCharacter.GetRelicCount(Relics.ThornbackTortoiseShell)
    if thornBackRelicCount > 0:
        playerCharacter.shield += Relics.ThornbackTortoiseShell.EXTRA_SHIELD_PER_TURN * thornBackRelicCount


def ProcessEnemyTurn():
    global enemiesInScene
    global playerCharacter
    import copy, time
    import Relics
    import Commands
    Commands.c_clear()
    tmpList = copy.copy(enemiesInScene)
    print(f"\n{Fore.RED}{'─' * 14} Enemies Act {'─' * 14}{Style.RESET_ALL}")
    # Don't bother if there are no enemies
    if len(tmpList) <= 0:
        return
    
    for enemy in tmpList:
        enemy.HandleNewTurn()
    
    print("Processing enemy turn!\n")
    for enemy in tmpList:
        enemy.DoTurn()
        time.sleep(0.2)
    CheckHandleEncounterEnd()

def OnLevelUp():
    import SkillSystem
    SkillSystem.playerSkillPoints += 1
    print(f"{Fore.YELLOW}Level up!{Fore.RESET} - +1 Skill Points!")
    pass
playerCharacter.level.e_OnLevelUp.Subscribe(OnLevelUp)