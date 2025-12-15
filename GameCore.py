import Items
import Entity
import Enemies
import random
from colorama import Fore, Back, Style

MAX_ENEMIES_IN_SCENE = 16

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

def Init():
    playerCharacter.name = input("Please state your name: ")
    if playerCharacter.name.strip() == "":
        playerCharacter.name = "Player"
    print("\nI see... your name is " + playerCharacter.name + "!"
           + "\n\nPlease take these items and begin your quest!!")
    playerCharacter.GiveItem(Items.GetItemByName("Rusty Sword"))
    playerCharacter.GiveItem(Items.GetItemByName("Lesser Health Potion"))

    SpawnEnemy(Enemies.CreateEnemyByName("Goblin"))

def SpawnEnemy(enemy: Entity.BasicEnemy | None, force: bool = False):
    global enemiesInScene
    global MAX_ENEMIES_IN_SCENE
    if enemy == None or (len(enemiesInScene) >= MAX_ENEMIES_IN_SCENE and not force):
        return
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

def GetAllEnemiesOfType(entityType: type) -> list | None:
    global enemiesInScene
    enemiesOfType = []
    if not issubclass(entityType, Entity.AEntity):
        return None
    
    for entity in enemiesInScene:
        if type(entity) is entityType:
            enemiesOfType.append(entity)

    return enemiesOfType

def CheckEncounterStatus(allowReward: bool = True):
    import Commands
    global enemiesInScene
    global playerCharacter
    global waitingLevelUpRewards
    if (len(enemiesInScene) > 0):
        return True
    if allowReward:
        GenerateReward(Commands)

    #for levelup in range(waitingLevelUpRewards):
    #    GiveLevelUpReward()

    waitingLevelUpRewards = 0
    EndPlayerTurn()
    ChooseNextEvent()

def GenerateReward(Commands):
    import Relics
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
    eventRoll = random.randrange(0, 100)
    if (eventRoll < 50):
        event = ge.GetRandomEvent()
        if (event != None):
            event.TriggerEvent()

    # Next encounter
    print("You venture deeper into the wilderness...")
    for i in range(0, random.randrange(1, 2 + playerCharacter.level.level // 5)):
        level = max(1, playerCharacter.level.level + random.randrange(-5, 3))
        enemy = Enemies.CreateRandomEnemy(1, level)
        if enemy is not None: 
            SpawnEnemy(enemy)

    OnCombatStart()

def OnCombatStart():
    import Relics
    import StatusEffect
    from AttackInfo import AttInfo
    from ElementTags import ElementTag
    global isFirstTurn
    global playerCharacter
    global playerHasAttackedThisTurn
    global enemiesInScene
    global currentTurn

    isFirstTurn = True
    currentTurn = 1
    playerHasAttackedThisTurn = False
    Relics.bloodOiledChainBonusDamagePerAttack = 0
    playerCharacter.bonusAttacks = 0
    playerCharacter._ironWillReady = True
    playerCharacter._unbreakableReady = True

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

    ProcessEnemyTurn()
    OnPlayerTurnStart()
    pass

def OnPlayerTurnStart():
    from time import sleep
    global playerCharacter
    global playerHasAttackedThisTurn
    global playerHasAttackedLastTurn
    global currentTurn

    print("\nNew turn!")
    currentTurn += 1
    playerCharacter.stamina = playerCharacter.maxStamina
    playerCharacter.DoTurn()
    playerHasAttackedLastTurn = playerHasAttackedThisTurn
    playerHasAttackedThisTurn = False

    if playerCharacter.stunCount > 0:
        playerCharacter.stunCount -= 1
        print(f"{Fore.MAGENTA}You are stunned and cannot act this turn!{Style.RESET_ALL}")
        sleep(2)
        EndPlayerTurn()

def ProcessEnemyTurn():
    global enemiesInScene
    global playerCharacter
    import copy, time
    import Relics
    import Commands
    Commands.c_clear()
    tmpList = copy.copy(enemiesInScene)

    # Don't bother if there are no enemies
    if len(tmpList) <= 0:
        return
    
    print("Processing enemy turn!\n")
    for enemy in tmpList:
        if playerCharacter.HasRelic(Relics.MindshackleTalisman):
            if random.randrange(0, 100) < int(Relics.MindshackleTalisman.SKIP_TURN_CHANCE * 100):
                print(f"{Fore.MAGENTA}The {Style.BRIGHT}{enemy.name}{Style.NORMAL}{Fore.MAGENTA} is unable to act this turn!{Style.RESET_ALL}")
                time.sleep(0.2)
                continue
        if enemy.stunCount > 0:
            enemy.stunCount -= 1
            print(f"{Fore.MAGENTA}The {Style.BRIGHT}{enemy.name}{Style.NORMAL}{Fore.MAGENTA} is stunned and cannot act this turn!{Style.RESET_ALL}")
            time.sleep(0.2)
            continue
        enemy.DoTurn()
        time.sleep(0.2)
    CheckEncounterStatus()

def OnLevelUp():
    import SkillSystem
    SkillSystem.playerSkillPoints += 1
    print(f"{Fore.YELLOW}Level up!{Fore.RESET} - +1 Skill Points!")
    pass
playerCharacter.level.e_OnLevelUp.Subscribe(OnLevelUp)