import Items
import Entity
import Enemies
import random
from colorama import Fore, Back, Style

MAX_ENEMIES_IN_SCENE = 16

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
    import Relics
    global gameRunning
    global killCount
    global playerCharacter
    if entity == None:
        return
    if type(entity) is Entity.Player:
        print("You died!")
        gameRunning = False
        return
    
    if issubclass(type(entity), Entity.BasicEnemy):
        if playerCharacter.HasRelic(Relics.SoulvesselJar):
            Relics.soulvesselJarKillsNeeded -= 1
            if Relics.soulvesselJarKillsNeeded <= 0:
                Relics.soulvesselJarKillsNeeded = 20
                print(f"{Fore.CYAN}Your {Style.BRIGHT}Soulvessel Jar{Style.RESET_ALL}{Fore.CYAN} has filled and grants you a their energy!{Style.RESET_ALL}")
                playerCharacter.maxStamina += 1

        print(entity.name + " has died!")
        RemoveEnemyFromScene(entity)
        killCount += 1
        return
    pass
Entity.e_EntityDeath.Subscribe(OnEntityDie)

def RemoveEnemyFromScene(enemy):
    global enemiesInScene
    if enemy in enemiesInScene:
            enemiesInScene.remove(enemy)
            CheckEncounterStatus()
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

def CheckEncounterStatus():
    import Commands
    global enemiesInScene
    global playerCharacter
    if (len(enemiesInScene) > 0):
        return True
    GenerateReward(Commands)

    EndPlayerTurn()
    ChooseNextEvent()

def GenerateReward(Commands):
    import Relics
    global additionalLootChance

    itemsToGive = 1
    itemsToGive += int(additionalLootChance % 1)
    percentLeft = additionalLootChance - (itemsToGive - 1)
    if (additionalLootChance >= 1.0):
        print(f"{Fore.YELLOW}Your {Style.BRIGHT}Fortune's Emblem{Style.RESET_ALL}{Fore.YELLOW} glows brightly, increasing your loot!{Style.RESET_ALL}")

    # check if player has the relic that gives extra loot
    global playerCharacter
    if playerCharacter.HasRelic(Relics.FortunesEmblem) and random.randrange(0, 100) < percentLeft:
        if (additionalLootChance < 1.0):
            print(f"{Fore.YELLOW}Your {Style.BRIGHT}Fortune's Emblem{Style.RESET_ALL}{Fore.YELLOW} glows brightly, increasing your loot!{Style.RESET_ALL}")
        itemsToGive += 1
    
    rolls = 2 if playerCharacter.HasRelic(Relics.FortunesEmblem) else 1
    for i in range(0, itemsToGive):
        rewardItem = Items.GetRandomItem(True, rolls)
        if (Commands.PromptYesNoQuestion(f"You have defeated all enemies in the area! You find a {Style.BRIGHT}{Fore.MAGENTA}{rewardItem.name}{Style.RESET_ALL} as a reward. Do you want to keep it?", True, True)):
            playerCharacter.GiveItem(rewardItem)

    # give relic reward chance
    if playerCharacter.level.level >= 5 and random.randrange(0, 100) < 5:
        GiveRelicReward(Commands)

def GiveRelicReward(Commands):
    import Relics
    relicReward = Relics.GetRandomRelic()
    if (Commands.PromptYesNoQuestion(f"As a reward for your victory, you find a {Style.BRIGHT}{Fore.CYAN}{relicReward.name}{Style.RESET_ALL}. Do you want to keep it?", True, True)):
        playerCharacter.GiveRelic(relicReward)

def ChooseNextEvent():
    import GameEvent as ge
    eventRoll = random.randrange(0, 100)
    if (eventRoll < 50):
        event = ge.GetRandomEvent()
        if (event != None):
            event.TriggerEvent()

    # Next encounter
    print("You venture deeper into the wilderness...")
    for i in range(0, random.randrange(1, 4 + playerCharacter.level.level // 2)):
        level = max(1, playerCharacter.level.level + random.randrange(-1, 2))
        enemy = Enemies.CreateRandomEnemy(1, level)
        if enemy is not None: 
            SpawnEnemy(enemy)

    OnCombatStart()

def OnCombatStart():
    import Relics
    import StatusEffect
    global isFirstTurn
    global playerCharacter

    isFirstTurn = True

    if playerCharacter.HasRelic(Relics.TimewornHourglass):
        playerCharacter.shield += 15
        print(f"{Fore.CYAN}Your {Style.BRIGHT}Timeworn Hourglass{Style.RESET_ALL}{Fore.CYAN} grants you a shield that absorbs 15 damage!{Style.RESET_ALL}")

    if playerCharacter.HasRelic(Relics.XenolithFragment):
        buff = StatusEffect.GetRandomEffect(positive=True)
        StatusEffect.Apply(playerCharacter, buff, 1)

    if playerCharacter.HasRelic(Relics.Dreamcatcher):
        playerCharacter.stamina += 2
        print(f"{Fore.CYAN}Your {Style.BRIGHT}Dreamcatcher{Style.RESET_ALL}{Fore.CYAN} grants you +2 stamina for the first turn!{Style.RESET_ALL}")


def EndPlayerTurn():
    global playerCharacter
    global playerHasAttackedThisTurn
    global playerHasAttackedLastTurn
    global isFirstTurn

    isFirstTurn = False
    ProcessEnemyTurn()
    print("\n\nNew turn!")
    playerCharacter.stamina = playerCharacter.maxStamina
    playerCharacter.DoTurn()
    playerHasAttackedLastTurn = playerHasAttackedThisTurn
    playerHasAttackedThisTurn = False
    pass


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
            if random.randrange(0, 100) < 20:
                print(f"{Fore.MAGENTA}The {Style.BRIGHT}{enemy.name}{Style.RESET_ALL}{Fore.MAGENTA} is unable to act this turn!{Style.RESET_ALL}")
                time.sleep(0.2)
                continue
        enemy.DoTurn()
        time.sleep(0.2)


playerCharacter = Entity.Player().SetName("Player").SetMaxHealth(100).SetHealth(100)
enemiesInScene = []
gameRunning = True
showPlayerInfo = True
godmode = False
killCount = 0
playerHasAttackedThisTurn = False
playerHasAttackedLastTurn = False
goldMultiplier = 1.0
additionalLootChance = 0.0
isFirstTurn = True
experienceMultiplier = 1.0